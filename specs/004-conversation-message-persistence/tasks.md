# Tasks: Conversation & Message Persistence

**Input**: Design documents from `/specs/004-conversation-message-persistence/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/conversations-api.md

**Tests**: Not requested in the feature specification. Tests are omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/` at repository root
- All file paths are relative to `/mnt/d/projects/hack2-phase3/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Restore routers directory and prepare project structure

- [x] T001 Restore `backend/routers/__init__.py` (empty init file, was deleted per git status)
- [x] T002 Restore `backend/routers/todos.py` from git history (was deleted per git status; content unchanged)

**Checkpoint**: Routers directory is restored; existing todos API remains functional

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define database models and Pydantic schemas that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Add Conversation SQLModel table class to `backend/models.py` with fields: id (UUID PK), user_id (VARCHAR(255), indexed), title (VARCHAR(255)), created_at (TIMESTAMPTZ), updated_at (TIMESTAMPTZ). Include SQLAlchemy relationship to Message with `cascade="all, delete-orphan"`. Follow existing Task model patterns (uuid4 default, `_utcnow` factory, `sa_column` for DateTime).
- [x] T004 Add Message SQLModel table class to `backend/models.py` with fields: id (UUID PK), conversation_id (UUID FK → conversations.id with `ondelete="CASCADE"`, indexed), role (VARCHAR(20)), content (Text), created_at (TIMESTAMPTZ). Include composite index on (conversation_id, created_at).
- [x] T005 Add Pydantic request/response schemas to `backend/models.py`: ConversationCreate (title: str, min_length=1, max_length=255), ConversationUpdate (title: Optional[str], min_length=1, max_length=255), ConversationResponse (id, title, user_id, created_at, updated_at with from_attributes=True), MessageCreate (role: Literal["user","assistant","system"], content: str min_length=1 max_length=16000), MessageResponse (id, conversation_id, role, content, created_at with from_attributes=True).

**Checkpoint**: Models and schemas defined. Tables auto-created on next server startup via `create_db_and_tables()`.

---

## Phase 3: User Story 1 - Create and Retrieve Conversations (Priority: P1) MVP

**Goal**: Users can create conversations and retrieve them by ID or as a list, with user-scoped data isolation.

**Independent Test**: Create a conversation via POST, retrieve it via GET by ID, list all conversations via GET, verify cross-user access returns 404.

### Implementation for User Story 1

- [x] T006 [US1] Create `backend/routers/conversations.py` with APIRouter (prefix="/conversations", tags=["conversations"]). Import get_current_user from auth, get_session from database, and Conversation/ConversationCreate/ConversationResponse from models. Implement POST `""` endpoint (create_conversation): extract user_id from JWT, create Conversation with title/user_id/timestamps, return 201 with ConversationResponse.
- [x] T007 [US1] Implement GET `""` endpoint (list_conversations) in `backend/routers/conversations.py`: query Conversations WHERE user_id matches authenticated user, ORDER BY updated_at DESC, return list of ConversationResponse.
- [x] T008 [US1] Implement GET `"/{conversation_id}"` endpoint (get_conversation) in `backend/routers/conversations.py`: query Conversation WHERE id matches AND user_id matches authenticated user, return 404 if not found, return ConversationResponse.
- [x] T009 [US1] Register conversations router in `backend/main.py`: import router from routers.conversations, add `app.include_router(conversations_router, prefix="/api")`. Ensure existing todos router import and registration remain unchanged.

**Checkpoint**: Conversations can be created, listed (ordered by updated_at DESC), and retrieved by ID. Cross-user access returns 404. Existing todos API still works.

---

## Phase 4: User Story 2 - Store and Retrieve Messages (Priority: P2)

**Goal**: Users can create messages within their conversations and retrieve full message history in chronological order.

**Independent Test**: Create a conversation, add multiple messages with different roles, retrieve messages and verify chronological order. Verify cross-user message access returns 404.

### Implementation for User Story 2

- [x] T010 [US2] Implement POST `"/{conversation_id}/messages"` endpoint (create_message) in `backend/routers/conversations.py`: verify conversation exists AND belongs to authenticated user (404 if not), create Message with conversation_id/role/content/created_at, update conversation's updated_at timestamp (per design decision D3), commit both changes, return 201 with MessageResponse.
- [x] T011 [US2] Implement GET `"/{conversation_id}/messages"` endpoint (list_messages) in `backend/routers/conversations.py`: verify conversation exists AND belongs to authenticated user (404 if not), query Messages WHERE conversation_id matches ORDER BY created_at ASC, return list of MessageResponse. Return empty list (not error) if no messages exist.

**Checkpoint**: Messages can be created and retrieved in chronological order. Conversation updated_at is bumped on new messages. Cross-user message operations return 404.

---

## Phase 5: User Story 3 - Manage Conversation Lifecycle (Priority: P3)

**Goal**: Users can update conversation titles and delete conversations with cascade message removal.

**Independent Test**: Create a conversation with messages, update the title and verify change persists, delete the conversation and verify both conversation and messages are gone.

### Implementation for User Story 3

- [x] T012 [US3] Implement PATCH `"/{conversation_id}"` endpoint (update_conversation) in `backend/routers/conversations.py`: verify conversation exists AND belongs to authenticated user (404 if not), apply title update from ConversationUpdate (exclude_unset), set updated_at to _utcnow(), commit and return ConversationResponse.
- [x] T013 [US3] Implement DELETE `"/{conversation_id}"` endpoint (delete_conversation) in `backend/routers/conversations.py`: verify conversation exists AND belongs to authenticated user (404 if not), delete conversation (cascade deletes messages via ORM relationship + DB FK), commit, return 204 No Content.

**Checkpoint**: Conversation titles can be updated. Deleting a conversation removes all associated messages. Cross-user operations return 404.

---

## Phase 6: Verification & Polish

**Purpose**: End-to-end validation across all user stories

- [x] T014 Verify server starts without errors and tables `conversations` and `messages` are auto-created in Neon PostgreSQL by running `uvicorn main:app --reload --port 8000` from `backend/`
- [x] T015 Run quickstart.md validation steps 3-9 from `specs/004-conversation-message-persistence/quickstart.md` to verify all CRUD operations, message ordering, cascade delete, and cross-user isolation
- [x] T016 Verify existing todos API still functions correctly (GET /api/todos, POST /api/todos) to confirm Compatibility Guarantee

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2 — creates the router file and core endpoints
- **Phase 4 (US2)**: Depends on Phase 3 — adds message endpoints to existing router
- **Phase 5 (US3)**: Depends on Phase 3 — adds lifecycle endpoints to existing router
- **Phase 6 (Verification)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2. Creates the router file that US2 and US3 extend.
- **US2 (P2)**: Can start after US1 (adds endpoints to same router file). Could theoretically run in parallel if endpoints are added to separate sections, but sequential is safer for a single file.
- **US3 (P3)**: Can start after US1 (adds endpoints to same router file). Independent of US2.

### Within Each User Story

- Models before endpoints (Phase 2 handles all models)
- Endpoint implementation in logical order (create → read → update → delete)
- Router registration (T009) after at least one endpoint exists

### Parallel Opportunities

- T001 and T002 (Phase 1) can run in parallel — different files
- T003, T004, T005 (Phase 2) are sequential — same file (`models.py`)
- T006, T007, T008 (Phase 3) are sequential — same file (`conversations.py`)
- T012 and T013 (Phase 5) are sequential — same file (`conversations.py`)
- T014, T015, T016 (Phase 6) are sequential — verification order matters

---

## Parallel Example: Phase 1

```bash
# Restore both router files in parallel:
Task: "Restore backend/routers/__init__.py"
Task: "Restore backend/routers/todos.py from git history"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Restore routers directory
2. Complete Phase 2: Add models and schemas to models.py
3. Complete Phase 3: Conversation CRUD endpoints + router registration
4. **STOP and VALIDATE**: Test conversation create/list/get via curl
5. Proceed to US2 and US3

### Incremental Delivery

1. Phase 1 + Phase 2 → Foundation ready (models defined, tables created)
2. Add US1 (Phase 3) → Conversations work → Validate (MVP!)
3. Add US2 (Phase 4) → Messages work → Validate
4. Add US3 (Phase 5) → Lifecycle management works → Validate
5. Phase 6 → Full end-to-end verification

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- All endpoints reuse `get_current_user` dependency from `backend/auth.py`
- All endpoints reuse `get_session` dependency from `backend/database.py`
- No new Python dependencies required
- Existing Task model and todos router remain completely untouched
- Tables auto-create on startup via existing `create_db_and_tables()` in `database.py`
- Commit after each phase or logical group
