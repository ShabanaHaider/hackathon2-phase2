# Feature Specification: MCP Server & Task Tools

**Feature Branch**: `005-mcp-server-task-tools`
**Created**: 2026-02-06
**Status**: Draft
**Input**: User description: "Expose task operations as MCP tools using the Official MCP SDK."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add and List Tasks via MCP Tools (Priority: P1)

An AI agent needs to create a new task for an authenticated user and then
retrieve the user's task list. The agent calls the `add_task` MCP tool with
a title, optional description, and the user's identity. It then calls
`list_tasks` to confirm the task was persisted and to display the user's
current task list.

**Why this priority**: Adding and listing tasks are the foundational
operations that every other tool depends on. Without these, no task
management is possible through MCP. This story alone delivers a viable MVP
that allows AI agents to create and view tasks.

**Independent Test**: Can be fully tested by invoking `add_task` with valid
parameters, then invoking `list_tasks` for the same user and verifying the
newly created task appears in the returned list.

**Acceptance Scenarios**:

1. **Given** an authenticated user with no tasks, **When** the agent calls
   `add_task` with a title "Buy groceries", **Then** the tool returns a
   success response containing the new task's unique identifier, title, and
   creation timestamp, and the task is persisted in the database.
2. **Given** an authenticated user with three existing tasks, **When** the
   agent calls `list_tasks`, **Then** the tool returns all three tasks with
   their identifiers, titles, completion status, and timestamps.
3. **Given** an unauthenticated or invalid user identity, **When** the
   agent calls `add_task` or `list_tasks`, **Then** the tool returns an
   error indicating the user is not authorized.

---

### User Story 2 - Update and Complete Tasks via MCP Tools (Priority: P2)

An AI agent needs to modify an existing task's details or mark it as
complete. The agent calls `update_task` to change the title or description,
and `complete_task` to toggle the completion status. These operations only
succeed if the task belongs to the authenticated user.

**Why this priority**: Updating and completing tasks are essential for a
functional task manager. They build on P1 (add/list) and enable the full
task lifecycle. Each tool can be tested independently once tasks exist.

**Independent Test**: Can be tested by creating a task via `add_task`, then
calling `update_task` to change its title and verifying the change persists,
then calling `complete_task` and verifying the completion status and
timestamp are set.

**Acceptance Scenarios**:

1. **Given** an existing task owned by the user, **When** the agent calls
   `update_task` with a new title, **Then** the tool returns the updated
   task with the new title and an updated timestamp.
2. **Given** an existing incomplete task owned by the user, **When** the
   agent calls `complete_task`, **Then** the tool returns the task with
   `is_completed` set to true and a `completed_at` timestamp.
3. **Given** an existing completed task owned by the user, **When** the
   agent calls `complete_task`, **Then** the tool returns the task with
   `is_completed` set to false and `completed_at` cleared (toggle behavior).
4. **Given** a task owned by a different user, **When** the agent calls
   `update_task` or `complete_task`, **Then** the tool returns an error
   indicating the task was not found.

---

### User Story 3 - Delete Tasks via MCP Tools (Priority: P3)

An AI agent needs to remove a task that the user no longer wants. The agent
calls `delete_task` with the task identifier and user identity. The task is
permanently removed from the database.

**Why this priority**: Deletion is the final lifecycle operation. It is less
frequently used than creation, listing, or completion, but is necessary for
complete task management. It can be tested independently once tasks exist.

**Independent Test**: Can be tested by creating a task via `add_task`,
calling `delete_task` with the task's identifier, then calling `list_tasks`
to confirm the task no longer appears.

**Acceptance Scenarios**:

1. **Given** an existing task owned by the user, **When** the agent calls
   `delete_task` with the task identifier, **Then** the tool returns a
   success confirmation and the task is permanently removed from the
   database.
2. **Given** a task identifier that does not exist, **When** the agent calls
   `delete_task`, **Then** the tool returns an error indicating the task was
   not found.
