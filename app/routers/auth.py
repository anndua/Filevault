from fastapi import APIRouter, Depends,HTTPException
from sqlmodel import Session
from fastapi.security import OAuth2PasswordRequestForm
from db import get_session
from schemas import UserCreate, UserResponse,UserLogin
from  service import create_user
from  service import authenticate_user
from dependencies import get_current_user
from sqlmodel import Session
from security import create_access_token
from models import User

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
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    user = authenticate_user(
        form_data.username,
        form_data.password,
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
@router.get("/me",response_model=UserResponse)
def get_me(current_user:User= Depends(get_current_user)):
    return current_user


