from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models import SavedCodeBase, SubmissionBase, UserBase
from app.schema.assignments import AssignmentPublic


class UserPublic(UserBase):
    id: UUID
    created_at: datetime | None
    updated_at: datetime | None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: datetime | None = None


class SubmissionForProfile(SubmissionBase):
    id: UUID
    user: UserPublic
    assignment: AssignmentPublic | None
    created_at: datetime | None
    updated_at: datetime | None


class SavedCodeForProfile(SavedCodeBase):
    id: UUID
    assignment: AssignmentPublic | None
    created_at: datetime | None
    updated_at: datetime | None


class AssignmentForProfile(AssignmentPublic):
    submissions: list[SubmissionBase] = []


class ProfilePublic(UserPublic):
    created_assignments: list[AssignmentForProfile] = []
    submissions: list[SubmissionForProfile] = []
    saved_codes: list[SavedCodeForProfile] = []


class ForgotPassword(BaseModel):
    email: str
