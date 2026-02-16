# Implementation Plan: Intermediate and Advanced Todo Features

**Branch**: `009-advanced-task-features` | **Date**: 2026-02-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/009-advanced-task-features/spec.md`

## Summary

Extend the existing Task CRUD system with intermediate features (priority, tags, search, filtering, sorting) and advanced features (due dates, reminders, recurring tasks). Implementation follows Constitution v2.0.0 event-driven architecture using Dapr for Pub/Sub abstraction over Kafka.

## Technical Context

**Language/Version**: Python 3.10+ (backend), TypeScript/Node.js 18+ (frontend)
**Primary Dependencies**: FastAPI, SQLModel, Pydantic, Dapr SDK (backend); Next.js 16+, React 18+ (frontend)
**Storage**: Neon Serverless PostgreSQL (existing)
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: Linux containers (Docker/Kubernetes)
**Project Type**: Web application (frontend + backend + microservices)
**Performance Goals**: <1s response for search/filter/sort on 10,000 tasks; <30s recurring task regeneration
**Constraints**: Backward compatible with existing `/api/todos` endpoints; Dapr sidecar required
**Scale/Scope**: 100 concurrent users, 10,000 tasks per user

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Cross-Service End-to-End Correctness | ✅ PASS | Events validated across backend, Dapr, Kafka, and microservices |
| II. User Data Isolation and Security | ✅ PASS | All queries filter by user_id; events carry user context |
| III. Multi-Service Spec-Driven Development | ✅ PASS | Spec defines event schemas, Dapr components, service responsibilities |
| IV. Framework-Idiomatic Implementation | ✅ PASS | Dapr sidecar model; no direct Kafka access |
| V. RESTful API Design (Additive Only) | ✅ PASS | New fields are optional; existing endpoints unchanged |
| VI. Environment-Based Secret Management | ✅ PASS | Kafka credentials via env vars/K8s secrets |
| VII. Agentic AI & Tool-Oriented Architecture | ✅ PASS | MCP tools publish events via Dapr after mutations |
| VIII. Stateless AI Interactions | ✅ PASS | Microservices remain stateless |
| IX. Event-Driven Architecture | ✅ PASS | task-events, reminders, notifications topics defined |
| X. Cloud-Native & Deployability | ✅ PASS | Helm charts for all services |
| XI. Backward Compatibility | ✅ PASS | REST CRUD unchanged; features are additive |

## Project Structure

### Documentation (this feature)

```text
specs/009-advanced-task-features/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI specs)
│   ├── tasks-extended.yaml
│   ├── tags.yaml
│   └── events.yaml
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── main.py                    # FastAPI app (existing)
├── models.py                  # SQLModel entities (extend)
├── database.py                # DB connection (existing)
├── auth.py                    # JWT verification (existing)
├── dapr_client.py             # NEW: Dapr Pub/Sub client
├── routers/
│   ├── todos.py               # Task CRUD (extend with filtering/sorting)
│   └── tags.py                # NEW: Tag management
├── services/
│   ├── event_publisher.py     # NEW: Dapr event publishing
│   └── search_service.py      # NEW: Task search logic
└── tests/
    ├── test_todos_extended.py
    ├── test_tags.py
    └── test_events.py

services/
├── recurring-task-service/    # NEW: Microservice for recurring tasks
│   ├── main.py
│   ├── Dockerfile
│   └── dapr/
│       └── subscription.yaml
└── notification-service/      # NEW: Microservice for reminders
    ├── main.py
    ├── Dockerfile
    └── dapr/
        └── subscription.yaml

frontend/
├── src/
│   ├── components/
│   │   ├── TaskList.tsx       # Extend with filters/sort
│   │   ├── TaskItem.tsx       # Extend with priority/tags/due date
│   │   ├── TaskForm.tsx       # Extend with new fields
│   │   ├── FilterBar.tsx      # NEW: Filter controls
│   │   ├── SearchBar.tsx      # NEW: Search input
│   │   ├── TagSelector.tsx    # NEW: Tag picker
│   │   └── PriorityBadge.tsx  # NEW: Priority display
│   ├── lib/
│   │   └── api.ts             # Extend with new endpoints
│   └── types/
│       └── task.ts            # NEW: Extended task types
└── tests/

