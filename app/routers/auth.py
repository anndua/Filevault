from fastapi import APIRouter, Depends
from sqlmodel import Session

from db import get_session
from schemas import UserCreate, UserResponse
from services import create_user

router = APIRouter()

@router.post("/register",response_model=UserResponse)
def register(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):

    user = create_user(user_data, session)

    return user
