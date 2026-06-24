from fastapi import HTTPException
from sqlmodel import Session, select

from models import User
from schemas import UserCreate
from security import hash_password


def get_user_by_email(email: str, session: Session):

    return session.exec(
        select(User).where(User.email == email)
    ).first()


def create_user(
    user_data: UserCreate,
    session: Session
) -> User:

    existing_user = get_user_by_email(
        user_data.email,
        session
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user