dapr/
├── components/
│   ├── pubsub-kafka.yaml      # Kafka Pub/Sub component
│   └── statestore.yaml        # State store (if needed)
└── config/
    └── config.yaml            # Dapr configuration

helm/
├── backend/
├── recurring-service/
├── notification-service/
└── kafka/
```

**Structure Decision**: Web application with microservices architecture. Extends existing `backend/` and `frontend/` structure, adds new `services/` directory for event-driven microservices, `dapr/` for Dapr component configs, and `helm/` for Kubernetes deployment charts.

## Complexity Tracking

No constitution violations. All features follow established patterns.

## Implementation Phases

### Phase 0: Research (Complete)

See [research.md](./research.md) for:
- Dapr Pub/Sub patterns for FastAPI
- SQLModel many-to-many relationships
- PostgreSQL ILIKE search performance
- Recurring task scheduling strategies

### Phase 1: Design (This Plan)

**1.1 Data Model Extensions**

See [data-model.md](./data-model.md) for complete entity definitions.

**1.2 API Contracts**

See [contracts/](./contracts/) for OpenAPI specifications.

**1.3 Event Schemas**

See [contracts/events.yaml](./contracts/events.yaml) for event definitions.

### Phase 2: Implementation (via /sp.tasks)

**Recommended Implementation Order:**

1. **Database Schema** (P1)
   - Add priority, due_at, is_recurring, recurrence_pattern to Task
   - Create Tag and TaskTag tables
   - Run migration

2. **Priority Feature** (P1)
   - Extend TaskCreate/TaskUpdate/TaskResponse models
   - Update todos router to handle priority

3. **Tags Feature** (P1)
   - Create Tag and TaskTag models
   - Create tags router
   - Implement many-to-many operations

4. **Filtering & Sorting** (P2)
   - Add query parameters to list_tasks endpoint
   - Implement filter/sort logic in SQLModel queries

5. **Search** (P2)
   - Implement ILIKE search across title, description
   - Join with tags for tag search

6. **Due Dates** (P3)
   - Add due_at field handling
   - Frontend date picker integration

7. **Event Publishing Infrastructure** (P3)
   - Set up Dapr Pub/Sub component
   - Create event publisher service
   - Publish events on task mutations

8. **Recurring Task Service** (P4)
   - Create microservice
   - Subscribe to task-completed events
   - Implement regeneration logic

9. **Reminder/Notification Service** (P3-P4)
   - Create microservice
   - Subscribe to reminder events
   - Implement notification dispatch

10. **Frontend Updates** (All phases)
    - Extend components progressively
    - Add filter/sort/search UI
    - Add tag management UI

## Architectural Decisions

### AD-1: Dapr Pub/Sub over Direct Kafka

**Decision**: Use Dapr HTTP API for all Pub/Sub operations
**Rationale**: Constitution Principle IX mandates no direct Kafka access; Dapr provides broker abstraction
**Trade-off**: Slight latency overhead vs. broker portability

### AD-2: Synchronous Tag Creation

**Decision**: Create tags inline during task save (not async)
**Rationale**: Simpler user experience; tags needed immediately for display
**Trade-off**: Slightly slower task creation vs. immediate tag availability

### AD-3: Basic Search (ILIKE)

**Decision**: Use PostgreSQL ILIKE for search
**Rationale**: Spec explicitly excludes full-text search; ILIKE sufficient for 10,000 items
**Trade-off**: No relevance scoring vs. simpler implementation

### AD-4: User-Scoped Tags

**Decision**: Tags are scoped per user (not global)
**Rationale**: Spec assumption; prevents tag namespace collision
**Trade-off**: No cross-user tag sharing vs. data isolation

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Dapr sidecar latency | Low | Medium | Local testing with Dapr; timeout configuration |
| Tag query performance | Medium | Low | Index on name column; cache popular tags |
| Recurring task duplication | Low | High | Idempotent event handling with event_id |
| Migration breaks existing data | Low | High | Backward-compatible additive columns only |

## Next Steps

1. Run `/sp.tasks` to generate task breakdown
2. Implement Phase 1 (P1 features: priority, tags)
3. Implement Phase 2 (P2 features: filtering, sorting, search)
4. Implement Phase 3 (P3 features: due dates, event infrastructure)
5. Implement Phase 4 (P4 features: recurring tasks, notifications)
