# Tasks: MCP Server & Task Tools

**Input**: Design documents from `/specs/005-mcp-server-task-tools/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/mcp-tools.md

**Tests**: Not explicitly requested in spec. Verification via quickstart.md manual testing.

**Organization**: Tasks grouped by user story (US1: add/list, US2: update/complete, US3: delete).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/` at repository root
- MCP server: `backend/mcp_server.py` (single new file)

---

## Phase 1: Setup

**Purpose**: Add MCP SDK dependency and create server skeleton

- [x] T001 Add `mcp[cli]` to backend/requirements.txt
- [x] T002 Create backend/mcp_server.py with FastMCP initialization and stdio transport
- [x] T003 Add synchronous database engine and session helper to backend/mcp_server.py

**Checkpoint**: MCP server can be started with `python mcp_server.py` (no tools yet)

---

## Phase 2: User Story 1 - Add and List Tasks (Priority: P1) 🎯 MVP

**Goal**: AI agent can create tasks and list a user's tasks via MCP tools

**Independent Test**: Invoke `add_task` with valid params, then `list_tasks` for same user — new task appears in list

### Implementation for User Story 1

- [x] T004 [US1] Implement `add_task` tool in backend/mcp_server.py
- [x] T005 [US1] Implement `list_tasks` tool in backend/mcp_server.py
- [x] T006 [US1] Add input validation for `add_task` (empty title, title > 255 chars, empty user_id)
- [x] T007 [US1] Add input validation for `list_tasks` (empty user_id)

**Checkpoint**: US1 complete — `add_task` and `list_tasks` work with valid/invalid inputs

---

## Phase 3: User Story 2 - Update and Complete Tasks (Priority: P2)

**Goal**: AI agent can modify task details and toggle completion status

**Independent Test**: Create task via `add_task`, call `update_task` to change title, verify change; call `complete_task`, verify status toggle

### Implementation for User Story 2

- [x] T008 [US2] Implement `update_task` tool in backend/mcp_server.py
- [x] T009 [US2] Implement `complete_task` tool in backend/mcp_server.py
- [x] T010 [US2] Add input validation for `update_task` (invalid UUID, empty update, cross-user)
- [x] T011 [US2] Add input validation for `complete_task` (invalid UUID, cross-user)

**Checkpoint**: US2 complete — `update_task` and `complete_task` work; cross-user returns not-found

---

## Phase 4: User Story 3 - Delete Tasks (Priority: P3)

**Goal**: AI agent can permanently remove a user's task

**Independent Test**: Create task via `add_task`, call `delete_task`, call `list_tasks` to confirm removal

### Implementation for User Story 3

- [x] T012 [US3] Implement `delete_task` tool in backend/mcp_server.py
- [x] T013 [US3] Add input validation for `delete_task` (invalid UUID, not found, cross-user)

**Checkpoint**: US3 complete — `delete_task` works; cross-user returns not-found

---

## Phase 5: Verification & Polish

**Purpose**: Validate all success criteria and ensure REST API compatibility

- [x] T014 Verify all 5 tools work via quickstart.md verification steps
- [x] T015 Verify cross-user isolation (SC-002) for all tools
- [x] T016 Verify REST API at /api/todos still works unchanged (SC-005)

**Checkpoint**: All success criteria verified — feature complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **US1 (Phase 2)**: Depends on Setup completion (T001-T003)
- **US2 (Phase 3)**: Can start after Setup, but builds on US1 for testing
- **US3 (Phase 4)**: Can start after Setup, but builds on US1 for testing
- **Verification (Phase 5)**: Depends on all user stories complete

### Within Each User Story

- Tool implementation before validation
- All tools in same file (backend/mcp_server.py) — sequential within story

### Parallel Opportunities

- T001 (requirements.txt) independent of T002-T003 (but T002-T003 need mcp installed)
- US2 and US3 could theoretically be parallel (different tools), but share same file
- T014, T015, T016 in Phase 5 are [P] — different verification targets

---

## Parallel Example: Phase 5 Verification

```bash
# These can run in parallel (different verification targets):
Task T014: "Verify all 5 tools work via quickstart.md verification steps"
Task T015: "Verify cross-user isolation (SC-002) for all tools"
Task T016: "Verify REST API at /api/todos still works unchanged (SC-005)"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: US1 — add_task + list_tasks (T004-T007)
3. **STOP and VALIDATE**: Test US1 with MCP Inspector or manual JSON-RPC
4. AI agent can now create and list tasks — MVP delivered!

### Incremental Delivery

1. Setup → US1 → Verify add/list work (MVP)
2. Add US2 → Verify update/complete work
3. Add US3 → Verify delete works
4. Full verification (Phase 5) → Feature complete

### Single Developer Strategy

All work is in `backend/mcp_server.py`, so tasks execute sequentially:
1. T001 → T002 → T003 (Setup)
2. T004 → T005 → T006 → T007 (US1)
3. T008 → T009 → T010 → T011 (US2)
4. T012 → T013 (US3)
5. T014 → T015 → T016 (Verification)

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| Setup | T001-T003 (3) | MCP SDK, server skeleton, DB session |
| US1 (P1) | T004-T007 (4) | add_task, list_tasks + validation |
| US2 (P2) | T008-T011 (4) | update_task, complete_task + validation |
| US3 (P3) | T012-T013 (2) | delete_task + validation |
| Verification | T014-T016 (3) | Quickstart, isolation, REST compat |
| **Total** | **16 tasks** | |

---

## Notes

- All 5 tools implemented in single file `backend/mcp_server.py`
- Uses synchronous SQLModel sessions (not async)
- user_id passed as explicit parameter to each tool
- Returns plain text strings for AI agent to reformulate
- Existing REST API unchanged (compatibility guarantee)
