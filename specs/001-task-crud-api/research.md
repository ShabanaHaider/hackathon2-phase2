# Research: Task CRUD API

**Feature Branch**: `001-task-crud-api`
**Date**: 2026-01-27

## R1: Primary Key Strategy — UUID vs Integer

**Decision**: UUID v4 as primary key for tasks; string user_id referencing
the external auth system.

**Rationale**: UUIDs prevent enumeration attacks (users cannot guess task IDs
by incrementing). They are generated client-independently, avoiding sequences
that leak information. The spec explicitly states "system-generated UUIDs."

**Alternatives considered**:
- Auto-increment integer: simpler, faster index lookups, but exposes
  ordering and enables enumeration. Rejected per security-by-default
  constitution principle.
- ULID/UUIDv7: time-ordered, good for range queries. Unnecessary complexity
  for this scope — no requirement for time-ordered IDs.

## R2: Task-to-User Relationship Design

**Decision**: The `tasks` table has a `user_id` column (string) that stores
the external user identifier. No foreign key to a local users table — the
user is an external entity managed by Better Auth.

**Rationale**: This feature explicitly excludes authentication. The user_id
is accepted as a trusted input parameter. Creating a local users table would
couple this feature to auth, violating the loose coupling constitution
principle and the spec scope.

**Alternatives considered**:
- Local users table with FK: provides referential integrity but requires
  syncing with Better Auth. Out of scope for this feature.
- Embedded user object: violates normalization. Rejected.

## R3: PATCH vs PUT Semantics for Updates

**Decision**: Use PATCH for partial updates. Clients send only the fields
they want to change.

**Rationale**: PATCH is idiomatic for partial updates in REST APIs. The spec
says users can update "title, description, or completion status" — implying
selective field updates, not full replacement. PUT would require clients to
send all fields, increasing payload size and error risk.

**Alternatives considered**:
- PUT (full replacement): simpler semantics but forces clients to resend
  unchanged fields. Risk of accidental data loss if a field is omitted.
  Rejected.
- Both PUT and PATCH: over-engineering for this scope. Rejected.

## R4: Handling Missing or Invalid Task IDs

**Decision**: Return 404 Not Found for both non-existent task IDs and
task IDs belonging to another user. Never return 403 Forbidden.

**Rationale**: Returning 404 for "exists but not yours" prevents information
leakage — an attacker cannot determine whether a task ID exists by
distinguishing 403 from 404. This aligns with the user data isolation
constitution principle.

**Alternatives considered**:
- 403 Forbidden for "not yours": reveals that the ID exists. Rejected per
  security-by-default principle.
- 400 Bad Request for invalid UUID format: acceptable as a separate case.
  Malformed UUIDs will return 422 from Pydantic validation.

## R5: SQLModel with Neon Serverless PostgreSQL

**Decision**: Use SQLModel with async SQLAlchemy engine via `asyncpg` driver
connecting to Neon's connection pooler endpoint.

**Rationale**: FastAPI is async-native; using async database access avoids
blocking the event loop. Neon provides a connection pooler URL specifically
for serverless environments. SQLModel wraps SQLAlchemy and Pydantic, matching
the constitution's framework-idiomatic requirement.

**Alternatives considered**:
- Sync `psycopg2`: blocks event loop in async FastAPI. Rejected.
- Raw asyncpg without ORM: loses Pydantic integration and type safety.
  Rejected per constitution (SQLModel is mandatory).

## R6: Timestamp Handling

**Decision**: Use `datetime` fields with UTC timezone. The database stores
`TIMESTAMP WITH TIME ZONE`. The API returns ISO 8601 strings.

**Rationale**: The spec requires ISO 8601 UTC timestamps. PostgreSQL
`TIMESTAMPTZ` stores the absolute instant. SQLModel/Pydantic serializes
`datetime` to ISO 8601 by default.

**Alternatives considered**:
- Unix epoch integers: compact but less readable. Spec requires ISO 8601.
- String storage: loses database-level time operations. Rejected.

## R7: Error Response Format

**Decision**: Use a consistent JSON error body:
`{"detail": "Human-readable message"}` for single errors, and
FastAPI's default 422 body for validation errors which includes field-level
detail.

**Rationale**: FastAPI generates 422 responses with structured field errors
automatically via Pydantic. For 404 and 500 errors, a simple `detail` field
is idiomatic FastAPI and consistent with its built-in exception handlers.

**Alternatives considered**:
- RFC 7807 Problem Details: more structured but over-engineered for this
  scope. Could be added later without breaking changes.
- Custom error schema: unnecessary complexity.
