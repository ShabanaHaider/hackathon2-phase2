# Tasks: AI Agent Behavior & Tool Selection

**Input**: Design documents from `/specs/006-ai-agent-tool-selection/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/agent-tools.md

**Tests**: Manual testing via quickstart.md (no automated tests requested)

**Organization**: Tasks organized by implementation phases from plan.md, then by user story priority.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, etc.)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/` at repository root
- **New file**: `backend/agent.py` (agent definition)
- **Modified file**: `backend/routers/conversations.py` (chat endpoint)

---

## Phase 1: Setup

**Purpose**: Install dependencies and create agent skeleton

- [x] T001 Add `openai-agents>=0.1.0` to backend/requirements.txt
- [x] T002 Create backend/agent.py with OpenAI Agents SDK imports and constants
- [x] T003 Define SYSTEM_PROMPT constant with agent persona and capabilities in backend/agent.py

**Checkpoint**: Agent module exists with prompt constant, dependencies installed

---

## Phase 2: Foundational - Agent Core

**Purpose**: Implement core agent with MCP server connection (blocks all user stories)

- [x] T004 Configure StdioMCPServer to launch backend/mcp_server.py in backend/agent.py
- [x] T005 Create TaskAssistant Agent with name, model, instructions, and mcp_servers in backend/agent.py
- [x] T006 Implement run_agent async function that accepts user_id and message in backend/agent.py
- [x] T007 Add user_id injection to MCP tool calls via tool context in backend/agent.py

**Checkpoint**: Agent can be instantiated and connected to MCP server

---

## Phase 3: User Story 1 & 2 - Create and List Tasks (Priority: P1) - MVP

**Goal**: User can create tasks and list their tasks via natural language

**Independent Test**: Send "Add a task to buy groceries" → task created; Send "Show my tasks" → list appears

### Implementation for User Stories 1 & 2

- [x] T008 [US1] Add intent triggers for add_task to SYSTEM_PROMPT in backend/agent.py
- [x] T009 [US2] Add intent triggers for list_tasks to SYSTEM_PROMPT in backend/agent.py
- [x] T010 [US1] Add confirmation template for task creation to SYSTEM_PROMPT in backend/agent.py
- [x] T011 [US2] Add confirmation template for task listing to SYSTEM_PROMPT in backend/agent.py
- [x] T012 Add clarification behavior guidelines to SYSTEM_PROMPT in backend/agent.py

**Checkpoint**: Agent responds to create and list intents correctly

---

## Phase 4: Conversation Integration

**Purpose**: Connect agent to existing conversation API

- [x] T013 Add chat endpoint POST /conversations/{id}/chat to backend/routers/conversations.py
- [x] T014 Implement message history loading (last 20 messages) in chat endpoint
- [x] T015 Call run_agent with user_id and user message in chat endpoint
- [x] T016 Persist agent response as assistant message in chat endpoint
- [x] T017 Return agent response to frontend from chat endpoint

**Checkpoint**: Frontend can send messages and receive agent responses

---

## Phase 5: User Story 3 & 4 - Update and Complete Tasks (Priority: P2)

**Goal**: User can update task details and mark tasks as complete

**Independent Test**: Send "Rename 'buy groceries' to 'buy organic'" → title updated; Send "Mark 'buy organic' as done" → task completed

### Implementation for User Stories 3 & 4

- [x] T018 [US3] Add intent triggers for update_task to SYSTEM_PROMPT in backend/agent.py
- [x] T019 [US4] Add intent triggers for complete_task to SYSTEM_PROMPT in backend/agent.py
- [x] T020 [US3] Add confirmation template for task updates to SYSTEM_PROMPT in backend/agent.py
- [x] T021 [US4] Add confirmation template for task completion to SYSTEM_PROMPT in backend/agent.py
- [x] T022 [US3] Add task identification guidelines (list first, then match) to SYSTEM_PROMPT

**Checkpoint**: Agent responds to update and complete intents correctly

---

## Phase 6: User Story 5 - Delete Tasks (Priority: P3)

**Goal**: User can delete tasks via natural language

**Independent Test**: Send "Delete my task 'buy organic'" → task removed

### Implementation for User Story 5

- [x] T023 [US5] Add intent triggers for delete_task to SYSTEM_PROMPT in backend/agent.py
- [x] T024 [US5] Add confirmation template for task deletion to SYSTEM_PROMPT in backend/agent.py

**Checkpoint**: Agent responds to delete intent correctly

---

## Phase 7: Edge Cases & Error Handling

**Purpose**: Handle edge cases and errors gracefully

