# Tasks: Authentication & JWT Security Integration

**Input**: Design documents from `/specs/002-auth-jwt-security/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/auth-endpoints.md, quickstart.md

**Tests**: Not explicitly requested in the feature specification. No test tasks generated.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/` (FastAPI) and `frontend/` (Next.js) at repository root
- Backend auth module: `backend/auth.py`
- Frontend auth config: `frontend/src/lib/auth.ts`, `frontend/src/lib/auth-client.ts`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the Next.js frontend project, install Better Auth, add backend JWT dependencies

- [x] T001 Initialize Next.js project in `frontend/` with App Router using `npx create-next-app@latest frontend --ts --app --tailwind --eslint --src-dir --no-import-alias`
- [x] T002 Install Better Auth and JWT plugin in `frontend/`: `npm install better-auth`
- [x] T003 [P] Create `frontend/.env.example` with placeholder variables: `BETTER_AUTH_SECRET`, `DATABASE_URL`, `NEXT_PUBLIC_API_URL=http://localhost:8000`
- [x] T004 [P] Add `PyJWT`, `cryptography`, and `httpx` to `backend/requirements.txt`
- [x] T005 [P] Add `BETTER_AUTH_URL=http://localhost:3000` to `backend/.env.example`
- [x] T006 [P] Add `frontend/.env.local` and `frontend/node_modules/` to `.gitignore`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Better Auth server configuration, auth database tables, JWT verification module — MUST be complete before ANY user story

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Create Better Auth server configuration in `frontend/src/lib/auth.ts`: import `betterAuth` from `better-auth`, configure with Neon PostgreSQL `DATABASE_URL`, enable the JWT plugin via `jwt()` from `better-auth/plugins`, define `definePayload` to include `sub` (user.id), `email` (user.email) — export the `auth` instance
- [x] T008 Create Better Auth client instance in `frontend/src/lib/auth-client.ts`: import `createAuthClient` from `better-auth/react`, configure with `baseURL` from environment, enable `jwtClient()` plugin — export `authClient` with `useSession`, `signIn`, `signUp`, `signOut` methods
- [x] T009 Create Better Auth API route handler in `frontend/src/app/api/auth/[...all]/route.ts`: import `auth` from `@/lib/auth`, export GET and POST handlers using `auth.handler(request)` pattern
- [x] T010 Run Better Auth database migration: `npx @better-auth/cli migrate` to create `user`, `session`, `account`, `verification`, and `jwks` tables in the Neon PostgreSQL database
- [x] T011 Create `backend/auth.py` with JWKS-based JWT verification: implement `fetch_jwks(url)` function using `httpx` to GET `BETTER_AUTH_URL/api/auth/jwks`, parse the JWKS response to extract the public key, cache the key in a module-level variable with a `kid`-based refresh strategy
- [x] T012 Implement `get_current_user` FastAPI dependency in `backend/auth.py`: extract `Bearer <token>` from `Authorization` header, decode and verify the JWT using `PyJWT` with the cached JWKS public key (supporting EdDSA/Ed25519 algorithm), return `{"user_id": payload["sub"], "email": payload["email"]}`, raise `HTTPException(401, "Not authenticated")` for missing header and `HTTPException(401, "Invalid or expired token")` for invalid/expired/tampered tokens
- [x] T013 Update `backend/main.py` CORS configuration: replace `allow_origins=["*"]` with explicit origin list including `http://localhost:3000` (frontend dev server), keep `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`

**Checkpoint**: Better Auth is configured and serves `/api/auth/jwks`. Backend can fetch the public key and verify JWTs. Frontend auth client is initialized. Auth database tables exist.

---

## Phase 3: User Story 1 — Sign Up for a New Account (Priority: P1) MVP

**Goal**: A new visitor creates an account with email and password. The system creates the account and signs them in immediately with a JWT credential.

**Independent Test**: Navigate to `/signup`, submit a valid email and password (8+ chars), verify the account is created and the user is signed in with a JWT token retrievable via `getSession()`.

### Implementation for User Story 1

