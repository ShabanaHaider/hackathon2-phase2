<!--
  Sync Impact Report
  ===================
  Version change: 1.1.0 → 2.0.0

  Modified principles:
    - Principle I: End-to-End Correctness → Cross-Service End-to-End Correctness
      (Expanded to include Dapr, Kafka, and dependent microservices validation)
    - Principle III: Spec-Driven Agentic Development → Multi-Service Spec-Driven Development
      (Expanded to require event schema definitions and service responsibility specs)
    - Principle VII: Agentic AI & Tool-Oriented Architecture
      (Expanded: MCP tools MUST publish events via Dapr after state mutation)
    - Principle VIII: Stateless AI Interactions with Persistent Memory
      (Extended to microservices; event consumers derive state from DB/payload)

  Added principles:
    - Principle IX: Event-Driven Architecture & Pub/Sub Discipline
    - Principle X: Cloud-Native & Deployability Requirements
    - Principle XI: Backward Compatibility & Additive Evolution

  Added sections:
    - Advanced Todo Domain Rules (Intermediate + Advanced features)
    - Microservices Architecture Rules
    - Dapr Abstraction Requirements
    - Kafka Integration Policy
    - CI/CD & Cloud Governance (within Governance section)

  Removed sections: None

  Templates requiring updates:
    - `.specify/templates/plan-template.md` — ✅ No update needed
      (generic; Constitution Check filled at plan time; new principles
      will be checked dynamically including event-driven requirements)
    - `.specify/templates/spec-template.md` — ✅ No update needed
      (generic structure compatible; event schemas and Dapr specs
      will be added as needed per feature)
    - `.specify/templates/tasks-template.md` — ✅ No update needed
      (MCP tool tasks, event publishing tasks, and microservice tasks
      fit existing phase/story structure)

  Follow-up TODOs: None
-->

# Todo Full-Stack Web Application Constitution

## Core Principles

### I. Cross-Service End-to-End Correctness

A feature is complete only when it functions correctly across all layers:

- Frontend (Next.js)
- Backend API (FastAPI)
- Database (PostgreSQL)
- Dapr Sidecar
- Event Bus (Kafka)
- Dependent Microservices

For Phase V:

- Event publishing MUST be verified.
- Event consumption MUST be validated.
- Recurring tasks MUST regenerate correctly.
- Reminder scheduling MUST trigger reliably.
- No silent event failures are allowed.

All API contracts MUST be validated with matching frontend calls, database
queries, and event publications. Data round-trips (create → read → update →
delete) MUST be tested through the full stack including event propagation.
Type mismatches between frontend requests, backend Pydantic/SQLModel schemas,
database columns, and event payloads MUST be caught before merge.

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

Extended to microservices:

- Every microservice MUST validate JWT where required.
- Events MUST carry user context explicitly.
- Services MUST NOT trust upstream payloads without validation.
- No cross-user event processing permitted.

### III. Multi-Service Spec-Driven Development

All implementation MUST originate from written specifications and plans.
No manual coding is allowed outside the Claude Code agentic workflow.

- The workflow is: Write spec → Generate plan → Break into tasks →
  Implement via Claude Code.
- Every feature MUST have a `spec.md` before a `plan.md`, and a `plan.md`
  before a `tasks.md`.
- Implementation tasks MUST reference their parent spec and plan.
- Changes not traceable to a spec are out of scope and MUST be rejected
  or formally specified first.

Phase V requires spec discipline across services. Every feature MUST include:

- Feature spec
- Event schema definition
- Dapr component spec
- Service responsibility spec

No microservice may be created without:

- Explicit contract
- Defined topic subscriptions
- Failure handling behavior

All logic MUST remain traceable to a spec.

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

Existing rules remain, plus:

- Dapr MUST be used idiomatically (sidecar model).
- Kafka MUST NOT be accessed directly from application services.
- Pub/Sub MUST go through Dapr HTTP/gRPC APIs only.
- No raw Kafka client libraries allowed in app services.

### V. RESTful API Design (Additive Only)

All API endpoints MUST follow REST conventions and be user-scoped.

- Resources MUST use plural nouns (e.g., `/api/todos`, not `/api/todo`).
- HTTP methods MUST match semantics: GET (read), POST (create),
  PUT/PATCH (update), DELETE (remove).
