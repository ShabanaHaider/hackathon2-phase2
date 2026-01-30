# Frontend API Client Contract

**Feature**: 003-todo-web-frontend
**Date**: 2026-01-28

## TypeScript Interfaces

### Task Entity

```typescript
interface Task {
  id: string;           // UUID
  title: string;        // 1-255 characters
  description: string | null;  // 0-2000 characters
  is_completed: boolean;
  completed_at: string | null;  // ISO 8601 datetime
  created_at: string;   // ISO 8601 datetime
  updated_at: string;   // ISO 8601 datetime
  user_id: string;      // Owner's user ID
}
```

### Request Payloads

```typescript
interface TaskCreateRequest {
  title: string;        // Required, 1-255 chars
  description?: string; // Optional, max 2000 chars
}

interface TaskUpdateRequest {
  title?: string;       // Optional, 1-255 chars
  description?: string; // Optional, max 2000 chars
  is_completed?: boolean; // Optional
}
```

### Error Response

```typescript
interface ApiError {
  detail: string;
}
```

## API Methods

### List Tasks

```typescript
async function listTasks(): Promise<Task[]>
// GET /api/todos
// Headers: Authorization: Bearer <jwt>
// Response: 200 OK, Task[]
// Error: 401 Unauthorized
```

### Create Task

```typescript
async function createTask(data: TaskCreateRequest): Promise<Task>
// POST /api/todos
// Headers: Authorization: Bearer <jwt>
// Body: { title: string, description?: string }
// Response: 201 Created, Task
// Errors: 401 Unauthorized, 422 Validation Error
```

### Update Task

```typescript
async function updateTask(id: string, data: TaskUpdateRequest): Promise<Task>
// PATCH /api/todos/{id}
// Headers: Authorization: Bearer <jwt>
// Body: { title?: string, description?: string, is_completed?: boolean }
// Response: 200 OK, Task
// Errors: 401 Unauthorized, 404 Not Found, 422 Validation Error
```

### Delete Task

```typescript
async function deleteTask(id: string): Promise<void>
// DELETE /api/todos/{id}
// Headers: Authorization: Bearer <jwt>
// Response: 204 No Content
// Errors: 401 Unauthorized, 404 Not Found
```

## Error Handling Contract

| Status Code | Meaning | Frontend Behavior |
|-------------|---------|-------------------|
| 200 | Success | Update UI with response data |
| 201 | Created | Add new item to list |
| 204 | Deleted | Remove item from list |
| 401 | Unauthorized | Redirect to /signin |
| 404 | Not Found | Show "Task not found" error |
| 422 | Validation Error | Display validation message |
| 500 | Server Error | Show generic error, offer retry |

## JWT Token Retrieval

Better Auth provides the JWT via the session. The API client must:

1. Call `authClient.getSession()` to get current session
2. Extract JWT from session (exact method depends on Better Auth config)
3. Attach as `Authorization: Bearer <token>` header
4. Handle token refresh automatically via Better Auth

## CORS Requirements

Backend must allow:
- Origin: `http://localhost:3000` (dev) and production domain
- Methods: GET, POST, PATCH, DELETE
- Headers: Authorization, Content-Type
- Credentials: true (for cookies if needed)
