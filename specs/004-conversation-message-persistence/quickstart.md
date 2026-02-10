# Quickstart: Conversation & Message Persistence

## Prerequisites

- Python 3.11+ with backend virtual environment activated
- Neon PostgreSQL database accessible
- Backend `.env` configured with `DATABASE_URL` and `BETTER_AUTH_URL`
- Frontend running (for JWT token generation)

## Verification Steps

### 1. Start the Backend

```bash
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uvicorn main:app --reload --port 8000
```

Tables `conversations` and `messages` are auto-created on startup.

### 2. Get a JWT Token

Sign in via the frontend at `http://localhost:3000/signin`, then retrieve
a token from the browser's `/api/auth/token` endpoint or network tab.

### 3. Create a Conversation

```bash
curl -X POST http://localhost:8000/api/conversations \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Chat"}'
```

Expected: 201 with conversation JSON including `id`.

### 4. List Conversations

```bash
curl http://localhost:8000/api/conversations \
  -H "Authorization: Bearer <TOKEN>"
```

Expected: 200 with array of conversations, ordered by `updated_at` DESC.

### 5. Add a Message

```bash
curl -X POST http://localhost:8000/api/conversations/<CONVERSATION_ID>/messages \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"role": "user", "content": "Hello!"}'
```

Expected: 201 with message JSON.

### 6. Retrieve Messages

```bash
curl http://localhost:8000/api/conversations/<CONVERSATION_ID>/messages \
  -H "Authorization: Bearer <TOKEN>"
```

Expected: 200 with array of messages, ordered by `created_at` ASC.

### 7. Update Conversation Title

```bash
curl -X PATCH http://localhost:8000/api/conversations/<CONVERSATION_ID> \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Renamed Chat"}'
```

Expected: 200 with updated conversation.

### 8. Delete Conversation (Cascade)

```bash
curl -X DELETE http://localhost:8000/api/conversations/<CONVERSATION_ID> \
  -H "Authorization: Bearer <TOKEN>"
```

Expected: 204 No Content. Subsequent message retrieval returns 404.

### 9. Cross-User Isolation Test

Using a token from a different user, attempt to access the conversation:

```bash
curl http://localhost:8000/api/conversations/<OTHER_USER_CONV_ID> \
  -H "Authorization: Bearer <OTHER_TOKEN>"
```

Expected: 404 Not Found.
