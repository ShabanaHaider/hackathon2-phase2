# Tasks: Todo Web Frontend Application

**Input**: Design documents from `/specs/003-todo-web-frontend/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (complete), contracts/api-client.md (complete)

**Tests**: Manual E2E testing per quickstart.md (no automated tests required)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/src/` (Next.js App Router)
- **Components**: `frontend/src/components/`
- **Library**: `frontend/src/lib/`
- **App Routes**: `frontend/src/app/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify existing frontend project and add required dependencies

- [x] T001 Verify Next.js project structure exists in frontend/
- [x] T002 Verify Better Auth dependencies installed in frontend/package.json
- [x] T003 [P] Verify Tailwind CSS configured in frontend/tailwind.config.ts
- [x] T004 [P] Verify environment variables template in frontend/.env.example

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**WARNING**: No user story work can begin until this phase is complete

### Better Auth Configuration

- [x] T005 Fix Better Auth server config in frontend/src/lib/auth.ts
- [x] T006 Fix Better Auth client instance in frontend/src/lib/auth-client.ts
- [x] T007 Fix Better Auth route handler in frontend/src/app/api/auth/[...all]/route.ts
- [x] T008 Verify Better Auth JWKS endpoint returns valid response at /api/auth/jwks

### API Client

- [x] T009 Create API client with JWT injection in frontend/src/lib/api.ts
- [x] T010 Add TypeScript interfaces (Task, TaskCreateRequest, TaskUpdateRequest) in frontend/src/lib/api.ts

### Layout and Navigation

- [x] T011 Update root layout with global styles in frontend/src/app/layout.tsx
- [x] T012 Create auth pages layout in frontend/src/app/(auth)/layout.tsx
- [x] T013 Create protected pages layout with auth guard in frontend/src/app/(protected)/layout.tsx
- [x] T014 Create auth middleware for route protection in frontend/src/middleware.ts

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Sign Up for New Account (Priority: P1)

**Goal**: New visitors can create accounts with email and password

**Independent Test**: Navigate to /signup, enter valid email and password (8+ chars), verify redirect to dashboard signed in

### Implementation for User Story 1

- [x] T015 [US1] Create sign-up page with form in frontend/src/app/(auth)/signup/page.tsx
- [x] T016 [US1] Add email input with validation in frontend/src/app/(auth)/signup/page.tsx
- [x] T017 [US1] Add password input with min 8 char validation in frontend/src/app/(auth)/signup/page.tsx
- [x] T018 [US1] Add form submission with Better Auth signUp.email in frontend/src/app/(auth)/signup/page.tsx
- [x] T019 [US1] Add error display for duplicate email in frontend/src/app/(auth)/signup/page.tsx
- [x] T020 [US1] Add loading state during form submission in frontend/src/app/(auth)/signup/page.tsx
- [x] T021 [US1] Add navigation link to sign-in page in frontend/src/app/(auth)/signup/page.tsx

**Checkpoint**: Sign-up flow fully functional and testable independently

---

## Phase 4: User Story 2 - Sign In to Existing Account (Priority: P1)

**Goal**: Returning users can sign in with existing credentials

**Independent Test**: Navigate to /signin, enter valid credentials, verify access to dashboard

### Implementation for User Story 2

- [x] T022 [US2] Create sign-in page with form in frontend/src/app/(auth)/signin/page.tsx
- [x] T023 [US2] Add email and password inputs in frontend/src/app/(auth)/signin/page.tsx
- [x] T024 [US2] Add form submission with Better Auth signIn.email in frontend/src/app/(auth)/signin/page.tsx
- [x] T025 [US2] Add error display for invalid credentials in frontend/src/app/(auth)/signin/page.tsx
- [x] T026 [US2] Add callbackUrl handling for redirect after sign-in in frontend/src/app/(auth)/signin/page.tsx
- [x] T027 [US2] Add loading state during form submission in frontend/src/app/(auth)/signin/page.tsx
- [x] T028 [US2] Add navigation link to sign-up page in frontend/src/app/(auth)/signin/page.tsx

**Checkpoint**: Sign-in flow fully functional and testable independently

---

## Phase 5: User Story 3 - View Task List (Priority: P1)

**Goal**: Authenticated users see all their tasks in a clear list

**Independent Test**: Sign in, verify task list displays, verify empty state if no tasks

### Implementation for User Story 3

- [x] T029 [P] [US3] Create EmptyState component in frontend/src/components/EmptyState.tsx
- [x] T030 [P] [US3] Create TaskItem component in frontend/src/components/TaskItem.tsx
- [x] T031 [US3] Create TaskList component with data fetching in frontend/src/components/TaskList.tsx
- [x] T032 [US3] Add loading state to TaskList in frontend/src/components/TaskList.tsx
- [x] T033 [US3] Add error state with retry to TaskList in frontend/src/components/TaskList.tsx
- [x] T034 [US3] Create dashboard page with TaskList in frontend/src/app/(protected)/page.tsx
- [x] T035 [US3] Add responsive styling for mobile (320px) to TaskList in frontend/src/components/TaskList.tsx

**Checkpoint**: Task list display fully functional and testable independently

---

## Phase 6: User Story 4 - Create a New Task (Priority: P1)

**Goal**: Authenticated users can create new tasks

**Independent Test**: Sign in, create task with title, verify it appears in list

### Implementation for User Story 4

- [x] T036 [US4] Create TaskForm component in frontend/src/components/TaskForm.tsx
- [x] T037 [US4] Add title input with required validation in frontend/src/components/TaskForm.tsx
- [x] T038 [US4] Add optional description textarea in frontend/src/components/TaskForm.tsx
- [x] T039 [US4] Add form submission calling POST /api/todos in frontend/src/components/TaskForm.tsx
- [x] T040 [US4] Add loading state during submission in frontend/src/components/TaskForm.tsx
- [x] T041 [US4] Add error display for validation errors in frontend/src/components/TaskForm.tsx
- [x] T042 [US4] Integrate TaskForm into dashboard and refresh list after create in frontend/src/app/(protected)/page.tsx

**Checkpoint**: Task creation fully functional and testable independently (MVP Complete!)

---

## Phase 7: User Story 5 - Mark Task as Complete (Priority: P2)

**Goal**: Users can toggle task completion status

**Independent Test**: Create task, mark complete, verify visual indicator, toggle back

### Implementation for User Story 5

- [x] T043 [US5] Add completion checkbox to TaskItem in frontend/src/components/TaskItem.tsx
- [x] T044 [US5] Add onClick handler calling PATCH /api/todos/{id} in frontend/src/components/TaskItem.tsx
- [x] T045 [US5] Add visual indicator (strikethrough/checkmark) for completed tasks in frontend/src/components/TaskItem.tsx
- [x] T046 [US5] Add loading state during toggle in frontend/src/components/TaskItem.tsx
- [x] T047 [US5] Refresh task list after completion toggle in frontend/src/components/TaskList.tsx

**Checkpoint**: Task completion toggle fully functional and testable independently

---

## Phase 8: User Story 6 - Edit Task Details (Priority: P2)

**Goal**: Users can edit task title and description

**Independent Test**: Create task, edit title and description, verify changes persist

### Implementation for User Story 6

- [x] T048 [US6] Add edit mode state to TaskItem in frontend/src/components/TaskItem.tsx
- [x] T049 [US6] Add inline edit form with title/description inputs in frontend/src/components/TaskItem.tsx
- [x] T050 [US6] Add save button calling PATCH /api/todos/{id} in frontend/src/components/TaskItem.tsx
- [x] T051 [US6] Add cancel button to exit edit mode in frontend/src/components/TaskItem.tsx
- [x] T052 [US6] Add validation preventing empty title on save in frontend/src/components/TaskItem.tsx
- [x] T053 [US6] Add loading state during save in frontend/src/components/TaskItem.tsx
- [x] T054 [US6] Refresh task list after edit in frontend/src/components/TaskList.tsx

**Checkpoint**: Task editing fully functional and testable independently

---

## Phase 9: User Story 7 - Delete a Task (Priority: P2)

**Goal**: Users can permanently remove tasks with confirmation

**Independent Test**: Create task, delete it, verify removal from list

### Implementation for User Story 7

- [x] T055 [US7] Add delete button to TaskItem in frontend/src/components/TaskItem.tsx
- [x] T056 [US7] Add window.confirm() confirmation dialog in frontend/src/components/TaskItem.tsx
- [x] T057 [US7] Add DELETE /api/todos/{id} call on confirm in frontend/src/components/TaskItem.tsx
- [x] T058 [US7] Add loading state during delete in frontend/src/components/TaskItem.tsx
- [x] T059 [US7] Remove task from list after successful delete in frontend/src/components/TaskList.tsx

**Checkpoint**: Task deletion fully functional and testable independently

---

## Phase 10: User Story 8 - Sign Out (Priority: P3)

**Goal**: Users can end their session securely

**Independent Test**: Sign in, click sign out, verify redirect to sign-in, verify protected pages inaccessible

### Implementation for User Story 8

- [x] T060 [US8] Add sign-out button to protected layout header in frontend/src/app/(protected)/layout.tsx
- [x] T061 [US8] Add onClick handler calling Better Auth signOut in frontend/src/app/(protected)/layout.tsx
- [x] T062 [US8] Add redirect to /signin after sign-out in frontend/src/app/(protected)/layout.tsx

**Checkpoint**: Sign-out fully functional and testable independently

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and verification

- [x] T063 [P] Add responsive styling for tablet (768px) breakpoint in all components
- [x] T064 [P] Add responsive styling for desktop (1024px+) breakpoint in all components
- [x] T065 Verify all loading states show spinner/indicator
- [x] T066 Verify all error states show user-friendly messages
- [x] T067 Verify 401 errors redirect to /signin
- [x] T068 Run quickstart.md verification checklist
- [x] T069 Test user isolation (User A cannot see User B's tasks)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - verify existing project
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **US1-US4 (Phases 3-6)**: All P1 priorities, can proceed sequentially
- **US5-US7 (Phases 7-9)**: All P2 priorities, require US3 (View Task List) complete
- **US8 (Phase 10)**: P3 priority, requires foundational complete
- **Polish (Phase 11)**: Depends on all user stories complete

### User Story Dependencies

| Story | Priority | Depends On | Notes |
|-------|----------|------------|-------|
| US1 (Sign Up) | P1 | Foundational | Gateway to all features |
| US2 (Sign In) | P1 | Foundational | Independent of US1 |
| US3 (View Tasks) | P1 | Foundational | Core display |
| US4 (Create Task) | P1 | US3 | Needs task list to verify |
| US5 (Mark Complete) | P2 | US3 | Modifies task in list |
| US6 (Edit Task) | P2 | US3 | Modifies task in list |
| US7 (Delete Task) | P2 | US3 | Removes task from list |
| US8 (Sign Out) | P3 | Foundational | Independent of tasks |

### Parallel Opportunities

Within Foundational Phase:
- T003 and T004 can run in parallel (verify configs)

Within User Story 3 (View Task List):
- T029 (EmptyState) and T030 (TaskItem) can run in parallel

Within Polish Phase:
- T063 and T064 can run in parallel (responsive styling)

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Sequential (dependencies)
T005 → T006 → T007 → T008 (Better Auth chain)
T009 → T010 (API client)

# Parallel opportunities
T011, T012, T013, T014 can run in parallel (different files)
```

