---
id: 013
title: Docker Minikube Helm Deployment Fixes
stage: misc
date: 2026-02-11
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: phase-IV
user: shaid
command: /resume
labels: ["deployment", "docker", "minikube", "helm", "cors", "authentication", "kubernetes"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/main.py
  - .gitignore
  - to-do/values.yaml
tests:
  - Manual testing of Docker Desktop deployment (localhost:3000, localhost:8000)
  - Manual testing of Minikube/Helm deployment (127.0.0.1:3030, 127.0.0.1:8080)
  - JWKS endpoint verification from backend pod
  - CORS preflight request verification
---

## Prompt

User requested to:
1. Resume previous session context about Docker/Minikube/Helm deployment
2. Test Minikube/Helm deployment and identify Helm chart location
3. Fix signin issues (Better Auth origin validation)
4. Fix CORS errors (backend not allowing frontend origin)
5. Fix JWKS fetch failures (backend couldn't reach frontend for JWT verification)
6. Rebuild Docker images for both environments
7. Commit and push changes
8. Guide on viewing Kubernetes pods in Docker Desktop

## Response snapshot

### Issues Identified and Fixed

1. **Better Auth Invalid Origin Error**
   - Problem: Frontend accessed via tunnel URL (127.0.0.1:36751) not in trusted origins
   - Fix: Added `BETTER_AUTH_TRUSTED_ORIGINS` env var to frontend deployment

2. **CORS Blocked Requests**
   - Problem: Backend had hardcoded CORS origins, not reading from env var
   - Fix: Modified `backend/main.py` to read `CORS_ORIGINS` from environment variable

3. **JWKS Fetch Failures**
   - Problem: Backend `BETTER_AUTH_URL` was set to localhost, unreachable from within pod
   - Fix: Set `BETTER_AUTH_URL` to internal Kubernetes service name `http://hack2-todo-frontend:3000`

4. **Frontend API URL Mismatch**
   - Problem: `NEXT_PUBLIC_API_URL` baked at build time with wrong URL
   - Fix: Rebuilt frontend Docker images with correct API URLs for each environment

### Helm Chart Location
- **Directory:** `/mnt/d/projects/hack2-phase4/to-do/`
- **Chart name:** `hack2-todo` (defined in Chart.yaml)
- **Key files:** Chart.yaml, values.yaml, templates/

### Final Working Configuration

| Environment | Frontend | Backend | Status |
|-------------|----------|---------|--------|
| Docker Desktop | localhost:3000 | localhost:8000 | Working |
| Minikube/Helm | 127.0.0.1:3030 | 127.0.0.1:8080 | Working |

### Commits Made
- "Make CORS origins configurable via environment variable" - backend/main.py, .gitignore

## Outcome

- ✅ Impact: Both Docker Desktop and Minikube/Helm deployments now working with proper authentication and CORS
- 🧪 Tests: Manual signin, todo CRUD operations verified; AI features rate-limited by Groq
- 📁 Files: backend/main.py (CORS from env), .gitignore (updated exclusions), to-do/values.yaml (Helm config)
- 🔁 Next prompts: Monitor Groq rate limit reset, consider upgrading Groq plan for AI features
- 🧠 Reflection: Key learning - NEXT_PUBLIC_* vars are build-time in Next.js; internal K8s service names needed for pod-to-pod communication

## Evaluation notes (flywheel)

- Failure modes observed: CORS hardcoded instead of env-driven; localhost unreachable from within K8s pods; build-time vs runtime env vars confusion
- Graders run and results (PASS/FAIL): PASS - both deployments functional
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add health check for JWKS endpoint availability before startup
