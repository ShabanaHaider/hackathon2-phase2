# Feature Specification: Intermediate and Advanced Todo Features

**Feature Branch**: `009-advanced-task-features`
**Created**: 2026-02-13
**Status**: Draft
**Input**: User description: "Extend the Todo system with production-ready task intelligence and scheduling including priorities, tags, search, filtering, sorting, due dates, reminders, and recurring tasks."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Set Task Priority (Priority: P1)

As a user, I want to assign a priority level (low, medium, high) to my tasks so that I can focus on what matters most and organize my work effectively.

**Why this priority**: Priority is a fundamental task attribute that enables all subsequent filtering and sorting features. Without priorities, users cannot effectively triage their workload.

**Independent Test**: Can be fully tested by creating tasks with different priorities and verifying they persist correctly. Delivers immediate organizational value.

**Acceptance Scenarios**:

1. **Given** I am creating a new task, **When** I do not specify a priority, **Then** the task is created with "medium" priority by default
2. **Given** I am creating a new task, **When** I specify a priority of "high", **Then** the task is saved with high priority
3. **Given** I have an existing task with medium priority, **When** I update it to high priority, **Then** the change persists and is reflected immediately
4. **Given** I attempt to set an invalid priority value, **When** I submit the task, **Then** the system rejects it with a clear error message

---

### User Story 2 - Tag Tasks with Categories (Priority: P1)

As a user, I want to tag my tasks with multiple categories so that I can group related tasks across different projects or contexts.

**Why this priority**: Tags provide flexible organization beyond priority, enabling cross-cutting categorization (e.g., "work", "urgent", "meeting-prep").

**Independent Test**: Can be tested by creating tasks with tags, verifying tag persistence, and confirming multiple tags can be assigned to a single task.

**Acceptance Scenarios**:

1. **Given** I am creating or editing a task, **When** I add one or more tags, **Then** all tags are saved and associated with the task
2. **Given** I have a task with tags, **When** I remove a tag, **Then** only that tag is removed; other tags remain
3. **Given** I add a tag that already exists in the system, **When** I save the task, **Then** the existing tag is reused (no duplicates created)
4. **Given** I add a new tag that doesn't exist, **When** I save the task, **Then** the new tag is created and associated with the task
5. **Given** a tag is no longer associated with any tasks, **When** I query tags, **Then** the orphan tag may still exist for future use

---

### User Story 3 - Filter Tasks (Priority: P2)

As a user, I want to filter my task list by status, priority, or tag so that I can quickly find relevant tasks without scrolling through everything.

**Why this priority**: Filtering depends on priorities and tags being implemented first. It transforms raw data into actionable views.

**Independent Test**: Can be tested by creating tasks with various attributes and verifying filter combinations return correct subsets.

**Acceptance Scenarios**:

1. **Given** I have tasks with different statuses, **When** I filter by status "pending", **Then** only pending tasks are displayed
2. **Given** I have tasks with different priorities, **When** I filter by priority "high", **Then** only high-priority tasks are displayed
3. **Given** I have tasks with various tags, **When** I filter by tag "work", **Then** only tasks tagged "work" are displayed
4. **Given** I apply multiple filters (e.g., status=pending AND priority=high), **When** I view results, **Then** only tasks matching ALL criteria are displayed
5. **Given** no tasks match my filter criteria, **When** I view results, **Then** an empty list is displayed with a helpful message

---

### User Story 4 - Sort Tasks (Priority: P2)

As a user, I want to sort my task list by different fields so that I can view tasks in the order that makes sense for my current workflow.

**Why this priority**: Sorting complements filtering to provide full control over task list presentation.

**Independent Test**: Can be tested by creating tasks with various creation dates, due dates, priorities, and titles, then verifying sort order accuracy.

**Acceptance Scenarios**:

1. **Given** I have multiple tasks, **When** I sort by created_at ascending, **Then** oldest tasks appear first
2. **Given** I have multiple tasks, **When** I sort by due_date ascending, **Then** tasks due soonest appear first (tasks without due dates appear last)
3. **Given** I have multiple tasks, **When** I sort by priority descending, **Then** high-priority tasks appear first, then medium, then low
4. **Given** I have multiple tasks, **When** I sort by title alphabetically, **Then** tasks are ordered A-Z
5. **Given** I apply both filter and sort, **When** I view results, **Then** filtered results are displayed in the sorted order

---

### User Story 5 - Search Tasks (Priority: P2)

As a user, I want to search my tasks by title, description, or tags so that I can quickly locate specific tasks by keyword.

**Why this priority**: Search provides rapid task discovery, especially valuable as task lists grow.

**Independent Test**: Can be tested by creating tasks with known keywords and verifying search returns matching tasks.

