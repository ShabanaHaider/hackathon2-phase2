# Implementation Plan: MCP Server & Task Tools

**Branch**: `005-mcp-server-task-tools` | **Date**: 2026-02-06 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-mcp-server-task-tools/spec.md`

## Summary

Implement a standalone MCP server module (`backend/mcp_server.py`) using
the Official MCP Python SDK (`FastMCP`). The server exposes 5 stateless
tools (`add_task`, `list_tasks`, `update_task`, `complete_task`,
`delete_task`) that perform CRUD operations on the existing Task table
via synchronous SQLModel sessions. The server runs as a separate process
using stdio transport and shares the database connection configuration
from `.env`.

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: `mcp[cli]` (Official MCP SDK), SQLModel, python-dotenv
**Storage**: Neon Serverless PostgreSQL (existing, via synchronous `sqlmodel.Session`)
**Testing**: Python script with MCP client or direct JSON-RPC over stdio
**Target Platform**: Linux server (WSL2 dev environment)
**Project Type**: Web application (backend module addition)
**Constraints**: Stateless tools, no in-memory state, no AI logic in tools

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. End-to-End Correctness | PASS | Each tool performs a single DB operation and returns the result |
| II. User Data Isolation | PASS | All tools filter by user_id; cross-user returns "not found" |
| III. Spec-Driven Development | PASS | Following spec → plan → tasks → implement workflow |
| IV. Framework-Idiomatic | PASS | Using official FastMCP decorator pattern |
| V. RESTful API Design | N/A | MCP tools, not REST endpoints |
| VI. Environment-Based Secrets | PASS | DATABASE_URL from .env, no hardcoded secrets |
| VII. Agentic AI & Tool-Oriented | PASS | Tools are pure DB wrappers, no AI logic inside |
| VIII. Stateless AI Interactions | PASS | No in-memory state between invocations |
| Compatibility Guarantee | PASS | REST API unchanged; MCP is additive |
| Loose Coupling | PASS | MCP server → DB only; no frontend access |

**Post-design re-check**: All gates PASS. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/005-mcp-server-task-tools/
├── plan.md              # This file
├── research.md          # Phase 0: 6 research decisions
├── data-model.md        # Phase 1: Task entity + tool schemas
├── quickstart.md        # Phase 1: 10 verification steps
├── contracts/
│   └── mcp-tools.md     # Phase 1: 5 tool contracts
└── tasks.md             # Phase 2 (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── mcp_server.py        # NEW: MCP server with 5 task tools
├── models.py            # EXISTING: Task SQLModel (no changes)
├── database.py          # EXISTING: async engine (not used by MCP)
├── main.py              # EXISTING: FastAPI app (no changes)
├── auth.py              # EXISTING: JWT auth (not used by MCP)
├── requirements.txt     # MODIFIED: add mcp[cli] dependency
└── routers/
    ├── todos.py          # EXISTING: REST API (unchanged)
    └── conversations.py  # EXISTING: REST API (unchanged)
```

**Structure Decision**: Single new file `backend/mcp_server.py`. The MCP
server imports the `Task` model from `models.py` and reads `DATABASE_URL`
from `.env` via `dotenv`. It creates its own synchronous `Engine` and
`Session` (separate from FastAPI's async engine) because it runs as a
standalone process.

## Design Decisions

### D1: Synchronous DB Access in MCP Server

The MCP server uses synchronous `sqlmodel.Session` with a standard
`create_engine` (not asyncpg). Rationale: The MCP server runs as a
standalone process outside FastAPI's async event loop. Sync access is
simpler and sufficient for sequential tool calls.

### D2: Single-File Module

All 5 tools in one file (`mcp_server.py`). Rationale: 5 simple CRUD
functions don't warrant a package structure. Each tool is a short
decorated function (10-30 lines).

### D3: user_id as Explicit Parameter

Every tool accepts `user_id` as a required string parameter. The AI agent
calling the tools is responsible for providing the correct user identity
from its authenticated session. The MCP server never parses JWTs.

### D4: Text Return Format

Tools return plain text strings describing the result. The AI agent
reformulates these into natural language for the user. No structured
JSON output schema is needed.

## Implementation Phases

### Phase 1: Foundation (Tasks 1-3)

- Add `mcp[cli]` to `requirements.txt`
- Create `backend/mcp_server.py` with FastMCP server initialization
- Create synchronous database engine and session helper
- Implement `add_task` and `list_tasks` tools

### Phase 2: Lifecycle Tools (Tasks 4-6)

- Implement `update_task` tool
- Implement `complete_task` tool
- Implement `delete_task` tool

### Phase 3: Validation & Testing (Tasks 7-8)

- Add input validation for all tools (empty titles, invalid UUIDs, etc.)
- Write verification test script
- Verify cross-user isolation
- Verify REST API compatibility (SC-005)

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Tool schema drift from REST API | Data inconsistency | Both use same Task model from models.py |
| Hidden state in MCP server | Violates Constitution VII | Stateless design: no globals, fresh session per call |
| DB connection string format | Sync engine needs different URL format | Reuse DATABASE_URL parsing from database.py (strip asyncpg params) |
