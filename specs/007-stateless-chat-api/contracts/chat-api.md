# API Contract: Stateless Chat Endpoint

**Feature**: 007-stateless-chat-api
**Date**: 2026-02-06
**Base URL**: `/api`

---

## POST /{user_id}/chat

Send a message to the AI assistant and receive a response.

### Path Parameters

| Parameter | Type   | Required | Description |
|-----------|--------|----------|-------------|
| user_id   | string | Yes      | The authenticated user's ID |

### Headers

| Header        | Value            | Required | Description |
|---------------|------------------|----------|-------------|
| Authorization | Bearer {token}   | Yes      | JWT token from Better Auth |
| Content-Type  | application/json | Yes      | Request body format |

### Request Body

```json
{
  "message": "string (1-16000 chars)"
}
```

| Field   | Type   | Required | Constraints | Description |
|---------|--------|----------|-------------|-------------|
| message | string | Yes      | 1-16000 chars | User's natural language message |

### Response (200 OK)

```json
{
  "user_message": {
    "id": "uuid",
    "conversation_id": "uuid",
    "role": "user",
    "content": "string",
    "created_at": "datetime"
  },
  "assistant_message": {
    "id": "uuid",
    "conversation_id": "uuid",
    "role": "assistant",
    "content": "string",
    "created_at": "datetime"
  },
  "tool_calls": [
    {
      "name": "string",
      "arguments": {},
      "result": "string",
      "duration_ms": 0
    }
  ]
}
```

| Field             | Type              | Nullable | Description |
|-------------------|-------------------|----------|-------------|
| user_message      | MessageResponse   | No       | The persisted user message |
| assistant_message | MessageResponse   | No       | The AI agent's response |
| tool_calls        | ToolCallInfo[]    | Yes      | List of tool invocations (null if none) |

### Error Responses

#### 400 Bad Request

Invalid request body or validation failure.

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "message"],
      "msg": "String should have at least 1 character",
      "input": ""
    }
  ]
}
```

#### 401 Unauthorized

Missing or invalid JWT token.

```json
{
  "detail": "Not authenticated"
}
```

#### 403 Forbidden

URL user_id does not match authenticated user.

```json
{
  "detail": "User ID mismatch"
}
```

#### 500 Internal Server Error

Agent failure (user message still persisted).

```json
{
  "detail": "AI agent error",
  "user_message": {
    "id": "uuid",
    "conversation_id": "uuid",
    "role": "user",
    "content": "string",
    "created_at": "datetime"
  }
}
```

---

## Behavior Specifications

### Automatic Conversation Creation

If the user has no existing conversation, one is automatically created with:
- `title`: "Task Assistant"
- `user_id`: From JWT token
- `created_at`: Current UTC timestamp

### Message History Context

The AI agent receives the last 20 messages as context for each request.
Messages are loaded in chronological order (oldest first).

### Data Persistence Guarantee

The user's message is persisted to the database **before** the AI agent is invoked.
This ensures the message survives even if the agent fails.

### Stateless Design

No conversation state is retained in memory between requests.
All context is reconstructed from the database on each request.

---

## Example Requests

### Create a Task

**Request**:
```bash
curl -X POST "http://localhost:8000/api/user123/chat" \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy groceries"}'
```

**Response**:
```json
{
  "user_message": {
    "id": "a1b2c3d4-...",
    "conversation_id": "e5f6g7h8-...",
    "role": "user",
    "content": "Add a task to buy groceries",
    "created_at": "2026-02-06T12:00:00Z"
  },
  "assistant_message": {
    "id": "i9j0k1l2-...",
    "conversation_id": "e5f6g7h8-...",
    "role": "assistant",
    "content": "I've created a task called 'buy groceries'. Is there anything else you'd like to add?",
    "created_at": "2026-02-06T12:00:01Z"
  },
  "tool_calls": [
    {
      "name": "add_task",
      "arguments": {"title": "buy groceries", "user_id": "user123"},
      "result": "Task created successfully.\nID: m3n4o5p6-...\nTitle: buy groceries",
      "duration_ms": 145
    }
  ]
}
```

### List Tasks

**Request**:
```bash
curl -X POST "http://localhost:8000/api/user123/chat" \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"message": "What are my tasks?"}'
```

**Response**:
```json
{
  "user_message": {
    "id": "...",
    "conversation_id": "...",
    "role": "user",
    "content": "What are my tasks?",
    "created_at": "2026-02-06T12:01:00Z"
  },
  "assistant_message": {
    "id": "...",
    "conversation_id": "...",
    "role": "assistant",
    "content": "Here are your tasks:\n\n1. [TODO] buy groceries\n\nWould you like to add, complete, or modify any tasks?",
    "created_at": "2026-02-06T12:01:01Z"
  },
  "tool_calls": [
    {
      "name": "list_tasks",
      "arguments": {"user_id": "user123"},
      "result": "Found 1 task(s):\n\n1. [TODO] buy groceries (ID: m3n4o5p6-...)",
      "duration_ms": 89
    }
  ]
}
```

---

## OpenAPI Schema

```yaml
paths:
  /api/{user_id}/chat:
    post:
      summary: Chat with AI Assistant
      description: Send a message to the AI assistant and receive a response
      operationId: chatWithAgent
      tags:
        - chat
      security:
        - BearerAuth: []
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
          description: The authenticated user's ID
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserChatRequest'
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserChatResponse'
        '400':
          description: Bad request
        '401':
          description: Unauthorized
        '403':
          description: Forbidden - user_id mismatch
        '500':
          description: Internal server error

components:
  schemas:
    UserChatRequest:
      type: object
      required:
        - message
      properties:
        message:
          type: string
          minLength: 1
          maxLength: 16000

    UserChatResponse:
      type: object
      required:
        - user_message
        - assistant_message
      properties:
        user_message:
          $ref: '#/components/schemas/MessageResponse'
        assistant_message:
          $ref: '#/components/schemas/MessageResponse'
        tool_calls:
          type: array
          nullable: true
          items:
            $ref: '#/components/schemas/ToolCallInfo'

    ToolCallInfo:
      type: object
      required:
        - name
        - arguments
        - result
        - duration_ms
      properties:
        name:
          type: string
        arguments:
          type: object
        result:
          type: string
        duration_ms:
          type: integer

    MessageResponse:
      type: object
      required:
        - id
        - conversation_id
        - role
        - content
        - created_at
      properties:
        id:
          type: string
          format: uuid
        conversation_id:
          type: string
          format: uuid
        role:
          type: string
        content:
          type: string
        created_at:
          type: string
          format: date-time

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```
