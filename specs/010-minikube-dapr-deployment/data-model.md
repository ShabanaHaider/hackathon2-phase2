# Data Model: Minikube Dapr Deployment

**Feature**: 010-minikube-dapr-deployment
**Date**: 2026-02-17

> This feature is infrastructure-focused. No new database tables or application-level data models are introduced. This document covers the Kubernetes and Dapr resource models.

## Kubernetes Resources

### Namespace

- **phase-v**: Target namespace for all application and Dapr resources.

### Deployments (4 application services)

| Deployment | Image | Port | Dapr Sidecar | Replicas |
|------------|-------|------|--------------|----------|
| backend | todo-backend:latest | 8000 | Yes (app-id: backend) | 1 |
| frontend | todo-frontend:latest | 3000 | No | 1 |
| notification-service | notification-service:latest | 8001 | Yes (app-id: notification-service) | 1 |
| recurring-task-service | recurring-task-service:latest | 8002 | Yes (app-id: recurring-task-service) | 1 |

### Services (4 ClusterIP services)

| Service | Target Port | Selector |
|---------|-------------|----------|
| backend | 8000 | app: backend |
| frontend | 3000 | app: frontend |
| notification-service | 8001 | app: notification-service |
| recurring-task-service | 8002 | app: recurring-task-service |

### Infrastructure Deployments

| Deployment | Image | Port | Purpose |
|------------|-------|------|---------|
| redis | redis:7-alpine | 6379 | Pub/Sub + State Store |

### Kubernetes Secrets

| Secret Name | Keys | Purpose |
|-------------|------|---------|
| app-secrets | DATABASE_URL, BETTER_AUTH_SECRET, BETTER_AUTH_URL, CORS_ORIGINS | Application credentials |

## Dapr Components

### Pub/Sub Component

| Field | Value |
|-------|-------|
| Name | pubsub-redis |
| Type | pubsub.redis |
| Redis Host | redis.phase-v.svc.cluster.local:6379 |
| Consumer Prefix | todo-app |

### State Store Component

| Field | Value |
|-------|-------|
| Name | statestore |
| Type | state.redis |
| Redis Host | redis.phase-v.svc.cluster.local:6379 |
| Key Prefix | app-id (default) |

### Secrets Store Component

| Field | Value |
|-------|-------|
| Name | kubernetes-secrets |
| Type | secretstores.kubernetes |

### Cron Binding Component

| Field | Value |
|-------|-------|
| Name | cron-check-overdue |
| Type | bindings.cron |
| Schedule | @every 5m |
| Direction | input |
| Target | recurring-task-service |

## Dapr Subscriptions (CRDs)

### notification-service Subscriptions

| Topic | Route | Pubsub |
|-------|-------|--------|
| reminders | /events/reminder-due | pubsub-redis |
| notifications | /events/notification | pubsub-redis |

### recurring-task-service Subscription

| Topic | Route | Pubsub |
|-------|-------|--------|
| task-events | /events/task-completed | pubsub-redis |

## Event Topics (unchanged from 009)

| Topic | Producer | Consumers | Schema |
|-------|----------|-----------|--------|
| task-events | backend | recurring-task-service | TaskEvent, TaskDeletedEvent |
| reminders | backend | notification-service | ReminderEvent |
| notifications | backend, recurring-task-service | notification-service | NotificationEvent |

## Environment Variables per Service

### Backend

| Variable | Value in K8s | Source |
|----------|-------------|--------|
| DATABASE_URL | (from secret) | Kubernetes Secret: app-secrets |
| BETTER_AUTH_URL | http://frontend:3000 | Helm values |
| DAPR_HTTP_PORT | 3500 | Helm values |
| PUBSUB_NAME | pubsub-redis | Helm values |
| CORS_ORIGINS | http://localhost:3000,http://frontend:3000 | Helm values |

### Frontend

| Variable | Value in K8s | Source |
|----------|-------------|--------|
| NEXT_PUBLIC_API_URL | http://localhost:8000 | Helm values (port-forward URL) |
| BETTER_AUTH_SECRET | (from secret) | Kubernetes Secret: app-secrets |
| BETTER_AUTH_URL | http://frontend:3000 | Helm values |
| DATABASE_URL | (from secret) | Kubernetes Secret: app-secrets |

### notification-service

| Variable | Value in K8s | Source |
|----------|-------------|--------|
| DAPR_HTTP_PORT | 3500 | Helm values |
| PUBSUB_NAME | pubsub-redis | Helm values |

### recurring-task-service

| Variable | Value in K8s | Source |
|----------|-------------|--------|
| DAPR_HTTP_PORT | 3500 | Helm values |
| PUBSUB_NAME | pubsub-redis | Helm values |
| BACKEND_URL | http://backend:8000 | Helm values |
