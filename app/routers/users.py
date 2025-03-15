from typing import Annotated, Dict
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from app.config import get_settings
from app.database import SessionDep
from app.email import send_email
from app.models import User
from app.routers.auth import CurrentUser, get_password_hash, get_role
from app.schema.users import (
    ForgotPassword,
    ProfilePublic,
    UserCreate,
    UserPublic,
    UserUpdate,
)

settings = get_settings()

CurrentUserWithRolePassed = Annotated[
    CurrentUser, Depends(get_role(["admin", "student"]))
]

router = APIRouter()


@router.post("/register", tags=["auth"], response_model=UserPublic)
async def register(data: UserCreate, session: SessionDep):
    user = session.exec(select(User).where(User.email == data.email)).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng",
        )
    user = User(
        email=data.email,
        password=get_password_hash(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        date_of_birth=data.date_of_birth,
        role=data.role,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.put("/update", tags=["users"], response_model=UserPublic)
async def update(data: UserUpdate, session: SessionDep, current_user: CurrentUser):
    if data.first_name is not None:
        current_user.first_name = data.first_name
    if data.last_name is not None:
        current_user.last_name = data.last_name
    if data.date_of_birth is not None:
        current_user.date_of_birth = data.date_of_birth
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.get("/profile/{user_id}", tags=["users"], response_model=ProfilePublic)
async def get_user_by_id(user_id: UUID, session: SessionDep, current_user: CurrentUser):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng",
        )
    if current_user.role == "student" and current_user.id != user_id:
        user.submissions = []
    return user


@router.delete("/delete/{user_id}", tags=["users"], response_model=UserPublic)
async def delete_user(
    user_id: UUID,
    session: SessionDep,
    current_user: Annotated[CurrentUser, Depends(get_role(["admin"]))],
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng",
        )
    session.delete(user)
    session.commit()
    return user


def createContent(user: User, new_password: str) -> str:
    return f"""
    <html>
    <body>
    <h2>Reset Password</h2>
    <p>Dear {user.first_name} {user.last_name},</p>
    <p>Your password has been reset successfully.</p>
    <p>Your new password is: <strong>{new_password}</strong></p>
    <p>Best regards,</p>
    <p>Admin</p>
    </body>
    </html>
    """


@router.post("/forgot", tags=["auth"], response_model=Dict)
async def forgot_password(data: ForgotPassword, session: SessionDep) -> Dict:
    user = session.exec(select(User).where(User.email == data.email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng",
        )
    new_password = uuid4().hex[:6]
    user.password = get_password_hash(new_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    try:
        r = await send_email(
            user.email, "Reset Password", createContent(user, new_password)
        )
        return r
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
