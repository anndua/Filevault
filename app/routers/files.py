from fastapi import APIRouter,Depends,UploadFile,File,HTTPException

from dependencies import(get_current_user,get_upload_service,get_download_service)
from models import User
from services.upload import UploadServices
from services.download_service import DownloadService
router=APIRouter(
    prefix="/files",
    tags=["Files"]

)
@router.get("/")
def list_files(file_id:int,current_user:User=Depends(get_current_user),
               Upload_services:UploadServices =Depends(get_upload_service)):
    file=Upload_services.get_file(file_id)
    if file.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Forbidden"
        )
    return file

@router.post("/upload")
def upload_file(file:UploadFile=File(...),
                current_user:User=Depends(get_current_user),
                upload_Services:UploadServices=Depends(get_upload_service)):
    saved_file =upload_Services.upload(
        user_id=current_user.id,
        filename=file.filename,
        content_type=file.content_type,
        data=file.file
    )
    return {"message":"file uploaded",
            "id":saved_file.id}
@router.get("/{file_id}")
def get_file(
    file_id:int,
    current_user:User=Depends(get_current_user),
    upload_sevice:UploadServices=Depends(get_upload_service)):
    file=upload_sevice.get_file(file_id)
    if file.owner_id !=current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Forbidden"
        )
    return file


   
@router.delete("/{file_id}")
def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    upload_service: UploadServices = Depends(get_upload_service),
):
    file = upload_service.get_file(file_id)

    if file.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Forbidden"
        )

    upload_service.delete_file(file_id)

    return {
        "message": "File deleted"
    }   
@router.get("/{file_id}/download")
def download_file(file_id:int,current_user:User=Depends(get_current_user),
                  download_service:DownloadService=Depends(get_download_service)):
    url=download_service.get_download_url(
        file_id=file_id,
        user=current_user
    )
    return{
        "url":url,
        "expires_in":30
    }


    



