---
id: 014
title: Docker Desktop Kubernetes Setup and Multi-Cluster Deployment
stage: misc
date: 2026-02-12
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: phase-IV
user: shaid
command: direct
labels: ["kubernetes", "docker-desktop", "kubeadm", "deployment", "multi-cluster", "minikube"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - None (all done via kubectl commands)
tests:
  - Manual verification of Docker Desktop Kubernetes cluster
  - Manual testing of practice-deployment (nginx with 2 replicas)
  - Manual testing of hack2-backend and hack2-frontend on Docker Desktop K8s
  - Verification of all three environments running simultaneously
---

## Prompt

User requested step-by-step guidance to:
1. Enable Kubernetes in Docker Desktop (kubeadm cluster provisioning)
2. Verify available kubectl contexts
3. Switch to Docker Desktop Kubernetes cluster
4. Create a test deployment (practice-deployment with nginx)
5. Verify pods running
6. Show all system pods
7. Confirm Minikube cluster remains unchanged
8. Deploy hack2-backend and hack2-frontend to Docker Desktop K8s
9. Access the application via localhost

## Response snapshot

### Steps Completed

1. **Enabled Kubernetes in Docker Desktop**
   - User enabled Kubernetes via Docker Desktop Settings
   - Selected "kubeadm" as cluster provisioning method
   - Waited for Kubernetes to start (green indicator)

2. **Verified Available Contexts**
   ```
   kubectl config get-contexts
   ```
   - docker-desktop (newly created)
   - minikube (existing)

3. **Switched to Docker Desktop Context**
   ```
   kubectl config use-context docker-desktop
   ```

4. **Created Test Deployment**
   ```
   kubectl create deployment practice-deployment --image=nginx --replicas=2
   ```
   - 2 nginx pods created successfully

5. **Verified All System Pods**
   ```
   kubectl get pods -A
   ```
   - kube-system components: coredns, etcd, kube-apiserver, kube-controller-manager, kube-proxy, kube-scheduler, storage-provisioner, vpnkit-controller

6. **Deployed hack2 Application to Docker Desktop K8s**
   - Created deployments for hack2-backend and hack2-frontend
   - Set environment variables (DATABASE_URL, CORS_ORIGINS, BETTER_AUTH_*, GROQ_API_KEY)
   - Set imagePullPolicy: Never (using local Docker images)
   - Created LoadBalancer services on ports 8001 and 3001

7. **Confirmed All Three Environments Running**

### Final Configuration

| Environment | Frontend | Backend | Status |
|-------------|----------|---------|--------|
| Docker Containers | localhost:3000 | localhost:8000 | ✅ Running |
| Docker Desktop K8s | localhost:3001 | localhost:8001 | ✅ Running |
| Minikube | localhost:3030 | localhost:8080 | ✅ Running |

### Key Commands Reference

```bash
# Switch between clusters
kubectl config use-context docker-desktop
kubectl config use-context minikube

# View all contexts
kubectl config get-contexts

# Check pods in current context
kubectl get pods

# Check all system pods
kubectl get pods -A
```

### Docker Desktop K8s Resources Created

- **Deployments:** hack2-backend, hack2-frontend, practice-deployment
- **Services:** hack2-backend (LoadBalancer:8001), hack2-frontend (LoadBalancer:3001)
- **Pods:** 4 total (2 hack2 + 2 nginx practice)

## Outcome

- ✅ Impact: Successfully set up Docker Desktop Kubernetes as third deployment environment alongside Docker containers and Minikube
- 🧪 Tests: All three environments tested and working simultaneously
- 📁 Files: No file changes - all done via kubectl commands
- 🔁 Next prompts: Consider creating Helm chart for Docker Desktop K8s deployment; explore Kubernetes Dashboard
- 🧠 Reflection: Docker Desktop K8s uses LoadBalancer type which automatically exposes services to localhost; different ports needed to avoid conflicts

## Evaluation notes (flywheel)

- Failure modes observed: None - clean setup process
- Graders run and results (PASS/FAIL): PASS - all environments functional
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add resource limits and health probes to Docker Desktop K8s deployments
