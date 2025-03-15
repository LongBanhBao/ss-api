from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from app.database import SessionDep
from app.models import Assignment, TestCase
from app.routers.auth import CurrentUser, get_role
from app.run_code import create_result
from app.schema.assignments import (
    AssignmentCreate,
    AssignmentCreatePublic,
    AssignmentGetAllPublic,
    AssignmentGetPublic,
    AssignmentPublic,
    AssignmentUpdate,
    AssignmentUpdatePublic,
)

router = APIRouter(prefix="/assignments", tags=["assignments"])


# Dependency
CurrentUserWithRolePassed = Annotated[
    CurrentUser, Depends(get_role(["admin", "teacher"]))
]


@router.post("/", response_model=AssignmentCreatePublic)
async def create_assignment(
    data: AssignmentCreate, session: SessionDep, current_user: CurrentUserWithRolePassed
):
    test_cases = []
    for tc in data.test_cases:
        test_case = TestCase(input=tc.input, output=tc.output, type=tc.type)
        session.add(test_case)
        session.commit()
        session.refresh(test_case)
        test_cases.append(test_case)
    assignment = Assignment(
        title=data.title,
        description=data.description,
        sample_code=data.sample_code,
        category=data.category,
        creator=current_user,
        test_cases=test_cases,
    )

    try:
        session.add(assignment)
        session.commit()
        session.refresh(assignment)
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return assignment


# Lấy tất cả bài tập, không cần role
@router.get("/", response_model=list[AssignmentGetAllPublic])
async def get_all_assignments(
    session: SessionDep, offset: int = 0, limit: int = 10, title: str | None = None
):
    query = select(Assignment).offset(offset).limit(limit)

    if title:
        query = query.where(Assignment.title.contains(title))

    assignments = session.exec(query).all()
    return assignments


@router.get("/{assignment_id}", response_model=AssignmentGetPublic)
async def get_assignment(
    assignment_id: UUID, session: SessionDep, current_user: CurrentUser
):
    assignment = session.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bài tập không tồn tại"
        )
    sample_test_cases = [tc for tc in assignment.test_cases if tc.type != "hidden"]
    user_submissions = [
        sm for sm in assignment.submissions if sm.user_id == current_user.id
    ]
    user_saved_codes = [
        sc for sc in assignment.saved_codes if sc.user_id == current_user.id
    ]
    if current_user.role == "teacher" and assignment.created_by != current_user.id:
        assignment.test_cases = sample_test_cases
        assignment.submissions = user_submissions
        assignment.saved_codes = user_saved_codes
        return assignment
    elif current_user.role == "student":
        assignment.test_cases = sample_test_cases
        assignment.submissions = user_submissions
        assignment.saved_codes = user_saved_codes
        return assignment
    else:
        return assignment


@router.put("/{assignment_id}", response_model=AssignmentUpdatePublic)
async def update_assignment(
    assignment_id: UUID,
    data: AssignmentUpdate,
    session: SessionDep,
    current_user: CurrentUserWithRolePassed,
):
    assignment = session.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bài tập không tồn tại"
        )

    if assignment.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Không có quyền truy cập"
        )

    assignment.title = data.title
    assignment.description = data.description
    assignment.sample_code = data.sample_code

    for tc in assignment.test_cases:
        session.delete(tc)

    session.commit()
    session.refresh(assignment)

    assignment.test_cases = [
        TestCase(input=tc.input, output=tc.output, type=tc.type)
        for tc in data.test_cases
    ]

    try:
        session.add(assignment)
        session.commit()
        session.refresh(assignment)
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    try:
        hidden_test_cases = [tc for tc in assignment.test_cases if tc.type == "hidden"]

        for submission in assignment.submissions:
            result = create_result(submission.code, hidden_test_cases)
            submission.result = result["result"]
            submission.status = result["status"]
            session.add(submission)
        session.commit()
        session.refresh(assignment)

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return assignment


@router.delete("/{assignment_id}", response_model=AssignmentPublic)
async def delete_assignment(
    assignment_id: UUID, session: SessionDep, current_user: CurrentUserWithRolePassed
):
    assignment = session.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bài tập không tồn tại"
        )

    if assignment.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Không có quyền truy cập"
        )

    session.delete(assignment)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return assignment
