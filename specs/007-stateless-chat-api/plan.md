# Implementation Plan: Stateless Chat API Endpoint

**Branch**: `007-stateless-chat-api` | **Date**: 2026-02-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-stateless-chat-api/spec.md`

## Summary

Create a user-scoped stateless chat endpoint at `POST /api/{user_id}/chat` that orchestrates conversation persistence and AI agent execution. The endpoint automatically manages conversation creation/lookup, message persistence, and agent invocation while maintaining complete statelessness between requests.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: FastAPI, SQLModel, Groq (llama-3.3-70b-versatile), Better Auth JWT
**Storage**: Neon Serverless PostgreSQL (existing Conversation, Message tables)
**Testing**: Manual testing via curl/frontend (no automated tests per project convention)
**Target Platform**: Linux server (Docker-compatible)
**Project Type**: Web application (backend API)
**Performance Goals**: 95% of responses within 5 seconds
**Constraints**: Stateless design, no in-memory state, user isolation via JWT
**Scale/Scope**: Single conversation per user, last 20 messages as context

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. End-to-End Correctness | ✅ PASS | Endpoint tested via frontend and curl |
| II. User Data Isolation | ✅ PASS | user_id from JWT validated against URL path |
| III. Spec-Driven Development | ✅ PASS | Derived from spec.md |
| IV. Framework-Idiomatic | ✅ PASS | FastAPI async endpoints, Pydantic validation |
| V. RESTful API Design | ✅ PASS | POST /api/{user_id}/chat follows REST conventions |
| VI. Environment-Based Secrets | ✅ PASS | Groq API key from env vars |
| VII. Agentic AI & Tools | ✅ PASS | Agent operates via MCP tool functions |
| VIII. Stateless AI Interactions | ✅ PASS | DB-backed context reconstruction, no in-memory state |

## Project Structure

### Documentation (this feature)

```text
specs/007-stateless-chat-api/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── chat-api.md      # API contract
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── main.py              # FastAPI app (add new router)
├── auth.py              # JWT auth (existing)
├── database.py          # Async session (existing)
├── models.py            # Existing + new schemas
├── mcp_server.py        # Task tools (existing)
├── agent.py             # AI agent (restore from 006 branch)
└── routers/
    ├── todos.py         # Task CRUD (existing)
    ├── conversations.py # Conversation CRUD (existing)
    └── chat.py          # NEW: Stateless chat endpoint
