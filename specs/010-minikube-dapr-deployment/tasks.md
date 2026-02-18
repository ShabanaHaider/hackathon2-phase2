# Tasks: Minikube Dapr Deployment

**Input**: Design documents from `/specs/010-minikube-dapr-deployment/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: No automated tests — validation is manual (kubectl, Dapr dashboard, frontend UI, service logs).

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Infrastructure**: `dapr/components/`, `helm/`, `scripts/`
- **Services**: `services/notification-service/`, `services/recurring-task-service/`
- **Application**: `backend/`, `frontend/` (no code changes — infrastructure only)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Deploy Redis and create all Dapr component YAMLs that multiple user stories depend on.

- [x] T001 [P] Create Redis deployment and service manifest in dapr/components/redis-deployment.yaml
- [x] T002 [P] Create Dapr Pub/Sub component (pubsub-redis) in dapr/components/pubsub-redis.yaml
- [x] T003 [P] Create Dapr State Store component (statestore) in dapr/components/statestore-redis.yaml
- [x] T004 [P] Create Dapr Secrets Store component (secretstores.kubernetes) in dapr/components/secretstore-kubernetes.yaml
- [x] T005 [P] Create Dapr Cron Binding component in dapr/components/cron-check-overdue.yaml
- [x] T006 Create Kubernetes Secret (app-secrets) with DATABASE_URL, BETTER_AUTH_SECRET, BETTER_AUTH_URL, CORS_ORIGINS in phase-v namespace
- [x] T007 Apply Redis deployment to phase-v namespace and verify pod Running (kubectl apply + kubectl get pods)
- [x] T008 Apply all Dapr components to phase-v namespace and verify registration (kubectl apply + dapr components -k)

**Checkpoint**: Redis running, all 4 Dapr components registered. Infrastructure ready for application deployment.

---

## Phase 2: Foundational (Docker Images + Helm Charts)

**Purpose**: Build Docker images and prepare Helm charts. MUST complete before any user story deployment.

**CRITICAL**: No user story work can begin until this phase is complete.

### Docker Image Builds

- [x] T009 Switch to Minikube Docker environment (eval $(minikube docker-env)) and verify connection
- [x] T010 [P] Build backend Docker image (todo-backend:latest) from backend/Dockerfile
- [x] T011 [P] Build frontend Docker image (todo-frontend:latest) from frontend/Dockerfile with --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000
- [x] T012 [P] Build notification-service Docker image from services/notification-service/Dockerfile
- [x] T013 [P] Build recurring-task-service Docker image from services/recurring-task-service/Dockerfile
- [x] T014 Verify all 4 images present in Minikube Docker daemon (docker images | grep -E "todo|notification|recurring")

### Helm Chart Creation & Updates

- [x] T015 [P] Create frontend Helm chart: helm/frontend/Chart.yaml (name: todo-frontend, version: 0.1.0, appVersion: 1.0.0)
- [x] T016 [P] Create frontend Helm values: helm/frontend/values.yaml (image: todo-frontend:latest, port: 3000, no Dapr sidecar, env vars for NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET from secret, DATABASE_URL from secret)
- [x] T017 [P] Create frontend deployment template: helm/frontend/templates/deployment.yaml (no Dapr annotations, secret env refs, port 3000)
- [x] T018 [P] Create frontend service template: helm/frontend/templates/service.yaml (ClusterIP, port 3000)
- [x] T019 Update backend Helm values: change PUBSUB_NAME to pubsub-kafka, add secret refs for DATABASE_URL in helm/backend/values.yaml
- [x] T020 Update backend deployment template: add envFrom/secretKeyRef for DATABASE_URL, BETTER_AUTH_URL, CORS_ORIGINS from app-secrets in helm/backend/templates/deployment.yaml
- [x] T021 [P] Update notification-service Helm values: change PUBSUB_NAME to pubsub-kafka in helm/notification-service/values.yaml
- [x] T022 [P] Update recurring-service Helm values: change PUBSUB_NAME to pubsub-kafka, verify BACKEND_URL is http://backend:8000 in helm/recurring-service/values.yaml
- [x] T023 [P] Update notification-service Dapr subscription: change pubsubname to pubsub-kafka in services/notification-service/dapr/subscription.yaml
- [x] T024 [P] Update recurring-task-service Dapr subscription: change pubsubname to pubsub-kafka in services/recurring-task-service/dapr/subscription.yaml

**Checkpoint**: All images built, all Helm charts ready. Application deployment can begin.

---

## Phase 3: User Story 1 — Deploy Backend and Frontend to Minikube (Priority: P1)

**Goal**: Deploy backend (with Dapr sidecar) and frontend (without Dapr) to Minikube. Verify pods Running, app accessible via port-forward, all 009 features working.

**Independent Test**: Port-forward both services, load frontend in browser, create/edit/delete tasks with priority, tags, due dates, search, filter, sort — all must work.

### Implementation for User Story 1

- [x] T025 [US1] Apply Dapr subscription CRDs to phase-v namespace (kubectl apply -f services/*/dapr/subscription.yaml -n phase-v)
- [x] T026 [US1] Install backend Helm release (helm install backend helm/backend -n phase-v) and verify pod reaches 2/2 Running
- [x] T027 [US1] Install frontend Helm release (helm install frontend helm/frontend -n phase-v) and verify pod reaches 1/1 Running
- [x] T028 [US1] Port-forward backend (kubectl port-forward svc/todo-backend 8080:8000 -n phase-v) and verify /health returns 200
- [x] T029 [US1] Port-forward frontend (kubectl port-forward svc/todo-frontend 3030:3000 -n phase-v) and verify app loads (HTTP 200)
- [ ] T030 [US1] Validate 009-advanced-task-features regression: create task with priority+tags+due_at, filter by tag, sort by priority, search by title — all PASS

**Checkpoint**: Backend and frontend running in Minikube. Core application functional. SC-001 (partial), SC-007 validated.

---

## Phase 4: User Story 2 — Event-Driven Communication via Dapr Pub/Sub (Priority: P1)

**Goal**: Deploy notification-service and recurring-task-service with Dapr sidecars. Verify Pub/Sub event flow end-to-end.

**Independent Test**: Create a task → check notification-service logs for event receipt. Complete a recurring task → check recurring-task-service creates next occurrence.

### Implementation for User Story 2

- [x] T031 [US2] Install notification-service Helm release (helm install notification helm/notification-service -n phase-v) and verify pod reaches 2/2 Running
- [x] T032 [US2] Install recurring-task-service Helm release (helm install recurring helm/recurring-service -n phase-v) and verify pod reaches 2/2 Running
- [x] T033 [US2] Verify all Dapr subscriptions registered (kubectl get subscriptions -n phase-v shows 3 subscriptions)
- [x] T034 [US2] Publish test event to task-events topic via Dapr sidecar API and verify delivery to recurring-task-service (DROP status = delivered but test payload didn't match schema)
- [x] T035 [US2] Publish test event to notifications topic and verify delivery to notification-service (confirmed via Dapr sidecar DROP log)
- [ ] T036 [US2] Create a recurring task, mark it complete, verify recurring-task-service creates next occurrence within 30 seconds
- [x] T037 [US2] Verify graceful degradation: temporarily delete pubsub-kafka component, confirm backend stays 2/2 Running, then re-apply component

**Checkpoint**: Full Pub/Sub event flow working. SC-001, SC-002, SC-003 validated.

---

## Phase 5: User Story 3 — Dapr State Store (Priority: P2)

**Goal**: Verify Dapr state store component is operational. Optionally update notification-service to use Dapr state for idempotency.

**Independent Test**: Use kubectl exec to call Dapr state API from a running pod, save and retrieve a key-value pair.

### Implementation for User Story 3

- [x] T038 [US3] Verify statestore Dapr component is registered (dapr components -k -n phase-v | grep statestore)
- [x] T039 [US3] Test state store from backend pod: save key-value via Dapr state API, GET retrieves {"message":"hello from dapr state store"}
- [x] T040 [US3] Add cron-check-overdue endpoint to recurring-task-service: POST /cron-check-overdue handler, rebuilt image, redeployed

**Checkpoint**: State store operational, verified via manual API call. SC-005 (partial) validated.

---

## Phase 6: User Story 4 — Scheduled Jobs via Dapr Cron Binding (Priority: P2)

**Goal**: Verify Dapr cron binding triggers the recurring-task-service endpoint on schedule.

**Independent Test**: Check recurring-task-service logs for periodic invocations from cron binding.

### Implementation for User Story 4

- [x] T041 [US4] Verify cron-check-overdue Dapr binding is registered and scoped to recurring-task-service
- [x] T042 [US4] Restart recurring-task-service pod to pick up cron binding (done during T040 redeploy)
- [x] T043 [US4] Cron binding invoked: logs show "POST /cron-check-overdue HTTP/1.1 200 OK"

**Checkpoint**: Cron binding triggers endpoint on schedule. SC-004 validated.

---

## Phase 7: User Story 5 — Secrets Management via Dapr Secrets API (Priority: P2)

**Goal**: Verify Kubernetes Secrets are accessible via Dapr Secrets API from running services.

**Independent Test**: Call Dapr Secrets API from backend pod, retrieve DATABASE_URL from app-secrets.

### Implementation for User Story 5

- [x] T044 [US5] Verify kubernetes-secrets Dapr component is registered
- [x] T045 [US5] Test Dapr Secrets API: retrieved all 5 keys (DATABASE_URL, BETTER_AUTH_SECRET, BETTER_AUTH_URL, CORS_ORIGINS, GROQ_API_KEY) after RBAC fix

**Checkpoint**: Secrets accessible via Dapr API. SC-005 validated.

---

## Phase 8: User Story 6 — Service-to-Service Invocation via Dapr (Priority: P3)

**Goal**: Verify recurring-task-service invokes backend via Dapr service invocation (not direct HTTP).

**Independent Test**: Complete a recurring task, verify recurring-task-service logs show Dapr invocation URL (localhost:3500/v1.0/invoke/backend/method/...) and backend creates new task.

### Implementation for User Story 6

- [x] T046 [US6] Verify Dapr app-ids: backend="backend", recurring-task-service="recurring-task-service"
- [x] T047 [US6] Dapr service invocation verified: recurring-task-service called backend /health via localhost:3500/v1.0/invoke/backend/method/health — returned {"status":"healthy"}
- [ ] T048 [US6] Verify the new task occurrence appears in the frontend task list with correct next due date (manual browser test)

**Checkpoint**: Service invocation working via Dapr. SC-006 validated.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, automation, and final validation.

- [x] T049 [P] Create deployment automation script in scripts/deploy-minikube.sh
- [x] T050 Update quickstart.md with Kafka, RBAC, GROQ_API_KEY, port conflict notes, automated script reference
- [x] T051 Dapr dashboard check: 4 components, 3 subscriptions, all pods Running, 6 Helm releases deployed
- [ ] T052 Run complete regression test through frontend UI (manual browser test)
- [x] T053 Kafka is primary broker — switching only requires Dapr component YAML + Helm values + subscription YAML, no code changes
- [x] T054 Update MEMORY.md with deployment state and Minikube-specific notes

**Checkpoint**: All success criteria validated. Deployment documented and reproducible. SC-007, SC-008, SC-009 validated.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (Redis + Dapr components must be deployed first)
- **US1 (Phase 3)**: Depends on Phase 2 (images built, Helm charts ready) — BLOCKS US2
- **US2 (Phase 4)**: Depends on US1 (backend must be running for event publishing)
- **US3 (Phase 5)**: Depends on Phase 1 (statestore component) — can run in parallel with US2
- **US4 (Phase 6)**: Depends on US2 (recurring-task-service must be deployed)
- **US5 (Phase 7)**: Depends on Phase 1 (secrets component) + US1 (backend must be running) — can run in parallel with US2
- **US6 (Phase 8)**: Depends on US2 (both services must be deployed with Dapr sidecars)
- **Polish (Phase 9)**: Depends on all user stories being complete

### Within Each User Story

- Deploy before verify
- Verify pods Running before testing functionality
- Test core flow before edge cases

### Parallel Opportunities

**After Phase 2 completes:**
- US1 starts immediately (deploy backend + frontend)

**After US1 completes:**
- US2 (deploy microservices + test Pub/Sub)
- US3 (test state store — only needs backend running)
- US5 (test secrets API — only needs backend running)

**After US2 completes:**
- US4 (cron binding — needs recurring-task-service deployed)
- US6 (service invocation — needs both services with Dapr)

---

## Parallel Example: Phase 1

```bash
# All Dapr component YAMLs can be created in parallel (T001-T005):
Task: "Create Redis deployment in dapr/components/redis-deployment.yaml"
Task: "Create Pub/Sub component in dapr/components/pubsub-redis.yaml"
Task: "Create State Store component in dapr/components/statestore-redis.yaml"
Task: "Create Secrets Store component in dapr/components/secretstore-kubernetes.yaml"
Task: "Create Cron Binding component in dapr/components/cron-check-overdue.yaml"
```

## Parallel Example: Phase 2 (Docker Builds)

```bash
# All Docker builds can run in parallel (T010-T013):
Task: "Build todo-backend:latest from backend/Dockerfile"
Task: "Build todo-frontend:latest from frontend/Dockerfile"
Task: "Build notification-service:latest from services/notification-service/Dockerfile"
Task: "Build recurring-task-service:latest from services/recurring-task-service/Dockerfile"
```

## Parallel Example: Phase 2 (Helm Charts)

```bash
# Frontend chart creation tasks can run in parallel (T015-T018):
Task: "Create helm/frontend/Chart.yaml"
Task: "Create helm/frontend/values.yaml"
Task: "Create helm/frontend/templates/deployment.yaml"
Task: "Create helm/frontend/templates/service.yaml"

