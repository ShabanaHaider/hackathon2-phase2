# Quickstart: Stateless Chat API Endpoint

## Prerequisites

1. **Backend running**: FastAPI server on port 8000
2. **Frontend running**: Next.js dev server on port 3000 (for obtaining JWT)
3. **Database**: Neon PostgreSQL with Conversation/Message tables (Spec 4)
4. **Agent ready**: `backend/agent.py` restored from 006 branch
5. **Environment variables**:
   - `DATABASE_URL`: Neon connection string
   - `GROQ_API_KEY`: Groq API key for AI agent
   - `BETTER_AUTH_URL`: Better Auth server URL

## Setup

### 1. Restore Agent Module

If `backend/agent.py` doesn't exist, restore it from the 006 branch:

```bash
cd backend
git checkout 006-ai-agent-tool-selection -- agent.py
```

### 2. Install Dependencies

```bash
cd backend
source .venv/bin/activate
pip install groq>=0.9.0
```

### 3. Verify Environment Variables

Check `backend/.env`:
```
DATABASE_URL=postgresql://...
BETTER_AUTH_URL=http://localhost:3000
GROQ_API_KEY=gsk_...
```

### 4. Start Backend

```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload
```

### 5. Obtain JWT Token

1. Start frontend: `cd frontend && npm run dev`
2. Sign in at http://localhost:3000
3. Open browser DevTools → Application → Cookies
4. Copy the `better-auth.session_token` value

Or use the auth debug endpoint:
```bash
curl http://localhost:3000/api/debug/auth-config
```

## Testing the Chat Endpoint

### Test 1: Create a Task

**Request**:
```bash
USER_ID="your-user-id"
TOKEN="your-jwt-token"

curl -X POST "http://localhost:8000/api/${USER_ID}/chat" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy groceries"}'
```

**Expected Response**:
```json
{
  "user_message": {
    "id": "...",
    "role": "user",
    "content": "Add a task to buy groceries"
  },
  "assistant_message": {
    "id": "...",
    "role": "assistant",
    "content": "I've created a task called 'buy groceries'."
  },
  "tool_calls": [
    {
      "name": "add_task",
      "arguments": {"title": "buy groceries"},
      "result": "Task created successfully...",
      "duration_ms": 150
    }
  ]
}
```

### Test 2: List Tasks

```bash
curl -X POST "http://localhost:8000/api/${USER_ID}/chat" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show my tasks"}'
```

### Test 3: Context Continuity

Send multiple messages and verify the assistant remembers context:

```bash
# First message
curl -X POST "http://localhost:8000/api/${USER_ID}/chat" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task called project deadline"}'

# Second message (references first)
curl -X POST "http://localhost:8000/api/${USER_ID}/chat" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Mark that task as done"}'
```

**Expected**: Agent should find and complete "project deadline" without needing the full name.

### Test 4: User Isolation

Try accessing another user's chat:

```bash
curl -X POST "http://localhost:8000/api/different-user-id/chat" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show my tasks"}'
```

**Expected**: 403 Forbidden response.

### Test 5: First-Time User (Auto-Create Conversation)

Use a user who has never chatted before:

```bash
curl -X POST "http://localhost:8000/api/${USER_ID}/chat" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

**Expected**: Conversation created automatically, response includes valid `conversation_id`.

## Verification Checklist

- [ ] Message sent successfully (200 response)
- [ ] User message appears in response
- [ ] Assistant message appears in response
- [ ] Tool calls array present when tools invoked
- [ ] Conversation auto-created for new users
- [ ] Context maintained across messages
- [ ] User isolation enforced (403 for mismatched user_id)
- [ ] Response time under 5 seconds

## Troubleshooting

### "Not authenticated" (401)

- Verify JWT token is valid and not expired
- Check `Authorization: Bearer` header format
- Ensure Better Auth is running

### "User ID mismatch" (403)

- The user_id in URL must match the user_id in the JWT token
- Decode JWT to verify the user_id claim

### Agent not responding

- Check `GROQ_API_KEY` is set correctly
- Verify Groq API status: https://status.groq.com
- Check backend logs for error messages

### Tool calls empty

- Some responses don't require tools (e.g., "Hello!")
- Check agent.py SYSTEM_PROMPT for tool triggers
- Verify MCP server tools are importable

### Slow responses (>5s)

- Groq typically responds in 1-2 seconds
- Check network latency to Groq API
- Monitor for rate limiting (429 errors)

### Database errors

- Verify `DATABASE_URL` is correct
- Check Neon dashboard for connection limits
- Ensure tables exist (run `create_db_and_tables()`)

## Performance Benchmarks

| Operation | Expected Time |
|-----------|--------------|
| Message persistence | <50ms |
| History loading (20 msgs) | <100ms |
| Groq inference | 1-2s |
| Tool execution | <200ms each |
| **Total round-trip** | **<3s typical** |
