from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import SessionDep
from app.models import Assignment, Submission
from app.routers.auth import CurrentUser, get_role
from app.run_code import create_result
from app.schema.submissions import SubmissionCreate, SubmissionPublic

CurrentUserWithRolePassed = Annotated[
    CurrentUser, Depends(get_role(["admin", "student"]))
]

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("/{assignment_id}", response_model=SubmissionPublic)
async def create_submission(
    assignment_id: UUID,
    data: SubmissionCreate,
    session: SessionDep,
    current_user: Annotated[CurrentUser, Depends(get_role(["admin", "student"]))],
):
    assignment = session.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Bài tập không tồn tại")

    test_cases = assignment.test_cases
    if len(test_cases) == 0:
        raise HTTPException(status_code=400, detail="Bài tập không có test case")

    hidden_test_cases = [tc for tc in test_cases if tc.type == "hidden"]

    try:
        result = create_result(data.code, hidden_test_cases)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    assignment.submissions.append(
        Submission(
            code=data.code,
            result=result["result"],
            status=result["status"],
            user=current_user,
        )
    )

    try:
        session.add(assignment)
        session.commit()
        session.refresh(assignment)
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return assignment.submissions[-1]


@router.get("/{assignment_id}", response_model=list[SubmissionPublic])
async def get_all_submissions(
    assignment_id: UUID,
    current_user: Annotated[
        CurrentUser, Depends(get_role(["admin", "student", "teacher"]))
    ],
    session: SessionDep,
):
    assignment = session.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Bài tập không tồn tại")

    if current_user.role == "teacher" and assignment.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền xem các bài nộp này truy cập bài nộp",
        )

    if current_user.role == "student":
        submissions = [
            s for s in assignment.submissions if s.user_id == current_user.id
        ]
        if len(submissions) == 0:
            raise HTTPException(
                status_code=404, detail="Không tìm thấy bài nộp của bạn"
            )
        return sorted(submissions, key=lambda x: x.created_at)

    return sorted(assignment.submissions, key=lambda x: x.created_at)
