
from fastapi import APIRouter, Depends,UploadFile,File
from uuid import UUID

from dependencies import (
    get_current_user,
    get_upload_session_service,
    get_chunk_service
)
from models import User
from schemas import UploadInitiateRequest
from services.chunk_service import ChunkService
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
@router.post("/{upload_id}/chunks/{chunk_number}")
def upload_chunk(
    upload_id:UUID,
    chunk_number:int,
    file:UploadFile=File(...),
    current_user:User=Depends(get_current_user),
    chunk_service:ChunkService=Depends(get_chunk_service)
):
    saved_chunk=chunk_service.upload_chunk(
        upload_id=upload_id,
        chunk_number=chunk_number,
        data=file.file
    )
   
    return {
        "message":"chunk uploded succesfully",
        "chunk_number":saved_chunk.chunk_number
    }
    
  
