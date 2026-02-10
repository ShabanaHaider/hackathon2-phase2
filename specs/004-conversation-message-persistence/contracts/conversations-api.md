# API Contract: Conversations & Messages

**Base URL**: `/api/conversations`
**Authentication**: All endpoints require `Authorization: Bearer <JWT>` header.

---

## POST /api/conversations

**Description**: Create a new conversation for the authenticated user.
**Request body**:
```json
{
  "title": "My Chat Session"
}
```
**Response** (201 Created):
```json
{
  "id": "uuid",
  "title": "My Chat Session",
  "user_id": "string",
  "created_at": "2026-02-05T10:00:00Z",
  "updated_at": "2026-02-05T10:00:00Z"
}
```
**Errors**:
- 401: Not authenticated
- 422: Validation error (empty title, title > 255 chars)

---

## GET /api/conversations

**Description**: List all conversations for the authenticated user, ordered
by most recently updated first.
**Response** (200 OK):
```json
[
  {
    "id": "uuid",
    "title": "My Chat Session",
    "user_id": "string",
    "created_at": "2026-02-05T10:00:00Z",
    "updated_at": "2026-02-05T10:00:00Z"
  }
]
```
**Errors**:
- 401: Not authenticated

---

## GET /api/conversations/{conversation_id}

**Description**: Retrieve a single conversation by ID (user-scoped).
**Response** (200 OK):
```json
{
  "id": "uuid",
  "title": "My Chat Session",
  "user_id": "string",
  "created_at": "2026-02-05T10:00:00Z",
  "updated_at": "2026-02-05T10:00:00Z"
}
```
**Errors**:
- 401: Not authenticated
- 404: Conversation not found (or belongs to another user)

---

## PATCH /api/conversations/{conversation_id}

**Description**: Update a conversation's title (user-scoped).
**Request body**:
```json
{
  "title": "Updated Title"
}
```
**Response** (200 OK):
```json
{
  "id": "uuid",
  "title": "Updated Title",
  "user_id": "string",
  "created_at": "2026-02-05T10:00:00Z",
  "updated_at": "2026-02-05T10:05:00Z"
}
```
**Errors**:
- 401: Not authenticated
- 404: Conversation not found (or belongs to another user)
- 422: Validation error

---

## DELETE /api/conversations/{conversation_id}

**Description**: Delete a conversation and all its messages (user-scoped).
**Response** (204 No Content): Empty body
**Errors**:
- 401: Not authenticated
- 404: Conversation not found (or belongs to another user)

---

## POST /api/conversations/{conversation_id}/messages

**Description**: Create a message within a conversation (user-scoped).
**Request body**:
```json
{
  "role": "user",
  "content": "Hello, can you help me with my tasks?"
}
```
**Response** (201 Created):
```json
{
  "id": "uuid",
  "conversation_id": "uuid",
  "role": "user",
  "content": "Hello, can you help me with my tasks?",
  "created_at": "2026-02-05T10:01:00Z"
}
```
**Errors**:
- 401: Not authenticated
- 404: Conversation not found (or belongs to another user)
- 422: Validation error (empty content, content > 16000 chars, invalid role)

---

## GET /api/conversations/{conversation_id}/messages

**Description**: Retrieve all messages for a conversation in chronological
order (user-scoped).
**Response** (200 OK):
```json
[
  {
    "id": "uuid",
    "conversation_id": "uuid",
    "role": "user",
    "content": "Hello, can you help me with my tasks?",
    "created_at": "2026-02-05T10:01:00Z"
  },
  {
    "id": "uuid",
    "conversation_id": "uuid",
    "role": "assistant",
    "content": "Of course! What would you like to do?",
    "created_at": "2026-02-05T10:01:01Z"
  }
]
```
**Errors**:
- 401: Not authenticated
- 404: Conversation not found (or belongs to another user)

---

## Error Response Format

All errors follow the existing pattern:
```json
{
  "detail": "Human-readable error message"
}
```
