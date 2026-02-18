# Quickstart: Minikube Dapr Deployment

**Feature**: 010-minikube-dapr-deployment
**Date**: 2026-02-17

## Prerequisites

- Minikube running with 4GB+ memory (`minikube status` shows Running)
- kubectl configured (`kubectl config current-context` returns `minikube`)
- Helm v3 installed (`helm version`)
- Dapr CLI installed and initialized in cluster (`dapr status -k`)
- Docker CLI available
- `phase-v` namespace exists (`kubectl get ns phase-v`)
- `~/.docker/config.json` must NOT contain `credsStore: desktop.exe` (WSL2 fix)

## Automated Deployment

```bash
# Run the deployment script from project root
./scripts/deploy-minikube.sh
```

## Manual Step-by-Step Deployment

### Step 1: Set Docker to Minikube's Daemon

```bash
eval $(minikube docker-env)
```

### Step 2: Build Docker Images

```bash
# From project root: /mnt/d/projects/hack2-phase5
docker build -t todo-backend:latest ./backend/
docker build -t todo-frontend:latest ./frontend/
docker build -t notification-service:latest ./services/notification-service/
docker build -t recurring-task-service:latest ./services/recurring-task-service/
```

### Step 3: Create Kubernetes Secrets

```bash
kubectl create secret generic app-secrets -n phase-v \
  --from-literal="DATABASE_URL=<your-neon-database-url>" \
  --from-literal="BETTER_AUTH_SECRET=<your-better-auth-secret>" \
  --from-literal="BETTER_AUTH_URL=http://todo-frontend:3000" \
  --from-literal="CORS_ORIGINS=http://localhost:3000,http://todo-frontend:3000" \
  --from-literal="GROQ_API_KEY=<your-groq-api-key>"
```

### Step 4: Create RBAC for Dapr Secrets Access

```bash
kubectl create role secret-reader --verb=get,list --resource=secrets -n phase-v
kubectl create rolebinding default-secret-reader --role=secret-reader --serviceaccount=phase-v:default -n phase-v
```

### Step 5: Deploy Redis (State Store) and Kafka (Pub/Sub)

```bash
kubectl apply -f dapr/components/redis-deployment.yaml
kubectl apply -f dapr/components/kafka-deployment.yaml
```

### Step 6: Apply Dapr Components

```bash
kubectl apply -f dapr/components/pubsub-kafka.yaml
kubectl apply -f dapr/components/statestore-redis.yaml
kubectl apply -f dapr/components/secretstore-kubernetes.yaml
kubectl apply -f dapr/components/cron-check-overdue.yaml
```

### Step 7: Apply Dapr Subscriptions

```bash
kubectl apply -f services/notification-service/dapr/subscription.yaml -n phase-v
kubectl apply -f services/recurring-task-service/dapr/subscription.yaml -n phase-v
```

### Step 8: Deploy Application Services via Helm

```bash
helm install backend helm/backend -n phase-v
helm install frontend helm/frontend -n phase-v
helm install notification helm/notification-service -n phase-v
helm install recurring helm/recurring-service -n phase-v
```

### Step 9: Access the Application

```bash
# Port-forward backend and frontend
kubectl port-forward svc/todo-backend 8000:8000 -n phase-v &
kubectl port-forward svc/todo-frontend 3000:3000 -n phase-v &

# Open browser
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
```

## Verification Checklist

- [ ] All pods Running (backend 2/2, frontend 1/1, notification 2/2, recurring 2/2, redis 1/1, kafka 1/1)
- [ ] Backend /health returns 200
- [ ] Frontend loads in browser at http://localhost:3000
- [ ] Create task via UI — check backend logs for Dapr publish
- [ ] Dapr state store: save/retrieve key-value via sidecar API
- [ ] Dapr secrets API: retrieve app-secrets from backend pod
- [ ] Dapr cron binding: recurring-task-service logs show periodic invocations
- [ ] Dapr service invocation: recurring-task-service can call backend /health via sidecar
- [ ] Check Dapr dashboard: `dapr dashboard -k -n phase-v`

## Key Notes from Deployment

- **Kafka consumer groups**: Each service must have its own consumer group. The pubsub-kafka component uses `consumerID: "{appID}"` to ensure this.
- **Subscription scopes**: Dapr subscriptions use `scopes` to target specific app-ids, preventing unintended message delivery.
- **Subscription schema**: v2alpha1 uses `routes.default`, NOT `route`.
- **GROQ_API_KEY**: Required by backend's agent.py — must be in app-secrets.
- **Port conflicts**: Stop any local dev servers on ports 3000/8000 before port-forwarding.
- **Service names**: Helm charts create services as `todo-backend`, `todo-frontend`, etc. (prefixed with chart name).

## Teardown

```bash
helm uninstall frontend backend notification recurring -n phase-v
kubectl delete -f dapr/components/ -n phase-v
kubectl delete secret app-secrets -n phase-v
kubectl delete role secret-reader -n phase-v
kubectl delete rolebinding default-secret-reader -n phase-v
```
