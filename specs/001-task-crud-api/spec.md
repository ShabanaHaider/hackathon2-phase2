# Feature Specification: Task CRUD API

**Feature Branch**: `001-task-crud-api`
**Created**: 2026-01-27
**Status**: Draft
**Input**: User description: "Persistent task storage with RESTful API correctness and user-scoped data handling"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create a New Task (Priority: P1)

A user creates a new task by providing a title and optional description. The
system persists the task in the database associated with the user's identity
and returns the created task with a unique identifier.

**Why this priority**: Task creation is the foundational operation. Without it,
no other CRUD operations have data to act on. This is the minimum viable
slice of the feature.

**Independent Test**: Can be fully tested by sending a POST request with a
title and user ID, then verifying the response contains the created task with
a generated ID, timestamps, and default status.

**Acceptance Scenarios**:

1. **Given** a user ID and a task title, **When** the user submits a create
   request, **Then** the system persists the task and returns it with a unique
   ID, the provided title, a default incomplete status, and creation timestamp.
2. **Given** a user ID, a title, and an optional description, **When** the user
   submits a create request, **Then** the system persists both title and
   description.
3. **Given** a missing or empty title, **When** the user submits a create
   request, **Then** the system rejects the request with a validation error.

---

### User Story 2 - List All Tasks for a User (Priority: P1)

A user retrieves all of their tasks. The system returns only tasks belonging to
that specific user, never tasks owned by another user.

**Why this priority**: Equally critical as creation — users must see their own
tasks to confirm the system works. Together with US1, this forms the core
read/write loop.

**Independent Test**: Can be tested by creating tasks for two different user
IDs, then listing tasks for one user and verifying only their tasks are
returned.

**Acceptance Scenarios**:

1. **Given** a user with existing tasks, **When** the user requests their task
   list, **Then** the system returns all tasks belonging to that user.
2. **Given** a user with no tasks, **When** the user requests their task list,
   **Then** the system returns an empty list.
3. **Given** tasks belonging to multiple users, **When** user A requests their
   task list, **Then** the response contains zero tasks belonging to user B.

---

### User Story 3 - View a Single Task (Priority: P2)

A user retrieves a single task by its unique identifier. The system returns
the task only if it belongs to that user.

**Why this priority**: Viewing details of a single task supports workflows
where the user needs to inspect or share a specific item. Depends on
creation existing but is independently testable.

**Independent Test**: Can be tested by creating a task, retrieving it by ID,
and verifying all fields match. Also test that fetching another user's task
by ID returns a not-found response.

**Acceptance Scenarios**:

1. **Given** a task owned by user A, **When** user A requests that task by ID,
   **Then** the system returns the full task details.
2. **Given** a task owned by user A, **When** user B requests that task by ID,
   **Then** the system returns a not-found response.
3. **Given** a non-existent task ID, **When** any user requests it, **Then**
   the system returns a not-found response.

---

### User Story 4 - Update an Existing Task (Priority: P2)

A user updates the title, description, or completion status of an existing
task they own. The system persists the changes and returns the updated task.

**Why this priority**: Updates are essential for task management (marking tasks
complete, editing text) but depend on create and read being functional first.

**Independent Test**: Can be tested by creating a task, sending an update
request with changed fields, then retrieving the task and verifying the
changes persisted.

**Acceptance Scenarios**:

1. **Given** a task owned by user A, **When** user A submits an update with a
   new title, **Then** the system persists the new title and returns the
   updated task.
2. **Given** a task owned by user A, **When** user A marks the task as
   complete, **Then** the system updates the completion status and records a
   completion timestamp.
3. **Given** a task owned by user A, **When** user B attempts to update it,
   **Then** the system returns a not-found response and makes no changes.
4. **Given** an update with an empty title, **When** the user submits it,
   **Then** the system rejects the request with a validation error.

---

### User Story 5 - Delete a Task (Priority: P3)

A user deletes a task they own. The system removes the task permanently and
confirms the deletion.

**Why this priority**: Delete completes the CRUD lifecycle but is the least
frequently used operation. The system is functional without it.

**Independent Test**: Can be tested by creating a task, deleting it, then
attempting to retrieve it and confirming it no longer exists.

**Acceptance Scenarios**:

1. **Given** a task owned by user A, **When** user A deletes it, **Then** the
   system removes the task and returns a success confirmation.
2. **Given** a task owned by user A, **When** user B attempts to delete it,
   **Then** the system returns a not-found response and the task remains.
3. **Given** a non-existent task ID, **When** any user attempts to delete it,
   **Then** the system returns a not-found response.

---

### Edge Cases

- What happens when a user submits a title exceeding 255 characters?
  The system MUST reject it with a validation error.
- What happens when a user submits a description exceeding 2000 characters?
  The system MUST reject it with a validation error.
- What happens when the database is unreachable?
  The system MUST return a server error response, not crash or hang.
- What happens when a user sends a malformed request body (e.g., wrong data
  types)? The system MUST return a validation error with details.
- What happens when a user attempts to set the task ID manually in a create
  request? The system MUST ignore client-supplied IDs and generate its own.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow a user to create a task with a title (required,
  1–255 characters) and description (optional, up to 2000 characters).
- **FR-002**: System MUST assign each task a unique identifier, creation
  timestamp, and default incomplete status upon creation.
- **FR-003**: System MUST persist every task with an associated user ID that
  identifies the owner.
- **FR-004**: System MUST return all tasks belonging to the requesting user
  when listing tasks, and never return tasks belonging to other users.
- **FR-005**: System MUST allow retrieval of a single task by its ID, only
  if the task belongs to the requesting user.
- **FR-006**: System MUST allow the owner to update a task's title,
  description, and completion status.
- **FR-007**: System MUST record a completion timestamp when a task is
  marked complete, and clear it if the task is marked incomplete again.
- **FR-008**: System MUST allow the owner to delete a task permanently.
- **FR-009**: System MUST return appropriate error responses for invalid
  input, non-existent resources, and unauthorized access attempts.
- **FR-010**: System MUST accept user identity as an input parameter on
  each request (no authentication enforcement in this feature scope).

### Assumptions

- User identity (user ID) is provided as a trusted input parameter. This
  spec does not cover how the user ID is verified — that is the
  responsibility of a separate authentication feature.
- Task IDs are system-generated UUIDs; clients cannot set them.
- Timestamps use ISO 8601 format in UTC.
- "Completed" status is a boolean toggle, not a workflow with multiple states.
- Deletion is permanent (hard delete), not soft delete.

### Key Entities

- **Task**: Represents a unit of work owned by a user. Key attributes: unique
  identifier, title, description, completion status, completion timestamp,
  creation timestamp, update timestamp, owner user ID.
- **User (reference only)**: An external entity identified by a user ID. Not
  managed by this feature — the user ID is accepted as input and used for
  data scoping.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create, read, update, and delete tasks through five
  distinct operations that each return correct results.
- **SC-002**: A user with 100 tasks can retrieve their full task list in a
  single request.
- **SC-003**: No user can access, modify, or delete another user's tasks
  under any combination of operations.
- **SC-004**: All invalid inputs (missing title, oversized fields, wrong
  types) produce clear error responses identifying the specific problem.
- **SC-005**: Task data persists across system restarts — tasks created before
  a restart are retrievable after.
- **SC-006**: All five CRUD operations use correct response codes and
  consistent response structure.
