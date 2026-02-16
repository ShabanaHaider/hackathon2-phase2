import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field as PydanticField
from sqlalchemy import Column, DateTime, ForeignKey, Index, Text
from sqlmodel import Field, Relationship, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RecurrencePattern(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TaskTagLink(SQLModel, table=True):
    __tablename__ = "task_tags"

    task_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("tasks.id", ondelete="CASCADE"),
            primary_key=True
        )
    )
    tag_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("tags.id", ondelete="CASCADE"),
            primary_key=True
        )
    )


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

    # --- NEW FIELDS FOR ADVANCED FEATURES ---
    priority: str = Field(default="medium", max_length=10, index=True)
    due_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, index=True)
    )
    is_recurring: bool = Field(default=False)
    recurrence_pattern: Optional[str] = Field(default=None, max_length=20)

    # --- RELATIONSHIPS ---
    tags: list["Tag"] = Relationship(
        back_populates="tasks",
        link_model=TaskTagLink,
        sa_relationship_kwargs={"lazy": "selectin"}
    )


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


# --- NEW MODELS FOR ADVANCED FEATURES ---

class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=50, index=True)
    user_id: str = Field(index=True, max_length=255)
    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    # --- RELATIONSHIPS ---
    tasks: list["Task"] = Relationship(
        back_populates="tags",
        link_model=TaskTagLink
    )


# --- Request / Response Schemas ---


class TaskCreate(BaseModel):
    title: str = PydanticField(min_length=1, max_length=255)
    description: Optional[str] = PydanticField(default=None, max_length=2000)
    priority: Priority = Priority.MEDIUM
    due_at: Optional[datetime] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[RecurrencePattern] = None
    tag_names: Optional[list[str]] = PydanticField(default=None, max_length=10)


class TaskUpdate(BaseModel):
    title: Optional[str] = PydanticField(default=None, min_length=1, max_length=255)
    description: Optional[str] = PydanticField(default=None, max_length=2000)
    is_completed: Optional[bool] = None
    priority: Optional[Priority] = None
    due_at: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    tag_names: Optional[list[str]] = None


class TagResponse(BaseModel):
    id: uuid.UUID
    name: str

    model_config = {"from_attributes": True}


class TaskResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str]
    is_completed: bool
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    user_id: str
    priority: str
    due_at: Optional[datetime]
    is_recurring: bool
    recurrence_pattern: Optional[str]
    tags: list[TagResponse] = []

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


# --- User Chat API Schemas (Spec 7: Stateless Chat API) ---


class ToolCallInfo(BaseModel):
    """Information about a tool call made by the AI agent."""
    name: str
    arguments: dict
    result: str
    duration_ms: int


class UserChatRequest(BaseModel):
    """Request body for POST /api/{user_id}/chat."""
    message: str = PydanticField(min_length=1, max_length=16000)


class UserChatResponse(BaseModel):
    """Response body for POST /api/{user_id}/chat."""
    user_message: MessageResponse
    assistant_message: MessageResponse
    tool_calls: Optional[list[ToolCallInfo]] = None


# --- Event Schemas (Dapr Pub/Sub) ---


class TaskEventPayload(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    is_completed: bool
    priority: str
    due_at: Optional[datetime] = None
    is_recurring: bool
    recurrence_pattern: Optional[str] = None
    tags: list[str] = []


class TaskEvent(BaseModel):
    event_id: uuid.UUID = PydanticField(default_factory=uuid.uuid4)
    event_type: str
    user_id: str
    task_id: uuid.UUID
    timestamp: datetime = PydanticField(default_factory=_utcnow)
    version: str = "1.0"
    payload: TaskEventPayload


class TaskDeletedPayload(BaseModel):
    title: str


class TaskDeletedEvent(BaseModel):
    event_id: uuid.UUID = PydanticField(default_factory=uuid.uuid4)
    event_type: str = "task.deleted"
    user_id: str
    task_id: uuid.UUID
    timestamp: datetime = PydanticField(default_factory=_utcnow)
    version: str = "1.0"
    payload: TaskDeletedPayload


class ReminderEventPayload(BaseModel):
    title: str
    due_at: datetime
    priority: str


class ReminderEvent(BaseModel):
    event_id: uuid.UUID = PydanticField(default_factory=uuid.uuid4)
    event_type: str = "reminder.due"
    user_id: str
    task_id: uuid.UUID
    timestamp: datetime = PydanticField(default_factory=_utcnow)
    version: str = "1.0"
    payload: ReminderEventPayload
