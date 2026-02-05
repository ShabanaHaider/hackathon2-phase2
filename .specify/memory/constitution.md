<!--
  Sync Impact Report
  ===================
  Version change: 1.0.0 → 1.1.0
  Modified principles: None
  Added principles:
    - Principle VII: Agentic AI & Tool-Oriented Architecture
    - Principle VIII: Stateless AI Interactions with Persistent Memory
  Added sections:
    - AI & MCP Constraints (Model Context Protocol, OpenAI Agents SDK)
    - Compatibility Guarantee
  Removed sections: None
  Templates requiring updates:
    - `.specify/templates/plan-template.md` — ✅ No update needed
      (generic; Constitution Check filled at plan time; new principles
      will be checked dynamically)
    - `.specify/templates/spec-template.md` — ✅ No update needed
      (generic structure compatible; AI chatbot features will use
      standard user-story format)
    - `.specify/templates/tasks-template.md` — ✅ No update needed
      (MCP tool tasks and agent tasks fit existing phase/story structure)
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

### VII. Agentic AI & Tool-Oriented Architecture

All AI behavior MUST be implemented using explicit, auditable agents and
tools. The AI model MUST NOT directly mutate application state.

- AI agents MUST operate exclusively via MCP tools.
- All task mutations MUST occur inside MCP tools backed by the database.
- Agent prompts MUST describe *intent and behavior*, never business logic.
- Tool schemas are the single source of truth for task operations.

This ensures:
- Deterministic state changes
- Auditable AI behavior
- Clear separation of reasoning vs execution

### VIII. Stateless AI Interactions with Persistent Memory

The backend server MUST remain stateless across requests, including AI
interactions.

- No in-memory conversation state may be retained between requests.
- Conversation context MUST be reconstructed from the database on every
  request.
- AI agents MUST receive full context explicitly via message history.
- System MUST remain resilient to server restarts.

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
| AI Agent SDK   | OpenAI Agents SDK           | `fastapi-backend`        |
| MCP Server     | Official MCP SDK            | `fastapi-backend`        |
| Spec-Driven    | Claude Code + Spec-Kit Plus | N/A                      |

### Authentication Flow

1. User logs in on Frontend → Better Auth creates a session and issues a JWT
2. Frontend makes API call → includes JWT in `Authorization: Bearer <token>`
3. Backend receives request → extracts token, verifies signature with shared secret
4. Backend identifies user → decodes token for user ID, email, etc.
5. Backend filters data → returns only resources belonging to that user

### AI & MCP Constraints

#### Model Context Protocol (MCP)

- MCP server MUST be implemented using the **Official MCP SDK**.
- MCP tools MUST:
  - Be stateless
  - Accept all required data as parameters
  - Persist all state changes to the database
- MCP server MUST NOT:
  - Access frontend state
  - Maintain session memory
  - Contain AI reasoning logic

#### OpenAI Agents SDK

- Agent logic MUST be implemented using OpenAI Agents SDK.
- Agents MUST:
  - Select tools based on user intent
  - Handle errors gracefully
  - Confirm actions conversationally
- Agents MUST NOT:
  - Perform direct database queries
  - Assume implicit state

### Loose Coupling Requirements

- Frontend and backend MUST communicate only via REST API; no shared
  runtime state.
- Backend and database MUST communicate only via SQLModel ORM; no raw
  SQL unless justified by an ADR.
- Frontend MUST NOT directly access the database.
- AI agents MUST interact with data exclusively through MCP tools; no
  direct database access from agent logic.
- All security-sensitive logic MUST reside in the backend and be
  verifiable and auditable.

### Compatibility Guarantee

- All Phase-2 REST APIs remain valid and unchanged.
- The AI chatbot is an **additive interface**, not a replacement.
- Manual Todo CRUD via REST MUST continue to work independently.

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
- AI agents MUST operate exclusively through MCP tools for state mutation.
- MCP tools MUST be stateless and database-backed.
- AI interactions MUST NOT retain in-memory state between requests.

### Success Criteria

- All 5 basic Todo features work for multiple users.
- Users can only access and modify their own tasks.
- All API requests require valid JWT authentication.
- Data persists correctly in PostgreSQL.
- System can be reviewed and evaluated spec-by-spec.
- AI chatbot can manage tasks via natural language through MCP tools.
- Existing REST API continues to function independently of AI chatbot.

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

**Version**: 1.1.0 | **Ratified**: 2026-01-27 | **Last Amended**: 2026-02-05