3. **Given** a task owned by a different user, **When** the agent calls
   `delete_task`, **Then** the tool returns an error indicating the task was
   not found (no data leakage about other users' tasks).

---

### Edge Cases

- What happens when `add_task` is called with an empty or whitespace-only
  title? The tool MUST return a validation error.
- What happens when `add_task` is called with a title exceeding 255
  characters? The tool MUST return a validation error indicating the limit.
- What happens when `update_task` is called with no fields to update
  (empty update)? The tool MUST return the task unchanged or a validation
  error indicating no updates were provided.
- What happens when `complete_task` is called on a non-existent task ID?
  The tool MUST return a not-found error.
- What happens when the MCP server receives a request with a malformed
  task identifier (not a valid UUID)? The tool MUST return a validation
  error.
- What happens when the database is temporarily unreachable? The tool MUST
  return a clear error message indicating a service failure, not crash or
  hang.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an MCP server implemented using the
  Official MCP SDK that exposes task management operations as tools.
- **FR-002**: System MUST provide an `add_task` tool that creates a new
  task with a title, optional description, and the authenticated user's
  identity, persisting it to the database.
- **FR-003**: System MUST provide a `list_tasks` tool that retrieves all
  tasks belonging to the authenticated user.
- **FR-004**: System MUST provide an `update_task` tool that modifies the
  title and/or description of an existing task owned by the authenticated
  user.
- **FR-005**: System MUST provide a `complete_task` tool that toggles the
  completion status of a task owned by the authenticated user.
- **FR-006**: System MUST provide a `delete_task` tool that permanently
  removes a task owned by the authenticated user.
- **FR-007**: All MCP tools MUST be stateless — they MUST NOT retain any
  in-memory state between invocations.
- **FR-008**: All MCP tools MUST accept all required data (including user
  identity) as explicit parameters and persist all state changes to the
  database.
- **FR-009**: All MCP tools MUST validate input parameters and return
  descriptive error messages for invalid inputs.
- **FR-010**: All MCP tools MUST enforce user data isolation — a user MUST
  NOT be able to access, modify, or delete tasks belonging to another user.
  Cross-user access attempts MUST return a not-found response.
- **FR-011**: MCP tools MUST NOT contain any AI reasoning or business logic
  — they are pure data operation wrappers.
- **FR-012**: The MCP server MUST NOT access frontend state or maintain
  session memory.

### Key Entities

- **MCP Server**: A server process that registers and exposes MCP tools.
  Runs alongside the backend. Communicates with the database for all
  state operations.
- **MCP Tool**: A named, stateless function registered with the MCP server.
  Each tool has a defined input schema (parameters), performs a single
  database operation, and returns a structured result.
- **Task**: Existing entity (from Spec 1). Attributes: unique identifier,
  title, optional description, completion status, timestamps, owning user
  identifier.

### Assumptions

- The existing Task model and database table from Spec 1 are reused
  without modification.
- User identity (user_id) is passed as an explicit parameter to each MCP
  tool, since MCP tools are stateless and do not have access to HTTP
  request context or JWT tokens.
- The MCP server runs as a separate process or integrated module within
  the backend, using the same database connection configuration.
- Tool input/output schemas follow the MCP SDK's standard JSON format.
- The `complete_task` tool toggles completion status (complete / incomplete)
  to match the existing REST API behavior.
- Title validation follows the same constraints as the REST API (1-255
  characters). Description limit is 2000 characters.
- The MCP server uses the `stdio` transport as the default transport
  mechanism, suitable for agent-to-server communication.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All five MCP tools (`add_task`, `list_tasks`, `update_task`,
  `complete_task`, `delete_task`) are operational and perform correct
  database mutations when invoked with valid parameters.
- **SC-002**: User data isolation is enforced — no tool allows access to
  or modification of another user's tasks, verified by cross-user access
  attempts returning not-found errors.
- **SC-003**: Tool input validation rejects 100% of invalid inputs (empty
  titles, malformed IDs, oversized content) with descriptive error
  messages.
- **SC-004**: Every tool invocation is stateless — the MCP server retains
  no in-memory state between calls, verified by server restart having no
  effect on tool behavior.
- **SC-005**: The existing REST API for tasks continues to function
  unchanged alongside the MCP server (compatibility guarantee).
