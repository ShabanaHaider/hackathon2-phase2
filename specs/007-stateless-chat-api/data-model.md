# Data Model: Stateless Chat API Endpoint

**Feature**: 007-stateless-chat-api
**Date**: 2026-02-06

## Overview

This feature reuses existing database models from Spec 4 (Conversation, Message) and adds new Pydantic schemas for the chat endpoint request/response.

## Existing Models (No Changes)

### Conversation

```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: uuid.UUID          # Primary key
    user_id: str           # Indexed, links to Better Auth user
    title: str             # Conversation title (max 255)
    created_at: datetime   # Timezone-aware
    updated_at: datetime   # Timezone-aware, indexed
```

**Index**: `ix_conversations_user_id` on `user_id` column

### Message

```python
class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: uuid.UUID          # Primary key
    conversation_id: uuid.UUID  # FK to conversations.id, CASCADE delete
    role: str              # "user" | "assistant" | "system"
    content: str           # Message text (TEXT column)
    created_at: datetime   # Timezone-aware
```

**Index**: `ix_messages_conversation_id_created_at` on `(conversation_id, created_at)`

---

## New Schemas (models.py additions)

### UserChatRequest

Request body for the chat endpoint.

```python
class UserChatRequest(BaseModel):
    """Request body for POST /api/{user_id}/chat"""
    message: str = PydanticField(min_length=1, max_length=16000)
```

**Validation**:
- `message`: Required, 1-16000 characters

### ToolCallInfo

Captures details of a single tool invocation.

```python
class ToolCallInfo(BaseModel):
    """Information about a tool call made by the AI agent"""
    name: str
    arguments: dict
    result: str
    duration_ms: int
```

**Fields**:
- `name`: Tool function name (e.g., "add_task")
- `arguments`: Parameters passed to the tool
- `result`: Tool execution result (string)
- `duration_ms`: Execution time in milliseconds

### UserChatResponse

Response body for the chat endpoint.

```python
class UserChatResponse(BaseModel):
    """Response body for POST /api/{user_id}/chat"""
    user_message: MessageResponse
    assistant_message: MessageResponse
    tool_calls: Optional[list[ToolCallInfo]] = None
```

**Fields**:
- `user_message`: The persisted user message
- `assistant_message`: The AI agent's response
- `tool_calls`: Optional list of tool invocations (null if no tools called)

---

## Entity Relationships

```
┌─────────────────┐       ┌─────────────────┐
│      User       │       │  Conversation   │
│  (Better Auth)  │──1:1──│                 │
│                 │       │  - id (PK)      │
│  - id           │       │  - user_id (IX) │
│  - email        │       │  - title        │
│                 │       │  - created_at   │
└─────────────────┘       │  - updated_at   │
                          └────────┬────────┘
                                   │
                                   │ 1:N
                                   │
                          ┌────────▼────────┐
                          │     Message     │
                          │                 │
                          │  - id (PK)      │
                          │  - conv_id (FK) │
                          │  - role         │
                          │  - content      │
                          │  - created_at   │
                          └─────────────────┘
```

**Cardinality**:
- User → Conversation: 1:1 (single conversation per user)
- Conversation → Message: 1:N (many messages per conversation)

---

## Query Patterns

### Get or Create Conversation

```python
# O(1) lookup with user_id index
statement = select(Conversation).where(Conversation.user_id == user_id)
conversation = (await session.exec(statement)).first()

if not conversation:
    conversation = Conversation(
        user_id=user_id,
        title="Task Assistant",
        created_at=_utcnow(),
        updated_at=_utcnow(),
    )
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
```

### Load Message History (Last 20)

```python
# Uses composite index on (conversation_id, created_at)
statement = (
    select(Message)
    .where(Message.conversation_id == conversation.id)
    .order_by(Message.created_at.desc())
    .limit(20)
)
messages = (await session.exec(statement)).all()
# Reverse to chronological order
messages = list(reversed(messages))
```

### Persist Message

```python
message = Message(
    conversation_id=conversation.id,
    role="user",  # or "assistant"
    content=content,
    created_at=_utcnow(),
)
session.add(message)
await session.commit()
await session.refresh(message)
```

---

## Schema Migration

No database schema changes required. All new types are Pydantic schemas for API request/response serialization only.
