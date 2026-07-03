from pydantic import BaseModel
from sqlmodel import SQLModel

class UserCreate(BaseModel):
    email:str
    password:str

class UserResponse(BaseModel):
    id:int
    email:str

class UserLogin(BaseModel):
    email:str
    password:str


class UploadInitiateRequest(SQLModel):
    filename: str
    total_chunks: int 