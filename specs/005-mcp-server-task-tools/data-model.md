# Data Model: MCP Server & Task Tools

## Existing Entity (No Changes)

### Task

Reuses the existing `Task` SQLModel table from Spec 1 without modification.

| Field         | Type              | Constraints                      |
|---------------|-------------------|----------------------------------|
| id            | UUID              | Primary key, auto-generated      |
| title         | str               | max_length=255, required         |
| description   | str (nullable)    | max_length=2000, optional        |
| is_completed  | bool              | default=False                    |
| completed_at  | datetime (nullable)| set when completed, cleared when uncompleted |
| created_at    | datetime          | auto-set on creation, timezone-aware |
| updated_at    | datetime          | auto-set on creation/update, timezone-aware |
| user_id       | str               | indexed, max_length=255          |

## MCP Tool Schemas

### add_task

| Parameter   | Type   | Required | Constraints            |
|-------------|--------|----------|------------------------|
| user_id     | str    | Yes      | Non-empty              |
| title       | str    | Yes      | 1-255 characters       |
| description | str    | No       | max 2000 characters    |

**Returns**: Task details (id, title, description, is_completed, created_at)

### list_tasks

| Parameter | Type | Required | Constraints |
|-----------|------|----------|-------------|
| user_id   | str  | Yes      | Non-empty   |

**Returns**: List of task summaries (id, title, is_completed, created_at, updated_at)

### update_task

| Parameter   | Type   | Required | Constraints            |
|-------------|--------|----------|------------------------|
| user_id     | str    | Yes      | Non-empty              |
| task_id     | str    | Yes      | Valid UUID             |
| title       | str    | No       | 1-255 characters       |
| description | str    | No       | max 2000 characters    |

**Returns**: Updated task details or not-found error

### complete_task

| Parameter | Type | Required | Constraints |
|-----------|------|----------|-------------|
| user_id   | str  | Yes      | Non-empty   |
| task_id   | str  | Yes      | Valid UUID  |

**Returns**: Task with toggled completion status or not-found error

### delete_task

| Parameter | Type | Required | Constraints |
|-----------|------|----------|-------------|
| user_id   | str  | Yes      | Non-empty   |
| task_id   | str  | Yes      | Valid UUID  |

**Returns**: Success confirmation or not-found error
