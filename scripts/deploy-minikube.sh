#!/bin/bash
set -euo pipefail

NAMESPACE="phase-v"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Phase-V Minikube Deployment ==="
echo "Project: $PROJECT_DIR"
echo "Namespace: $NAMESPACE"
echo ""

# Step 1: Verify prerequisites
echo "[1/9] Verifying prerequisites..."
command -v minikube >/dev/null 2>&1 || { echo "ERROR: minikube not found"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "ERROR: kubectl not found"; exit 1; }
command -v helm >/dev/null 2>&1 || { echo "ERROR: helm not found"; exit 1; }
command -v dapr >/dev/null 2>&1 || { echo "ERROR: dapr CLI not found"; exit 1; }
minikube status >/dev/null 2>&1 || { echo "ERROR: minikube not running"; exit 1; }
echo "  All prerequisites OK"

# Step 2: Ensure namespace exists
echo "[2/9] Ensuring namespace $NAMESPACE exists..."
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Step 3: Deploy Redis (state store backend)
echo "[3/9] Deploying Redis..."
kubectl apply -f "$PROJECT_DIR/dapr/components/redis-deployment.yaml"
kubectl wait --for=condition=ready pod -l app=redis -n "$NAMESPACE" --timeout=60s

# Step 4: Deploy Kafka (pub/sub backend)
echo "[4/9] Deploying Kafka..."
kubectl apply -f "$PROJECT_DIR/dapr/components/kafka-deployment.yaml"
kubectl wait --for=condition=ready pod -l app=kafka -n "$NAMESPACE" --timeout=120s

# Step 5: Create Kubernetes secret
echo "[5/9] Creating app-secrets (if not exists)..."
if ! kubectl get secret app-secrets -n "$NAMESPACE" >/dev/null 2>&1; then
    echo "  WARNING: app-secrets not found. Create it manually:"
    echo "  kubectl create secret generic app-secrets -n $NAMESPACE \\"
    echo "    --from-literal=DATABASE_URL=<your-url> \\"
    echo "    --from-literal=BETTER_AUTH_SECRET=<your-secret> \\"
    echo "    --from-literal=BETTER_AUTH_URL=http://frontend:3000 \\"
    echo "    --from-literal=CORS_ORIGINS=http://localhost:3000,http://frontend:3000 \\"
    echo "    --from-literal=GROQ_API_KEY=<your-key>"
    exit 1
fi
echo "  app-secrets exists"

# Step 6: Apply Dapr components
echo "[6/9] Applying Dapr components..."
kubectl apply -f "$PROJECT_DIR/dapr/components/pubsub-kafka.yaml"
kubectl apply -f "$PROJECT_DIR/dapr/components/statestore-redis.yaml"
kubectl apply -f "$PROJECT_DIR/dapr/components/secretstore-kubernetes.yaml"
kubectl apply -f "$PROJECT_DIR/dapr/components/cron-check-overdue.yaml"
echo "  Dapr components applied"

# Step 7: Build Docker images
echo "[7/9] Building Docker images in Minikube..."
eval $(minikube docker-env)
docker build -t todo-backend:latest "$PROJECT_DIR/backend/"
docker build -t todo-frontend:latest "$PROJECT_DIR/frontend/"
docker build -t notification-service:latest "$PROJECT_DIR/services/notification-service/"
docker build -t recurring-task-service:latest "$PROJECT_DIR/services/recurring-task-service/"
echo "  All 4 images built"

# Step 8: Apply Dapr subscriptions
echo "[8/9] Applying Dapr subscriptions..."
kubectl apply -f "$PROJECT_DIR/services/notification-service/dapr/subscription.yaml" -n "$NAMESPACE"
kubectl apply -f "$PROJECT_DIR/services/recurring-task-service/dapr/subscription.yaml" -n "$NAMESPACE"

# Step 9: Install/upgrade Helm releases
echo "[9/9] Installing Helm releases..."
helm upgrade --install backend "$PROJECT_DIR/helm/backend" -n "$NAMESPACE"
helm upgrade --install frontend "$PROJECT_DIR/helm/frontend" -n "$NAMESPACE"
helm upgrade --install notification "$PROJECT_DIR/helm/notification-service" -n "$NAMESPACE"
helm upgrade --install recurring "$PROJECT_DIR/helm/recurring-service" -n "$NAMESPACE"

echo ""
echo "=== Deployment complete ==="
echo "Waiting for pods..."
sleep 10
kubectl get pods -n "$NAMESPACE"
echo ""
echo "Port-forward commands:"
echo "  kubectl port-forward svc/todo-backend 8000:8000 -n $NAMESPACE &"
echo "  kubectl port-forward svc/todo-frontend 3000:3000 -n $NAMESPACE &"
echo ""
echo "Open http://localhost:3000 in your browser"
