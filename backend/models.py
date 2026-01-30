import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field as PydanticField
from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    is_completed: bool = Field(default=False)
    completed_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    user_id: str = Field(index=True)


# --- Request / Response Schemas ---


class TaskCreate(BaseModel):
    title: str = PydanticField(min_length=1, max_length=255)
    description: Optional[str] = PydanticField(default=None, max_length=2000)


class TaskUpdate(BaseModel):
    title: Optional[str] = PydanticField(default=None, min_length=1, max_length=255)
    description: Optional[str] = PydanticField(default=None, max_length=2000)
    is_completed: Optional[bool] = None


class TaskResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str]
    is_completed: bool
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    user_id: str

    model_config = {"from_attributes": True}
