#!/bin/bash
# Start the web todo app on Minikube

# 1. Check if minikube is running, start if not
if ! minikube status &>/dev/null; then
    echo "Starting minikube..."
    minikube start
fi

# 2. Wait for pods to be ready
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=todo-frontend -n phase-v --timeout=120s
kubectl wait --for=condition=ready pod -l app=todo-backend -n phase-v --timeout=120s

# 3. Kill any existing port-forward on port 3000
pkill -f "kubectl port-forward.*3000" 2>/dev/null
sleep 1

# 4. Start port-forward
kubectl port-forward -n phase-v svc/todo-frontend 3000:3000 --address 0.0.0.0 &

echo ""
echo "App is running at http://localhost:3000"
echo "Press Ctrl+C to stop"
wait
