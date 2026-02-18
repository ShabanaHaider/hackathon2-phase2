# Implementation Plan: Minikube Dapr Deployment

**Branch**: `010-minikube-dapr-deployment` | **Date**: 2026-02-17 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/010-minikube-dapr-deployment/spec.md`

## Summary

Deploy the Phase-V application (backend, frontend, notification-service, recurring-task-service) to a local Minikube cluster in the `phase-v` namespace with full Dapr support. This includes 5 Dapr building blocks: Pub/Sub (Redis, with Kafka upgrade path), State Store (Redis), Cron Binding, Kubernetes Secrets Store, and Service Invocation. The deployment must preserve all 009-advanced-task-features functionality and use Python 3.12 for backend services.

## Technical Context

**Language/Version**: Python 3.12 (backend, microservices), Node.js 20 (frontend)
**Primary Dependencies**: Dapr 1.16.9, Helm v3.20.0, Redis 7, Minikube (Docker driver, WSL2)
**Storage**: Neon Serverless PostgreSQL (external), Redis (in-cluster state store)
**Testing**: Manual validation via frontend UI, kubectl pod status, Dapr dashboard, service logs
**Target Platform**: Minikube on WSL2 (Linux 6.6.87.2-microsoft-standard-WSL2)
**Project Type**: Multi-service web application (Kubernetes deployment)
**Performance Goals**: All pods Running within 5 minutes, Pub/Sub event delivery within 10 seconds
**Constraints**: Limited WSL2 memory — use Redis instead of Kafka for local dev
**Scale/Scope**: 4 application services + 1 Redis instance + 4 Dapr components in single namespace

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Cross-Service End-to-End Correctness | PASS | Deployment validates full event flow: backend → Dapr Pub/Sub → microservices |
| II. User Data Isolation | PASS | JWT auth unchanged. Secrets in Kubernetes Secrets, not plaintext. |
| III. Multi-Service Spec-Driven Development | PASS | Spec → Plan → Tasks workflow followed. Event schemas from 009 contracts reused. |
| IV. Framework-Idiomatic Implementation | PASS | Dapr sidecar model used idiomatically. No direct broker client libraries. |
| V. RESTful API Design (Additive Only) | PASS | No API changes. Existing endpoints preserved. |
| VI. Environment-Based Secret Management | PASS | Secrets via Kubernetes Secrets + Dapr Secrets API. No hardcoded values. |
| VII. Agentic AI & Tool-Oriented Architecture | PASS | MCP server unchanged. Events published via Dapr HTTP API. |
| VIII. Stateless AI Interactions | PASS | All services remain stateless. State store provides persistence externally. |
| IX. Event-Driven Architecture | PASS | Pub/Sub via Dapr. Topics: task-events, reminders, notifications. |
| X. Cloud-Native & Deployability | PASS | All services containerized with Helm charts. Health checks present. |
| XI. Backward Compatibility | PASS | Zero code changes to existing services. Infrastructure-only additions. |

**Post-Phase 1 Re-check**: All gates PASS. The plan uses Redis instead of Kafka for local dev — this is a Dapr component-level change (not a code change), consistent with Principle IV (Kafka-agnostic via Dapr abstraction).

## Architecture Overview

### Deployment Topology

```
┌─────────────────────────────── Minikube Cluster ───────────────────────────────┐
│                              namespace: phase-v                                │
│                                                                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────────┐ │
│  │ Dapr Control Plane│  │     Redis        │  │    Kubernetes Secrets        │ │
│  │ (operator,sentry, │  │  (Pub/Sub +      │  │    (app-secrets)             │ │
│  │  injector,etc.)   │  │   State Store)   │  │                              │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────────────────┘ │
│                                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   backend    │  │   frontend   │  │ notification │  │  recurring   │      │
│  │  (FastAPI)   │  │  (Next.js)   │  │   service    │  │   service    │      │
│  │  Port: 8000  │  │  Port: 3000  │  │  Port: 8001  │  │  Port: 8002  │      │
│  │  ┌────────┐  │  │              │  │  ┌────────┐  │  │  ┌────────┐  │      │
│  │  │ Dapr   │  │  │  (no Dapr)   │  │  │ Dapr   │  │  │  │ Dapr   │  │      │
│  │  │sidecar │  │  │              │  │  │sidecar │  │  │  │sidecar │  │      │
│  │  └────────┘  │  │              │  │  └────────┘  │  │  └────────┘  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                                    ▲                ▲               │
│         │          Dapr Pub/Sub (Redis)       │                │               │
│         └────────── task-events ─────────────┼────────────────┘               │
│         └────────── reminders ───────────────┘                                │
│                                                                                │
│  ┌────────────────────────┐    ┌────────────────────────┐                     │
│  │  Dapr Cron Binding     │───▶│  recurring-task-service │                     │
│  │  (@every 5m)           │    │  /cron-check-overdue    │                     │
│  └────────────────────────┘    └────────────────────────┘                     │
│                                                                                │
└──────────────────────────── External: Neon PostgreSQL ─────────────────────────┘
```

### Event Flow

```
User Action (Frontend) → Backend API → Dapr Sidecar → Redis Pub/Sub → Dapr Sidecar → Microservice

