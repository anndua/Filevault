
from fastapi import APIRouter, Depends,UploadFile,File,HTTPException
from uuid import UUID
from dependencies import get_complete_upload_service, get_rate_limiter

from dependencies import (
    get_current_user,
    get_upload_session_service,
    get_chunk_service
)
from models import User
from schemas import UploadInitiateRequest
from services.chunk_service import ChunkService
from services.upload_session import UploadSessionService
from services.complete_upload import CompleteUploadService
from storage.exceptions import StorageError, UploadIncomplete, UploadSessionNotFound
from services.rate_limiter import RateLimitExceeded, RateLimiter
from config import upload_rate_limit, chunk_rate_limit


router = APIRouter(
    prefix="/uploads",
    tags=["Uploads"],
)

@router.post("/initiate")
def initiate_upload(
    request:UploadInitiateRequest,
    current_user:User=Depends(get_current_user),
    upload_session_service:UploadSessionService=Depends(get_upload_session_service),
    limiter: RateLimiter = Depends(get_rate_limiter)):
    try:
        limiter.consume("upload-initiate", str(current_user.id), upload_rate_limit, 60)
    except RateLimitExceeded as exc:
        raise HTTPException(status_code=429, detail="Upload initiation rate limit exceeded",
                            headers={"Retry-After": str(exc.retry_after)}) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    
    session=upload_session_service.initiate_upload(
        user_id=current_user.id,
        filename=request.filename,
        total_chunks=request.total_chunks
    )
    
    
    return {
        "upload_id":session.upload_id,
        "object_key":session.object_key
    }
@router.post("/{upload_id}/chunks/{chunk_number}")
def upload_chunk(
    upload_id:UUID,
    chunk_number:int,
    file:UploadFile=File(...),
    current_user:User=Depends(get_current_user),
    chunk_service:ChunkService=Depends(get_chunk_service),
    limiter: RateLimiter = Depends(get_rate_limiter),
):
    try:
        limiter.consume("upload-chunk", str(current_user.id), chunk_rate_limit, 60)
    except RateLimitExceeded as exc:
        raise HTTPException(status_code=429, detail="Chunk upload rate limit exceeded",
                            headers={"Retry-After": str(exc.retry_after)}) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    try:
        saved_chunk=chunk_service.upload_chunk(
            upload_id=upload_id,
            chunk_number=chunk_number,
            user_id=current_user.id,
            data=file.file
        )
    except UploadSessionNotFound as exc:
        raise HTTPException(status_code=404, detail="Upload session not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except StorageError as exc:
        raise HTTPException(status_code=503, detail="Object storage is unavailable") from exc
   
    return {
        "message":"chunk uploded succesfully",
        "chunk_number":saved_chunk.chunk_number
    }
@router.post("/{upload_id}/complete")
def complete_upload(upload_id:UUID,
                    current_user:User=Depends(get_current_user),
                    complete_upload_service:CompleteUploadService=Depends(get_complete_upload_service)):
    try:
        complete_upload_service.complete_upload(upload_id, current_user.id)
    except UploadSessionNotFound as exc:
        raise HTTPException(status_code=404, detail="Upload session not found") from exc
    except UploadIncomplete as exc:
        raise HTTPException(status_code=400, detail="Upload is missing chunks") from exc
    except StorageError as exc:
        raise HTTPException(status_code=503, detail="Object storage is unavailable") from exc

    return {
        "message": "upload completed successfully"
    }
    
    
  