# Existing chart updates can run in parallel (T021-T024):
Task: "Update helm/notification-service/values.yaml"
Task: "Update helm/recurring-service/values.yaml"
Task: "Update services/notification-service/dapr/subscription.yaml"
Task: "Update services/recurring-task-service/dapr/subscription.yaml"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup (Redis + Dapr components)
2. Complete Phase 2: Foundational (Docker images + Helm charts)
3. Complete Phase 3: US1 (deploy backend + frontend)
4. **STOP and VALIDATE**: App loads in browser, all 009 features work in Minikube

### Incremental Delivery

1. Setup + Foundational → Infrastructure ready
2. US1 → Backend + Frontend in Minikube → Validate (MVP!)
3. US2 → Microservices + Pub/Sub → Validate event flow
4. US3 + US4 + US5 → State/Cron/Secrets → Validate Dapr building blocks
5. US6 → Service invocation → Validate inter-service communication
6. Polish → Documentation + full regression

---

## Task Summary

| Phase | Story | Tasks | Parallel |
|-------|-------|-------|----------|
| Phase 1: Setup | — | T001-T008 (8) | T001-T005 parallel |
| Phase 2: Foundational | — | T009-T024 (16) | T010-T013, T015-T018, T021-T024 parallel |
| Phase 3: US1 | Deploy Backend+Frontend | T025-T030 (6) | — |
| Phase 4: US2 | Pub/Sub Events | T031-T037 (7) | — |
| Phase 5: US3 | State Store | T038-T040 (3) | — |
| Phase 6: US4 | Cron Binding | T041-T043 (3) | — |
| Phase 7: US5 | Secrets API | T044-T045 (2) | — |
| Phase 8: US6 | Service Invocation | T046-T048 (3) | — |
| Phase 9: Polish | — | T049-T054 (6) | T049 parallel |
| **Total** | | **54 tasks** | |

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- This is an infrastructure-focused feature — most tasks are YAML creation, kubectl commands, and manual verification
- No automated test suite — validation is via kubectl pod status, service logs, Dapr dashboard, and frontend UI
- All application code remains unchanged except subscription YAML pubsubname field (T023, T024) and one new endpoint (T040)
