# Data Model: Conversation & Message Persistence

**Feature**: 004-conversation-message-persistence
**Date**: 2026-02-05

## Entity Relationship

```
User (external, from Better Auth)
 ├── 1:N ── Task (existing, unchanged)
 └── 1:N ── Conversation
              └── 1:N ── Message
```

## Entity: Conversation

**Table name**: `conversations`

| Field       | Type                     | Constraints                          |
|-------------|--------------------------|--------------------------------------|
| id          | UUID                     | PK, default uuid4                    |
| user_id     | VARCHAR(255)             | NOT NULL, INDEX, FK to auth users    |
| title       | VARCHAR(255)             | NOT NULL                             |
| created_at  | TIMESTAMP WITH TIME ZONE | NOT NULL, default utcnow             |
| updated_at  | TIMESTAMP WITH TIME ZONE | NOT NULL, default utcnow             |

**Indexes**:
- `ix_conversations_user_id` on `user_id` (for user-scoped list queries)
- `ix_conversations_updated_at` on `updated_at` (for ordering)

**Relationships**:
- Has many Messages (cascade delete)

## Entity: Message

**Table name**: `messages`

| Field            | Type                     | Constraints                              |
|------------------|--------------------------|------------------------------------------|
| id               | UUID                     | PK, default uuid4                        |
| conversation_id  | UUID                     | NOT NULL, FK → conversations.id, INDEX   |
| role             | VARCHAR(20)              | NOT NULL, CHECK IN (user, assistant, system) |
| content          | TEXT                     | NOT NULL                                 |
| created_at       | TIMESTAMP WITH TIME ZONE | NOT NULL, default utcnow                 |

**Indexes**:
- `ix_messages_conversation_id` on `conversation_id` (for message retrieval)
- Composite index on `(conversation_id, created_at)` for ordered retrieval

**Relationships**:
- Belongs to one Conversation (FK with ON DELETE CASCADE)

## Pydantic Request/Response Schemas

### ConversationCreate
- `title`: str (min_length=1, max_length=255)

### ConversationUpdate
- `title`: Optional[str] (min_length=1, max_length=255)

### ConversationResponse
- `id`: UUID
- `title`: str
- `created_at`: datetime
- `updated_at`: datetime
- `user_id`: str

### MessageCreate
- `role`: Literal["user", "assistant", "system"]
- `content`: str (min_length=1, max_length=16000)

### MessageResponse
- `id`: UUID
- `conversation_id`: UUID
- `role`: str
- `content`: str
- `created_at`: datetime

## Migration Strategy

SQLModel's `create_all` auto-creates tables on startup (existing pattern).
New tables (`conversations`, `messages`) will be created alongside the
existing `tasks` table without affecting it.

No manual migration scripts needed — the `create_db_and_tables()` function
in `database.py` handles this via `SQLModel.metadata.create_all`.
