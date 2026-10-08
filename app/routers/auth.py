from fastapi import APIRouter, Depends,HTTPException, Request
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
from dependencies import get_rate_limiter
from services.rate_limiter import RateLimitExceeded, RateLimiter
from config import login_rate_limit

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
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
    limiter: RateLimiter = Depends(get_rate_limiter),
):
    identity = request.headers.get("X-Real-IP") or (
        request.client.host if request.client else "unknown"
    )
    try:
        limiter.consume("login", identity, login_rate_limit, 60)
    except RateLimitExceeded as exc:
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts",
            headers={"Retry-After": str(exc.retry_after)},
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

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
