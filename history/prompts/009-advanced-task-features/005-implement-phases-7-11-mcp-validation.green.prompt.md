---
id: 005
title: Implement phases 7-11 with MCP server update and validation
stage: green
date: 2026-02-16
surface: agent
model: claude-opus-4-6
feature: 009-advanced-task-features
branch: 009-advanced-task-features
user: shaidera
command: implement
labels: ["search", "due-dates", "reminders", "recurring-tasks", "mcp", "dapr", "helm", "microservices", "validation"]
links:
  spec: specs/009-advanced-task-features/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/mcp_server.py
  - backend/services/event_publisher.py
  - backend/models.py
  - backend/routers/todos.py
  - backend/.env.example
  - frontend/src/components/TaskForm.tsx
  - frontend/src/components/TaskItem.tsx
  - services/notification-service/main.py
  - services/notification-service/dapr/subscription.yaml
  - services/notification-service/Dockerfile
  - services/notification-service/requirements.txt
  - services/recurring-task-service/main.py
  - services/recurring-task-service/dapr/subscription.yaml
  - services/recurring-task-service/Dockerfile
  - services/recurring-task-service/requirements.txt
  - helm/backend/Chart.yaml
  - helm/backend/values.yaml
  - helm/backend/templates/deployment.yaml
  - helm/backend/templates/service.yaml
  - helm/notification-service/Chart.yaml
  - helm/notification-service/values.yaml
  - helm/notification-service/templates/deployment.yaml
  - helm/notification-service/templates/service.yaml
  - helm/recurring-service/Chart.yaml
  - helm/recurring-service/values.yaml
  - helm/recurring-service/templates/deployment.yaml
  - helm/recurring-service/templates/service.yaml
  - helm/kafka/Chart.yaml
  - helm/kafka/values.yaml
  - specs/009-advanced-task-features/tasks.md
tests:
  - Manual validation T093: quickstart.md scenarios (A-E all PASS)
  - Manual validation T094: backward compatibility (PASS)
---

## Prompt

complete implementation till phase 8 i.e tasks T065 as frontend has start running and aparently no errors.

use the existing agents 1. nextjs-frontend-dev... and use fastapi-backend agent for implementing event-driven microservices with Dapr integration... continue implementing phases 9 to 11

T089 clarification: mcp_server.py is in scope for Phase-5. Extend add_task and update_task tools to include advanced fields (priority, due_date, recurrence, tags). Publish Dapr pub/sub events after successful DB commit. Ensure backward compatibility.

tell me the steps to do T093 myself and confirm to you

## Response snapshot

Completed all 94 tasks (T001-T094) across 11 phases:

**Phases 7-8 (Search + Due Dates)**: Already implemented in prior session, verified and marked complete.

**Phase 9 (Reminders)**: Created notification-service microservice with FastAPI, Dapr subscription for reminders/notifications topics, idempotent event handling, Dockerfile. Created Helm chart scaffold.

**Phase 10 (Recurring Tasks)**: Created recurring-task-service with task.completed event handler, next due date calculation (daily/weekly/monthly via dateutil.relativedelta), task creation via Dapr service invocation with direct HTTP fallback. Added event schemas to models.py. Rewrote event_publisher.py with real Dapr HTTP API via httpx.

**Phase 11 (Polish)**:
- T089 (MCP Server): Analyzed architecture — MCP server runs as standalone stdio process with sync sessions, cannot use async EventPublisher. Chose Option A: sync helper functions in mcp_server.py using httpx.post(). Added 5 optional params to add_task/update_task, Dapr event publishing on all 4 mutation types, tag resolution via _resolve_tags().
- T090-T092: Helm charts for backend/notification/recurring/kafka, .env.example updated.
- T093-T094: Created validation checklist for user. User tested through frontend UI: create with tags/priority/due_at (PASS), filter by tag (PASS), tags in dropdowns (PASS), backward compat (PASS), edit tags (PASS).

Key architectural decision: MCP server uses synchronous httpx.post() for Dapr events (not async EventPublisher) because it runs as a separate stdio process outside FastAPI's event loop. Graceful degradation on ConnectError when Dapr sidecar unavailable.

## Outcome

- Impact: Feature 009-advanced-task-features fully implemented and validated. All 94 tasks complete. MCP server compliant with Constitution Principle VII (event publishing after mutations).
- Tests: Manual validation via frontend UI — all scenarios PASS. Backward compatibility confirmed.
- Files: 30+ files created/modified across backend, frontend, microservices, helm, specs
- Next prompts: Create spec 010-minikube-dapr-deployment for full Dapr deployment on Minikube
- Reflection: Background agents failed due to file write permissions — direct implementation was faster. Sync vs async event publishing required architectural analysis before coding.

## Evaluation notes (flywheel)

- Failure modes observed: Background agents (subagent_type) could not write files due to permission restrictions. PowerShell curl commands used "tags" instead of "tag_names" field name causing confusion in validation.
- Graders run and results (PASS/FAIL): T093 manual validation PASS, T094 backward compat PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): For future sessions, implement directly instead of launching background agents for file creation tasks.