**Acceptance Scenarios**:

1. **Given** I have tasks with "meeting" in the title, **When** I search for "meeting", **Then** those tasks appear in results
2. **Given** I have tasks with "quarterly review" in the description, **When** I search for "quarterly", **Then** those tasks appear in results
3. **Given** I have tasks tagged "work", **When** I search for "work", **Then** tasks with that tag appear in results
4. **Given** I search for a term that matches title, description, and tags across different tasks, **When** I view results, **Then** all matching tasks are returned
5. **Given** I search for a term with no matches, **When** I view results, **Then** an empty list is displayed with a helpful message
6. **Given** I search with mixed case (e.g., "Meeting"), **When** I view results, **Then** the search is case-insensitive

---

### User Story 6 - Set Due Dates (Priority: P3)

As a user, I want to set optional due dates on my tasks so that I can track deadlines and plan my work accordingly.

**Why this priority**: Due dates enable time-based organization and are prerequisite for reminders and recurring tasks.

**Independent Test**: Can be tested by creating tasks with and without due dates, verifying persistence and display.

**Acceptance Scenarios**:

1. **Given** I am creating a task, **When** I set a due date, **Then** the due date is saved in UTC format
2. **Given** I am creating a task, **When** I do not set a due date, **Then** the task is created with no due date (null)
3. **Given** I have a task with a due date, **When** I update the due date, **Then** the new date is saved
4. **Given** I have a task with a due date, **When** I remove the due date, **Then** the task no longer has a due date
5. **Given** I view my task list, **When** a task's due date is in the past, **Then** it is visually indicated as overdue

---

### User Story 7 - Receive Task Reminders (Priority: P3)

As a user, I want to receive reminders for tasks with upcoming due dates so that I don't miss important deadlines.

**Why this priority**: Reminders add proactive notification capability, building on due dates. Requires event infrastructure.

**Independent Test**: Can be tested by setting due dates and verifying reminder events are published at appropriate times.

**Acceptance Scenarios**:

1. **Given** I have a task with a due date set, **When** the reminder time is reached, **Then** a reminder event is published
2. **Given** I have a task without a due date, **When** time passes, **Then** no reminder event is generated
3. **Given** I update a task's due date, **When** the new reminder time is reached, **Then** the reminder reflects the updated due date
4. **Given** I complete a task before its due date, **When** the original reminder time arrives, **Then** no reminder is sent for the completed task
5. **Given** I delete a task with a due date, **When** the reminder time arrives, **Then** no reminder is sent

---

### User Story 8 - Create Recurring Tasks (Priority: P4)

As a user, I want to create recurring tasks that automatically regenerate on a schedule so that I don't have to manually recreate routine tasks.

**Why this priority**: Recurring tasks are the most advanced feature, requiring event-driven architecture and a separate service.

**Independent Test**: Can be tested by creating a recurring task, completing it, and verifying a new instance is automatically created.

**Acceptance Scenarios**:

1. **Given** I create a task with is_recurring=true and recurrence_pattern="daily", **When** I complete the task, **Then** a new task is created with a due date one day later
2. **Given** I create a task with is_recurring=true and recurrence_pattern="weekly", **When** I complete the task, **Then** a new task is created with a due date one week later
3. **Given** I create a task with is_recurring=true and recurrence_pattern="monthly", **When** I complete the task, **Then** a new task is created with a due date one month later
4. **Given** I have a recurring task, **When** I update is_recurring to false, **Then** completing the task does not generate a new instance
5. **Given** I complete a recurring task, **When** the system creates the next occurrence, **Then** the new task inherits priority, tags, and other attributes from the original
6. **Given** a recurring task has no due date, **When** I mark it complete, **Then** the next occurrence is created with a due date relative to the completion date

---

### Edge Cases

- What happens when a user tries to filter by a tag that doesn't exist? → Empty results returned with no error
- What happens when a recurring task is deleted? → No future occurrences are generated
- What happens when a task is completed multiple times rapidly? → Only one recurrence is created (idempotent)
- What happens when the reminder service is unavailable? → Events are queued and processed when service recovers
- What happens when a user sets a due date in the past? → Task is created/updated; shown as overdue
- What happens when searching with special characters? → Characters are escaped; no injection vulnerabilities

## Requirements *(mandatory)*

### Functional Requirements

**Priority**
- **FR-001**: System MUST support task priority levels: low, medium, high
- **FR-002**: System MUST default new tasks to "medium" priority when not specified
- **FR-003**: Users MUST be able to update task priority at any time

**Tags**
- **FR-004**: System MUST support assigning multiple tags to a single task
- **FR-005**: System MUST store tags in a separate entity with a many-to-many relationship to tasks
- **FR-006**: System MUST reuse existing tags when a user enters a tag name that already exists
- **FR-007**: System MUST allow creating new tags when entering a tag name that doesn't exist

