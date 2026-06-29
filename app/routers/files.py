from fastapi import APIRouter,Depends,UploadFile,File

from dependencies import(get_current_user,get_upload_services)
from models import User
from services.upload import UploadServices
router=APIRouter(
    prefix="/files",
    tags=["Files"]

)
@router.post("/upload")
def upload_file(file:UploadFile=File(...),
                current_user:User=Depends(get_current_user),
                upload_Services:UploadServices=Depends(get_upload_services)):
    key=upload_Services.upload(user_id=current_user.id,
                               filename=file.filename,
                               data=file.file)
    return {"message":"file uploaded",
            key:key}
    


