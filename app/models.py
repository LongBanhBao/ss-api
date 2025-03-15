import uuid
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel


class UUIDBase(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class TimeStampedBase(SQLModel):
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )


class UserBase(SQLModel):
    email: str = Field(index=True, unique=True)
    # user.model_dump(exclude={"password": False}) sẽ hiện password
    password: str = Field(exclude=True)
    first_name: str
    last_name: str
    date_of_birth: datetime
    role: str = "student"


class ClassBase(SQLModel):
    title: str
    description: str
    image_url: Optional[str]


class AssignmentBase(SQLModel):
    title: str
    description: str
    sample_code: str = Field(exclude=True)
    category: str = "general"


class TestCaseBase(SQLModel):
    input: str
    output: str
    type: str


class SubmissionBase(SQLModel):
    code: str
    status: str = "pending"
    result: float

    @field_validator("result")
    @classmethod
    def validate_result(cls, v):
        if not (0 <= v <= 100):
            raise ValueError("Kết quả phải nằm trong khoảng từ 0 đến 100")
        return v


class SavedCodeBase(SQLModel):
    code: str


class MessageBase(SQLModel):
    content: str


class User(UserBase, UUIDBase, TimeStampedBase, table=True):
    class_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="class.id", ondelete="SET NULL"
    )

    # Class
    created_classes: List["Class"] = Relationship(
        back_populates="teacher",
        sa_relationship_kwargs={"foreign_keys": "Class.teacher_id"},
    )
    my_class: Optional["Class"] = Relationship(
        back_populates="students",
        sa_relationship_kwargs={"foreign_keys": "User.class_id"},
    )

    # Assignment
    created_assignments: List["Assignment"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"foreign_keys": "Assignment.created_by"},
    )

    # Submission - Bỏ cascade delete-orphan
    submissions: List["Submission"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "foreign_keys": "Submission.user_id",
        },
    )

    # Saved code - Bỏ cascade delete-orphan
    saved_codes: List["SavedCode"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "foreign_keys": "SavedCode.user_id",
        },
    )

    # Message
    messages: List["Message"] = Relationship(
        back_populates="sender",
        sa_relationship_kwargs={"foreign_keys": "Message.sender_id"},
    )


class Class(ClassBase, UUIDBase, TimeStampedBase, table=True):
    teacher_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="user.id", ondelete="CASCADE"
    )

    class_code: str = Field(default_factory=lambda: uuid.uuid4().hex[:6])

    # User
    teacher: Optional["User"] = Relationship(
        back_populates="created_classes",
        sa_relationship_kwargs={"foreign_keys": "Class.teacher_id"},
    )
    students: List["User"] = Relationship(
        back_populates="my_class",
        sa_relationship_kwargs={"foreign_keys": "User.class_id"},
    )

    # Submission
    submissions: List["Submission"] = Relationship(
        back_populates="of_class",
        sa_relationship_kwargs={
            "foreign_keys": "Submission.class_id",
            "cascade": "all, delete-orphan",
        },
    )

    # Message
    messages: List["Message"] = Relationship(
        back_populates="of_class",
        sa_relationship_kwargs={
            "foreign_keys": "Message.class_id",
            "cascade": "all, delete-orphan",
        },
    )


class Assignment(AssignmentBase, UUIDBase, TimeStampedBase, table=True):
    created_by: Optional[uuid.UUID] = Field(
        default=None, foreign_key="user.id", ondelete="CASCADE"
    )

    # User
    creator: Optional["User"] = Relationship(back_populates="created_assignments")

    # Chỉ giữ cascade delete-orphan ở phía Assignment
    test_cases: List["TestCase"] = Relationship(
        back_populates="assignment",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    submissions: List["Submission"] = Relationship(
        back_populates="assignment",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    saved_codes: List["SavedCode"] = Relationship(
        back_populates="assignment",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    # Message
    messages: List["MessageAssignment"] = Relationship(
        back_populates="assignment",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class TestCase(TestCaseBase, UUIDBase, TimeStampedBase, table=True):
    assignment_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="assignment.id", ondelete="CASCADE"
    )

    # Assignment
    assignment: Optional["Assignment"] = Relationship(
        back_populates="test_cases",
    )


class Submission(SubmissionBase, UUIDBase, TimeStampedBase, table=True):
    user_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="user.id", ondelete="CASCADE"
    )
    assignment_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="assignment.id", ondelete="CASCADE"
    )
    class_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="class.id", ondelete="CASCADE"
    )

    # User - một user có thể có nhiều submissions
    user: Optional["User"] = Relationship(
        back_populates="submissions",
    )
    # Assignment - một assignment có thể có nhiều submissions
    assignment: Optional["Assignment"] = Relationship(
        back_populates="submissions",
    )
    # Class - một class có thể có nhiều submissions
    of_class: Optional["Class"] = Relationship(
        back_populates="submissions",
    )


class SavedCode(SavedCodeBase, UUIDBase, TimeStampedBase, table=True):
    user_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="user.id", ondelete="CASCADE"
    )
    assignment_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="assignment.id", ondelete="CASCADE"
    )

    # User - một user có thể có nhiều saved codes
    user: Optional["User"] = Relationship(
        back_populates="saved_codes",
    )
    # Assignment - một assignment có thể có nhiều saved codes
    assignment: Optional["Assignment"] = Relationship(
        back_populates="saved_codes",
    )


class Message(MessageBase, UUIDBase, TimeStampedBase, table=True):
    sender_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="user.id", ondelete="CASCADE"
    )
    class_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="class.id", ondelete="CASCADE"
    )

    # User
    sender: Optional["User"] = Relationship(back_populates="messages")
    # Class - một class có thể có nhiều messages
    of_class: Optional["Class"] = Relationship(
        back_populates="messages",
    )

    # Assignments
    messages: List["MessageAssignment"] = Relationship(
        back_populates="message",
    )


class MessageAssignment(UUIDBase, TimeStampedBase, table=True):
    assignment_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="assignment.id", ondelete="CASCADE"
    )
    message_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="message.id", ondelete="CASCADE"
    )

    # Assignment - một assignment có thể có nhiều message assignments
    assignment: Optional["Assignment"] = Relationship(
        back_populates="messages",
    )
    # Message - một message có thể có nhiều message assignments
    message: Optional["Message"] = Relationship(
        back_populates="messages",
    )