- [x] T014 [US1] Create sign-up page in `frontend/src/app/(auth)/signup/page.tsx`: build a form with email input, password input (min 8 chars), and submit button. On submit, call `authClient.signUp.email({ email, password, name: email })`. On success, redirect to the protected area (`/`). On error (duplicate email, validation failure), display error message. Mark as `"use client"`.
- [x] T015 [US1] Create auth layout in `frontend/src/app/(auth)/layout.tsx`: minimal centered layout for sign-up and sign-in pages, no auth guard (these pages must be accessible to unauthenticated users)
- [ ] T016 [US1] Verify sign-up flow end-to-end: create an account via the sign-up page, confirm the `user` table has the new record in Neon PostgreSQL, confirm `getSession()` returns a valid session with a JWT in the `set-auth-jwt` response header

**Checkpoint**: Users can create accounts. Duplicate emails are rejected. New users are immediately signed in with a JWT.

---

## Phase 4: User Story 2 — Sign In to an Existing Account (Priority: P1)

**Goal**: A returning user signs in with email and password. The system verifies credentials and issues a JWT token.

**Independent Test**: Create an account via sign-up, sign out, then sign in again. Verify a new JWT is issued and the user can retrieve their session.

### Implementation for User Story 2

- [x] T017 [US2] Create sign-in page in `frontend/src/app/(auth)/signin/page.tsx`: build a form with email input, password input, and submit button. On submit, call `authClient.signIn.email({ email, password })`. On success, redirect to `/`. On error, display generic "Invalid credentials" message (never reveal which field is wrong). Mark as `"use client"`.
- [x] T018 [US2] Add navigation links between sign-up and sign-in pages: on `/signup` add "Already have an account? Sign in" link, on `/signin` add "Don't have an account? Sign up" link
- [ ] T019 [US2] Verify sign-in flow end-to-end: sign in with valid credentials (200 + JWT), sign in with wrong password (generic error), sign in with non-existent email (same generic error)

**Checkpoint**: Returning users can sign in. Invalid credentials show generic error. JWT is issued on success.

---

## Phase 5: User Story 3 — Access Protected API with Valid Token (Priority: P1)

**Goal**: Authenticated users make API requests with JWT. Backend verifies the token and returns user-scoped data. Invalid/missing tokens get 401.

**Independent Test**: Sign in, make a `GET /api/todos` request with the JWT. Verify 200 response. Then try without token (401), with tampered token (401), and with expired token (401).

### Implementation for User Story 3

- [x] T020 [US3] Update `backend/routers/todos.py` router prefix from `/users/{user_id}/todos` to `/todos` per contracts/auth-endpoints.md route transition (R7)
- [x] T021 [US3] Update `POST /api/todos` endpoint in `backend/routers/todos.py`: remove `user_id` path parameter, add `current_user: dict = Depends(get_current_user)` dependency, extract `user_id` from `current_user["user_id"]`, create task with authenticated user's identity
- [x] T022 [US3] Update `GET /api/todos` (list) endpoint in `backend/routers/todos.py`: remove `user_id` path parameter, add `current_user: dict = Depends(get_current_user)` dependency, filter tasks by `current_user["user_id"]`
- [x] T023 [US3] Update `GET /api/todos/{task_id}` (single) endpoint in `backend/routers/todos.py`: remove `user_id` path parameter, add `current_user: dict = Depends(get_current_user)` dependency, query by `task_id AND user_id` from authenticated user
- [x] T024 [US3] Update `PATCH /api/todos/{task_id}` endpoint in `backend/routers/todos.py`: remove `user_id` path parameter, add `current_user: dict = Depends(get_current_user)` dependency, extract `user_id` from token
- [x] T025 [US3] Update `DELETE /api/todos/{task_id}` endpoint in `backend/routers/todos.py`: remove `user_id` path parameter, add `current_user: dict = Depends(get_current_user)` dependency, extract `user_id` from token
- [x] T026 [US3] Create API client helper in `frontend/src/lib/api.ts`: implement a `fetchWithAuth` function that retrieves the JWT from `authClient.getSession()` (extracting from the `set-auth-jwt` header or `authClient.$fetch` response), attaches it as `Authorization: Bearer <token>` header, and makes requests to `NEXT_PUBLIC_API_URL`
- [ ] T027 [US3] Verify protected API access end-to-end: sign in, create a task via `POST /api/todos` with JWT (201), list tasks via `GET /api/todos` (200, user-scoped), try without token (401), try with tampered token (401)

