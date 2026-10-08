from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email:EmailStr
    password:str=Field(min_length=8,max_length=128)

class UserResponse(BaseModel):
    id:int
    email:str

class UserLogin(BaseModel):
    email:EmailStr
    password:str=Field(min_length=8,max_length=128)


class UploadInitiateRequest(BaseModel):
    filename: str=Field(min_length=1,max_length=255)
    total_chunks: int=Field(gt=0,le=10000)


class FileResponse(BaseModel):
    id: int
    filename: str
    size: int
    content_type: str
    status: str
    created_at: datetime


class FileDetailResponse(FileResponse):
    object_key: str
    owner_id: int


class FileListResponse(BaseModel):
    items: list[FileResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class ShareCreateRequest(BaseModel):
    expires_in_hours: int = Field(default=24, ge=1, le=720)
    max_downloads: int | None = Field(default=None, ge=1, le=10000)


class ShareResponse(BaseModel):
    id: int
    share_url: str | None
    expires_at: datetime
    download_count: int
    max_downloads: int | None
    revoked: bool