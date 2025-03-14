from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

from app.models import ClassBase, User


class ClassPublic(ClassBase):
    id: UUID
    teacher: User
    created_at: datetime | None
    updated_at: datetime | None


class ClassCreate(ClassBase):
    pass


class ClassUpdate(ClassBase):
    pass


class JoinClassCreate(BaseModel):
    class_code: str


class JoinClassPublic(ClassBase):
    id: UUID
    class_code: str