**Checkpoint**: All 5 CRUD endpoints require JWT authentication. User identity comes from token, not URL. 401 for missing/invalid/expired tokens. User data is isolated by authenticated identity.

---

## Phase 6: User Story 4 — Sign Out (Priority: P2)

**Goal**: Authenticated user signs out. Session is cleared on the frontend. Subsequent API requests are rejected.

**Independent Test**: Sign in, verify API access works, sign out, verify API requests now return 401.

### Implementation for User Story 4

- [x] T028 [US4] Implement sign-out functionality: add a sign-out button/action in the protected area that calls `authClient.signOut()`, clears the local session/JWT state, and redirects to `/signin`
- [ ] T029 [US4] Verify sign-out flow: sign in, access protected resource (200), sign out, attempt to access protected resource (401 or redirect to sign-in)

**Checkpoint**: Users can sign out. Post-sign-out API requests are rejected. User is redirected to sign-in page.

---

## Phase 7: User Story 5 — Redirect Unauthenticated Users (Priority: P2)

**Goal**: Unauthenticated users attempting to access protected pages are redirected to sign-in. After sign-in, they return to the originally requested page.

**Independent Test**: Access `/` (protected) without being signed in → redirected to `/signin`. Sign in → redirected back to `/`.

### Implementation for User Story 5

- [x] T030 [US5] Create Next.js middleware in `frontend/src/middleware.ts`: check for active session on protected routes (all routes except `/signin`, `/signup`, `/api/auth/*`), redirect unauthenticated users to `/signin` with a `callbackUrl` query parameter preserving the originally requested URL
- [x] T031 [US5] Create protected layout in `frontend/src/app/(protected)/layout.tsx`: use `authClient.useSession()` to verify auth state on the client side, show loading state while checking, redirect to `/signin` if not authenticated
- [x] T032 [US5] Update sign-in page (`frontend/src/app/(auth)/signin/page.tsx`) to read `callbackUrl` from query params: after successful sign-in, redirect to `callbackUrl` if present, otherwise redirect to `/`
- [x] T033 [US5] Create a basic protected home page in `frontend/src/app/(protected)/page.tsx`: display the authenticated user's email, a sign-out button, and a placeholder for the todo list UI (todo list UI is a future feature)
- [ ] T034 [US5] Verify redirect flow: access `/` without auth → redirected to `/signin?callbackUrl=/`, sign in → redirected back to `/`, access `/signup` without auth → page loads normally (no redirect)

**Checkpoint**: Unauthenticated access to protected pages redirects to sign-in. Post-sign-in redirect returns user to original page. Auth pages remain accessible without authentication.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Security hardening, error handling, cross-cutting improvements

- [x] T035 [P] Ensure `backend/auth.py` fails securely: if `BETTER_AUTH_URL` is not set or JWKS endpoint is unreachable, all protected requests must be rejected with 401 (never allow unauthenticated access as fallback) — per spec edge case EC-002
- [x] T036 [P] Add `BETTER_AUTH_URL` environment variable validation in `backend/auth.py`: raise `RuntimeError` at import time if the variable is missing, preventing the app from starting without auth configuration
- [x] T037 [P] Install backend dependencies: activate venv and run `pip install -r requirements.txt` to install PyJWT, cryptography, httpx
- [ ] T038 Run quickstart.md verification checklist: test all items — sign-up creates account, sign-in issues JWT, wrong password shows generic error, duplicate email rejected, valid JWT gets 200, missing token gets 401, invalid token gets 401, expired token gets 401, user A cannot see user B's tasks, user A cannot modify user B's tasks, old routes no longer exist, new routes work with JWT, sign-out clears session, unauthenticated redirect works, JWKS endpoint returns public keys

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **US1 Sign Up (Phase 3)**: Depends on Foundation (T007-T013)
- **US2 Sign In (Phase 4)**: Depends on Foundation (T007-T013) — can run parallel with US1
- **US3 Protected API (Phase 5)**: Depends on Foundation — requires at least one account to exist (logically after US1, but can be implemented in parallel)
- **US4 Sign Out (Phase 6)**: Depends on Foundation — requires sign-in to work (logically after US2)
- **US5 Redirect (Phase 7)**: Depends on Foundation — requires sign-in page to exist (logically after US2)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (Sign Up)**: After Foundation — no dependencies on other stories
- **US2 (Sign In)**: After Foundation — no dependencies on other stories (sign-up can be done via API/DB for testing)
- **US3 (Protected API)**: After Foundation — no dependencies on other stories (backend-focused, tokens can be obtained manually)
- **US4 (Sign Out)**: After Foundation — benefits from US2 being done but not strictly required
- **US5 (Redirect)**: After Foundation — benefits from US2 being done but not strictly required