## Parallel Example: User Story 3

```bash
# Launch components in parallel:
Task: "Create EmptyState component in frontend/src/components/EmptyState.tsx"
Task: "Create TaskItem component in frontend/src/components/TaskItem.tsx"

# Then sequentially:
Task: "Create TaskList component with data fetching..." (uses above)
```

---

## Implementation Strategy

### MVP First (User Stories 1-4)

1. Complete Phase 1: Setup (verify existing)
2. Complete Phase 2: Foundational (CRITICAL - Better Auth fixes)
3. Complete Phase 3: US1 - Sign Up
4. Complete Phase 4: US2 - Sign In
5. Complete Phase 5: US3 - View Task List
6. Complete Phase 6: US4 - Create Task
7. **STOP and VALIDATE**: Test all P1 stories via quickstart.md
8. Deploy/demo MVP

### Incremental Delivery

1. MVP (US1-US4) → Test → Deploy
2. Add US5 (Mark Complete) → Test → Deploy
3. Add US6 (Edit Task) → Test → Deploy
4. Add US7 (Delete Task) → Test → Deploy
5. Add US8 (Sign Out) → Test → Deploy
6. Polish Phase → Final verification → Deploy

---

## Summary

| Phase | Tasks | Parallel Tasks |
|-------|-------|----------------|
| Setup | 4 | 2 |
| Foundational | 10 | 4 |
| US1 - Sign Up | 7 | 0 |
| US2 - Sign In | 7 | 0 |
| US3 - View Tasks | 7 | 2 |
| US4 - Create Task | 7 | 0 |
| US5 - Mark Complete | 5 | 0 |
| US6 - Edit Task | 7 | 0 |
| US7 - Delete Task | 5 | 0 |
| US8 - Sign Out | 3 | 0 |
| Polish | 7 | 2 |
| **Total** | **69** | **10** |

---

## Notes

- [P] tasks = different files, no dependencies on other tasks in same phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Focus on MVP (US1-US4) first, then add P2/P3 features incrementally
