from pydantic import BaseModel

class UserCreate(BaseModel):
    email:str
    password:str

class UserResponse(BaseModel):
    id:int
    email:str

class UserLogin(BaseModel):
    email:str
    password:str