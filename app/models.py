from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel,Field,Relationship
from uuid import UUID,uuid4
from datetime import datetime
from typing import Optional

class User(SQLModel,table=True):
    id:int |None =Field(default=None,primary_key=True)
    email:str
    hashed_password:str
    created_at:datetime=Field(default_factory=datetime.utcnow)
    files:list["File"]=Relationship(back_populates="owner")

class File(SQLModel,table=True):
    id:int|None=Field(default=None,primary_key=True)
    filename:str
    object_key: str=Field(unique=True,index=True)
    size:int
    content_type:str
    status:str=Field(default="READY")
    created_at:datetime=Field(default_factory=datetime.utcnow)
    owner_id:int=Field(foreign_key="user.id")
    owner:Optional["User"]=Relationship(back_populates="files") #we using optional coz initiall files.owner might not be fetched


class UploadSession(SQLModel,table=True):
    id:Optional[int]=Field(default=None,primary_key=True)
    upload_id:UUID =Field(default_factory=uuid4,index=True)

    filename:str

    object_key:str
    owner_id:int =Field(foreign_key="user.id")
    status:str=Field(default="INITIATED")
    total_chunks:int
    uploaded_chunks:int =Field(default=0)
    created_at:datetime=Field(default_factory=datetime.utcnow)


class Chunk(SQLModel,table=True):
    id:int |None =Field(default=None,primary_key=True)
    UploadSession_id:int =Field(foreign_key="uploadsession.id")

    chunk_number:int
    size:int
    object_key: str

    checksum: str|None=None
    status:str=Field(default="UPLOADED")

    created_at:datetime=Field(
        default_factory=datetime.utcnow
    )      




