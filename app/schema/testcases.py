from uuid import UUID

from app.models import TestCaseBase


class TestCasePublic(TestCaseBase):
    id: UUID
