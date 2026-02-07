# Research: Stateless Chat API Endpoint

**Feature**: 007-stateless-chat-api
**Date**: 2026-02-06

## Research Questions

### R1: Conversation Lookup Pattern

**Question**: How to efficiently find or create a user's conversation in a stateless context?

**Research**:
- Existing codebase has `Conversation` model with `user_id` index
- Single conversation per user model (per spec assumption)
- Need atomic get-or-create to avoid race conditions

**Decision**: Use SQLModel `get_or_create` pattern
```python
# Query by user_id, create if not found
statement = select(Conversation).where(Conversation.user_id == user_id)
conversation = session.exec(statement).first()
if not conversation:
    conversation = Conversation(user_id=user_id, title="Task Assistant")
    session.add(conversation)
    await session.commit()
```

**Rationale**:
- Simple O(1) lookup with existing user_id index
- No URL complexity (conversation_id not needed in path)
- Atomic creation on first message

**Alternatives Rejected**:
- Conversation UUID in URL: Adds complexity, requires separate creation step
- Pre-creating conversations at signup: Over-engineering, lazy creation sufficient

---

### R2: Concurrent Request Handling

**Question**: How to maintain message ordering when multiple requests arrive simultaneously?

**Research**:
- PostgreSQL guarantees atomicity of individual INSERTs
- `created_at` timestamps with timezone provide natural ordering
- Existing index `ix_messages_conversation_id_created_at` supports efficient queries

**Decision**: Rely on database-level timestamp ordering
- Each message gets `created_at = datetime.now(timezone.utc)` at insertion
- Message queries order by `created_at.asc()`
- Acceptable ~millisecond resolution for human conversation

**Rationale**:
- No additional locking or queuing needed
- PostgreSQL timestamp precision (microseconds) sufficient
- Worst case: two messages same millisecond → arbitrary but consistent order

**Alternatives Rejected**:
- Request queuing: Over-engineering for expected single-user load
- Sequence numbers: Requires additional column, complicates schema
- Pessimistic locking: Performance overhead not justified

---

### R3: Tool Call Logging

**Question**: Where and how to capture AI agent tool invocations?

**Research**:
- Spec requires: "log all tool calls made by the AI agent (tool name, arguments, result, duration)"
- Options: response body, console logging, database table
- Existing agent.py does not capture tool call metadata

**Decision**: Return tool calls in response body + console logging
```python
@dataclass
class ToolCallInfo:
    name: str
    arguments: dict
    result: str
    duration_ms: int
```

**Rationale**:
- Response body: Frontend/API consumers can display tool activity
- Console logging: Backend debugging and audit trail
- No new database table: Avoids schema migration, keeps scope minimal

**Alternatives Rejected**:
- Database-only: Frontend can't show tool activity
- New ToolCall table: Schema change out of scope; can add later if needed
- No logging: Violates FR-009 (tool call logging requirement)

---

### R4: Agent Error Handling

**Question**: How to handle agent failures while preserving user messages?

**Research**:
- Spec requires: "User messages are persisted even when agent fails"
- Current pattern: commit user message, then call agent
- Need to handle: Groq API errors, timeouts, tool failures

**Decision**: Two-phase commit pattern
1. Persist user message and commit immediately
2. Call agent (may fail)
3. On success: persist assistant message
4. On failure: return error response with user_message in body

**Rationale**:
- User message always survives agent failure
- Error response includes the persisted user message for client awareness
- No orphaned messages (user message has valid conversation_id)

**Implementation**:
```python
# Phase 1: Persist user message
user_message = Message(...)
session.add(user_message)
await session.commit()  # Committed regardless of agent outcome

# Phase 2: Call agent (may fail)
try:
    agent_response = await run_agent(...)
    assistant_message = Message(...)
    session.add(assistant_message)
    await session.commit()
except Exception as e:
    return {"user_message": user_message, "error": str(e)}
```

---

## Technology Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Conversation lookup | get-or-create by user_id | Simple, indexed, atomic |
| Message ordering | DB timestamp | No locking, sufficient precision |
| Tool call logging | Response body + console | No schema change, visible to frontend |
| Error handling | Two-phase commit | User message always persisted |
| Agent framework | Groq API (from Spec 6) | Already implemented, fast inference |

---

## Dependencies Verified

- [x] Conversation model with user_id index exists
- [x] Message model with conversation_id FK exists
- [x] Index on (conversation_id, created_at) exists
- [x] Agent implementation on 006 branch available
- [x] Groq API key in environment variables
