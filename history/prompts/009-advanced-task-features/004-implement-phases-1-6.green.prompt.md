---
id: 004
title: Implement Phases 1-6 Advanced Task Features
stage: green
date: 2026-02-14
surface: agent
model: claude-opus-4-6
feature: 009-advanced-task-features
branch: 009-advanced-task-features
user: shaid
command: implement
labels: ["implementation", "priority", "tags", "filter", "sort", "due-dates"]
links:
  spec: specs/009-advanced-task-features/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/services/__init__.py
  - backend/services/event_publisher.py
  - backend/routers/tags.py
  - backend/routers/todos.py
  - backend/main.py
  - frontend/src/components/PriorityBadge.tsx
  - frontend/src/components/TagSelector.tsx
  - frontend/src/components/FilterBar.tsx
  - frontend/src/components/TaskForm.tsx
  - frontend/src/components/TaskItem.tsx
  - frontend/src/components/TaskList.tsx
  - specs/009-advanced-task-features/tasks.md
tests:
  - None (tests not requested in spec)
---

## Prompt

complete implementation of phase no 1 to 6 of 009-advanced-task-features

## Response snapshot

Implemented all phases 1-6 covering User Stories 1-4 (Priority, Tags, Filter, Sort) plus foundational infrastructure. Key changes:

**Backend:**
- Fixed event publisher to be a graceful no-op stub (no Dapr SDK dependency)
- Created tags router (GET/POST/DELETE /api/tags) with user-scoped tags
- Fixed priority sort to use CASE WHEN numeric mapping (high=1, medium=2, low=3)
- Fixed potential double-join when tag filter + search both active
- Fixed tag_names extraction in update_task to avoid setting invalid attribute on Task model

**Frontend:**
- Created PriorityBadge component with color-coded badges (red/yellow/blue)
- Created TagSelector component with autocomplete, create-new, and chip display
- Created FilterBar component with search, status/priority/tag filters, sort controls
- Extended TaskForm with priority dropdown, due date picker, and tag selector
- Extended TaskItem with priority badge, tag chips, due date display, overdue indicator
- Updated TaskList to manage filter/sort state and pass to API (removed client-side sort)

**Note:** T002/T003 (database migration execution) still pending - requires running against Neon PostgreSQL. Also, search (Phase 7/US5) backend + frontend is also implemented as a bonus since FilterBar includes search and backend already handles the `q` parameter.

## Outcome

- ✅ Impact: Phases 1-6 fully implemented (T001-T050, except T002/T003 migration execution)
- 🧪 Tests: None (not requested in spec)
- 📁 Files: 12 files modified/created
- 🔁 Next prompts: Run database migration (T002/T003), implement phases 7-11
- 🧠 Reflection: Event publisher needed to be decoupled from Dapr SDK for phases that don't need event infrastructure. Priority sort required CASE WHEN mapping since string comparison gives wrong alphabetical order.

## Evaluation notes (flywheel)

- Failure modes observed: tag_names was being set as attribute on Task model via setattr loop; double-join when tag filter and search both active
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run migration and verify end-to-end
