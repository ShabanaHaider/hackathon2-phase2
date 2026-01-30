# Tasks: Task CRUD API

**Input**: Design documents from `/specs/001-task-crud-api/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Tests**: Not explicitly requested in the feature specification. No test tasks generated.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app (backend only)**: `backend/` at repository root
- Paths assume `backend/` as the project root per plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependency declaration, environment configuration

- [x] T001 Create `backend/` directory with `routers/` subdirectory
- [x] T002 [P] Create `backend/requirements.txt` with dependencies: fastapi, uvicorn[standard], sqlmodel, asyncpg, python-dotenv
- [x] T003 [P] Create `backend/.env.example` with `DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require`
- [x] T004 [P] Add `backend/.env` and `backend/__pycache__/` and `backend/.venv/` to `.gitignore`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database connection, SQLModel engine, FastAPI app skeleton — MUST be complete before ANY user story

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create `backend/database.py` with async SQLAlchemy engine using `DATABASE_URL` from environment, async session factory (`AsyncSession`), and `create_db_and_tables()` function that calls `SQLModel.metadata.create_all()` via `run_sync`
- [x] T006 Create `backend/models.py` with SQLModel `Task` table class containing all 8 fields from data-model.md: `id` (UUID, default uuid4, primary key), `title` (str, max 255, not null), `description` (Optional[str], max 2000), `is_completed` (bool, default False), `completed_at` (Optional[datetime], nullable), `created_at` (datetime, default utcnow), `updated_at` (datetime, default utcnow), `user_id` (str, not null, indexed)
- [x] T007 Create Pydantic request/response schemas in `backend/models.py`: `TaskCreate` (title: str required 1-255, description: Optional[str] max 2000), `TaskUpdate` (title: Optional[str] 1-255, description: Optional[str] max 2000, is_completed: Optional[bool]) with all fields optional for partial update, `TaskResponse` (all 8 fields, serialized with ISO 8601 datetimes)
- [x] T008 Create `backend/main.py` with FastAPI app, lifespan event that calls `create_db_and_tables()` on startup, CORS middleware (allow all origins for dev), and include the todos router under prefix `/api`
- [x] T009 Create empty `backend/routers/__init__.py` and `backend/__init__.py` files
- [x] T010 Create `backend/routers/todos.py` with an `APIRouter` registered at `/users/{user_id}/todos`, import session dependency — leave endpoint functions as stubs returning placeholder responses

**Checkpoint**: FastAPI app starts, connects to Neon PostgreSQL, creates `tasks` table, and serves the `/docs` endpoint. Router is mounted but endpoints return stubs.

---

## Phase 3: User Story 1 — Create a New Task (Priority: P1) MVP

**Goal**: A user can create a task with a title and optional description. The system persists it and returns the created task with UUID, timestamps, and default status.

**Independent Test**: `curl -X POST http://localhost:8000/api/users/user-1/todos -H "Content-Type: application/json" -d '{"title":"Test task"}'` returns 201 with full task object.

### Implementation for User Story 1

- [x] T011 [US1] Implement `POST /api/users/{user_id}/todos` endpoint in `backend/routers/todos.py`: accept `TaskCreate` body and `user_id` path param, create `Task` instance with `user_id` set from path, persist via async session, return `TaskResponse` with status 201
- [x] T012 [US1] Add auto-timestamp logic in `backend/models.py` or endpoint: set `created_at` and `updated_at` to `datetime.utcnow()` on creation, ensure `is_completed` defaults to `False` and `completed_at` is `None`
- [x] T013 [US1] Add validation in `backend/models.py` `TaskCreate` schema: title must be 1-255 chars (use Pydantic `Field(min_length=1, max_length=255)`), description max 2000 chars — ensure 422 response on violation

**Checkpoint**: POST creates a task in the database and returns it with UUID id, timestamps, and correct status. Invalid titles return 422.

---

## Phase 4: User Story 2 — List All Tasks for a User (Priority: P1)

**Goal**: A user retrieves all their tasks. The system returns only tasks belonging to that user.

**Independent Test**: Create tasks for user-1 and user-2, then `curl http://localhost:8000/api/users/user-1/todos` returns only user-1's tasks.

### Implementation for User Story 2

- [x] T014 [US2] Implement `GET /api/users/{user_id}/todos` endpoint in `backend/routers/todos.py`: query `tasks` table filtered by `user_id == path param`, return list of `TaskResponse`, status 200
- [x] T015 [US2] Ensure empty list response (not error) when user has no tasks — return `[]` with status 200

**Checkpoint**: GET list returns only the requesting user's tasks. Different user_ids return different task sets. Empty users get `[]`.

---

## Phase 5: User Story 3 — View a Single Task (Priority: P2)

**Goal**: A user retrieves a single task by UUID. Returns the task only if it belongs to that user.

**Independent Test**: Create a task for user-1, GET it by ID as user-1 (200), GET it as user-2 (404), GET non-existent UUID (404).

### Implementation for User Story 3

- [x] T016 [US3] Implement `GET /api/users/{user_id}/todos/{task_id}` endpoint in `backend/routers/todos.py`: query by `id == task_id AND user_id == user_id`, return `TaskResponse` with status 200, raise `HTTPException(404)` if not found or wrong user
- [x] T017 [US3] Ensure 404 response uses consistent JSON format `{"detail": "Task not found"}` — never 403, per research decision R4

**Checkpoint**: GET single returns task for owner, 404 for non-owner and non-existent IDs.

---

## Phase 6: User Story 4 — Update an Existing Task (Priority: P2)

