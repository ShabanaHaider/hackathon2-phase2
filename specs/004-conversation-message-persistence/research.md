# Research: Conversation & Message Persistence

**Feature**: 004-conversation-message-persistence
**Date**: 2026-02-05

## R1: SQLModel Relationship Patterns for Parent-Child Entities

**Decision**: Use SQLModel `Relationship()` with `back_populates` for
Conversation → Message one-to-many relationship. Use SQLAlchemy `cascade`
on the foreign key column for database-level cascade delete.

**Rationale**: SQLModel's relationship support maps directly to SQLAlchemy
relationships. Using `cascade="all, delete-orphan"` on the parent side
ensures that deleting a Conversation automatically deletes all child
Messages at the ORM level, while `ondelete="CASCADE"` on the FK column
ensures database-level integrity.

**Alternatives considered**:
- Manual deletion of messages before conversation: Rejected — requires
  extra queries and risks orphaned messages if the deletion sequence fails.
- Soft delete (is_deleted flag): Rejected — spec explicitly states cascade
  delete is acceptable and soft delete is deferred.

## R2: Message Ordering Strategy

**Decision**: Use `created_at` timestamp with database-level index for
message ordering. Messages are always returned `ORDER BY created_at ASC`
within a conversation.

**Rationale**: Timestamp-based ordering is simple, sufficient for the
current scale (no pagination), and aligns with the existing `_utcnow()`
pattern used in the Task model. Neon PostgreSQL timestamps have microsecond
precision, making collisions extremely unlikely.

**Alternatives considered**:
- Sequential integer `sequence_number` column: Rejected — adds complexity
  for concurrent inserts (requires SELECT FOR UPDATE or sequences) without
  clear benefit at current scale. Can be added later if needed.
- UUID v7 (time-ordered): Rejected — adds dependency and over-engineers
  the ordering problem when timestamps suffice.

## R3: Message Role Validation

**Decision**: Use a Python string `Literal["user", "assistant", "system"]`
for Pydantic validation and a `VARCHAR` column with a CHECK constraint for
database-level enforcement.

**Rationale**: Three fixed roles align with standard LLM conversation
formats (OpenAI, Anthropic). Using Pydantic `Literal` provides immediate
request validation. A CHECK constraint provides database-level safety.

**Alternatives considered**:
- Python Enum with PostgreSQL ENUM type: Rejected — PostgreSQL ENUM types
  are difficult to alter and add migration complexity. VARCHAR with CHECK
  is simpler and equally safe.
- Free-form string: Rejected — spec requires specific role values.

## R4: Router Organization

**Decision**: Create a new `backend/routers/conversations.py` router file
for all conversation and message endpoints. Mount at `/api/conversations`.

**Rationale**: Follows the existing pattern (todos router mounted at
`/api/todos`). Keeps conversation logic separate from task logic per the
loose coupling requirement. Messages are nested under conversations
(`/api/conversations/{id}/messages`) since they are always accessed in
the context of a conversation.

**Alternatives considered**:
- Separate messages router at `/api/messages`: Rejected — messages are
  always scoped to a conversation; top-level messages endpoint would
  require conversation_id as a query parameter, which is less RESTful.
- Combined router with todos: Rejected — violates separation of concerns.

## R5: User Ownership Verification Pattern

**Decision**: Follow the exact same pattern as the existing todos router:
use `get_current_user` dependency to extract `user_id` from JWT, then
filter all queries with `WHERE user_id == authenticated_user_id`. Return
404 (not 403) for unauthorized access to prevent enumeration.

**Rationale**: Reuses proven patterns from Phase 2. Returning 404 instead
of 403 prevents users from discovering the existence of other users'
conversations (security through opacity).

**Alternatives considered**: None — this is mandated by Constitution
Principle II and the existing codebase pattern.

## R6: Existing Dependencies Sufficiency

**Decision**: No new Python dependencies required. The existing stack
(FastAPI, SQLModel, asyncpg, Pydantic) fully supports the new models
and endpoints.

**Rationale**: SQLModel handles model definitions and relationships.
FastAPI handles routing and dependency injection. Pydantic handles
request/response validation. asyncpg handles async PostgreSQL access.

**Alternatives considered**: None — all needed capabilities exist.
