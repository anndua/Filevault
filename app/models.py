from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel,Field,Relationship

class User(SQLModel,table=True):
    id:int |None =Field(default=None,primary_key=True)
    email:str
    hashed_password:str
    created_at:datetime=Field(default_factory=datetime.utcnow)
    files:list["File"]=Relationship(back_populates="owner")

class File(SQLModel,table=True):
    id:int|None=Field(default=None,primary_key=True)
    filename:str
    size:int
    created_at:datetime=Field(default_factory=datetime.utcnow)
    owner_id:int=Field(foreign_key="user.id")
    owner:Optional["User"]=Relationship(back_populates="files") 
