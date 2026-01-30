# Data Model: Authentication & JWT Security Integration

**Feature**: `002-auth-jwt-security`
**Date**: 2026-01-28

## Entities

### User Account (managed by Better Auth)

Better Auth manages its own database tables for users and sessions. These
are created via `npx @better-auth/cli migrate`. The backend does NOT manage
user tables directly.

Better Auth creates these tables (in the same Neon PostgreSQL database):

| Table | Key Fields |
|-------|------------|
| `user` | `id` (string, PK), `email` (unique), `name`, `createdAt`, `updatedAt` |
| `session` | `id` (PK), `userId` (FK → user), `token`, `expiresAt` |
| `account` | `id` (PK), `userId` (FK → user), `providerId`, `password` (hashed) |
| `verification` | `id` (PK), `identifier`, `value`, `expiresAt` |
| `jwks` | `id` (PK), `publicKey`, `privateKey`, `createdAt` |

### JWT Token (issued by Better Auth, verified by backend)

Not stored in backend database. Stateless, self-contained.

| Claim | Type | Description |
|-------|------|-------------|
| `sub` | string | User ID (maps to `user.id` in Better Auth, and `tasks.user_id` in backend) |
| `email` | string | User's email address |
| `iat` | number | Issued-at timestamp (Unix epoch) |
| `exp` | number | Expiration timestamp (Unix epoch, default 15 min after iat) |
| `iss` | string | Issuer URL (the frontend/auth server URL) |
| `aud` | string | Audience (the frontend/auth server URL) |

### Task (existing, from feature 001)

No schema changes. The `user_id` field on the `tasks` table stores the
Better Auth user ID (`user.id`). No foreign key constraint since the
backend database does not own the `user` table — Better Auth does.

## Relationships

```
Better Auth user.id  ──────────>  tasks.user_id (string, indexed)
       │
       ├── session (1:many, managed by Better Auth)
       ├── account (1:many, password stored here)
       └── jwks (system-level, key pairs for JWT signing)
```

## Index Requirements

No new indexes needed. The existing `tasks.user_id` index supports
the query pattern `WHERE user_id = <authenticated_user_id>`.
