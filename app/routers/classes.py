from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from uuid import UUID

from app.models import Class
from app.database import SessionDep
from app.routers.auth import CurrentUser, get_role
from app.schema.classes import (
    ClassCreate,
    ClassPublic,
    ClassUpdate,
    JoinClassCreate,
    JoinClassPublic,
)

router = APIRouter(prefix="/classes", tags=["classes"])


CurrentUserWithRolePassed = Annotated[
    CurrentUser, Depends(get_role(["admin", "teacher"]))
]


@router.post("/", response_model=ClassPublic)
async def create_class(
    data: ClassCreate,
    session: SessionDep,
    current_user: Annotated[CurrentUser, Depends(get_role(["teacher"]))],
):
    c = Class(**data.model_dump(), teacher_id=current_user.id)
    session.add(c)
    session.commit()
    session.refresh(c)
    return c


@router.put("/{class_id}", response_model=ClassPublic)
async def update_class(
    class_id: UUID,
    data: ClassUpdate,
    session: SessionDep,
    current_user: Annotated[CurrentUser, Depends(get_role(["teacher"]))],
):
    c = session.get(Class, class_id)
    if c is None:
        raise HTTPException(status_code=404, detail="Lớp học không tồn tại")

    if c.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Không có quyền truy cập")

    for field, value in data.model_dump().items():
        setattr(c, field, value)

    session.add(c)
    session.commit()
    session.refresh(c)
    return c


@router.get("/{class_id}", response_model=ClassPublic)
async def get_class(class_id: UUID, session: SessionDep, current_user: CurrentUser):
    c = session.get(Class, class_id)
    if c is None:
        raise HTTPException(status_code=404, detail="Lớp học không tồn tại")
    if current_user.role == "teacher" and c.teacher_id != current_user.id:
        c.students = []
        c.messages = []
    if current_user.role == "student" and current_user.id not in [
        s.id for s in c.students
    ]:
        raise HTTPException(status_code=403, detail="Không có quyền truy cập")
    return c


@router.get("/", response_model=list[ClassPublic])
async def get_classes(session: SessionDep, current_user: CurrentUserWithRolePassed):
    if current_user.role == "admin":
        classes = session.exec(select(Class)).all()
    else:
        classes = session.exec(
            select(Class).where(Class.teacher_id == current_user.id)
        ).all()
    return classes


@router.post("/join", response_model=ClassPublic)
async def join_class(
    data: JoinClassCreate,
    session: SessionDep,
    current_user: Annotated[CurrentUser, Depends(get_role(["student"]))],
):
    c = session.exec(select(Class).where(Class.class_code == data.class_code)).first()
    if c is None:
        raise HTTPException(status_code=404, detail="Lớp học không tồn tại")
    if current_user.id in [s.id for s in c.students]:
        raise HTTPException(status_code=400, detail="Bạn đã tham gia lớp học này")
    c.students.append(current_user)
    session.add(c)
    session.commit()
    session.refresh(c)
    return c


@router.put("/{class_id}/leave/{student_id}", response_model=JoinClassPublic)
async def leave_class(
    class_id: UUID,
    student_id: UUID,
    session: SessionDep,
    current_user: Annotated[CurrentUser, Depends(get_role(["student", "teacher"]))],
):
    c = session.get(Class, class_id)
    if c is None:
        raise HTTPException(status_code=404, detail="Lớp học không tồn tại")
    if current_user.role == "teacher" and c.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Không có quyền truy cập")
    if current_user.role == "student" and student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Không có quyền truy cập")
    if student_id not in [s.id for s in c.students]:
        raise HTTPException(
            status_code=400, detail="Sinh viên này chưa tham gia lớp học này"
        )
    c.students = [s for s in c.students if s.id != student_id]
    session.add(c)
    session.commit()
    session.refresh(c)
    return c
