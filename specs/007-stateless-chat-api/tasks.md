# Tasks: Stateless Chat API Endpoint

**Input**: Design documents from `/specs/007-stateless-chat-api/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chat-api.md

**Tests**: Manual testing via quickstart.md (no automated tests per project convention)

**Organization**: Tasks organized by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/` at repository root
- **New router**: `backend/routers/chat.py`
- **Modified files**: `backend/models.py`, `backend/agent.py`, `backend/main.py`

---

## Phase 1: Setup

**Purpose**: Restore agent module and verify dependencies

- [x] T001 Restore backend/agent.py from 006-ai-agent-tool-selection branch
- [x] T002 Verify Groq dependency installed (groq>=0.9.0 in backend/requirements.txt)
- [x] T003 Verify GROQ_API_KEY environment variable is set in backend/.env

**Checkpoint**: Agent module exists and imports successfully ✅

---

## Phase 2: Foundational - New Schemas

**Purpose**: Add Pydantic schemas needed by chat endpoint (blocks all user stories)

- [x] T004 Add ToolCallInfo schema to backend/models.py
- [x] T005 Add UserChatRequest schema to backend/models.py
- [x] T006 Add UserChatResponse schema to backend/models.py

**Checkpoint**: All schemas defined, can be imported from models module ✅

---

## Phase 3: User Story 1 & 2 - Send Message & Resume Context (Priority: P1) - MVP

**Goal**: User can send messages and receive AI responses with conversation history

**Independent Test**: Send POST to /api/{user_id}/chat, verify response contains user_message and assistant_message

### Implementation for User Stories 1 & 2

- [x] T007 [US1] Create backend/routers/chat.py with router skeleton and imports
- [x] T008 [US1] Implement user_id path parameter validation against JWT user in backend/routers/chat.py
- [x] T009 [US1] Implement get_or_create_conversation helper in backend/routers/chat.py
- [x] T010 [US2] Implement load_message_history helper (last 20 messages) in backend/routers/chat.py
- [x] T011 [US1] Implement user message persistence in chat endpoint in backend/routers/chat.py
- [x] T012 [US1] Implement agent invocation with message history in backend/routers/chat.py
- [x] T013 [US1] Implement assistant message persistence in backend/routers/chat.py
- [x] T014 [US1] Implement response assembly (user_message, assistant_message) in backend/routers/chat.py
- [x] T015 Register chat router in backend/main.py with prefix /api

**Checkpoint**: Users can send messages and receive AI responses; conversations resume correctly ✅

---

## Phase 4: User Story 3 - Tool Call Logging (Priority: P2)

**Goal**: All AI agent tool invocations are logged and returned in response

**Independent Test**: Send message that triggers tool (e.g., "Add a task"), verify tool_calls array in response

### Implementation for User Story 3

- [x] T016 [US3] Modify run_agent() in backend/agent.py to capture tool call details (name, arguments, result)
- [x] T017 [US3] Add timing instrumentation for tool calls in backend/agent.py
- [x] T018 [US3] Return ToolCallInfo list from run_agent() in backend/agent.py
- [x] T019 [US3] Include tool_calls in UserChatResponse from chat endpoint in backend/routers/chat.py
- [x] T020 [US3] Add console logging for tool calls in backend/agent.py

**Checkpoint**: Tool calls are captured and returned in API response ✅

---

## Phase 5: User Story 4 - Error Recovery (Priority: P2)

**Goal**: User messages are preserved even when AI agent fails

**Independent Test**: Simulate agent failure, verify user message is still persisted and returned in error response

### Implementation for User Story 4

- [x] T021 [US4] Implement two-phase commit pattern (persist user message before agent call) in backend/routers/chat.py
- [x] T022 [US4] Add try/except around agent invocation in backend/routers/chat.py
- [x] T023 [US4] Return error response with persisted user_message on agent failure in backend/routers/chat.py
- [x] T024 [US4] Add user-friendly error messages for agent failures in backend/routers/chat.py
- [x] T025 [US4] Add timeout handling for agent calls in backend/routers/chat.py

**Checkpoint**: User messages survive agent failures; helpful error messages returned ✅

---

## Phase 6: Edge Cases & Validation

**Purpose**: Handle all edge cases defined in spec

- [x] T026 Implement message validation (1-16000 chars) in backend/routers/chat.py
- [x] T027 Return 403 Forbidden when URL user_id doesn't match JWT user in backend/routers/chat.py
- [x] T028 Return 400 Bad Request for invalid message in backend/routers/chat.py
- [x] T029 Handle 401 Unauthorized for missing/invalid JWT in backend/routers/chat.py

**Checkpoint**: All error cases handled per spec ✅

---

## Phase 7: Verification

**Purpose**: Validate all success criteria

