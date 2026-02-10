# Data Model: Task CRUD API

**Feature Branch**: `001-task-crud-api`
**Date**: 2026-01-27

## Entity: Task

### Fields

| Field          | Type                     | Constraints                     | Notes                                      |
|----------------|--------------------------|---------------------------------|--------------------------------------------|
| id             | UUID                     | PK, generated, not client-set   | uuid4 default                              |
| title          | String(255)              | NOT NULL, 1-255 chars           | Required on create                         |
| description    | String(2000)             | Nullable, max 2000 chars        | Optional                                   |
| is_completed   | Boolean                  | NOT NULL, default false         | Toggle for completion status               |
| completed_at   | DateTime (UTC, nullable) | Nullable                        | Set when is_completed=true, cleared on false |
| created_at     | DateTime (UTC)           | NOT NULL, auto-set on create    | Immutable after creation                   |
| updated_at     | DateTime (UTC)           | NOT NULL, auto-set on change    | Updated on every modification              |
| user_id        | String                   | NOT NULL, indexed               | External user identifier from auth system  |

### Indexes

| Index Name           | Columns        | Type   | Purpose                          |
|----------------------|----------------|--------|----------------------------------|
| pk_tasks             | id             | PK     | Primary key lookup               |
| ix_tasks_user_id     | user_id        | B-tree | Fast user-scoped queries (FR-004)|

### Relationships

- **Task → User**: Many-to-one via `user_id`. No foreign key constraint —
  user is an external entity managed by Better Auth. The `user_id` column
  is a string reference, not a FK.

### State Transitions

```text
                   create
                     │
                     ▼
              ┌──────────────┐
              │ is_completed │
              │   = false    │
              └──────┬───────┘
                     │ update (is_completed=true)
                     ▼
              ┌──────────────┐
              │ is_completed │
              │   = true     │
              │ completed_at │
              │   = now()    │
              └──────┬───────┘
                     │ update (is_completed=false)
                     ▼
              ┌──────────────┐
              │ is_completed │
              │   = false    │
              │ completed_at │
              │   = null     │
              └──────────────┘
```

### Validation Rules

- `title`: Required, 1-255 characters. Empty string or null rejected (422).
- `description`: Optional. If provided, max 2000 characters (422 if exceeded).
- `is_completed`: Boolean. Non-boolean values rejected (422).
- `id`: Read-only. Client-supplied values in create requests are ignored.
- `created_at`: Read-only. Set once at creation time.
- `updated_at`: Read-only. Auto-updated on every write operation.
- `completed_at`: Read-only. Managed automatically based on `is_completed`.

### Database DDL (PostgreSQL)

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description VARCHAR(2000),
    is_completed BOOLEAN NOT NULL DEFAULT false,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    user_id VARCHAR NOT NULL
);

CREATE INDEX ix_tasks_user_id ON tasks (user_id);
```
