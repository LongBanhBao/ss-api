from uuid import UUID
from datetime import datetime
from sqlmodel import select
from fastapi import APIRouter, HTTPException, status

from app.database import SessionDep
from app.models import SavedCode, SavedCodeBase, Assignment, User
from app.routers.auth import CurrentUser

router = APIRouter(prefix="/savedcodes", tags=["savedcodes"])


class SavedCodeCreate(SavedCodeBase):
    pass


class SavedCodeUpdate(SavedCodeBase):
    pass


class SavedCodePublic(SavedCodeBase):
    id: UUID
    user: User
    assignment: Assignment
    created_at: datetime
    updated_at: datetime


@router.post("/{assignment_id}", response_model=SavedCodePublic)
async def create_saved_code(
    assignment_id: UUID,
    data: SavedCodeCreate,
    current_user: CurrentUser,
    session: SessionDep,
):
    assignment = session.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài tập"
        )

    saved_code = session.exec(
        select(SavedCode)
        .where(SavedCode.assignment_id == assignment_id)
        .where(SavedCode.user_id == current_user.id)
    ).first()

    if saved_code:
        saved_code.code = data.code
        session.add(saved_code)
        session.commit()
        session.refresh(saved_code)
        return saved_code
    else:
        saved_code = SavedCode(
            code=data.code, assignment_id=assignment_id, user_id=current_user.id
        )
        session.add(saved_code)
        session.commit()
        session.refresh(saved_code)
        return saved_code


@router.put("/{assignment_id}", response_model=SavedCodePublic)
async def update_saved_code(
    assignment_id: UUID,
    data: SavedCodeUpdate,
    current_user: CurrentUser,
    session: SessionDep,
):
    saved_code = session.exec(
        select(SavedCode)
        .where(SavedCode.assignment_id == assignment_id)
        .where(SavedCode.user_id == current_user.id)
    ).first()
    if not saved_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài tập"
        )

    saved_code.code = data.code
    session.commit()
    return saved_code


@router.get("/{assignment_id}", response_model=SavedCodePublic)
async def get_saved_code(
    assignment_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
):
    saved_code = session.exec(
        select(SavedCode)
        .where(SavedCode.assignment_id == assignment_id)
        .where(SavedCode.user_id == current_user.id)
    ).first()
    if not saved_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài tập"
        )

    return saved_code
