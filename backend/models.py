import uuid
from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field as PydanticField
from sqlalchemy import Column, DateTime, ForeignKey, Index, Text
from sqlmodel import Field, Relationship, SQLModel


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
    user_id: str = Field(index=True, max_length=255)


class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: str = Field(index=True, max_length=255)
    title: str = Field(max_length=255)
    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True),
    )

    messages: list["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class Message(SQLModel, table=True):
    __tablename__ = "messages"
    __table_args__ = (
        Index("ix_messages_conversation_id_created_at", "conversation_id", "created_at"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    role: str = Field(max_length=20)
    content: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    conversation: Optional[Conversation] = Relationship(back_populates="messages")


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


# --- Conversation Request / Response Schemas ---


class ConversationCreate(BaseModel):
    title: str = PydanticField(min_length=1, max_length=255)


class ConversationUpdate(BaseModel):
    title: Optional[str] = PydanticField(default=None, min_length=1, max_length=255)


class ConversationResponse(BaseModel):
    id: uuid.UUID
    title: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Message Request / Response Schemas ---


class MessageCreate(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = PydanticField(min_length=1, max_length=16000)


class MessageResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Chat Request / Response Schemas ---


class ChatRequest(BaseModel):
    message: str = PydanticField(min_length=1, max_length=16000)


class ChatResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse
