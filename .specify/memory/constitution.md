<!--
  Sync Impact Report
  ===================
  Version change: 0.0.0 (template) → 1.0.0
  Modified principles: N/A (initial population from template)
  Added sections:
    - Principle I: End-to-End Correctness
    - Principle II: User Data Isolation and Security
    - Principle III: Spec-Driven Agentic Development
    - Principle IV: Framework-Idiomatic Implementation
    - Principle V: RESTful API Design
    - Principle VI: Environment-Based Secret Management
    - Section: Technology Constraints
    - Section: Development Workflow
    - Governance rules
  Removed sections: None (all template placeholders replaced)
  Templates requiring updates:
    - `.specify/templates/plan-template.md` — ✅ No update needed (generic; Constitution Check filled at plan time)
    - `.specify/templates/spec-template.md` — ✅ No update needed (generic structure compatible)
    - `.specify/templates/tasks-template.md` — ✅ No update needed (web app path convention already present)
  Follow-up TODOs: None
-->

# Todo Full-Stack Web Application Constitution

## Core Principles

### I. End-to-End Correctness

Every feature MUST be verified across all three layers — frontend (Next.js),
backend (FastAPI), and database (Neon PostgreSQL) — before it is considered
complete. A feature that works in isolation on one layer but fails at
integration boundaries is not done.

- All API contracts MUST be validated with matching frontend calls and
  database queries.
- Data round-trips (create → read → update → delete) MUST be tested
  through the full stack.
- Type mismatches between frontend requests, backend Pydantic/SQLModel
  schemas, and database columns MUST be caught before merge.

### II. User Data Isolation and Security

All user data MUST be strictly isolated. No user may read, modify, or
delete another user's data under any circumstance.

- Every database query that returns user-owned data MUST filter by the
  authenticated user's ID.
- All protected API routes MUST validate the JWT Bearer token before
  processing any request.
- Token verification MUST use a shared secret stored exclusively in
  environment variables.
- Authorization checks MUST be enforced at the backend; frontend checks
  are supplementary, never sufficient.

### III. Spec-Driven Agentic Development

All implementation MUST originate from written specifications and plans.
No manual coding is allowed outside the Claude Code agentic workflow.

- The workflow is: Write spec → Generate plan → Break into tasks →
  Implement via Claude Code.
- Every feature MUST have a `spec.md` before a `plan.md`, and a `plan.md`
  before a `tasks.md`.
- Implementation tasks MUST reference their parent spec and plan.
- Changes not traceable to a spec are out of scope and MUST be rejected
  or formally specified first.

### IV. Framework-Idiomatic Implementation

Each technology in the stack MUST be used according to its canonical
patterns and conventions. Do not fight the framework.

- Next.js: Use App Router, server components by default, client components
  only when interactivity requires it.
- FastAPI: Use dependency injection, Pydantic models for validation,
  async endpoints where appropriate.
- SQLModel: Use SQLModel classes for both Pydantic validation and
  SQLAlchemy ORM mapping.
- Better Auth: Use its built-in session management and JWT issuance;
  do not roll custom auth logic.

### V. RESTful API Design

All API endpoints MUST follow REST conventions and be user-scoped.

- Resources MUST use plural nouns (e.g., `/api/todos`, not `/api/todo`).
- HTTP methods MUST match semantics: GET (read), POST (create),
  PUT/PATCH (update), DELETE (remove).
- All endpoints returning user-owned resources MUST scope queries to the
  authenticated user.
- Error responses MUST use standard HTTP status codes with consistent
  JSON error bodies.

### VI. Environment-Based Secret Management

All secrets, tokens, and connection strings MUST be managed via environment
variables. No secret may appear in source code, committed files, or logs.

- Database connection strings, JWT shared secrets, and API keys MUST be
  stored in `.env` files.
- `.env` files MUST be listed in `.gitignore` and never committed.
- Application code MUST read secrets from environment variables at runtime.
- Documentation MUST include a `.env.example` with placeholder values.

## Technology Constraints

The following stack is mandatory for this project. Deviations require an
ADR with explicit justification.

| Layer          | Technology                  | Agent Route              |
|----------------|-----------------------------|--------------------------|
| Frontend       | Next.js 16+ (App Router)    | `nextjs-frontend-dev`    |
| Backend        | Python FastAPI              | `fastapi-backend`        |
| ORM            | SQLModel                    | `fastapi-backend`        |
| Database       | Neon Serverless PostgreSQL  | `neon-postgres-manager`  |
| Authentication | Better Auth with JWT        | `auth-security`          |
| Spec-Driven    | Claude Code + Spec-Kit Plus | N/A                      |

### Authentication Flow

1. User logs in on Frontend → Better Auth creates a session and issues a JWT
2. Frontend makes API call → includes JWT in `Authorization: Bearer <token>`
3. Backend receives request → extracts token, verifies signature with shared secret
4. Backend identifies user → decodes token for user ID, email, etc.
5. Backend filters data → returns only resources belonging to that user

### Loose Coupling Requirements

- Frontend and backend MUST communicate only via REST API; no shared
  runtime state.
- Backend and database MUST communicate only via SQLModel ORM; no raw
  SQL unless justified by an ADR.
- Frontend MUST NOT directly access the database.
- All security-sensitive logic MUST reside in the backend and be
  verifiable and auditable.

## Development Workflow

### Agentic Dev Stack Process

1. **Specify** (`/sp.specify`): Write feature spec from user description.
2. **Plan** (`/sp.plan`): Generate architectural plan from spec.
3. **Tasks** (`/sp.tasks`): Break plan into ordered, testable tasks.
4. **Implement** (`/sp.implement`): Execute tasks via Claude Code agents.
5. **Review**: Validate against spec acceptance criteria.

### Agent Routing for Skills

- `auth-skill` → `auth-security` agent
- `frontend-skill` → `nextjs-frontend-dev` agent
- `database-skill` → `neon-postgres-manager` agent
- `backend-skill` → `fastapi-backend` agent

### Quality Gates

- All features MUST be derived from written specs and plans.
- All API endpoints MUST be RESTful and user-scoped.
- Authentication MUST be enforced via JWT on every protected route.
- Frontend, backend, and database MUST remain loosely coupled.
- All security-sensitive logic MUST be verifiable and auditable.

### Success Criteria

- All 5 basic Todo features work for multiple users.
- Users can only access and modify their own tasks.
- All API requests require valid JWT authentication.
- Data persists correctly in PostgreSQL.
- System can be reviewed and evaluated spec-by-spec.

## Governance

This constitution is the authoritative source of project principles and
constraints. All specs, plans, tasks, and implementations MUST comply.

- **Amendments**: Any change to this constitution MUST be documented with
  a rationale, approved by the project owner, and versioned.
- **Versioning**: Follows semantic versioning — MAJOR for principle
  removals or redefinitions, MINOR for additions or material expansions,
  PATCH for clarifications and wording fixes.
- **Compliance**: Every PR and code review MUST verify alignment with
  these principles. Violations MUST be resolved before merge.
- **ADRs**: Architecturally significant decisions MUST be documented via
  `/sp.adr` with explicit tradeoff analysis.
- **Runtime Guidance**: See `CLAUDE.md` for agent-specific development
  guidance and tool routing.

**Version**: 1.0.0 | **Ratified**: 2026-01-27 | **Last Amended**: 2026-01-27