- All endpoints returning user-owned resources MUST scope queries to the
  authenticated user.
- Error responses MUST use standard HTTP status codes with consistent
  JSON error bodies.

Phase V expands capabilities but MUST NOT break:

- Existing `/api/todos` endpoints
- Authentication model
- JWT verification logic

All new fields (priority, due_at, recurrence, tags) MUST be additive.
No breaking changes allowed.

### VI. Environment-Based Secret Management

All secrets, tokens, and connection strings MUST be managed via environment
variables. No secret may appear in source code, committed files, or logs.

- Database connection strings, JWT shared secrets, and API keys MUST be
  stored in `.env` files.
- `.env` files MUST be listed in `.gitignore` and never committed.
- Application code MUST read secrets from environment variables at runtime.
- Documentation MUST include a `.env.example` with placeholder values.

Extended to include:

- Kafka broker credentials
- Dapr component configs
- Cloud deployment secrets
- CI/CD secrets

Secrets MUST be injected via environment variables or Kubernetes secrets.

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

Expanded for event-driven architecture:

- Agents MUST publish events when task mutations occur.
- Agents MUST remain unaware of Kafka directly.
- Agents operate strictly through MCP tools.
- MCP tools MUST publish events via Dapr after state mutation.

### VIII. Stateless AI Interactions with Persistent Memory

The backend server MUST remain stateless across requests, including AI
interactions.

- No in-memory conversation state may be retained between requests.
- Conversation context MUST be reconstructed from the database on every
  request.
- AI agents MUST receive full context explicitly via message history.
- System MUST remain resilient to server restarts.

Now extended:

- AI agents MUST remain stateless.
- Microservices MUST remain stateless.
- Event consumers MUST derive all state from database or event payload.
- System MUST tolerate pod restarts without data loss.

### IX. Event-Driven Architecture & Pub/Sub Discipline

Phase V introduces event-driven architecture.

Mandatory Rules:

- All cross-service communication MUST occur via Pub/Sub.
- Direct HTTP calls between microservices are discouraged.
- Events MUST follow versioned schemas.

Each topic MUST have:

- Defined producer
- Defined consumers
- Defined schema

Event payload MUST include:

- `event_id`
- `event_type`
- `user_id`
- `timestamp`
- `version`

Core Topics:

- `task-events`
- `reminders`
- `notifications`

No undocumented topic may exist.

### X. Cloud-Native & Deployability Requirements

All services MUST:

- Be containerized
- Be independently deployable
- Support horizontal scaling
- Have health checks
- Be Kubernetes-compatible

Dapr MUST be enabled per service.

Helm charts MUST exist for:

- Backend
- Recurring Service
- Notification Service
- Kafka
- Dapr components

CI/CD MUST:

- Run tests
- Build images
- Push to registry
- Deploy via pipeline

### XI. Backward Compatibility & Additive Evolution

Phase V MUST NOT break Phase IV.

- REST CRUD operations remain functional.
- AI chatbot remains additive.
- Event system enhances — does not replace — CRUD.
- Database migrations MUST be backward compatible.

## Advanced Todo Domain Rules

Phase V introduces intermediate and advanced features.

### Intermediate Features

- **Priority**: `low | medium | high`
- **Tags**: many-to-many relationship
- **Search**: title, description, tags
- **Filtering**
- **Sorting**

### Advanced Features

- **due_at**: UTC datetime
- **is_recurring**: boolean flag
- **recurrence_pattern**: cron or human-readable pattern
- **Reminder scheduling**: via Dapr Jobs or events
- **Recurring regeneration**: on completion

All advanced features MUST:

- Be optional
- Preserve existing task schema compatibility
- Emit events on mutation

## Microservices Architecture Rules

Phase V services:

- Core Backend Service
- Recurring Task Service
- Notification Service

Rules:

- Each service has single responsibility.
- No shared database session across services.
- Communication via Pub/Sub only.
- Each service MUST validate incoming event schema.

## Dapr Abstraction Requirements

Dapr is the mandatory abstraction layer.

Services MUST:

- Publish via Dapr PubSub API
- Subscribe via Dapr topic subscription
- Use Dapr State Store abstraction
- Retrieve secrets via Dapr secrets API (in Kubernetes)

