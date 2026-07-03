
from fastapi import APIRouter, Depends

from dependencies import (
    get_current_user,
    get_upload_session_service,
)
from models import User
from schemas import UploadInitiateRequest
from services.upload_session import UploadSessionService

router = APIRouter(
    prefix="/uploads",
    tags=["Uploads"],
)

@router.post("/initiate")
def initiate_upload(
    request:UploadInitiateRequest,
    current_user:User=Depends(get_current_user),
    upload_session_service:UploadSessionService=Depends(get_upload_session_service)):
    
    session=upload_session_service.initiate_upload(
        user_id=current_user.id,
        filename=request.filename,
        total_chunks=request.total_chunks
    )
    
    return {
        "upload_id":session.upload_id,
        "object_key":session.object_key
    }
  
