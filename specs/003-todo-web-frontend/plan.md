# Implementation Plan: Todo Web Frontend Application

**Branch**: `003-todo-web-frontend` | **Date**: 2026-01-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-todo-web-frontend/spec.md`

## Summary

Build a responsive web frontend for task management using Next.js 16+ with App Router.
The application provides authentication flows (sign-up, sign-in, sign-out) via Better Auth
and a protected dashboard for CRUD operations on user-scoped tasks. All data operations
go through the REST API (Feature 001), with JWT tokens attached automatically to every
request. The frontend uses client-side data fetching, React local state for task data,
and Tailwind CSS for responsive styling.

## Technical Context

**Language/Version**: TypeScript 5.x with Next.js 16+
**Primary Dependencies**: Next.js, React, Better Auth, Tailwind CSS
**Storage**: None (frontend consumes REST API; no direct database access)
**Testing**: Manual E2E testing per quickstart.md
**Target Platform**: Modern web browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (frontend only for this feature)
**Performance Goals**: 3-second load time, responsive UI on mobile and desktop
**Constraints**: No offline support, no real-time updates, no direct database access
**Scale/Scope**: Single authenticated user, task list UI, CRUD operations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. End-to-End Correctness | PASS | Frontend integrates with existing backend API; data round-trips verified via quickstart.md checklist |
| II. User Data Isolation | PASS | JWT attached to all API requests (R3); backend enforces user-scoping; frontend shows only user's tasks |
| III. Spec-Driven Development | PASS | Spec exists at spec.md; plan derived from spec; tasks will follow |
| IV. Framework-Idiomatic | PASS | Next.js App Router, client components for interactivity, Tailwind for styling |
| V. RESTful API Design | PASS | Frontend consumes existing RESTful `/api/todos` endpoints |
| VI. Secret Management | PASS | API URL via `NEXT_PUBLIC_API_URL`; Better Auth secrets in `.env.local` |

**Gate result**: PASS — all principles satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/003-todo-web-frontend/
├── plan.md              # This file
├── research.md          # 7 research decisions (R1-R7)
├── quickstart.md        # Setup and verification guide
├── contracts/
│   └── api-client.md    # TypeScript interfaces and API methods
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (frontend/)

```text
frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── layout.tsx       # Auth pages layout (no auth guard)
│   │   │   ├── signin/
│   │   │   │   └── page.tsx     # Sign-in form
│   │   │   └── signup/
│   │   │       └── page.tsx     # Sign-up form
│   │   ├── (protected)/
│   │   │   ├── layout.tsx       # Protected layout (auth guard)
│   │   │   └── page.tsx         # Dashboard with task list
│   │   ├── api/
│   │   │   └── auth/
│   │   │       └── [...all]/
│   │   │           └── route.ts # Better Auth API handler
│   │   ├── globals.css          # Global styles + Tailwind
│   │   └── layout.tsx           # Root layout
│   ├── components/
│   │   ├── TaskList.tsx         # Task list component
│   │   ├── TaskItem.tsx         # Single task row
│   │   ├── TaskForm.tsx         # Create/edit task form
│   │   └── EmptyState.tsx       # No tasks placeholder
│   ├── lib/
│   │   ├── auth.ts              # Better Auth server config
│   │   ├── auth-client.ts       # Better Auth client instance
│   │   └── api.ts               # API client with JWT injection
│   └── middleware.ts            # Auth redirect middleware
├── .env.local                   # Environment variables (gitignored)
├── .env.example                 # Environment template
└── package.json
```

**Structure Decision**: Web application frontend-only layout. The `frontend/` directory
was initialized in Feature 002. This feature adds task management components and completes
the authentication UI integration.

## Key Design Decisions

### D1: Client-Side Data Fetching (Research R1)

Use client-side data fetching with React hooks instead of Server Components for task data.
Tasks are user-specific authenticated content that changes frequently with CRUD operations.
Client-side fetching provides simpler state management after mutations.

### D2: No Global State Library (Research R2)

Use React Context for auth state (via Better Auth `useSession`) and local component state
for task data. The application is simple enough that Redux/Zustand would be over-engineering.
Task list is refetched on dashboard mount, ensuring fresh data.

### D3: Thin API Client with JWT Injection (Research R3)

Create a minimal `api.ts` module wrapping `fetch` that automatically attaches the JWT token
from Better Auth session. Centralizes error handling for 401 responses (redirect to sign-in).

### D4: Component-Level Loading/Error States (Research R4)

Each data-fetching component manages `isLoading`, `error`, and `data` states locally.
Simple pattern that covers all use cases without external libraries.

### D5: Tailwind CSS for Responsive Design (Research R5)

Use Tailwind CSS (already installed) for all styling. Mobile-first responsive design
with breakpoints at 768px (md) and 1024px (lg). No additional UI component libraries.

### D6: Native Confirmation for Delete (Research R6)

Use `window.confirm()` for delete confirmation. Simple, familiar to users, no additional
component complexity. Acceptable for hackathon MVP scope.

## Implementation Phases

### Phase 1: Fix Better Auth Integration

The Better Auth route handler from Feature 002 needs debugging. The `/api/auth/*` routes
are returning 404 instead of handling authentication.

- Verify Better Auth configuration in `frontend/src/lib/auth.ts`
- Ensure route handler at `frontend/src/app/api/auth/[...all]/route.ts` is correct
- Test that `/api/auth/get-session` returns valid response
- Confirm JWKS endpoint at `/api/auth/jwks` is working

### Phase 2: Complete Authentication Pages

Build on the scaffolded auth pages from Feature 002:

- Verify sign-up page form validation and error handling
- Verify sign-in page with callbackUrl redirect
- Add proper error message display for auth failures
- Ensure navigation links between sign-up and sign-in work

### Phase 3: Task List UI

Build the main dashboard with task display:

- Create `TaskList` component that fetches and displays tasks
- Create `TaskItem` component for individual task rows
- Create `EmptyState` component for when no tasks exist
- Implement loading state while fetching
- Implement error state with retry option

### Phase 4: Task Create Form

Add task creation functionality:

- Create `TaskForm` component with title and description inputs
- Implement form validation (title required, max lengths)
- Handle form submission with API call
- Refresh task list after successful creation
- Show loading state during submission

### Phase 5: Task Complete Toggle

Add task completion functionality:

- Add checkbox/toggle to TaskItem for completion status
- Implement optimistic UI update (optional) or loading state
- Call PATCH API with `is_completed` update
- Refresh task list after successful update

### Phase 6: Task Edit and Delete

Complete CRUD operations:

- Add edit mode to TaskItem (inline or modal)
- Implement title/description editing with validation
- Add delete button with confirmation dialog
- Handle delete API call and remove from list
- Proper error handling for all operations

### Phase 7: Final Polish and Verification

Complete all requirements and verify:

- Responsive design testing (mobile, tablet, desktop)
- Loading states for all async operations
- Error handling for all failure scenarios
- Run full quickstart.md verification checklist
- User isolation testing (multi-user scenario)

## Artifacts Generated

| Artifact | Path | Status |
|----------|------|--------|
| Research | specs/003-todo-web-frontend/research.md | Complete (7 decisions) |
| API Contract | specs/003-todo-web-frontend/contracts/api-client.md | Complete |
| Quickstart | specs/003-todo-web-frontend/quickstart.md | Complete |
| Plan | specs/003-todo-web-frontend/plan.md | Complete (this file) |

## Complexity Tracking

No constitution violations. No complexity justifications needed.
