---
id: 0004
title: Fix recurring tasks and frontend proxy for Minikube
stage: green
date: 2026-02-20
surface: agent
model: claude-opus-4-6
feature: 010-minikube-dapr-deployment
branch: 010-minikube-dapr-deployment
user: shaid
command: interactive session
labels: ["recurring-tasks", "dapr", "event-driven", "frontend-proxy", "minikube", "wsl2", "accessibility"]
links:
  spec: null
  ticket: null
  adr: null
  pr: https://github.com/ShabanaHaider/hackathon2-phase2/tree/phase-V
files:
  - backend/auth.py
  - frontend/next.config.ts
  - frontend/src/lib/api.ts
  - frontend/src/lib/chat-api.ts
  - frontend/src/components/ChatContainer.tsx
  - frontend/src/components/FilterBar.tsx
  - frontend/src/components/TaskForm.tsx
  - frontend/src/components/TaskItem.tsx
  - services/recurring-task-service/main.py
  - scripts/web-todo-app.sh
tests:
  - curl end-to-end test: create recurring task, mark complete, verify new pending instance created via Dapr service invocation (PASS)
  - browser end-to-end test: create recurring task from UI, mark complete, verify new pending instance appears with next due date (PASS)
  - Next.js rewrite proxy test: verify /api/todos proxied from frontend to backend inside cluster (PASS)
---

## Prompt

User reported recurring tasks not creating new pending instances when marked complete from browser. Multiple debugging sessions to identify root cause: browser requests were hitting a local Windows backend instead of the Minikube K8s backend. Also fixed Dapr service invocation routing bug and WSL2 networking issues.

Key user messages:
- "i have added clean the room and set recurring pattern as daily and after the passing of due date time, i set it as task completed... it should be seen as due tomorrow and shown in pending task list"
- "apply event driven approach instead of inline"
- "im reproducing the exact requirement of part B: local deployment"
- "i have just add eat dinner at chinatown, just check" (first successful browser-to-K8s test)
- "yes it correctly showing the newly created task with due tomorrow"

## Response snapshot

### Root causes identified and fixed:

1. **Browser hitting local Windows backend, not K8s**: User had local uvicorn running on Windows port 8000. Browser requests went to local backend (no Dapr) instead of Minikube backend. Identified by checking Neon DB — tasks existed but zero requests in K8s backend logs.

2. **Dapr auth header mismatch**: Backend checked `dapr-app-id` header, but Dapr service invocation sets `dapr-caller-app-id`. Fixed auth.py to check `dapr-caller-app-id` first with `dapr-app-id` fallback.

3. **Dapr routing loop**: Recurring service sent `dapr-app-id: recurring-task-service` header in Dapr invoke calls. Dapr interpreted this as routing override, sending request back to recurring service (404). Fixed by splitting into `dapr_headers` (no dapr-app-id) for Dapr invoke and `direct_headers` (with dapr-app-id) for direct fallback.

4. **WSL2 networking**: Windows couldn't reach WSL2 localhost (interop disabled). Set up netsh portproxy rules. Then added Next.js rewrites to proxy all /api/* requests to backend internally within cluster — browser only needs port 3000.

### Changes made:
- `backend/auth.py` — check dapr-caller-app-id for Dapr service invocation auth
- `services/recurring-task-service/main.py` — split Dapr vs direct call headers
- `frontend/next.config.ts` — add rewrites to proxy API calls to backend inside cluster
- `frontend/src/lib/api.ts` and `chat-api.ts` — default API_URL to same-origin
- `frontend/src/components/*.tsx` — add aria-labels, use canonical Tailwind classes
- `scripts/web-todo-app.sh` — startup script for Minikube

## Outcome

- ✅ Impact: Recurring task event-driven flow working end-to-end from browser through full Dapr pipeline (Browser → Frontend → Backend → Kafka → Recurring-Task-Service → Backend)
- 🧪 Tests: curl and browser end-to-end tests PASS; TypeScript type-check PASS
- 📁 Files: 10 files changed across backend, frontend, recurring service, and scripts
- 🔁 Next prompts: Consider enabling WSL interop for simpler networking; consider minikube tunnel for production-like access
- 🧠 Reflection: The root cause was deceptively simple — local backend intercepting browser traffic. Hours of debugging Dapr/Kafka/events were misdirected because the requests never reached K8s. Always verify the request actually reaches the target service first.

## Evaluation notes (flywheel)

- Failure modes observed: Local dev server intercepting K8s traffic; Dapr header routing override; WSL2 localhost forwarding disabled
- Graders run and results (PASS/FAIL): Manual browser test PASS, curl integration test PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add BACKEND_INTERNAL_URL env var to K8s deployment for configurable backend proxy target