**Goal**: A user partially updates their task's title, description, or completion status. Only provided fields are changed.

**Independent Test**: Create a task, PATCH `{"is_completed": true}`, verify `is_completed` is true and `completed_at` is set. PATCH `{"title": "New"}`, verify title changed but `is_completed` unchanged.

### Implementation for User Story 4

- [x] T018 [US4] Implement `PATCH /api/users/{user_id}/todos/{task_id}` endpoint in `backend/routers/todos.py`: query by `id AND user_id`, apply only non-null fields from `TaskUpdate` body using `model.model_dump(exclude_unset=True)`, update `updated_at` to now, persist and return `TaskResponse` with status 200, raise 404 if not found or wrong user
- [x] T019 [US4] Implement `completed_at` auto-management in the PATCH endpoint: when `is_completed` changes to `True`, set `completed_at = datetime.utcnow()`; when it changes to `False`, set `completed_at = None` — per data-model.md state transitions
- [x] T020 [US4] Add validation for `TaskUpdate` in `backend/models.py`: if `title` is provided, it must be 1-255 chars; if `description` is provided, max 2000 chars — use Pydantic `Field` with constraints, all fields `Optional` with `None` default

**Checkpoint**: PATCH updates only provided fields. Completion toggle manages `completed_at` automatically. Invalid updates return 422. Cross-user updates return 404.

---

## Phase 7: User Story 5 — Delete a Task (Priority: P3)

**Goal**: A user permanently deletes a task they own. The system confirms deletion.

**Independent Test**: Create a task, DELETE it (204), GET it (404). Try DELETE as another user (404).

### Implementation for User Story 5

- [x] T021 [US5] Implement `DELETE /api/users/{user_id}/todos/{task_id}` endpoint in `backend/routers/todos.py`: query by `id AND user_id`, delete from database, return status 204 (no content body), raise 404 if not found or wrong user
- [x] T022 [US5] Ensure DELETE returns empty response body with 204 status using FastAPI `Response(status_code=204)` — not a JSON body

**Checkpoint**: DELETE removes the task permanently. 204 with no body on success. 404 for non-owner or non-existent.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Error handling hardening, validation edge cases, database error handling

- [x] T023 [P] Add global exception handler in `backend/main.py` for database connection errors — return 500 with `{"detail": "Internal server error"}`, do not expose connection strings or stack traces
- [x] T024 [P] Verify all endpoints ignore client-supplied `id`, `created_at`, `updated_at`, and `completed_at` fields in create/update request bodies — ensure `TaskCreate` and `TaskUpdate` schemas do not accept these fields
- [x] T025 Run quickstart.md verification checklist manually via curl: test all 9 items (POST 201, GET list scoping, GET single 404, PATCH partial, PATCH completed_at, DELETE 204, DELETE 404, POST empty title 422, persistence across restart)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (Phase 3) and US2 (Phase 4) can proceed in parallel after Foundation
  - US3 (Phase 5) can proceed after Foundation (independent of US1/US2)
  - US4 (Phase 6) can proceed after Foundation (independent, but logically benefits from US1 existing)
  - US5 (Phase 7) can proceed after Foundation (independent)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (Create)**: After Foundation — no dependencies on other stories
- **US2 (List)**: After Foundation — no dependencies on other stories
- **US3 (View Single)**: After Foundation — no dependencies on other stories
- **US4 (Update)**: After Foundation — no dependencies on other stories
- **US5 (Delete)**: After Foundation — no dependencies on other stories

All user stories are independently implementable and testable after the Foundation phase.

### Within Each User Story

- Endpoint implementation before validation hardening
- Core logic before edge-case handling
- Story complete before moving to next priority

### Parallel Opportunities

- T002, T003, T004 can run in parallel (different files, Phase 1)
- T023, T024 can run in parallel (different concerns, Phase 8)
- All user story phases (3-7) can theoretically run in parallel since they all modify `backend/routers/todos.py` — but since they share a file, sequential execution within `todos.py` is safer. Models file tasks are separate.

---

## Parallel Example: Phase 1 Setup

```bash
# Launch all setup tasks together:
Task: "Create backend/requirements.txt"
Task: "Create backend/.env.example"
Task: "Add .gitignore entries"
```

## Parallel Example: User Stories After Foundation

```bash
# After Phase 2 is complete, stories can start:
# Sequential within todos.py is recommended, but models work can parallel:
Task: "Implement POST endpoint (US1)"
Task: "Implement GET list endpoint (US2)"
# Then:
Task: "Implement GET single endpoint (US3)"
Task: "Implement PATCH endpoint (US4)"
Task: "Implement DELETE endpoint (US5)"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: US1 — Create Task
4. Complete Phase 4: US2 — List Tasks
5. **STOP and VALIDATE**: Create tasks and list them. Verify user scoping.
6. This is the MVP — a user can create and view tasks.

### Incremental Delivery

1. Setup + Foundation → App starts and connects to DB
2. Add US1 (Create) → Test POST independently → Verify DB persistence
3. Add US2 (List) → Test GET list → Verify user scoping
4. Add US3 (View) → Test GET single → Verify 404 security
5. Add US4 (Update) → Test PATCH → Verify partial updates + completed_at
6. Add US5 (Delete) → Test DELETE → Verify 204 + permanence
7. Polish → Error handling + validation edge cases
8. Run full quickstart.md checklist

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable after Foundation
- No test tasks generated — spec did not request automated tests
- Total: 25 tasks across 8 phases
- All endpoints share `backend/routers/todos.py` — execute story implementations sequentially within this file
- Commit after each phase or logical group
