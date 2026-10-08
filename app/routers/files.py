from typing import Literal

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import RedirectResponse

from config import share_public_base_url
from dependencies import (
    get_current_user,
    get_download_service,
    get_share_service,
    get_upload_service,
)
from models import User
from schemas import (
    FileDetailResponse,
    FileListResponse,
    FileResponse,
    ShareCreateRequest,
    ShareResponse,
)
from services.download_service import DownloadService
from services.share_service import ShareExpired, ShareLimitReached, ShareService
from services.upload import UploadServices
from storage.exceptions import (
    FileAccessDenied,
    FileNotFound,
    ShareNotFound,
    StorageError,
)

router = APIRouter(prefix="/files", tags=["Files"])
public_share_router = APIRouter(prefix="/share", tags=["Sharing"])


def _storage_unavailable(exc: StorageError) -> HTTPException:
    return HTTPException(status_code=503, detail="Object storage is unavailable")


@router.get("/", response_model=FileListResponse | FileDetailResponse)
def list_files(
    file_id: int | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, max_length=255),
    sort_by: Literal["filename", "size", "created_at"] = "created_at",
    sort_order: Literal["asc", "desc"] = "desc",
    current_user: User = Depends(get_current_user),
    upload_service: UploadServices = Depends(get_upload_service),
):
    if file_id is not None:
        try:
            file = upload_service.get_file(file_id)
        except FileNotFound as exc:
            raise HTTPException(status_code=404, detail="File not found") from exc
        if file.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        return file

    total = upload_service.count_files(current_user.id, search)
    files = upload_service.search_files(
        owner_id=current_user.id,
        offset=(page - 1) * page_size,
        limit=page_size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return {
        "items": files,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    upload_service: UploadServices = Depends(get_upload_service),
):
    try:
        saved_file = upload_service.upload(
            user_id=current_user.id,
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            data=file.file,
        )
    except StorageError as exc:
        raise _storage_unavailable(exc) from exc
    return {"message": "file uploaded", "id": saved_file.id}


@router.get("/{file_id}", response_model=FileDetailResponse)
def get_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    upload_service: UploadServices = Depends(get_upload_service),
):
    try:
        file = upload_service.get_file(file_id)
    except FileNotFound as exc:
        raise HTTPException(status_code=404, detail="File not found") from exc
    if file.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return file


@router.get("/{file_id}/download")
def download_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    download_service: DownloadService = Depends(get_download_service),
):
    try:
        url = download_service.get_download_url(file_id=file_id, user=current_user)
    except FileNotFound as exc:
        raise HTTPException(status_code=404, detail="File not found") from exc
    except FileAccessDenied as exc:
        raise HTTPException(status_code=403, detail="Forbidden") from exc
    except StorageError as exc:
        raise _storage_unavailable(exc) from exc
    return {"url": url, "expires_in": 300}


@router.delete("/{file_id}")
def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    upload_service: UploadServices = Depends(get_upload_service),
):
    try:
        file = upload_service.get_file(file_id)
        if file.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        upload_service.delete_file(file_id)
    except FileNotFound as exc:
        raise HTTPException(status_code=404, detail="File not found") from exc
    except StorageError as exc:
        raise _storage_unavailable(exc) from exc
    return {"message": "File deleted"}


@router.post("/{file_id}/share", response_model=ShareResponse, status_code=201)
def create_share(
    file_id: int,
    request: Request,
    body: ShareCreateRequest,
    current_user: User = Depends(get_current_user),
    share_service: ShareService = Depends(get_share_service),
):
    try:
        share, token = share_service.create(
            file_id=file_id,
            owner_id=current_user.id,
            expires_in_hours=body.expires_in_hours,
            max_downloads=body.max_downloads,
        )
    except FileNotFound as exc:
        raise HTTPException(status_code=404, detail="File not found") from exc
    except FileAccessDenied as exc:
        raise HTTPException(status_code=403, detail="Forbidden") from exc
    base_url = share_public_base_url or str(request.base_url).rstrip("/")
    return {
        "id": share.id,
        "share_url": f"{base_url}/share/{token}",
        "expires_at": share.expires_at,
        "download_count": share.download_count,
        "max_downloads": share.max_downloads,
        "revoked": share.revoked,
    }


@router.get("/{file_id}/shares", response_model=list[ShareResponse])
def list_shares(
    file_id: int,
    current_user: User = Depends(get_current_user),
    share_service: ShareService = Depends(get_share_service),
):
    try:
        shares = share_service.list_for_file(file_id, current_user.id)
    except FileNotFound as exc:
        raise HTTPException(status_code=404, detail="File not found") from exc
    except FileAccessDenied as exc:
        raise HTTPException(status_code=403, detail="Forbidden") from exc
    return [
        {
            "id": share.id,
            "share_url": None,
            "expires_at": share.expires_at,
            "download_count": share.download_count,
            "max_downloads": share.max_downloads,
            "revoked": share.revoked,
        }
        for share in shares
    ]


@router.delete("/{file_id}/share/{share_id}", response_model=ShareResponse)
def revoke_share(
    file_id: int,
    share_id: int,
    current_user: User = Depends(get_current_user),
    share_service: ShareService = Depends(get_share_service),
):
    try:
        share = share_service.revoke(share_id, file_id, current_user.id)
    except ShareNotFound as exc:
        raise HTTPException(status_code=404, detail="Share link not found") from exc
    return {
        "id": share.id,
        "share_url": None,
        "expires_at": share.expires_at,
        "download_count": share.download_count,
        "max_downloads": share.max_downloads,
        "revoked": share.revoked,
    }


@public_share_router.get("/{token}", include_in_schema=True)
def download_shared_file(
    token: str,
    share_service: ShareService = Depends(get_share_service),
):
    try:
        url = share_service.get_download_url(token)
    except ShareNotFound as exc:
        raise HTTPException(status_code=404, detail="Share link not found") from exc
    except ShareExpired as exc:
        raise HTTPException(status_code=410, detail="Share link has expired") from exc
    except ShareLimitReached as exc:
        raise HTTPException(status_code=410, detail="Share download limit reached") from exc
    except StorageError as exc:
        raise _storage_unavailable(exc) from exc
    return RedirectResponse(url=url, status_code=307)
