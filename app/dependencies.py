from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from db import get_session
from security import decode_access_token
from  service import get_user_by_email
from pathlib import Path

from storage.local import LocalStrorage
from services.upload import UploadServices
from storage.base import storageBackend
from repositories.file_repository import FileRepsitory
from repositories.postgres_file_repository import PostgresFileRepository
from services.upload_session import UploadSessionService
from repositories.postgres_upload_session_repository import PostgresUploadSessionRepository
from repositories.postgres_chunk_repository import PostgressChunkRepository
from services.chunk_service import ChunkService
from repositories.chunk_repositiry import ChunkRepository
from repositories.upload_session_repository import UploadSessionRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token:str=Depends(oauth2_scheme),session:Session=Depends(get_session)):
    payload=decode_access_token(token)
    email=payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=401,
            detail="invalid"
        )
    user=get_user_by_email(email,session)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="user not found"
        )
    return user

def get_storage()->LocalStrorage:

    return LocalStrorage(
        root=Path("storage_data/objects")
    )
def get_file_repository(
        session:Session=Depends(get_session)
):
    return PostgresFileRepository(session)

def get_upload_service(
        storage:storageBackend=Depends(get_storage),
        file_repository:FileRepsitory=Depends(get_file_repository),
):
    return UploadServices(
        storage=storage,
        file_repository=file_repository
    )


    

def get_upload_session_repository(
        session:Session=Depends(get_session)
):
    return PostgresUploadSessionRepository(session)

def get_upload_session_service(
        repository:PostgresUploadSessionRepository=Depends(get_upload_session_repository)):
    return UploadSessionService(repository)

def get_chunk_repository(
        session:Session=Depends(get_session)
):
    return PostgressChunkRepository(session)

def get_chunk_service(
        storage:storageBackend=Depends(get_storage),
        upload_session_repository:UploadSessionRepository=Depends(get_upload_session_repository),
        chunk_repository:ChunkRepository=Depends(get_chunk_repository)):
    return ChunkService(
        storage=storage,
        upload_session_repository=upload_session_repository,
        chunk_repository=chunk_repository
    )