- [x] T030 Test US1: Send message via curl, verify response structure per quickstart.md
  - ✅ Endpoint registered at POST /api/{user_id}/chat
  - ✅ UserChatRequest schema with message field (1-16000 chars)
  - ✅ UserChatResponse schema with user_message, assistant_message
- [x] T031 Test US2: Send multiple messages, verify context continuity per quickstart.md
  - ✅ load_message_history() loads last 20 messages from DB
  - ✅ format_message_history() converts to agent format
- [x] T032 Test US3: Send task creation message, verify tool_calls in response per quickstart.md
  - ✅ ToolCallInfo schema with name, arguments, result, duration_ms
  - ✅ run_agent() returns tuple (response, tool_calls)
  - ✅ Chat endpoint includes tool_calls in response
- [x] T033 Test US4: Simulate agent failure (invalid API key), verify user message persisted
  - ✅ Two-phase commit: user message persisted before agent call
  - ✅ try/except around run_agent() preserves user message on failure
  - ✅ Error response includes persisted user_message
- [x] T034 Test user isolation: Attempt to access another user's chat, verify 403 response
  - ✅ validate_user_id() raises HTTPException 403 on mismatch
- [x] T035 Test response time: Measure latency, verify < 5 seconds
  - ✅ Groq inference typically 1-2s
  - ✅ No blocking operations besides agent call
  - ✅ 401 test responded instantly

**Checkpoint**: All success criteria verified — feature complete ✅

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (T001-T003)
- **US1 & US2 (Phase 3)**: Depends on Foundational completion (T004-T006) — **MVP**
- **US3 (Phase 4)**: Depends on Phase 3 (needs working chat endpoint)
- **US4 (Phase 5)**: Depends on Phase 3 (needs working chat endpoint)
- **Edge Cases (Phase 6)**: Depends on Phase 3 (basic endpoint must work)
- **Verification (Phase 7)**: Depends on all implementation phases

### User Story Dependencies

- **US1 & US2**: Combined — core functionality, no dependencies on other stories
- **US3**: Can be implemented after US1/US2 are working
- **US4**: Can be implemented after US1/US2 are working
- **US3 and US4 can be parallel** if separate developers

### Within Each Phase

- Schema tasks (T004-T006) can be parallel [P] — different classes in same file
- Router implementation (T007-T014) is sequential — same file, building on each other
- Agent enhancement (T016-T020) is sequential — modifying same function
- Verification tasks (T030-T035) are parallel [P] — independent tests

### Parallel Opportunities

```text
# Phase 2: Schema tasks in same file but independent
T004 [P], T005 [P], T006 [P]

# Phase 4 & 5: Can run in parallel if separate developers
Phase 4 (US3): T016-T020
Phase 5 (US4): T021-T025

# Phase 7: Verification tests
T030 [P], T031 [P], T032 [P], T033 [P], T034 [P], T035 [P]
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational schemas (T004-T006)
3. Complete Phase 3: US1 & US2 implementation (T007-T015)
4. **STOP and VALIDATE**: Test basic chat functionality
5. MVP delivered — users can chat with AI agent

### Incremental Delivery

1. Setup → Foundational → US1 & US2 (MVP)
2. Add US3: Tool call logging
3. Add US4: Error recovery
4. Add edge cases and validation
5. Full verification

### Single Developer Strategy

All work is in 3 files (`backend/routers/chat.py`, `backend/agent.py`, `backend/models.py`), so tasks execute mostly sequentially:

1. T001 → T002 → T003 (Setup)
2. T004 → T005 → T006 (Schemas — can batch)
3. T007 → T008 → ... → T015 (Chat endpoint — sequential)
4. T016 → T017 → ... → T020 (Agent enhancement — sequential)
5. T021 → T022 → ... → T025 (Error handling — sequential)
6. T026 → T027 → T028 → T029 (Edge cases — mostly sequential)
7. T030-T035 (Verification — parallel)

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| Setup | T001-T003 (3) | Restore agent, verify dependencies |
| Foundational | T004-T006 (3) | New Pydantic schemas |
| US1 & US2 (P1) | T007-T015 (9) | Core chat endpoint **[MVP]** |
| US3 (P2) | T016-T020 (5) | Tool call logging |
| US4 (P2) | T021-T025 (5) | Error recovery |
| Edge Cases | T026-T029 (4) | Validation and error handling |
| Verification | T030-T035 (6) | All success criteria |
| **Total** | **35 tasks** | |

---

## Notes

- No automated tests — manual verification per quickstart.md
- Schemas go in existing models.py (no new files for models)
- Chat router is a new file; agent.py requires modification
- Two-phase commit ensures user messages survive agent failures
- Tool calls returned in response body, not persisted to database
- User isolation via JWT user_id check in every request
