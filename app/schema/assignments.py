from datetime import datetime
from uuid import UUID

from app.models import (
    AssignmentBase,
    SavedCodeBase,
    SubmissionBase,
    TestCaseBase,
    UserBase,
)
from app.schema.testcases import TestCasePublic


class UserPublic(UserBase):
    id: UUID
    created_at: datetime | None
    updated_at: datetime | None


class AssignmentCreate(AssignmentBase):
    test_cases: list[TestCaseBase]


class AssignmentUpdate(AssignmentCreate):
    pass


class AssignmentPublic(AssignmentBase):
    id: UUID
    created_at: datetime | None
    updated_at: datetime | None


class AssignmentCreatePublic(AssignmentPublic):
    sample_code: str


class AssignmentUpdatePublic(AssignmentCreatePublic):
    pass


class AssignmentGetAllPublic(AssignmentBase):
    id: UUID
    creator: UserPublic


class SubmissionForAssignment(SubmissionBase):
    id: UUID
    user: UserPublic | None
    created_at: datetime | None
    updated_at: datetime | None


class SavedCodeForAssignment(SavedCodeBase):
    id: UUID
    user: UserPublic | None
    created_at: datetime | None
    updated_at: datetime | None


class AssignmentGetPublic(AssignmentPublic):
    id: UUID
    sample_code: str | None
    creator: UserPublic | None
    test_cases: list[TestCasePublic] = []
    submissions: list[SubmissionForAssignment] = []
    saved_codes: list[SavedCodeForAssignment] = []
