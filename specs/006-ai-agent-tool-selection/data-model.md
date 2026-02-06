# Data Model: AI Agent Behavior & Tool Selection

## Existing Entities (No Changes Required)

This feature reuses existing database tables from previous specs without modification.

### Task (Spec 1)

The agent manages tasks through MCP tools. No changes to the Task model.

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | Primary key |
| title | str | Task title |
| description | str (nullable) | Task description |
| is_completed | bool | Completion status |
| completed_at | datetime (nullable) | When completed |
| created_at | datetime | Creation timestamp |
| updated_at | datetime | Last update timestamp |
| user_id | str | Owner's user ID |

### Conversation (Spec 4)

The agent operates within existing conversations. No changes to the Conversation model.

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | Primary key |
| user_id | str | Owner's user ID |
| title | str | Conversation title |
| created_at | datetime | Creation timestamp |
| updated_at | datetime | Last update timestamp |

### Message (Spec 4)

Agent responses are persisted as messages. No changes to the Message model.

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | Primary key |
| conversation_id | UUID | Parent conversation |
| role | str | "user", "assistant", or "system" |
| content | str | Message text |
| created_at | datetime | Creation timestamp |

## Agent Configuration (Not Persisted)

The agent is configured in code, not in the database.

### Agent Definition

| Property | Value | Notes |
|----------|-------|-------|
| name | "TaskAssistant" | Agent identifier |
| model | "gpt-4o" | OpenAI model (configurable via env) |
| instructions | System prompt | Defines agent behavior |
| mcp_servers | [StdioMCPServer] | Connection to MCP server |

### System Prompt (Instructions)

The system prompt is stored as a constant in `backend/agent.py`. It defines:

1. **Role**: "You are a helpful task management assistant"
2. **Capabilities**: Create, list, update, complete, and delete tasks
3. **Tool selection rules**: When to use each MCP tool
4. **Clarification behavior**: Ask when intent is unclear
5. **Confirmation format**: Acknowledge actions with details
6. **Error handling**: Translate tool errors to friendly messages

### MCP Server Configuration

| Property | Value | Notes |
|----------|-------|-------|
| transport | stdio | Subprocess communication |
| command | python | Python interpreter |
| args | ["mcp_server.py"] | Path to MCP server |
| cwd | backend/ | Working directory |
| cache_tools_list | True | Reduce latency |

## Intent-to-Tool Mapping

The agent uses the following mapping (encoded in system prompt):

| User Intent | MCP Tool | Required Parameters |
|-------------|----------|---------------------|
| Create/add task | add_task | user_id, title, description? |
| List/show tasks | list_tasks | user_id |
| Update/change task | update_task | user_id, task_id, title?, description? |
| Complete/finish task | complete_task | user_id, task_id |
| Delete/remove task | delete_task | user_id, task_id |

## Message Flow

```
User Message → Load History → Agent SDK → MCP Tool → Tool Result → Agent Response → Save Message
     ↑                                                                                    ↓
     └────────────────────────── Database (Conversation/Message) ────────────────────────┘
```
