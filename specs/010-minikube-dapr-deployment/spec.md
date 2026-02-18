# Feature Specification: Minikube Dapr Deployment

**Feature Branch**: `010-minikube-dapr-deployment`
**Created**: 2026-02-17
**Status**: Draft
**Input**: User description: "Deploy the Phase-V application locally on Minikube with full Dapr support, including Pub/Sub, State, Bindings (cron), Secrets, and Service Invocation."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy Backend and Frontend to Minikube (Priority: P1)

As a developer, I want to deploy the backend (FastAPI) and frontend (Next.js) to my local Minikube cluster inside the `phase-v` namespace so that the application runs in a Kubernetes environment with Dapr sidecars injected.

**Why this priority**: Without the core services running in Minikube with Dapr sidecars, no other Dapr building block can function. This is the foundation for all subsequent stories.

**Independent Test**: Deploy backend and frontend pods, verify they are Running with Dapr sidecars attached, and access the application through a Minikube service URL or port-forward.

**Acceptance Scenarios**:

1. **Given** Minikube is running with the `phase-v` namespace, **When** the developer runs the Helm install commands for backend and frontend, **Then** both pods reach Running status with 2/2 containers (app + Dapr sidecar).
2. **Given** both pods are running, **When** the developer port-forwards the frontend service, **Then** the application loads in the browser and connects to the backend API.
3. **Given** the backend is deployed with Python 3.12 base image, **When** the pod starts, **Then** it does not hang or crash from SQLModel/Python version incompatibilities.
4. **Given** existing advanced features (priority, tags, due dates, recurring tasks, search, filter, sort) are present in the backend code, **When** the application runs inside Minikube, **Then** all advanced features from 009-advanced-task-features continue to work without regression.

---

### User Story 2 - Event-Driven Communication via Dapr Pub/Sub (Priority: P1)

As a developer, I want Dapr Pub/Sub configured in Minikube so that the backend can publish events (task.created, task.updated, task.completed, task.deleted) and microservices (notification-service, recurring-task-service) can subscribe to them.

**Why this priority**: Pub/Sub is the primary integration mechanism for the event-driven microservices architecture. Without it, notification and recurring task services have no input.

**Independent Test**: Trigger a task creation from the frontend, verify the event is published via Dapr, and confirm the notification-service and recurring-task-service receive and process the event.

**Acceptance Scenarios**:

1. **Given** a message broker is deployed in Minikube and the Dapr Pub/Sub component is configured, **When** the backend creates a task, **Then** a `task.created` event is published to the `task-events` topic.
2. **Given** the notification-service is subscribed to the `reminders` topic, **When** a reminder event is published, **Then** the notification-service receives and acknowledges the event.
3. **Given** the recurring-task-service is subscribed to the `task-events` topic, **When** a `task.completed` event is published for a recurring task, **Then** the recurring-task-service creates the next occurrence of the task.
4. **Given** the message broker becomes temporarily unavailable, **When** the backend attempts to publish an event, **Then** the application logs a warning but does not crash or block the user request.

---

### User Story 3 - Dapr State Store for Application State (Priority: P2)

As a developer, I want a Dapr State Store component configured in Minikube so that services can use Dapr's state management API for caching, session data, or idempotency tracking.

**Why this priority**: State management enables idempotency in event processing (notification-service already tracks processed events in-memory) and provides a foundation for distributed caching.

**Independent Test**: Use the Dapr state API from a running service to save and retrieve a key-value pair.

**Acceptance Scenarios**:

1. **Given** a state store component is deployed and configured, **When** a service saves state via the Dapr state API, **Then** the state is persisted and retrievable across pod restarts.
2. **Given** the notification-service tracks processed event IDs, **When** the service is configured to use Dapr state instead of in-memory tracking, **Then** idempotency survives pod restarts.

---

### User Story 4 - Scheduled Jobs via Dapr Cron Binding (Priority: P2)

As a developer, I want a Dapr cron binding configured so that the recurring-task-service can be triggered on a schedule to check for overdue tasks and generate reminders.

