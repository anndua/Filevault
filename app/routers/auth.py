from fastapi import APIRouter, Depends,HTTPException
from sqlmodel import Session

from db import get_session
from schemas import UserCreate, UserResponse,UserLogin
from services import create_user
from services import authenticate_user
from sqlmodel import Session
from security import create_access_token

router = APIRouter()

@router.post("/register",response_model=UserResponse)
def register(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):

    user = create_user(user_data, session)

    return user
@router.post("/login")
def login(
    login_data: UserLogin,
    session: Session = Depends(get_session)
):
    user = authenticate_user(
        login_data.email,
        login_data.password,
        session
    )
    if user is None:

        raise HTTPException(
        status_code=401,
        detail="Invalid email or password"
    )

    token = create_access_token(
    {"sub": user.email}
)
    return{
        "access_token":token,
        "token_type":"bearer"
    }