Direct Kafka client usage is prohibited.

## Kafka Integration Policy

Kafka is infrastructure, not application logic.

- Kafka config lives in Dapr component YAML.
- Application services MUST remain Kafka-agnostic.
- Switching Kafka → Redpanda → Cloud PubSub MUST require no code changes.

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
| Event Bus      | Apache Kafka (via Dapr)     | `fastapi-backend`        |
| Runtime        | Dapr                        | `fastapi-backend`        |
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
  - Publish events via Dapr after state mutation
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
  - Access Kafka directly

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
- Microservices MUST communicate only via Dapr Pub/Sub; no direct HTTP
  calls between services.

### Compatibility Guarantee

- All Phase-2 REST APIs remain valid and unchanged.
- The AI chatbot is an **additive interface**, not a replacement.
- Manual Todo CRUD via REST MUST continue to work independently.
- Event-driven features enhance but do not replace existing functionality.

## Development Workflow

### Agentic Dev Stack Process (Phase V Expanded)

1. **Specify** (`/sp.specify`): Write feature spec from user description.
2. **Plan** (`/sp.plan`): Generate architectural plan from spec.
3. **Tasks** (`/sp.tasks`): Break plan into ordered, testable tasks.
4. **Implement** (`/sp.implement`): Execute tasks via Claude Code agents.
5. **Integration Test**: Multi-service validation.
6. **Event Validation**: Verify event publishing and consumption.
7. **Cloud Deploy Validation**: Confirm deployment success.

No direct coding outside this flow.

### Agent Routing for Skills

- `auth-skill` → `auth-security` agent
- `frontend-skill` → `nextjs-frontend-dev` agent
- `database-skill` → `neon-postgres-manager` agent
- `backend-skill` → `fastapi-backend` agent

### Quality Gates (Expanded)

Before merge:

- All features MUST be derived from written specs and plans.
- All API endpoints MUST be RESTful and user-scoped.
- Authentication MUST be enforced via JWT on every protected route.
- Frontend, backend, and database MUST remain loosely coupled.
- All security-sensitive logic MUST be verifiable and auditable.
- AI agents MUST operate exclusively through MCP tools for state mutation.
- MCP tools MUST be stateless and database-backed.
- AI interactions MUST NOT retain in-memory state between requests.
- REST endpoints verified.
- Event publishing verified.
- Event consumption verified.
- Recurring logic verified.
- No direct Kafka imports.
- All services stateless.
- All specs traceable.

### Success Criteria (Phase V)

System MUST demonstrate:

- All 5 basic Todo features work for multiple users.
- Users can only access and modify their own tasks.
- All API requests require valid JWT authentication.
- Data persists correctly in PostgreSQL.
- System can be reviewed and evaluated spec-by-spec.
- AI chatbot can manage tasks via natural language through MCP tools.
- Existing REST API continues to function independently of AI chatbot.
- Advanced task features working (priority, due_at, tags, recurrence).
- Recurring tasks auto-generated on completion.
- Reminder events triggered reliably.
- Notifications processed by notification service.
- Event-driven architecture functioning correctly.
- Services independently scalable.
- Full cloud deploy success.

## Governance

This constitution is the authoritative source of project principles and
constraints. All specs, plans, tasks, and implementations MUST comply.

- **Amendments**: Any change to this constitution MUST be documented with
  a rationale, approved by the project owner, and versioned.
- **Versioning**: Follows semantic versioning — MAJOR for principle
  removals or redefinitions (including architectural shifts), MINOR for
  additions or material expansions, PATCH for clarifications and wording
  fixes.
- **Compliance**: Every PR and code review MUST verify alignment with
  these principles. Violations MUST be resolved before merge.
- **ADRs**: Architecturally significant decisions MUST be documented via
  `/sp.adr` with explicit tradeoff analysis. ADR required for deviations
  from Dapr abstraction.
- **Runtime Guidance**: See `CLAUDE.md` for agent-specific development
  guidance and tool routing.
- **CI/CD & Cloud Governance**: All amendments require documented rationale.
  All services MUST remain spec-traceable.

**Version**: 2.0.0 | **Ratified**: 2026-01-27 | **Last Amended**: 2026-02-13