1. Task Created:  backend → task-events topic → recurring-task-service (no action unless recurring)
2. Task Completed: backend → task-events topic → recurring-task-service (creates next if recurring)
3. Reminder Due:   backend → reminders topic → notification-service (logs/processes reminder)
4. Cron Tick:      Dapr cron → recurring-task-service /cron-check-overdue (check for overdue tasks)
```

### Service Invocation Flow

```
recurring-task-service → Dapr sidecar (localhost:3500) → /v1.0/invoke/backend/method/api/todos → backend
```

## Implementation Phases

### Phase 1: Infrastructure Setup (Redis + Dapr Components)

**Goal**: Deploy Redis and all Dapr components in `phase-v` namespace.

**Tasks**:
1. Create Redis deployment and service YAML manifests
2. Create Dapr Pub/Sub component (pubsub-redis) YAML
3. Create Dapr State Store component (statestore) YAML
4. Create Dapr Secrets Store component (secretstores.kubernetes) YAML
5. Create Dapr Cron Binding component YAML
6. Create Kubernetes Secret (`app-secrets`) with actual credentials
7. Apply all resources to `phase-v` namespace
8. Verify Redis pod Running, all Dapr components registered

**Files to create/modify**:
- `dapr/components/redis-deployment.yaml` (NEW)
- `dapr/components/pubsub-redis.yaml` (NEW)
- `dapr/components/statestore-redis.yaml` (NEW)
- `dapr/components/secretstore-kubernetes.yaml` (NEW)
- `dapr/components/cron-check-overdue.yaml` (NEW)

### Phase 2: Docker Image Builds

**Goal**: Build all 4 application Docker images in Minikube's Docker daemon.

**Tasks**:
1. Switch to Minikube Docker env (`eval $(minikube docker-env)`)
2. Build backend image (todo-backend:latest)
3. Build frontend image (todo-frontend:latest) with NEXT_PUBLIC_API_URL build arg
4. Build notification-service image
5. Build recurring-task-service image
6. Verify all images present (`docker images | grep todo`)

**Prerequisite**: Phase 1 (infrastructure must be ready)

### Phase 3: Helm Chart Updates + Frontend Chart

**Goal**: Update existing Helm charts and create missing frontend chart.

**Tasks**:
1. Create `helm/frontend/` chart (Chart.yaml, values.yaml, templates/deployment.yaml, templates/service.yaml)
2. Update backend Helm values: change PUBSUB_NAME to `pubsub-redis`, add DATABASE_URL secret ref
3. Update notification-service Helm values: change PUBSUB_NAME to `pubsub-redis`
4. Update recurring-service Helm values: change PUBSUB_NAME to `pubsub-redis`, set BACKEND_URL to `http://backend:8000`
5. Update subscription YAMLs: ensure pubsubname matches `pubsub-redis`
6. Add environment variable injection from Kubernetes Secrets in backend deployment template

**Files to create/modify**:
- `helm/frontend/Chart.yaml` (NEW)
- `helm/frontend/values.yaml` (NEW)
- `helm/frontend/templates/deployment.yaml` (NEW)
- `helm/frontend/templates/service.yaml` (NEW)
- `helm/backend/values.yaml` (MODIFY)
- `helm/backend/templates/deployment.yaml` (MODIFY)
- `helm/notification-service/values.yaml` (MODIFY)
- `helm/recurring-service/values.yaml` (MODIFY)
- `services/notification-service/dapr/subscription.yaml` (MODIFY — pubsubname)
- `services/recurring-task-service/dapr/subscription.yaml` (MODIFY — pubsubname)

### Phase 4: Deploy Application Services

**Goal**: Install all Helm charts and verify pods are Running.

**Tasks**:
1. Apply Dapr subscription CRDs to namespace
2. Install backend Helm release
3. Install frontend Helm release
4. Install notification-service Helm release
5. Install recurring-task-service Helm release
6. Wait for all pods to reach Running state (backend 2/2, frontend 1/1, notification 2/2, recurring 2/2)
7. Verify Dapr sidecar injection via pod annotations

### Phase 5: Validation & End-to-End Testing

**Goal**: Verify all Dapr building blocks and application features work.