```

**Structure Decision**: Backend-only change. New router `chat.py` with single endpoint. Reuses existing models and agent from Spec 6.

## Complexity Tracking

> No Constitution Check violations. Simple extension of existing patterns.

---

## Phase 0: Research

### Research Questions

1. **Conversation lookup pattern**: How to efficiently find or create a user's conversation?
2. **Concurrent request handling**: How to maintain message ordering with simultaneous requests?
3. **Tool call logging**: Where to capture tool invocations (response body vs database)?

### Research Findings

**R1: Conversation Lookup Pattern**
- Decision: Use `get_or_create` pattern - query by user_id, create if not found
- Rationale: Single conversation per user simplifies lookup to O(1) with index
- Alternatives: UUID in URL (rejected - adds complexity for single-conversation model)

**R2: Concurrent Request Handling**
- Decision: Database-level ordering via `created_at` timestamps
- Rationale: PostgreSQL handles concurrent inserts; message ordering is guaranteed by timestamp index
- Alternatives: Request queuing (rejected - over-engineering for expected load)

**R3: Tool Call Logging**
- Decision: Return tool calls in response body, log to console (not database)
- Rationale: Avoids schema changes; sufficient for debugging; can add DB logging later
- Alternatives: New ToolCall table (rejected - out of scope per spec)

---

## Phase 1: Design

### Data Model

Reuses existing models from Spec 4 with minor additions:

**Existing Models (no changes)**:
- `Conversation`: id, user_id, title, created_at, updated_at
- `Message`: id, conversation_id, role, content, created_at

**New Schemas (models.py)**:
- `UserChatRequest`: message (str, 1-16000 chars)
- `UserChatResponse`: user_message, assistant_message, tool_calls (optional list)
- `ToolCallInfo`: name, arguments, result, duration_ms

### API Contract

**Endpoint**: `POST /api/{user_id}/chat`

**Request**:
```json
{
  "message": "Add a task to buy groceries"
}
```

**Response (200 OK)**:
```json
{
  "user_message": {
    "id": "uuid",
    "conversation_id": "uuid",
    "role": "user",
    "content": "Add a task to buy groceries",
    "created_at": "2026-02-06T12:00:00Z"
  },
  "assistant_message": {
    "id": "uuid",
    "conversation_id": "uuid",
    "role": "assistant",
    "content": "I've created a task called 'buy groceries'.",
    "created_at": "2026-02-06T12:00:01Z"
  },
  "tool_calls": [
    {
      "name": "add_task",
      "arguments": {"title": "buy groceries"},
      "result": "Task created successfully...",
      "duration_ms": 150
    }
  ]
}
```

**Error Responses**:
- `400 Bad Request`: Invalid message (empty, too long)
- `401 Unauthorized`: Missing or invalid JWT
- `403 Forbidden`: URL user_id doesn't match authenticated user
- `500 Internal Server Error`: Agent failure (user message still persisted)

### Implementation Approach

1. **New router**: `backend/routers/chat.py` with single endpoint
2. **Auth validation**: Compare `user_id` path param with JWT-extracted user_id
3. **Conversation get-or-create**: Query by user_id, create with default title if missing
4. **Message persistence**: Save user message BEFORE agent call (data integrity)
5. **Agent invocation**: Call `run_agent()` with message history
6. **Tool call capture**: Modify `run_agent()` to return tool call details
7. **Response assembly**: Return both messages plus tool calls

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     POST /api/{user_id}/chat                    │
├─────────────────────────────────────────────────────────────────┤
│  1. Validate JWT & match user_id                                │
│  2. Get or create conversation for user                         │
│  3. Load last 20 messages from DB                               │
│  4. Persist user message (commit immediately)                   │
│  5. Call run_agent(user_id, message, history)                   │
│     └─> Groq API → tool calls → MCP functions → DB mutations    │
│  6. Persist assistant message                                   │
│  7. Return {user_message, assistant_message, tool_calls}        │
└─────────────────────────────────────────────────────────────────┘
```

### Stateless Guarantees

- No global variables storing conversation state
- No caching of user data in memory
- All state reconstructed from database on each request
- Server restarts do not affect conversation continuity

---

## Implementation Phases

### Phase A: Setup & Agent Restoration
1. Restore `backend/agent.py` from 006 branch
2. Verify agent imports and Groq connectivity

### Phase B: New Schemas
1. Add `UserChatRequest`, `UserChatResponse`, `ToolCallInfo` to models.py

### Phase C: Chat Router
1. Create `backend/routers/chat.py`
2. Implement user_id validation against JWT
3. Implement get-or-create conversation logic
4. Implement message history loading
5. Wire up agent invocation
6. Handle error cases (agent failure, validation)

### Phase D: Agent Enhancement
1. Modify `run_agent()` to return tool call details
2. Add timing instrumentation for tool calls

### Phase E: Integration & Verification
1. Register chat router in main.py
2. Test via curl with JWT token
3. Verify conversation resumption
4. Verify user isolation

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Context truncation (>20 messages) | Medium | Low | 20-message limit per spec; warn in response if truncated |
| Agent timeout (>5s) | Low | Medium | Return partial response with user message; log timeout |
| Concurrent message ordering | Low | Low | DB timestamp ordering; acceptable race condition |
| Groq API rate limits | Low | Medium | Graceful error handling; suggest retry |

---

## Dependencies

- **Spec 4**: Conversation/Message models (complete)
- **Spec 6**: AI Agent with Groq (agent.py exists on 006 branch)
- **Better Auth**: JWT authentication (complete)

---

## Success Criteria Mapping

| Spec Criterion | Implementation |
|----------------|----------------|
| SC-001: 5s response | Groq inference ~1-2s typical |
| SC-002: History continuity | DB-backed reconstruction |
| SC-003: Data integrity | User message committed before agent |
| SC-004: Tool call logging | Returned in response body |
| SC-005: No memory leaks | No global state |
| SC-006: User isolation | JWT user_id === URL user_id check |
