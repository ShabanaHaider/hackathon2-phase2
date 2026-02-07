# MCP Tool Contracts: Task Tools

## Server Configuration

- **Server name**: `todo-task-tools`
- **Transport**: `stdio`
- **SDK**: `mcp` (Official Python MCP SDK via `FastMCP`)
- **Entry point**: `backend/mcp_server.py`

## Tool 1: `add_task`

**Description**: Create a new task for a user.

**Parameters**:

| Name        | Type   | Required | Description                    |
|-------------|--------|----------|--------------------------------|
| user_id     | string | Yes      | The authenticated user's ID    |
| title       | string | Yes      | Task title (1-255 chars)       |
| description | string | No       | Task description (max 2000)    |

**Success response** (text):
```
Task created successfully.
ID: <uuid>
Title: <title>
Description: <description or "None">
Created: <timestamp>
```

**Error responses**:
- Empty/whitespace title: `"Error: Title is required and must be 1-255 characters."`
- Title > 255 chars: `"Error: Title is required and must be 1-255 characters."`
- Empty user_id: `"Error: user_id is required."`
- DB failure: `"Error: Failed to create task. Please try again."`

---

## Tool 2: `list_tasks`

**Description**: List all tasks for a user.

**Parameters**:

| Name    | Type   | Required | Description                 |
|---------|--------|----------|-----------------------------|
| user_id | string | Yes      | The authenticated user's ID |

**Success response** (text):
```
Found <N> task(s):

1. [<status>] <title> (ID: <uuid>)
   Created: <timestamp>
2. [<status>] <title> (ID: <uuid>)
   Created: <timestamp>
```

Where `<status>` is `DONE` or `TODO`.

**Empty list**: `"No tasks found for this user."`

**Error responses**:
- Empty user_id: `"Error: user_id is required."`
- DB failure: `"Error: Failed to list tasks. Please try again."`

---

## Tool 3: `update_task`

**Description**: Update the title or description of an existing task.

**Parameters**:

| Name        | Type   | Required | Description                    |
|-------------|--------|----------|--------------------------------|
| user_id     | string | Yes      | The authenticated user's ID    |
| task_id     | string | Yes      | UUID of the task to update     |
| title       | string | No       | New title (1-255 chars)        |
| description | string | No       | New description (max 2000)     |

**Success response** (text):
```
Task updated successfully.
ID: <uuid>
Title: <title>
Description: <description or "None">
Updated: <timestamp>
```

**Error responses**:
- Task not found / wrong user: `"Error: Task not found."`
- Invalid UUID: `"Error: Invalid task_id format."`
- No fields to update: `"Error: No fields to update. Provide title or description."`
- DB failure: `"Error: Failed to update task. Please try again."`

---

## Tool 4: `complete_task`

**Description**: Toggle the completion status of a task.

**Parameters**:

| Name    | Type   | Required | Description                  |
|---------|--------|----------|------------------------------|
| user_id | string | Yes      | The authenticated user's ID  |
| task_id | string | Yes      | UUID of the task to complete |

**Success response** (text):
```
Task marked as completed.
ID: <uuid>
Title: <title>
Completed: <timestamp>
```

Or if toggled back:
```
Task marked as incomplete.
ID: <uuid>
Title: <title>
```

**Error responses**:
- Task not found / wrong user: `"Error: Task not found."`
- Invalid UUID: `"Error: Invalid task_id format."`
- DB failure: `"Error: Failed to update task. Please try again."`

---

## Tool 5: `delete_task`

**Description**: Permanently delete a task.

**Parameters**:

| Name    | Type   | Required | Description                 |
|---------|--------|----------|-----------------------------|
| user_id | string | Yes      | The authenticated user's ID |
| task_id | string | Yes      | UUID of the task to delete  |

**Success response** (text):
```
Task deleted successfully.
ID: <uuid>
Title: <title>
```

**Error responses**:
- Task not found / wrong user: `"Error: Task not found."`
- Invalid UUID: `"Error: Invalid task_id format."`
- DB failure: `"Error: Failed to delete task. Please try again."`
