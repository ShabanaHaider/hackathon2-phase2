# Implementation Plan: Conversation & Message Persistence

**Branch**: `004-conversation-message-persistence` | **Date**: 2026-02-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-conversation-message-persistence/spec.md`

## Summary

Introduce persistent Conversation and Message tables to support stateless
AI interactions (Constitution Principle VIII). Conversations are user-scoped
containers; Messages are ordered utterances within a conversation. The
implementation adds two new SQLModel table classes, Pydantic request/response
schemas, and a new FastAPI router with 7 REST endpoints. No new Python
dependencies are required. Existing Task CRUD API remains unchanged
(Compatibility Guarantee).

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI >=0.115.0, SQLModel >=0.0.22, asyncpg >=0.30.0, Pydantic (via SQLModel)
**Storage**: Neon Serverless PostgreSQL (existing)
**Testing**: Manual API testing via curl/quickstart.md
**Target Platform**: Linux server (backend API)
**Project Type**: Web application (backend only for this feature)
**Performance Goals**: Standard web app — sub-second response for all endpoints
**Constraints**: No new dependencies, no changes to existing Task API
**Scale/Scope**: Backend-only — 2 new models, 1 new router, 7 endpoints

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. End-to-End Correctness | ✅ PASS | Backend + DB tested via quickstart; frontend out of scope |
| II. User Data Isolation | ✅ PASS | All queries filter by `user_id`; 404 for cross-user access |
| III. Spec-Driven Development | ✅ PASS | spec.md → plan.md → tasks.md workflow followed |
| IV. Framework-Idiomatic | ✅ PASS | SQLModel models, FastAPI DI, Pydantic validation, async endpoints |
| V. RESTful API Design | ✅ PASS | `/api/conversations` (plural), proper HTTP methods, user-scoped |
| VI. Environment Secrets | ✅ PASS | No new secrets needed; reuses existing DATABASE_URL and BETTER_AUTH_URL |
| VII. Agentic AI & Tools | ✅ N/A | AI logic out of scope for this feature |
| VIII. Stateless AI | ✅ PASS | This feature *enables* Principle VIII by providing persistent storage |
| Compatibility Guarantee | ✅ PASS | Existing `/api/todos` router untouched |
| Loose Coupling | ✅ PASS | Backend-only; no frontend changes; SQLModel ORM only |

**Post-design re-check**: All gates still pass.

## Project Structure

### Documentation (this feature)

```text
specs/004-conversation-message-persistence/
├── plan.md                              # This file
├── research.md                          # Phase 0: research decisions
├── data-model.md                        # Phase 1: entity definitions
├── quickstart.md                        # Phase 1: verification steps
├── contracts/
│   └── conversations-api.md             # Phase 1: REST API contract
├── checklists/
│   └── requirements.md                  # Spec quality checklist
└── tasks.md                             # Phase 2 (/sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── models.py              # MODIFY: Add Conversation, Message models + schemas
├── main.py                # MODIFY: Register conversations router
├── database.py            # UNCHANGED
├── auth.py                # UNCHANGED
├── requirements.txt       # UNCHANGED (no new deps)
├── routers/
│   ├── __init__.py        # RESTORE (was deleted)
│   ├── todos.py           # RESTORE (was deleted) — UNCHANGED content
│   └── conversations.py   # NEW: Conversation + Message CRUD endpoints
└── .env.example           # UNCHANGED
```

**Structure Decision**: Web application (backend only). This feature adds
to the existing backend directory structure. The `routers/` directory needs
its deleted files restored (`__init__.py`, `todos.py`) and a new
`conversations.py` added. Models are co-located in `models.py` following
the existing single-file pattern.

## Design Decisions

### D1: Models in Single File vs. Separate Files

**Decision**: Add Conversation and Message models to the existing
`backend/models.py` file.

**Rationale**: The project has a single `models.py` with the Task model.
Adding two more models keeps consistency. The file stays manageable at
~120 lines. Splitting into separate model files would require restructuring
imports across existing code — unnecessary churn for this scope.

### D2: Router Structure — Nested Messages

**Decision**: Messages are nested under conversations:
`/api/conversations/{id}/messages` rather than a top-level `/api/messages`.

**Rationale**: Messages always exist within the context of a conversation.
Nesting makes the ownership hierarchy explicit in the URL and simplifies
authorization — verifying conversation ownership once implicitly covers all
messages within it.

### D3: Conversation `updated_at` Auto-Update on Message Creation

**Decision**: When a new message is added to a conversation, the
conversation's `updated_at` timestamp is automatically updated.

**Rationale**: The spec requires conversations to be listed by "most
recently updated first." Without this, a conversation that receives new
messages would not bubble up in the list. This matches user expectations
— the most recently active conversation appears first.

### D4: CASCADE Delete at Database Level

**Decision**: Use `ON DELETE CASCADE` on the `messages.conversation_id`
foreign key, plus SQLAlchemy `cascade="all, delete-orphan"` on the
relationship.

**Rationale**: Provides both ORM-level and database-level cascade
guarantee. If messages are deleted via ORM, SQLAlchemy handles it. If
a direct database operation occurs, PostgreSQL handles it. Belt and
suspenders approach prevents orphaned messages.

## Implementation Phases

### Phase 1: Models & Schemas
- Add `Conversation` and `Message` SQLModel table classes to `models.py`
- Add Pydantic request/response schemas
- Tables auto-created on next server startup via `create_db_and_tables()`

### Phase 2: Conversations Router
- Create `backend/routers/conversations.py`
- Implement: POST create, GET list, GET by ID, PATCH update, DELETE
- All endpoints use `get_current_user` dependency for JWT auth
- All queries filter by `user_id`

### Phase 3: Messages Endpoints
- Add POST create message and GET list messages to the conversations router
- Messages nested under `/api/conversations/{conversation_id}/messages`
- Verify conversation ownership before message operations
- Auto-update conversation `updated_at` on message creation

### Phase 4: Router Registration & Restore
- Restore `backend/routers/__init__.py` and `backend/routers/todos.py`
- Register conversations router in `main.py`
- Verify existing todos endpoints still work

### Phase 5: Verification
- Run quickstart.md validation steps
- Test cross-user isolation
- Test cascade delete
- Test message ordering

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Incorrect message ordering under concurrent inserts | Low | Medium | `created_at` timestamps with microsecond precision; index on `(conversation_id, created_at)` |
| Cross-user data leakage | Low | Critical | All queries filter by `user_id`; 404 (not 403) for unauthorized access; follows proven todos pattern |
| Orphaned messages after conversation deletion | Low | Medium | Dual cascade: ORM-level `cascade="all, delete-orphan"` + DB-level `ON DELETE CASCADE` |
| Routers directory restoration breaks existing code | Low | High | Restore exact content from git history; verify todos endpoints after registration |
