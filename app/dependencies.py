from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from db import get_session
from security import decode_access_token
from services import get_user_by_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token:str=Depends(oauth2_scheme),session:Session=Depends(get_session)):
    payload=decode_access_token(token)
    email=payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=401,
            detail="invalid"
        )
    user=get_current_user(email,session)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="user not found"
        )
    return user