**Tasks**:
1. Port-forward frontend (3000) and backend (8000)
2. Verify frontend loads and connects to backend
3. Create a task via frontend UI — verify backend publishes event to Pub/Sub
4. Complete a recurring task — verify recurring-task-service creates next occurrence
5. Verify Dapr state store: save/retrieve state from notification-service
6. Verify cron binding triggers recurring-task-service endpoint (check logs)
7. Verify secrets are accessible via Dapr Secrets API (backend retrieves DATABASE_URL)
8. Verify service invocation: recurring-task-service → backend via Dapr
9. Run full regression: priority, tags, due dates, search, filter, sort all working
10. Check Dapr dashboard for component health

### Phase 6: Documentation & Cleanup

**Goal**: Finalize deployment documentation and deployment scripts.

**Tasks**:
1. Create a deployment script (`scripts/deploy-minikube.sh`) that automates steps 1-7 from quickstart
2. Update quickstart.md with any adjustments from actual deployment
3. Document Kafka upgrade path
4. Update MEMORY.md with deployment state

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Pub/Sub Broker | Redis (primary), Kafka (upgrade path) | Redis uses 128MB vs Kafka 1.5GB. WSL2 resource constraints. |
| State Store | Redis | Same instance as Pub/Sub, minimizes resource usage |
| Secrets Store | Kubernetes Secrets | Native, no extra infrastructure needed |
| Frontend Dapr | No sidecar | Frontend doesn't use Dapr directly (no pub/sub, no state, no secrets at runtime) |
| Image Registry | Local Minikube Docker daemon | `eval $(minikube docker-env)` avoids registry setup |
| Subscription Model | Declarative CRDs | Already implemented in 009, Kubernetes-native |

## Project Structure

### Documentation (this feature)

```text
specs/010-minikube-dapr-deployment/
├── plan.md              # This file
├── research.md          # Phase 0: broker choice, state store, secrets research
├── data-model.md        # Kubernetes & Dapr resource models
├── quickstart.md        # Step-by-step deployment guide
├── contracts/
│   ├── dapr-components.yaml    # Dapr component definitions
│   └── kubernetes-resources.yaml  # Redis, secrets resource definitions
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/                        # FastAPI backend (unchanged code, new Helm config)
├── Dockerfile
├── main.py
├── models.py
├── services/event_publisher.py
└── routers/

frontend/                       # Next.js frontend (unchanged code, new Helm chart)
├── Dockerfile
└── src/

services/
├── notification-service/       # Notification microservice
│   ├── Dockerfile
│   ├── main.py
│   └── dapr/subscription.yaml  # MODIFY: pubsubname → pubsub-redis
└── recurring-task-service/     # Recurring task microservice
    ├── Dockerfile
    ├── main.py
    └── dapr/subscription.yaml  # MODIFY: pubsubname → pubsub-redis

helm/
├── backend/                    # MODIFY: secret refs, PUBSUB_NAME
├── frontend/                   # NEW: frontend Helm chart
├── notification-service/       # MODIFY: PUBSUB_NAME
├── recurring-service/          # MODIFY: PUBSUB_NAME, BACKEND_URL
└── kafka/                      # EXISTING: for Kafka upgrade path

dapr/
└── components/
    ├── pubsub-kafka.yaml       # EXISTING: for Kafka upgrade path
    ├── pubsub-redis.yaml       # NEW: Redis Pub/Sub component
    ├── statestore-redis.yaml   # NEW: Redis State Store component
    ├── secretstore-kubernetes.yaml  # NEW: Kubernetes Secrets component
    ├── cron-check-overdue.yaml # NEW: Cron binding for overdue checks
    └── redis-deployment.yaml   # NEW: Redis Deployment + Service

scripts/
└── deploy-minikube.sh          # NEW: Automated deployment script
```

**Structure Decision**: Existing multi-service web application structure preserved. This feature adds infrastructure configuration (Dapr components, Helm charts, K8s manifests) without modifying application code. The only code-level changes are subscription YAML `pubsubname` field updates.

## Complexity Tracking

> No constitution violations. All gates pass.

## Risks

1. **WSL2 memory pressure**: Redis + 4 app pods + Dapr control plane (~8 pods) may strain limited memory. Mitigation: resource limits set in Helm values; Redis is lightweight (~128MB).
2. **Neon database connectivity from Minikube**: External HTTPS calls from pods depend on Minikube's network configuration. Mitigation: test connectivity early in Phase 4; fallback is `minikube tunnel`.
3. **Frontend NEXT_PUBLIC_API_URL timing**: Build-time env var must point to port-forwarded backend URL. If port changes, image must be rebuilt. Mitigation: document clearly in quickstart.
