from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from app.database import SessionDep
from app.models import User
from app.routers.auth import CurrentUser, get_password_hash, get_role
from app.schema.users import ProfilePublic, UserCreate, UserPublic, UserUpdate

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