**Search**
- **FR-008**: System MUST support searching tasks by title (case-insensitive)
- **FR-009**: System MUST support searching tasks by description (case-insensitive)
- **FR-010**: System MUST support searching tasks by tag name (case-insensitive)
- **FR-011**: System MUST return tasks matching any of the searched fields (title OR description OR tags)

**Filtering**
- **FR-012**: System MUST support filtering tasks by status (pending, completed, all)
- **FR-013**: System MUST support filtering tasks by priority (low, medium, high)
- **FR-014**: System MUST support filtering tasks by tag
- **FR-015**: System MUST support combining multiple filters with AND logic

**Sorting**
- **FR-016**: System MUST support sorting tasks by created_at (ascending/descending)
- **FR-017**: System MUST support sorting tasks by due_date (ascending/descending)
- **FR-018**: System MUST support sorting tasks by priority (high→medium→low or reverse)
- **FR-019**: System MUST support sorting tasks by title (alphabetical)
- **FR-020**: Tasks without due dates MUST appear at the end when sorting by due_date ascending

**Due Dates**
- **FR-021**: System MUST support optional due dates on tasks
- **FR-022**: System MUST store due dates in UTC format
- **FR-023**: System MUST index due dates for efficient querying

**Reminders**
- **FR-024**: System MUST publish a reminder event when a task with a due date approaches its deadline
- **FR-025**: System MUST NOT send reminders for tasks without due dates
- **FR-026**: System MUST NOT send reminders for completed or deleted tasks
- **FR-027**: System MUST update scheduled reminders when due dates change

**Recurring Tasks**
- **FR-028**: System MUST support marking tasks as recurring with a pattern (daily, weekly, monthly)
- **FR-029**: System MUST automatically create the next occurrence when a recurring task is completed
- **FR-030**: System MUST publish a task completion event for the recurring service to process
- **FR-031**: New recurring task occurrences MUST inherit priority, tags, title, and description from the original
- **FR-032**: System MUST set the new due date relative to the original due date (if present) or completion date

**Event-Driven Requirements**
- **FR-033**: System MUST publish events to the task-events topic when tasks are created, updated, completed, or deleted
- **FR-034**: System MUST publish reminder events to the reminders topic
- **FR-035**: All events MUST include event_id, event_type, user_id, timestamp, and version fields

### Key Entities

- **Task (extended)**: Represents a user's todo item. Extended with priority (enum), due_at (datetime, nullable), is_recurring (boolean), recurrence_pattern (string, nullable)

- **Tag**: Represents a category or label. Attributes: id, name (unique, case-insensitive)

- **TaskTag**: Join entity representing the many-to-many relationship between tasks and tags. Attributes: task_id, tag_id

- **TaskEvent**: Represents an event published when task state changes. Attributes: event_id, event_type, user_id, task_id, timestamp, version, payload

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can set and modify task priority within 2 seconds of interaction
- **SC-002**: Users can add or remove tags from a task within 2 seconds of interaction
- **SC-003**: Search results return within 1 second for task lists up to 10,000 items
- **SC-004**: Filter and sort operations complete within 1 second for task lists up to 10,000 items
- **SC-005**: 95% of reminder notifications are delivered within 5 minutes of the scheduled time
- **SC-006**: Recurring task regeneration occurs within 30 seconds of task completion
- **SC-007**: Zero data loss for task events during normal operation and service restarts
- **SC-008**: All new features work without breaking existing task CRUD operations (backward compatible)
- **SC-009**: Users can combine search, filter, and sort in a single query without errors
- **SC-010**: System handles 100 concurrent users performing filter/sort operations without degradation

## Assumptions

- Reminder timing is based on the due date itself (not a configurable offset before due date)
- Tags are user-specific (each user has their own tag namespace)
- The notification delivery mechanism (email, push, in-app) is handled by a separate notification service
- Recurrence patterns are limited to daily, weekly, monthly (no custom cron expressions in initial release)
- Search is basic keyword matching (not full-text search with relevance scoring)

## Dependencies

- Existing Task CRUD API (spec 001-task-crud-api)
- JWT authentication (spec 002-auth-jwt-security)
- Dapr runtime for Pub/Sub (Constitution Principle IX)
- Kafka for event bus (Constitution technology stack)
- Recurring Task Service (new microservice to be created)
- Notification Service (new microservice to be created)

## Out of Scope

- Custom reminder offsets (e.g., "remind me 1 hour before")
- Complex recurrence patterns (e.g., "every 2nd Tuesday")
- Bulk tag operations
- Tag hierarchy/nesting
- Full-text search with relevance scoring
- Task sharing between users