**Why this priority**: Scheduled task checking is essential for the reminder and recurring task systems to operate proactively rather than only reacting to events.

**Independent Test**: Configure a cron binding with a short interval, verify the recurring-task-service endpoint receives periodic invocations.

**Acceptance Scenarios**:

1. **Given** a Dapr cron binding is configured with a schedule, **When** the scheduled time arrives, **Then** the bound service endpoint is invoked automatically.
2. **Given** the cron binding triggers a check for overdue tasks, **When** overdue tasks exist, **Then** reminder events are published to the appropriate topic.

---

### User Story 5 - Secrets Management via Dapr Secrets API (Priority: P2)

As a developer, I want application secrets (database connection strings, auth keys) managed through Kubernetes Secrets and accessible via the Dapr Secrets API, so that secrets are not hardcoded or stored in environment variable plaintext.

**Why this priority**: Secrets management is important for security best practices, but the application can function with environment variables as a fallback. This is an incremental security improvement.

**Independent Test**: Store a secret in Kubernetes, configure the Dapr secrets component, and retrieve the secret from a running service via the Dapr Secrets API.

**Acceptance Scenarios**:

1. **Given** Kubernetes Secrets are created in the `phase-v` namespace, **When** a service requests a secret via the Dapr Secrets API, **Then** the correct secret value is returned.
2. **Given** the backend requires a database connection string, **When** the pod starts, **Then** it retrieves the connection string from the Dapr Secrets API rather than from a plaintext environment variable.

---

### User Story 6 - Service-to-Service Invocation via Dapr (Priority: P3)

As a developer, I want services to communicate with each other using Dapr service invocation so that the recurring-task-service can call the backend API to create new task occurrences without needing to know the backend's cluster IP or DNS name.

**Why this priority**: Dapr service invocation provides service discovery, load balancing, and mTLS for free. The recurring-task-service already has a direct HTTP fallback, so this is an enhancement.

**Independent Test**: From the recurring-task-service, invoke the backend's task creation endpoint via Dapr service invocation and verify the task is created.

**Acceptance Scenarios**:

1. **Given** both backend and recurring-task-service have Dapr sidecars, **When** the recurring-task-service invokes the backend via `http://localhost:3500/v1.0/invoke/backend/method/api/todos`, **Then** the request is routed to the backend and a new task is created.
2. **Given** the backend pod is restarted and gets a new IP, **When** the recurring-task-service invokes the backend via Dapr, **Then** Dapr handles service discovery and the call succeeds without configuration changes.

---

### Edge Cases

- What happens when Minikube runs out of memory or CPU due to Kafka + multiple services? The system should support a lightweight alternative (Redis) for resource-constrained environments.
- What happens when Dapr is not yet initialized but pods are starting? Pods should have appropriate startup probes to wait for Dapr sidecar readiness.
- What happens when the external Neon PostgreSQL database is unreachable from inside Minikube? The backend health check should report unhealthy and the pod should not accept traffic.
- What happens when a Helm chart upgrade is applied while pods are running? Rolling updates should ensure zero-downtime transitions.
- What happens when Docker images are not built in Minikube's Docker environment? Image pull will fail with ErrImagePull. Documentation must clearly state the `eval $(minikube docker-env)` prerequisite.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST deploy the backend service (FastAPI, Python 3.12) to the `phase-v` namespace in Minikube with a Dapr sidecar injected.
- **FR-002**: System MUST deploy the frontend service (Next.js) to the `phase-v` namespace in Minikube, configured to communicate with the backend.
- **FR-003**: System MUST deploy the notification-service to the `phase-v` namespace with a Dapr sidecar for Pub/Sub subscription.
- **FR-004**: System MUST deploy the recurring-task-service to the `phase-v` namespace with a Dapr sidecar for Pub/Sub subscription and service invocation.
- **FR-005**: System MUST initialize Dapr on the Minikube cluster before deploying application services.
- **FR-006**: System MUST configure a Dapr Pub/Sub component backed by a message broker deployed inside Minikube. Primary option: Kafka. Alternative option: Redis Pub/Sub for resource-constrained environments.
- **FR-007**: System MUST configure a Dapr State Store component for persistent state management across services.
- **FR-008**: System MUST configure a Dapr Cron Binding component to trigger scheduled operations on the recurring-task-service.
- **FR-009**: System MUST configure a Dapr Secrets Store component backed by Kubernetes Secrets for secure credential management.
- **FR-010**: System MUST support Dapr service invocation between the recurring-task-service and the backend.
- **FR-011**: All Docker images MUST be built using Python 3.12 (not 3.14) to maintain SQLModel compatibility.
- **FR-012**: All Dapr components and service configurations MUST be manageable through Helm values files.
- **FR-013**: System MUST preserve all existing functionality from 009-advanced-task-features (priority, tags, due dates, search, filter, sort, recurring tasks, reminders) without regression.
- **FR-014**: Backend MUST use Dapr HTTP/gRPC APIs for Pub/Sub publishing, not direct broker client libraries.
- **FR-015**: System MUST provide a documented deployment procedure (step-by-step) that a developer can follow to set up the entire stack from scratch.
- **FR-016**: System MUST include health check endpoints for all services, used by Kubernetes liveness and readiness probes.

