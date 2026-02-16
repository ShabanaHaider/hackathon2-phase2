# Tasks: Intermediate and Advanced Todo Features

**Input**: Design documents from `/specs/009-advanced-task-features/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, research.md, quickstart.md

**Tests**: Tests NOT explicitly requested in spec - included only where critical for event-driven features.

**Organization**: Tasks grouped by user story (8 stories: US1-US8) to enable independent implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1-US8 mapping to spec.md user stories
- All paths relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Database schema migration and Dapr infrastructure setup

- [X] T001 Create database migration file in backend/migrations/009_advanced_task_features.sql with schema from data-model.md
- [X] T002 Run database migration against Neon PostgreSQL to add priority, due_at, is_recurring, recurrence_pattern columns to tasks table
- [X] T003 Create tags and task_tags tables per migration script
- [X] T004 [P] Create Priority and RecurrencePattern enums in backend/models.py
- [X] T005 [P] Create Dapr components directory at dapr/components/
- [X] T006 Create Dapr Pub/Sub component config in dapr/components/pubsub-kafka.yaml

**Checkpoint**: Database schema extended, Dapr infrastructure ready

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models and services required by ALL user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Extend Task model in backend/models.py with priority, due_at, is_recurring, recurrence_pattern fields
- [X] T008 Create TaskTagLink model in backend/models.py for many-to-many relationship
- [X] T009 Create Tag model in backend/models.py with user_id scoping and unique constraint
- [X] T010 Extend TaskCreate schema in backend/models.py with priority, due_at, is_recurring, recurrence_pattern, tag_names fields
- [X] T011 Extend TaskUpdate schema in backend/models.py with new optional fields
- [X] T012 Extend TaskResponse schema in backend/models.py with new fields and tags list
- [X] T013 Create TagResponse schema in backend/models.py
- [X] T014 [P] Create event publisher service in backend/services/event_publisher.py using Dapr HTTP client
- [X] T015 [P] Create extended task types in frontend/src/types/task.ts with Priority, Tag, and extended Task interface
- [X] T016 Update frontend/src/lib/api.ts Task interface with priority, due_at, is_recurring, recurrence_pattern, tags fields

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Set Task Priority (Priority: P1) 🎯 MVP

**Goal**: Users can assign low/medium/high priority to tasks with "medium" as default

**Independent Test**: Create task without priority → verify medium default; create with "high" → verify saved correctly

### Implementation for User Story 1

- [X] T017 [US1] Update create_task endpoint in backend/routers/todos.py to accept and persist priority field
- [X] T018 [US1] Update update_task endpoint in backend/routers/todos.py to allow priority modification
- [X] T019 [US1] Add priority validation in backend/routers/todos.py to reject invalid values with 422 error
- [X] T020 [P] [US1] Create PriorityBadge component in frontend/src/components/PriorityBadge.tsx for visual display
- [X] T021 [US1] Extend TaskForm in frontend/src/components/TaskForm.tsx with priority dropdown (low/medium/high)
- [X] T022 [US1] Extend TaskItem in frontend/src/components/TaskItem.tsx to display PriorityBadge
- [X] T023 [US1] Update api.createTask in frontend/src/lib/api.ts to include priority in request body
- [X] T024 [US1] Update api.updateTask in frontend/src/lib/api.ts to include priority in request body

**Checkpoint**: Priority feature complete - tasks can be created/updated with priorities

---

## Phase 4: User Story 2 - Tag Tasks with Categories (Priority: P1)

**Goal**: Users can assign multiple tags to tasks; tags are user-scoped and reusable

**Independent Test**: Create task with tags → verify tags persisted; add existing tag → verify reused

### Implementation for User Story 2

- [X] T025 [US2] Create tags router in backend/routers/tags.py with list, create, delete endpoints
- [X] T026 [US2] Register tags router in backend/main.py with /api/tags prefix
- [X] T027 [US2] Implement get-or-create tag logic in backend/routers/todos.py for handling tag_names on task create
- [X] T028 [US2] Implement tag association update in backend/routers/todos.py for handling tag_names on task update
- [X] T029 [US2] Add Task.tags relationship loading with selectin strategy in backend/routers/todos.py list and get endpoints
- [X] T030 [P] [US2] Create TagSelector component in frontend/src/components/TagSelector.tsx with autocomplete and create-new
- [X] T031 [US2] Extend TaskForm in frontend/src/components/TaskForm.tsx to include TagSelector
- [X] T032 [US2] Extend TaskItem in frontend/src/components/TaskItem.tsx to display tag chips
- [X] T033 [US2] Add api.listTags, api.createTag, api.deleteTag methods in frontend/src/lib/api.ts

**Checkpoint**: Tags feature complete - tasks can have multiple tags

---

## Phase 5: User Story 3 - Filter Tasks (Priority: P2)

**Goal**: Users can filter task list by status, priority, or tag with AND logic

**Independent Test**: Create tasks with varied attributes → apply filter → verify correct subset returned

### Implementation for User Story 3

- [X] T034 [US3] Add status, priority, tag query parameters to list_tasks endpoint in backend/routers/todos.py
- [X] T035 [US3] Implement status filter logic (pending/completed/all) in backend/routers/todos.py
- [X] T036 [US3] Implement priority filter logic in backend/routers/todos.py
- [X] T037 [US3] Implement tag filter logic with JOIN in backend/routers/todos.py
- [X] T038 [US3] Implement combined filter logic with AND in backend/routers/todos.py
- [X] T039 [P] [US3] Create FilterBar component in frontend/src/components/FilterBar.tsx with dropdowns for status/priority/tag
- [X] T040 [US3] Integrate FilterBar into task list page in frontend/src/app/(protected)/layout.tsx or appropriate location
- [X] T041 [US3] Update api.listTasks in frontend/src/lib/api.ts to accept filter parameters
- [X] T042 [US3] Update TaskList in frontend/src/components/TaskList.tsx to pass filter state to API

**Checkpoint**: Filtering complete - users can filter by status, priority, tag

---

## Phase 6: User Story 4 - Sort Tasks (Priority: P2)

**Goal**: Users can sort task list by created_at, due_date, priority, or title

**Independent Test**: Create tasks with varied attributes → apply sort → verify correct order

### Implementation for User Story 4

- [X] T043 [US4] Add sort_by, sort_order query parameters to list_tasks endpoint in backend/routers/todos.py
- [X] T044 [US4] Implement sort by created_at logic in backend/routers/todos.py
- [X] T045 [US4] Implement sort by due_at logic with nullslast in backend/routers/todos.py
- [X] T046 [US4] Implement sort by priority logic (map to numeric for ordering) in backend/routers/todos.py
- [X] T047 [US4] Implement sort by title logic in backend/routers/todos.py
- [X] T048 [US4] Add sort controls to FilterBar in frontend/src/components/FilterBar.tsx
- [X] T049 [US4] Update api.listTasks in frontend/src/lib/api.ts to accept sort_by and sort_order parameters
- [X] T050 [US4] Update TaskList in frontend/src/components/TaskList.tsx to pass sort state to API and remove client-side sort

**Checkpoint**: Sorting complete - users can sort by multiple fields

---

## Phase 7: User Story 5 - Search Tasks (Priority: P2)

**Goal**: Users can search tasks by title, description, or tags (case-insensitive)

**Independent Test**: Create tasks with known keywords → search → verify matching tasks returned

### Implementation for User Story 5

- [X] T051 [US5] Add q (search query) parameter to list_tasks endpoint in backend/routers/todos.py
- [X] T052 [US5] Implement ILIKE search on title field in backend/routers/todos.py
- [X] T053 [US5] Implement ILIKE search on description field in backend/routers/todos.py
- [X] T054 [US5] Implement ILIKE search on tag names with outerjoin in backend/routers/todos.py
- [X] T055 [US5] Combine search with OR logic and add .distinct() in backend/routers/todos.py
- [X] T056 [P] [US5] Search integrated into FilterBar component (debounced input) instead of separate SearchBar
- [X] T057 [US5] Search integrated into FilterBar which is part of TaskList
- [X] T058 [US5] Update api.listTasks in frontend/src/lib/api.ts to accept q parameter
- [X] T059 [US5] Update TaskList in frontend/src/components/TaskList.tsx to pass search query to API

**Checkpoint**: Search complete - users can find tasks by keyword

---

## Phase 8: User Story 6 - Set Due Dates (Priority: P3)

**Goal**: Users can set optional due dates on tasks; overdue tasks visually indicated

**Independent Test**: Create task with due_at → verify UTC storage; view overdue task → verify visual indicator

### Implementation for User Story 6

- [X] T060 [US6] Ensure due_at field handling in create_task endpoint (already in schema from T010)
- [X] T061 [US6] Ensure due_at field handling in update_task endpoint including removal (set to null)
- [X] T062 [P] [US6] Add date picker to TaskForm in frontend/src/components/TaskForm.tsx for due_at selection
- [X] T063 [US6] Add due date display to TaskItem in frontend/src/components/TaskItem.tsx with formatted date
- [X] T064 [US6] Add overdue visual indicator in TaskItem when due_at < now and not completed
- [X] T065 [US6] Handle timezone conversion in frontend (display local, send UTC)

**Checkpoint**: Due dates complete - users can set and view deadlines

---

## Phase 9: User Story 7 - Receive Task Reminders (Priority: P3)

**Goal**: System publishes reminder events for tasks with upcoming due dates

**Independent Test**: Create task with due_at → verify reminder event published at due time

### Implementation for User Story 7

- [X] T066 [US7] Create reminder event schema in backend/models.py (ReminderEvent)
- [X] T067 [US7] Create notification service scaffold in services/notification-service/main.py with FastAPI
- [X] T068 [US7] Create Dapr subscription config in services/notification-service/dapr/subscription.yaml for reminders topic
- [X] T069 [US7] Implement reminder event handler endpoint in notification service
- [X] T070 [US7] Create Dockerfile for notification service in services/notification-service/Dockerfile
- [X] T071 [US7] Add reminder scheduling logic - publish reminder event when due_at approaches (stub implementation)
- [X] T072 [P] [US7] Create Helm chart scaffold in helm/notification-service/

**Checkpoint**: Reminder infrastructure complete - events published and consumed

---

## Phase 10: User Story 8 - Create Recurring Tasks (Priority: P4)

**Goal**: Recurring tasks auto-regenerate on completion with next due date

**Independent Test**: Create recurring daily task → complete → verify new task created with +1 day due_at

### Implementation for User Story 8

- [X] T073 [US8] Ensure is_recurring and recurrence_pattern fields handled in create/update endpoints (already in schema)
- [X] T074 [US8] Add validation: recurrence_pattern only allowed when is_recurring=true
- [X] T075 [US8] Create task event schema in backend/models.py (TaskEvent, TaskEventPayload)
- [X] T076 [US8] Publish task.completed event via Dapr in update_task when is_completed changes to true
- [X] T077 [US8] Create recurring task service scaffold in services/recurring-task-service/main.py with FastAPI
- [X] T078 [US8] Create Dapr subscription config in services/recurring-task-service/dapr/subscription.yaml for task-events topic
- [X] T079 [US8] Implement task.completed event handler in recurring service to check is_recurring flag
- [X] T080 [US8] Implement next occurrence creation logic in recurring service (calculate next due_at, copy attributes)
- [X] T081 [US8] Add idempotent event handling with event_id tracking in recurring service
- [X] T082 [US8] Create Dockerfile for recurring service in services/recurring-task-service/Dockerfile
- [X] T083 [P] [US8] Create Helm chart scaffold in helm/recurring-service/
- [X] T084 [US8] Add recurring indicator to TaskItem in frontend/src/components/TaskItem.tsx
- [X] T085 [US8] Add recurrence pattern selector to TaskForm in frontend/src/components/TaskForm.tsx

**Checkpoint**: Recurring tasks complete - tasks regenerate automatically

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Integration, validation, and deployment readiness

- [X] T086 Publish task.created event in create_task endpoint via event_publisher service
- [X] T087 Publish task.updated event in update_task endpoint via event_publisher service
- [X] T088 Publish task.deleted event in delete_task endpoint via event_publisher service
- [X] T089 Update MCP server tools in backend/mcp_server.py to include new task fields and publish events
- [X] T090 [P] Create Helm chart for backend in helm/backend/ with Dapr annotations
- [X] T091 [P] Create Helm chart for Kafka in helm/kafka/ (or reference existing)
- [X] T092 Update backend/.env.example with DAPR_HTTP_PORT, PUBSUB_NAME variables
- [X] T093 Validate quickstart.md scenarios manually
- [X] T094 Run backward compatibility check - verify existing /api/todos endpoints work without new fields

**Checkpoint**: Feature complete and deployment-ready

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1 (Setup) → Phase 2 (Foundational) → [User Stories can proceed in priority order or parallel]

Phase 2 BLOCKS all user stories

User Stories:
  US1 (Priority) ─┐
  US2 (Tags)     ─┼→ US3 (Filter) requires US1+US2 for meaningful filters
                  │
                  └→ US4 (Sort) can start after Phase 2
                  └→ US5 (Search) requires US2 for tag search

  US6 (Due Dates) → US7 (Reminders) requires US6
                  → US8 (Recurring) requires US6 + event infrastructure

Phase 11 (Polish) → After all stories complete
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US1 (Priority) | Phase 2 | US2 |
| US2 (Tags) | Phase 2 | US1 |
| US3 (Filter) | US1, US2 | US4 after US1+US2 |
| US4 (Sort) | Phase 2 | US3, US5 |
| US5 (Search) | US2 | US3, US4 |
| US6 (Due Dates) | Phase 2 | US1-US5 |
| US7 (Reminders) | US6 | US8 |
| US8 (Recurring) | US6, US7 (partial) | - |

### Parallel Opportunities

**Phase 1**:
- T004 (Enums) ‖ T005 (Dapr dir) ‖ T006 (Dapr config)

**Phase 2**:
- T014 (Event publisher) ‖ T015 (Frontend types) ‖ T016 (API types)

**Within User Stories**:
- US1: T020 (PriorityBadge) can run parallel with backend tasks
- US2: T030 (TagSelector) can run parallel with backend tasks
- US3: T039 (FilterBar) can run parallel with backend tasks
- US5: T056 (SearchBar) can run parallel with backend tasks

---

## Parallel Example: Phase 2 Foundation

```bash
# Launch in parallel:
Task T014: "Create event publisher service in backend/services/event_publisher.py"
Task T015: "Create extended task types in frontend/src/types/task.ts"
Task T016: "Update frontend/src/lib/api.ts Task interface"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T016)
3. Complete Phase 3: User Story 1 - Priority (T017-T024)
4. Complete Phase 4: User Story 2 - Tags (T025-T033)
5. **STOP and VALIDATE**: Test priority and tags independently
6. Deploy/demo MVP with priority + tags

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 + US2 → Test → Deploy (MVP: Priority + Tags)
3. US3 + US4 + US5 → Test → Deploy (Filter/Sort/Search)
4. US6 → Test → Deploy (Due Dates)
5. US7 + US8 → Test → Deploy (Reminders + Recurring)
6. Polish → Final deployment

### Estimated Task Counts

| Phase | Tasks | Parallel Opportunities |
|-------|-------|------------------------|
| Setup | 6 | 3 |
| Foundational | 10 | 3 |
| US1 Priority | 8 | 1 |
| US2 Tags | 9 | 1 |
| US3 Filter | 9 | 1 |
| US4 Sort | 8 | 0 |
| US5 Search | 9 | 1 |
| US6 Due Dates | 6 | 1 |
| US7 Reminders | 7 | 1 |
| US8 Recurring | 13 | 1 |
| Polish | 9 | 2 |
| **Total** | **94** | **15** |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [USn] label maps task to specific user story from spec.md
- Backend tasks use absolute paths from repo root (backend/...)
- Frontend tasks use absolute paths from repo root (frontend/src/...)
- Event-driven tasks require Dapr sidecar running
- All database changes are additive (backward compatible)
- Existing endpoints remain unchanged until explicitly extended
