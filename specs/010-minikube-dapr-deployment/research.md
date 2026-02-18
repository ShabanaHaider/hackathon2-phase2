# Research: Minikube Dapr Deployment

**Feature**: 010-minikube-dapr-deployment
**Date**: 2026-02-17

## R1: Dapr Installation on Minikube

**Decision**: Dapr 1.16.9 already initialized in `phase-v` namespace via `dapr init -k --namespace phase-v`.

**Rationale**: Dapr CLI installs the control plane (operator, sidecar-injector, sentry, placement-server, scheduler-server, dashboard) directly into the target namespace. All 8 pods confirmed Running.

**Alternatives considered**:
- Helm-based Dapr install: More customizable but unnecessary for local dev. CLI method is simpler.
- Default namespace install: Would require cross-namespace component references. Installing in `phase-v` keeps everything co-located.

## R2: Message Broker — Kafka vs Redis

**Decision**: Start with Redis Pub/Sub (lightweight) with Kafka as a documented upgrade path.

**Rationale**:
- Minikube is running on WSL2 with limited resources. Kafka + Zookeeper requires ~1.5GB RAM minimum.
- Redis requires ~128MB RAM and provides adequate Pub/Sub for local development.
- The application already uses Dapr HTTP API for publishing — switching between Redis and Kafka requires only a Dapr component YAML change, zero code changes.
- Constitution (Principle IV): "Kafka MUST NOT be accessed directly from application services" — since we use Dapr abstraction, the broker is swappable.

**Alternatives considered**:
- Kafka via Bitnami Helm: Production-ready but heavy for local dev. Helm chart already scaffolded at `helm/kafka/`. Can be enabled when resources allow.
- Kafka via KRaft (no Zookeeper): Lighter but Bitnami chart defaults to Zookeeper mode. More configuration needed.

## R3: Dapr State Store Backend

**Decision**: Use Redis as Dapr State Store backend (same Redis instance as Pub/Sub).

**Rationale**:
- Redis supports both Pub/Sub and State Store Dapr components simultaneously.
- Single Redis deployment minimizes resource usage on Minikube.
- notification-service currently uses in-memory `processed_events` set — migrating to Dapr State Store provides persistence across pod restarts.

**Alternatives considered**:
- PostgreSQL (Neon) as state store: Would work but adds latency for external calls. Redis is local and faster for key-value operations.
- Separate Redis instances: Unnecessary for local dev.

## R4: Dapr Secrets Store

**Decision**: Use Kubernetes Secrets as Dapr secret store.

**Rationale**:
- Kubernetes Secrets are native to the platform and require no additional infrastructure.
- Dapr's `secretstores.kubernetes` component reads directly from Kubernetes Secrets.
- Secrets include: DATABASE_URL, BETTER_AUTH_SECRET, BETTER_AUTH_URL, CORS_ORIGINS.

**Alternatives considered**:
- HashiCorp Vault: Overkill for local dev. Production concern.
- Dapr local secret store (JSON file): Not Kubernetes-native, harder to manage.

## R5: Dapr Cron Binding

**Decision**: Configure a Dapr input binding of type `bindings.cron` targeting the recurring-task-service.

**Rationale**:
- The recurring-task-service needs periodic invocation to check for overdue tasks and trigger reminders.
- Dapr cron binding invokes a configured endpoint on schedule — no application-side scheduler needed.
- Schedule: every 5 minutes (`@every 5m`) for local dev, configurable via Helm values.

**Alternatives considered**:
- Kubernetes CronJob: Heavier, creates new pods per invocation. Dapr binding reuses existing pod.
- In-app scheduler (APScheduler, etc.): Violates stateless service principle. Pod restart loses schedule state.

## R6: Frontend Helm Chart

**Decision**: Create a new `helm/frontend/` chart (does not exist yet).

**Rationale**:
- Existing Helm charts cover backend, notification-service, recurring-service, and kafka.
- Frontend needs its own chart with: Next.js container, environment variables (NEXT_PUBLIC_API_URL pointing to backend K8s service), no Dapr sidecar (frontend doesn't use Dapr directly).

**Alternatives considered**:
- Use `to-do-phase5/` umbrella chart: Too generic, doesn't support multi-service deployment well.
- Deploy frontend outside Minikube: Loses the benefit of full-stack K8s testing.

## R7: Docker Image Building Strategy

**Decision**: Build images directly in Minikube's Docker daemon via `eval $(minikube docker-env)`.

**Rationale**:
- Avoids needing a container registry for local dev.
- `imagePullPolicy: IfNotPresent` in Helm values ensures Kubernetes uses locally built images.
- All Dockerfiles already exist and use Python 3.12 / Node 20.

**Alternatives considered**:
- Push to local registry (minikube registry addon): Extra step, same result.
- Push to Docker Hub: Unnecessary for local dev, requires auth.

## R8: Backend Database Connectivity from Minikube

**Decision**: Backend pods connect to external Neon PostgreSQL via the existing DATABASE_URL.

**Rationale**:
- Neon is the authoritative database (Constitution: "Database: Neon Serverless PostgreSQL").
- Minikube has external network access by default.
- DATABASE_URL will be stored as a Kubernetes Secret and injected via Dapr Secrets API or environment variables.

**Alternatives considered**:
- Local PostgreSQL in Minikube: Would require data migration, defeats purpose of using Neon.
- Port-forward to local database: Unnecessary complexity.

## R9: Frontend-to-Backend Communication in Kubernetes

**Decision**: Frontend uses Kubernetes service DNS (`http://backend:8000`) for server-side API calls. Browser-side calls use port-forwarded URL.

**Rationale**:
- Next.js server components can resolve Kubernetes DNS names.
- Browser-side fetch requires an externally accessible URL (via `minikube service` or port-forward).
- `NEXT_PUBLIC_API_URL` will be set to the port-forwarded backend URL for client-side calls.

**Alternatives considered**:
- Ingress controller: More production-like but adds complexity for local dev.
- NodePort service: Simpler but port conflicts possible. Port-forward is more flexible.

## R10: Dapr Subscription Delivery

**Decision**: Use declarative Dapr Subscriptions (Kubernetes CRDs) rather than programmatic subscriptions.

**Rationale**:
- Subscription YAML files already exist in `services/notification-service/dapr/subscription.yaml` and `services/recurring-task-service/dapr/subscription.yaml`.
- These are Dapr `Subscription` CRDs (v2alpha1) that need to be applied to the `phase-v` namespace.
- Declarative approach is more Kubernetes-native and doesn't require code changes.

**Alternatives considered**:
- Programmatic subscriptions via `/dapr/subscribe` endpoint: Requires code changes, less K8s-native.
- Topic routing rules: More complex, not needed for current simple routing.