### Key Entities

- **Minikube Cluster**: Local Kubernetes cluster hosting all services. Contains the `phase-v` namespace.
- **Dapr Sidecar**: Injected per-pod proxy that provides Pub/Sub, State, Secrets, Bindings, and Service Invocation capabilities.
- **Message Broker**: Kafka (primary) or Redis (alternative) — handles event routing for Pub/Sub topics (`task-events`, `reminders`, `notifications`).
- **State Store**: Persistent key-value store for service state (idempotency tracking, caching). Backed by Redis or PostgreSQL.
- **Cron Binding**: Dapr input binding that triggers endpoints on a time schedule.
- **Kubernetes Secrets**: Native secret storage for database URLs, auth keys, and broker credentials.
- **Helm Charts**: Parameterized deployment templates for each service (backend, frontend, notification-service, recurring-task-service, message broker).

## Assumptions

- Minikube is already installed and running on the developer's machine.
- The `phase-v` namespace already exists (confirmed active).
- Helm v3 is installed and available on the developer's PATH.
- Docker CLI is available and can target Minikube's Docker daemon via `eval $(minikube docker-env)`.
- The Neon PostgreSQL database is accessible from within Minikube pods (external network access enabled).
- The developer has sufficient local resources (minimum 4GB RAM, 2 CPUs allocated to Minikube) for Kafka deployment; otherwise Redis is used.
- Better Auth frontend authentication continues to work when accessed via Minikube service URLs or port-forwards.
- Dapr CLI is installed or will be installed as part of the deployment procedure.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All four application pods (backend, frontend, notification-service, recurring-task-service) reach Running status with 2/2 containers within 5 minutes of deployment.
- **SC-002**: A task created through the frontend UI generates a Pub/Sub event that is received by the notification-service within 10 seconds.
- **SC-003**: Completing a recurring task through the frontend results in a new task occurrence being created within 30 seconds via the recurring-task-service.
- **SC-004**: The Dapr cron binding triggers the scheduled endpoint at least once within the configured interval (verified via service logs).
- **SC-005**: A secret stored in Kubernetes Secrets is retrievable via the Dapr Secrets API from any service pod.
- **SC-006**: The recurring-task-service successfully creates tasks via Dapr service invocation to the backend (verified via backend logs and database).
- **SC-007**: All existing advanced task features (priority, tags, due dates, search, filter, sort) function correctly when the application runs inside Minikube — zero regression from local development.
- **SC-008**: The entire deployment procedure (from clean Minikube to fully operational stack) can be completed by following the documentation in under 30 minutes.
- **SC-009**: Switching between Kafka and Redis Pub/Sub requires changing only Helm values and Dapr component configuration — no application code changes.
