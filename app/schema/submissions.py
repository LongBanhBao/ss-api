from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models import SubmissionBase
from app.schema.assignments import AssignmentPublic
from app.schema.users import UserPublic


class SubmissionCreate(BaseModel):
    code: str


class SubmissionUpdate(SubmissionBase):
    pass


class SubmissionPublic(SubmissionBase):
    id: UUID
    user: UserPublic
    assignment: AssignmentPublic
    created_at: datetime | None
    updated_at: datetime | None
