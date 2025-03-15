from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.database import SessionDep
from app.models import Assignment
from app.run_ai import create_prompt_check_code, run_prompt

router = APIRouter(prefix="/ai", tags=["ai"])


class CompareCodeCreate(BaseModel):
    user_code: str


class CompareCodeResponse(BaseModel):
    message: str


@router.post("/assignments/{assignment_id}", response_model=CompareCodeResponse)
async def compare_code(
    assignment_id: UUID, data: CompareCodeCreate, session: SessionDep
):
    assignment = session.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bài tập",
        )

    prompt = create_prompt_check_code(
        user_code=data.user_code,
        sample_code=assignment.sample_code,
    )
    try:
        response = run_prompt(prompt)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    return CompareCodeResponse(message=response)
