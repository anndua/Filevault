from passlib.context import CryptContext
from datetime import datetime,timedelta,UTC
from jose import jwt
from config import SECRET_KEY,ALGORITHM,ACCESS_TOKEN_EXPIRE_MINUTES
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
    payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    return payload