### Within Each User Story

- Configuration before UI
- Backend before frontend integration
- Core logic before edge-case handling
- Story complete before moving to next priority

### Parallel Opportunities

- T003, T004, T005, T006 can run in parallel (different files, Phase 1)
- T011 and T012 can run in parallel (different files: `backend/auth.py`)
- US1 (Phase 3) and US2 (Phase 4) can run in parallel (different pages)
- US4 (Phase 6) and US5 (Phase 7) can run in parallel (different concerns)
- T035, T036, T037 can run in parallel (different concerns, Phase 8)

---

## Parallel Example: Phase 1 Setup

```bash
# Launch all parallel setup tasks together:
Task: "Create frontend/.env.example" (T003)
Task: "Add PyJWT, cryptography, httpx to backend/requirements.txt" (T004)
Task: "Add BETTER_AUTH_URL to backend/.env.example" (T005)
Task: "Add frontend/.env.local and node_modules to .gitignore" (T006)
```

## Parallel Example: User Stories After Foundation

```bash
# After Phase 2 is complete, frontend stories can start in parallel:
Task: "Create sign-up page (US1, T014)"
Task: "Create sign-in page (US2, T017)"

# Backend route migration (US3) can proceed independently:
Task: "Update router prefix to /todos (T020)"
Task: "Update POST endpoint with auth dependency (T021)"
# ... remaining endpoints sequentially within todos.py
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 + 3)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: US1 — Sign Up
4. Complete Phase 4: US2 — Sign In
5. Complete Phase 5: US3 — Protected API Access
6. **STOP and VALIDATE**: Users can create accounts, sign in, and access their own tasks via authenticated API calls. This is the core security MVP.

### Incremental Delivery

1. Setup + Foundation → Better Auth configured, JWKS working, backend can verify JWTs
2. Add US1 (Sign Up) → Test account creation → Verify JWT issuance
3. Add US2 (Sign In) → Test returning user flow → Verify credential validation
4. Add US3 (Protected API) → Test authenticated CRUD → Verify user isolation (MVP!)
5. Add US4 (Sign Out) → Test session clearing → Verify post-logout rejection
6. Add US5 (Redirect) → Test unauthenticated redirect → Verify callback URL
7. Polish → Security hardening + full verification checklist
8. Run full quickstart.md checklist

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable after Foundation
- No automated test tasks generated — spec did not request automated tests
- Total: 38 tasks across 8 phases
  - Phase 1 (Setup): 6 tasks
  - Phase 2 (Foundational): 7 tasks
  - Phase 3 (US1 Sign Up): 3 tasks
  - Phase 4 (US2 Sign In): 3 tasks
  - Phase 5 (US3 Protected API): 8 tasks
  - Phase 6 (US4 Sign Out): 2 tasks
  - Phase 7 (US5 Redirect): 5 tasks
  - Phase 8 (Polish): 4 tasks
- US3 (Protected API) has the most tasks because it requires modifying all 5 existing CRUD endpoints plus creating the frontend API client
- All backend endpoint changes in US3 modify `backend/routers/todos.py` — execute T020-T025 sequentially within this file
- Frontend pages in US1 and US2 can be built in parallel (different files)
