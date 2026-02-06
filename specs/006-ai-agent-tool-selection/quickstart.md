# Quickstart: AI Agent Behavior & Tool Selection

## Prerequisites

1. **Backend running**: FastAPI server on port 8000
2. **Frontend running**: Next.js dev server on port 3000
3. **Database**: Neon PostgreSQL with Conversation/Message tables
4. **MCP Server**: `backend/mcp_server.py` functional (Spec 5)
5. **Environment variables**:
   - `DATABASE_URL`: Neon connection string
   - `GROQ_API_KEY`: Groq API key for agent (get from https://console.groq.com)

## Setup

### 1. Install Dependencies

```bash
cd backend
source .venv/bin/activate
pip install groq
```

### 2. Add Groq API Key

Add to `backend/.env`:
```
GROQ_API_KEY=gsk_...
```

### 3. Start Backend

```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload
```

### 4. Start Frontend

```bash
cd frontend
npm run dev
```

## Testing the Agent

### Test 1: Create Task via Natural Language

**Input**: "Add a task to buy groceries"

**Expected behavior**:
1. Agent detects `add_task` intent
2. Agent extracts title: "buy groceries"
3. Agent calls `add_task(user_id, title="buy groceries")`
4. Agent responds: "I've created a task called 'buy groceries'. Is there anything else you'd like to add?"

**Verification**:
- Check task appears in task list (dashboard or via "show my tasks")

### Test 2: List Tasks

**Input**: "What are my tasks?"

**Expected behavior**:
1. Agent detects `list_tasks` intent
2. Agent calls `list_tasks(user_id)`
3. Agent formats and presents task list

**Verification**:
- Response includes all tasks for the authenticated user
- Tasks created by other users are NOT shown

### Test 3: Update Task

**Prerequisites**: Have at least one task (e.g., "buy groceries")

**Input**: "Rename 'buy groceries' to 'buy organic groceries'"

**Expected behavior**:
1. Agent detects `update_task` intent
2. Agent identifies task by title
3. Agent calls `update_task(user_id, task_id, title="buy organic groceries")`
4. Agent confirms: "I've updated the task to 'buy organic groceries'."

**Verification**:
- Task title is updated in list

### Test 4: Complete Task

**Input**: "Mark 'buy organic groceries' as done"

**Expected behavior**:
1. Agent detects `complete_task` intent
2. Agent identifies task by title
3. Agent calls `complete_task(user_id, task_id)`
4. Agent confirms: "Great job! I've marked 'buy organic groceries' as complete."

**Verification**:
- Task shows as completed in list

### Test 5: Delete Task

**Input**: "Delete the groceries task"

**Expected behavior**:
1. Agent detects `delete_task` intent
2. Agent identifies task by title (partial match)
3. Agent calls `delete_task(user_id, task_id)`
4. Agent confirms: "I've deleted the task 'buy organic groceries'."

**Verification**:
- Task no longer appears in list

## Edge Case Tests

### Test 6: Ambiguous Intent

**Input**: "Do something with my tasks"

**Expected**: Agent asks for clarification about what action to take.

### Test 7: Missing Title

**Input**: "Add a task"

**Expected**: Agent asks "What would you like to call this task?"

### Test 8: Task Not Found

**Input**: "Complete the 'nonexistent task'"

**Expected**: Agent says task wasn't found and offers to show the task list.

### Test 9: Multiple Matching Tasks

**Prerequisites**: Create "Buy milk" and "Buy eggs"

**Input**: "Complete the buy task"

**Expected**: Agent lists matching tasks and asks which one.

### Test 10: Out of Scope Request

**Input**: "What's the weather today?"

**Expected**: Agent explains it can only help with task management.

## Cross-User Isolation Test

1. Sign in as User A
2. Create task: "User A's private task"
3. Sign out
4. Sign in as User B
5. Ask: "Show my tasks"
6. **Expected**: User A's task is NOT visible

## Performance Test

1. Send a message
2. Measure time to response
3. **Target**: Response within 3 seconds (SC-002)

## Troubleshooting

### Agent not responding

- Check `GROQ_API_KEY` is set
- Check Groq API status (https://status.groq.com)
- Check backend logs for errors

### Tool errors

- Verify MCP server works standalone: `python mcp_server.py`
- Check DATABASE_URL is correct
- Check user_id is being passed correctly

### Slow responses

- Groq is typically very fast (100+ tokens/second)
- Limit message history to last 20 messages (already implemented)
- Check network latency to Groq

### Cross-user data visible

- Verify user_id is extracted from JWT, not user input
- Check MCP tools filter by user_id
