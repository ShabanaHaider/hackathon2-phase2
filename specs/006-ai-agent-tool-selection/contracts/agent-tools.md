# Agent Tools Contract: AI Agent Behavior & Tool Selection

## Overview

This document defines the contract between the AI agent and the MCP tools. The agent invokes these tools based on user intent, passing the user's ID and extracted parameters.

## Tool Invocation Interface

All tools are invoked via the MCP protocol through stdio transport. The agent SDK handles serialization and deserialization automatically.

### Common Parameters

| Parameter | Type | Required | Source |
|-----------|------|----------|--------|
| user_id | str | Yes | Injected from authenticated session |

The `user_id` is NOT extracted from user input. It is injected by the agent runner from the authenticated user's session context.

---

## Tool: add_task

**Purpose**: Create a new task for the authenticated user.

**When to use**: User wants to create, add, or make a new task.

**Intent triggers**:
- "Add a task to..."
- "Create a task for..."
- "I need to..."
- "Remind me to..."
- "New task:..."

### Parameters

| Parameter | Type | Required | Validation |
|-----------|------|----------|------------|
| user_id | str | Yes | Non-empty |
| title | str | Yes | 1-255 characters |
| description | str | No | Max 2000 characters |

### Response Format

**Success**:
```
Task created successfully.
ID: <uuid>
Title: <title>
Description: <description or None>
Created: <iso_timestamp>
```

**Error**:
```
Error: <error_message>
```

### Agent Confirmation Template

"I've created a task called '[title]'. Is there anything else you'd like to add?"

---

## Tool: list_tasks

**Purpose**: Retrieve all tasks for the authenticated user.

**When to use**: User wants to see, view, list, or check their tasks.

**Intent triggers**:
- "What are my tasks?"
- "Show my to-do list"
- "What do I need to do?"
- "List my tasks"

### Parameters

| Parameter | Type | Required | Validation |
|-----------|------|----------|------------|
| user_id | str | Yes | Non-empty |

### Response Format

**Success (tasks found)**:
```
Found N task(s):

1. [TODO/DONE] <title> (ID: <uuid>)
   Created: <iso_timestamp>
...
```

**Success (no tasks)**:
```
No tasks found for this user.
```

### Agent Confirmation Template

For tasks found: "Here are your tasks: [formatted list]. Would you like to add, complete, or delete any of these?"

For no tasks: "You don't have any tasks yet. Would you like me to create one?"

---

## Tool: update_task

**Purpose**: Update the title or description of an existing task.

**When to use**: User wants to change, update, rename, or edit a task.

**Intent triggers**:
- "Change the title of..."
- "Rename my task..."
- "Update the description..."
- "Edit my task..."

### Parameters

| Parameter | Type | Required | Validation |
|-----------|------|----------|------------|
| user_id | str | Yes | Non-empty |
| task_id | str | Yes | Valid UUID |
| title | str | No | 1-255 characters |
| description | str | No | Max 2000 characters |

At least one of `title` or `description` must be provided.

### Response Format

**Success**:
```
Task updated successfully.
ID: <uuid>
Title: <title>
Description: <description or None>
Updated: <iso_timestamp>
```

**Error**:
```
Error: <error_message>
```

### Agent Confirmation Template

"I've updated the task '[old_title]' to '[new_title]'. Anything else?"

### Task Identification

When the user refers to a task by title (not ID), the agent should:
1. Call `list_tasks` first to get the task list
2. Find the matching task by title (partial match acceptable)
3. If multiple matches, ask user to clarify
4. If no match, inform user the task wasn't found

---

## Tool: complete_task

**Purpose**: Toggle the completion status of a task.

**When to use**: User wants to mark a task as done/complete or undo completion.

**Intent triggers**:
- "Mark ... as done"
- "Complete the task..."
- "I finished..."
- "Done with..."
- "Unmark ... as complete" (toggle back)

### Parameters

| Parameter | Type | Required | Validation |
|-----------|------|----------|------------|
| user_id | str | Yes | Non-empty |
| task_id | str | Yes | Valid UUID |

### Response Format

**Success (marked complete)**:
```
Task marked as completed.
ID: <uuid>
Title: <title>
Completed: <iso_timestamp>
```

**Success (marked incomplete)**:
```
Task marked as incomplete.
ID: <uuid>
Title: <title>
```

**Error**:
```
Error: <error_message>
```

### Agent Confirmation Template

Completed: "Great job! I've marked '[title]' as complete."

Incomplete: "I've marked '[title]' as incomplete. It's back on your to-do list."

---

## Tool: delete_task

**Purpose**: Permanently remove a task.

**When to use**: User wants to delete, remove, or get rid of a task.

**Intent triggers**:
- "Delete the task..."
- "Remove my task..."
- "Get rid of..."
- "I don't need ... anymore"

### Parameters

| Parameter | Type | Required | Validation |
|-----------|------|----------|------------|
| user_id | str | Yes | Non-empty |
| task_id | str | Yes | Valid UUID |

### Response Format

**Success**:
```
Task deleted successfully.
ID: <uuid>
Title: <title>
```

**Error**:
```
Error: <error_message>
```

### Agent Confirmation Template

"I've deleted the task '[title]'. This can't be undone. Is there anything else?"

---

## Error Handling

### Common Errors

| Error Message | User-Friendly Translation |
|---------------|---------------------------|
| "Error: user_id is required." | Internal error (should not occur) |
| "Error: Title is required and must be 1-255 characters." | "Please provide a title for the task." |
| "Error: Invalid task_id format." | "I couldn't understand which task you meant. Can you be more specific?" |
| "Error: Task not found." | "I couldn't find that task. Would you like to see your task list?" |
| "Error: No fields to update." | "What would you like to change about this task?" |

### Agent Error Behavior

1. **Never show raw error messages to users**
2. **Always offer a helpful next step** (e.g., "Would you like to see your tasks?")
3. **Ask for clarification** when the issue is unclear input
4. **Apologize briefly** but don't over-explain

---

## Clarification Behavior

When the agent cannot determine intent or identify a task:

1. **Ambiguous intent**: "I'm not sure what you'd like to do. Would you like to add a new task, see your tasks, or update an existing one?"

2. **Missing task title**: "What would you like to call this task?"

3. **Multiple task matches**: "I found several tasks matching that description: [list]. Which one did you mean?"

4. **No matching task**: "I couldn't find a task called '[query]'. Here are your current tasks: [list]"

5. **Out of scope request**: "I can help you manage your tasks — creating, viewing, updating, completing, or deleting them. What would you like to do?"
