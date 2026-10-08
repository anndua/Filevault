from passlib.context import CryptContext
from datetime import datetime,timedelta,UTC
from jose import jwt
from jose.exceptions import JWTError
from sqlmodel import Session
from config import SECRET_KEY,ALGORITHM,ACCESS_TOKEN_EXPIRE_MINUTES
from models import User

pwd_context=CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)
def hash_password(password:str):
    return pwd_context.hash(password)

def verify_password(password:str,hashed_password:str):

    return pwd_context.verify(password,hashed_password)


def create_access_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now(UTC)+timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp":expire})
    encoded_jwt=jwt.encode(to_encode,
                           SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token:str):
    try:
        return jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid or expired access token") from exc
