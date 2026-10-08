from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose.exceptions import JWTError
from sqlmodel import Session
from config import endpoint,public_endpoint,minio_region,access_key,secret_key,bucket,secure,redis_url
from db import get_session
from security import decode_access_token
from  service import get_user_by_email
from pathlib import Path
from storage.minio_storage import MinioStorage
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
from services.complete_upload import CompleteUploadService
from services.download_service import DownloadService
from repositories.postgres_share_repository import PostgresShareRepository
from repositories.share_repository import ShareRepository
from services.share_service import ShareService
from services.rate_limiter import RateLimiter
import redis
from functools import lru_cache
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token:str=Depends(oauth2_scheme),session:Session=Depends(get_session)):
    try:
        payload=decode_access_token(token)
    except (ValueError, JWTError) as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired access token") from exc
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

def get_storage()->storageBackend:
    return MinioStorage(
        endpoint=endpoint,
        access_key=access_key,
        secret_key=secret_key,
        bucket=bucket,
        secure=secure,
        public_endpoint=public_endpoint,
        region=minio_region
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

def get_complete_upload_service(storage:storageBackend=Depends(get_storage),
                                upload_session_repository:UploadSessionRepository=Depends(get_upload_session_repository),
                                chunk_repository:ChunkRepository=Depends(get_chunk_repository),
                                file_repository:FileRepsitory=Depends(get_file_repository)):
    return CompleteUploadService(
        storage=storage,
        upload_session_repository=upload_session_repository,
        chunk_repository=chunk_repository,
        file_repository=file_repository
    ) 
def get_download_service(
        storage:storageBackend =Depends(get_storage),
        file_repository:FileRepsitory=Depends(get_file_repository)
):
    return DownloadService(
        storage=storage,
        file_repository=file_repository
    )

def get_share_repository(session: Session = Depends(get_session)) -> ShareRepository:
    return PostgresShareRepository(session)

def get_share_service(
    storage: storageBackend = Depends(get_storage),
    file_repository: FileRepsitory = Depends(get_file_repository),
    share_repository: ShareRepository = Depends(get_share_repository),
) -> ShareService:
    return ShareService(storage, file_repository, share_repository)

@lru_cache(maxsize=1)
def get_rate_limiter() -> RateLimiter:
    client = redis.Redis.from_url(
        redis_url,
        socket_connect_timeout=2,
        socket_timeout=2,
        decode_responses=False,
    )
    return RateLimiter(client)