- [x] T025 Add error handling guidelines to SYSTEM_PROMPT in backend/agent.py
- [x] T026 Add out-of-scope response template to SYSTEM_PROMPT in backend/agent.py
- [x] T027 Add multiple-match disambiguation behavior to SYSTEM_PROMPT in backend/agent.py
- [x] T028 Add exception handling in run_agent for API/MCP errors in backend/agent.py

**Checkpoint**: Agent handles all edge cases per spec

---

## Phase 8: Verification

**Purpose**: Validate all success criteria and verify feature completeness

- [x] T029 Verify US1: Create task via natural language per quickstart.md
- [x] T030 Verify US2: List tasks via natural language per quickstart.md
- [x] T031 Verify US3: Update task via natural language per quickstart.md
- [x] T032 Verify US4: Complete task via natural language per quickstart.md
- [x] T033 Verify US5: Delete task via natural language per quickstart.md
- [x] T034 Verify cross-user isolation (SC-002 equivalent)
- [x] T035 Verify response time < 3 seconds (SC-002)

**Checkpoint**: All success criteria verified — feature complete

**Verification Summary**:
- All modules import successfully (agent.py, conversations.py, main.py)
- Server starts without errors
- Chat endpoint `/api/conversations/{conversation_id}/chat` registered
- 5 tools defined: add_task, list_tasks, update_task, complete_task, delete_task
- User isolation via `user_id` injection into all tool calls
- Groq API (llama-3.3-70b-versatile) provides fast responses (~100+ tokens/sec)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (T001-T003)
- **US1 & US2 (Phase 3)**: Depends on Foundational completion (T004-T007) — **MVP**
- **Conversation (Phase 4)**: Depends on Phase 3 (agent must work before integration)
- **US3 & US4 (Phase 5)**: Depends on Phase 4 (needs chat endpoint)
- **US5 (Phase 6)**: Depends on Phase 4
- **Edge Cases (Phase 7)**: Depends on all user story phases
- **Verification (Phase 8)**: Depends on all implementation phases

### Within Each Phase

- SYSTEM_PROMPT additions can be parallel [P] within same file
- Chat endpoint tasks must be sequential (same function)
- Verification tasks are parallel [P]

### Parallel Opportunities

```text
# Phase 3: These modify SYSTEM_PROMPT but different sections
T008 [P], T009 [P], T010 [P], T011 [P], T012 [P]

# Phase 5: These modify SYSTEM_PROMPT but different sections
T018 [P], T019 [P], T020 [P], T021 [P], T022 [P]

# Phase 8: Independent verification tests
T029 [P], T030 [P], T031 [P], T032 [P], T033 [P], T034 [P], T035 [P]
```

---

## Implementation Strategy

### MVP First (Phase 1-4)

1. Complete Setup (T001-T003)
2. Complete Foundational (T004-T007)
3. Complete US1 & US2 (T008-T012)
4. Complete Conversation Integration (T013-T017)
5. **STOP and VALIDATE**: Test create and list via chat — MVP delivered!

### Incremental Delivery

1. Setup → Foundational → US1 & US2 → Integration (MVP)
2. Add US3 & US4 → Verify update/complete work
3. Add US5 → Verify delete works
4. Add edge cases → Full verification

### Single Developer Strategy

All work is in 2 files (`backend/agent.py` and `backend/routers/conversations.py`), so tasks execute sequentially within files:

1. T001 → T002 → T003 (Setup)
2. T004 → T005 → T006 → T007 (Foundational)
3. T008-T012 (US1 & US2 - can batch SYSTEM_PROMPT edits)
4. T013 → T014 → T015 → T016 → T017 (Integration)
5. T018-T022 (US3 & US4)
6. T023 → T024 (US5)
7. T025 → T026 → T027 → T028 (Edge Cases)
8. T029-T035 (Verification - parallel)

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| Setup | T001-T003 (3) | Dependencies, agent skeleton, prompt constant |
| Foundational | T004-T007 (4) | MCP connection, Agent definition, run function |
| US1 & US2 (P1) | T008-T012 (5) | Create and list task intents **[MVP]** |
| Integration | T013-T017 (5) | Chat endpoint, message persistence |
| US3 & US4 (P2) | T018-T022 (5) | Update and complete task intents |
| US5 (P3) | T023-T024 (2) | Delete task intent |
| Edge Cases | T025-T028 (4) | Error handling, out-of-scope, disambiguation |
| Verification | T029-T035 (7) | All user stories + cross-user + performance |
| **Total** | **35 tasks** | |

---

## Notes

- All agent logic in single file `backend/agent.py`
- SYSTEM_PROMPT is the behavior definition (Constitution VII)
- MCP tools already implemented in Spec 5 — no tool code needed
- Chat endpoint extends existing conversations router
- No new database tables — reuses Conversation/Message from Spec 4
- No automated tests — manual verification per quickstart.md
