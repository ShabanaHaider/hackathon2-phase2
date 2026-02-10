# Implementation Plan: Task CRUD API

**Branch**: `001-task-crud-api` | **Date**: 2026-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-task-crud-api/spec.md`

## Summary

Build a RESTful API for task management using FastAPI and SQLModel backed by
Neon Serverless PostgreSQL. The API exposes five CRUD endpoints scoped by
user_id (accepted as a path parameter). Tasks are persisted with UUID
primary keys, ISO 8601 timestamps, and boolean completion status. User
identity is a trusted input — no authentication enforcement in this feature.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, SQLModel, asyncpg, uvicorn, pydantic
**Storage**: Neon Serverless PostgreSQL (via asyncpg + SQLAlchemy async engine)
**Testing**: Manual API testing via curl/Postman; pytest available for future use
**Target Platform**: Linux server (backend API)
**Project Type**: Web application (backend only for this feature)
**Performance Goals**: Standard web API; 100-task list retrieval in a single request
**Constraints**: No auth enforcement; user_id as trusted path parameter
**Scale/Scope**: Multi-user task management; hackathon evaluation scope

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. End-to-End Correctness | PASS (partial) | Backend + DB verified; frontend out of scope for this feature |
| II. User Data Isolation | PASS | All queries filter by user_id; 404 returned for cross-user access (R4) |
| III. Spec-Driven Development | PASS | Spec exists at spec.md; plan derived from spec; tasks will follow |
| IV. Framework-Idiomatic | PASS | FastAPI DI, Pydantic models, SQLModel ORM, async endpoints (R5) |
| V. RESTful API Design | PASS | Plural nouns `/todos`, correct HTTP methods, user-scoped paths (contract) |
| VI. Secret Management | PASS | DATABASE_URL via .env; .env.example provided (quickstart.md) |

**Gate result**: PASS — all principles satisfied within feature scope.

## Project Structure

### Documentation (this feature)

```text
specs/001-task-crud-api/
├── plan.md              # This file
├── research.md          # Phase 0 output — 7 research decisions
├── data-model.md        # Phase 1 output — Task entity schema
├── quickstart.md        # Phase 1 output — Setup and verification guide
├── contracts/
│   └── openapi.yaml     # Phase 1 output — OpenAPI 3.1 contract
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── main.py              # FastAPI app creation, CORS, lifespan
├── database.py          # Async engine, session factory, table creation
├── models.py            # SQLModel Task model (table + Pydantic schemas)
├── routers/
│   └── todos.py         # CRUD endpoints for /api/users/{user_id}/todos
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
└── .env                 # Local secrets (gitignored)
```

**Structure Decision**: Web application backend-only layout. The `backend/`
directory contains the FastAPI application. No `frontend/` directory for this
feature — frontend is out of scope. The structure follows the constitution's
web app convention with `backend/` as the root.

## Key Design Decisions

### D1: UUID Primary Keys (Research R1)

Tasks use UUID v4 as primary keys. Prevents enumeration attacks and aligns
with the spec requirement for system-generated UUIDs. No auto-increment
integers.

### D2: No Local Users Table (Research R2)

The `user_id` column is a plain string — no foreign key to a users table.
The user is an external entity from Better Auth. This keeps the feature
decoupled from authentication.

### D3: PATCH for Partial Updates (Research R3)

Updates use HTTP PATCH with partial payloads. Only fields present in the
request body are modified. This is idiomatic REST for selective updates.

### D4: 404 for Cross-User Access (Research R4)

All "not found or not yours" cases return 404. Never 403. This prevents
information leakage about task ID existence.

### D5: Async Database Access (Research R5)

SQLModel with async SQLAlchemy engine and `asyncpg` driver. Non-blocking
database I/O matches FastAPI's async nature.

### D6: Automatic Timestamp Management (Research R6)

`created_at` set on insert, `updated_at` set on every write, `completed_at`
set/cleared based on `is_completed` toggle. All UTC, all read-only to clients.

## API Endpoint Summary

| Method | Path                                  | Status | Description       |
|--------|---------------------------------------|--------|-------------------|
| POST   | /api/users/{user_id}/todos            | 201    | Create task       |
| GET    | /api/users/{user_id}/todos            | 200    | List user's tasks |
| GET    | /api/users/{user_id}/todos/{task_id}  | 200    | Get single task   |
| PATCH  | /api/users/{user_id}/todos/{task_id}  | 200    | Update task       |
| DELETE | /api/users/{user_id}/todos/{task_id}  | 204    | Delete task       |

Error responses: 404 (not found / not owner), 422 (validation), 500 (server error).

Full contract: [contracts/openapi.yaml](./contracts/openapi.yaml)

## Implementation Phases

### Phase 1: Project Setup
- Create `backend/` directory structure
- Initialize `requirements.txt` with dependencies
- Create `.env.example` with `DATABASE_URL` placeholder
- Create `main.py` with FastAPI app skeleton

### Phase 2: Database Layer
- Create `database.py` with async engine and session management
- Connect to Neon PostgreSQL via `DATABASE_URL` environment variable
- Implement table auto-creation on startup via lifespan event

### Phase 3: Data Model
- Create `models.py` with SQLModel `Task` table model
- Define Pydantic schemas: `TaskCreate`, `TaskUpdate`, `TaskResponse`
- Implement field validation (title length, description length)
- Implement automatic timestamp handling

### Phase 4: CRUD Endpoints
- Create `routers/todos.py` with all five endpoints
- Implement user_id scoping on all queries
- Implement PATCH partial update logic
- Implement completed_at auto-management on is_completed toggle
- Return correct HTTP status codes per contract

### Phase 5: Error Handling & Validation
- Return 404 for non-existent or cross-user task access
- Return 422 for validation failures (empty title, oversized fields)
- Return 500 with safe error message for database failures
- Ensure consistent JSON error response format

## Complexity Tracking

No constitution violations. No complexity justifications needed.

## Artifacts Generated

| Artifact | Path | Status |
|----------|------|--------|
| Research | specs/001-task-crud-api/research.md | Complete (7 decisions) |
| Data Model | specs/001-task-crud-api/data-model.md | Complete |
| API Contract | specs/001-task-crud-api/contracts/openapi.yaml | Complete (OpenAPI 3.1) |
| Quickstart | specs/001-task-crud-api/quickstart.md | Complete |
| Plan | specs/001-task-crud-api/plan.md | Complete (this file) |
