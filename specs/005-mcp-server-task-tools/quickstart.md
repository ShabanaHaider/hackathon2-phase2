# Quickstart: MCP Server & Task Tools

## Prerequisites

- Python 3.10+ with backend virtual environment activated
- Neon PostgreSQL database accessible
- Backend `.env` configured with `DATABASE_URL`
- `mcp` package installed (`pip install "mcp[cli]"`)

## Verification Steps

### 1. Install MCP SDK

```bash
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install "mcp[cli]"
```

### 2. Start the MCP Server

```bash
python mcp_server.py
```

The server communicates via stdio — it will wait for JSON-RPC messages on
stdin. For testing, use the MCP Inspector or a test script.

### 3. Test with MCP Inspector (Optional)

```bash
mcp dev mcp_server.py
```

This opens an interactive inspector in your browser to test tool calls.

### 4. Test add_task

Send a JSON-RPC call to the running server:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "add_task",
    "arguments": {
      "user_id": "test-user-001",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread"
    }
  }
}
```

Expected: Response with "Task created successfully" and task details.

### 5. Test list_tasks

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "list_tasks",
    "arguments": {
      "user_id": "test-user-001"
    }
  }
}
```

Expected: Response listing the task created in step 4.

### 6. Test update_task

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "update_task",
    "arguments": {
      "user_id": "test-user-001",
      "task_id": "<TASK_ID_FROM_STEP_4>",
      "title": "Buy organic groceries"
    }
  }
}
```

Expected: Response with "Task updated successfully" and new title.

### 7. Test complete_task

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "complete_task",
    "arguments": {
      "user_id": "test-user-001",
      "task_id": "<TASK_ID_FROM_STEP_4>"
    }
  }
}
```

Expected: Response with "Task marked as completed" and completed_at timestamp.

### 8. Test delete_task

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tools/call",
  "params": {
    "name": "delete_task",
    "arguments": {
      "user_id": "test-user-001",
      "task_id": "<TASK_ID_FROM_STEP_4>"
    }
  }
}
```

Expected: Response with "Task deleted successfully".

### 9. Cross-User Isolation Test

Create a task with user A, then try to access it with user B:

```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "tools/call",
  "params": {
    "name": "complete_task",
    "arguments": {
      "user_id": "different-user-002",
      "task_id": "<TASK_ID_FROM_USER_A>"
    }
  }
}
```

Expected: Response with "Error: Task not found."

### 10. Verify REST API Still Works

While the MCP server is running (or stopped), confirm the FastAPI REST
API at `http://localhost:8000/api/todos` still functions normally:

```bash
curl http://localhost:8000/api/todos \
  -H "Authorization: Bearer <TOKEN>"
```

Expected: 200 with task list (compatibility guarantee).
