# Implementation Plan: Authentication & JWT Security Integration

**Branch**: `002-auth-jwt-security` | **Date**: 2026-01-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-auth-jwt-security/spec.md`

## Summary

Integrate user authentication into the Todo application using Better Auth
(Next.js frontend) for account management and JWT token issuance, with
FastAPI backend verification via JWKS public keys. This replaces the
trusted `user_id` path parameter from feature 001 with cryptographically
verified identity extracted from Bearer tokens. The API routes transition
from `/api/users/{user_id}/todos` to `/api/todos`.

## Technical Context

**Language/Version**: Python 3.11+ (backend), Node.js / Next.js 16+ (frontend)
**Primary Dependencies**: Better Auth + JWT plugin (frontend), PyJWT + cryptography (backend), FastAPI, SQLModel
**Storage**: Neon Serverless PostgreSQL (shared database — Better Auth tables + tasks table)
**Testing**: Manual verification via curl; pytest for JWT verification unit tests
**Target Platform**: Linux server (backend API), Vercel-compatible (frontend)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: JWT verification < 10ms (cached JWKS); no per-request DB calls for auth
**Constraints**: Stateless backend auth; no session store on backend; JWKS-based verification
**Scale/Scope**: Multi-user task management; hackathon evaluation scope

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. End-to-End Correctness | PASS | Auth flow verified across frontend (Better Auth) → backend (PyJWT) → database (user-scoped queries) |
| II. User Data Isolation | PASS | JWT `sub` claim = user_id; all queries filter by authenticated identity; 401 for invalid tokens |
| III. Spec-Driven Development | PASS | Spec at spec.md; plan derived from spec; research.md validates assumptions |
| IV. Framework-Idiomatic | PASS | Better Auth for Next.js auth (Principle IV); FastAPI `Depends()` injection for verification (R6) |
| V. RESTful API Design | PASS | Routes simplified to `/api/todos`; user identity from token, not path (R7) |
| VI. Secret Management | PASS (updated) | No shared secret needed — JWKS public key fetched at runtime (R1). `BETTER_AUTH_URL` in .env |

**Gate result**: PASS — all principles satisfied. Note: Constitution Principle II mentions
"shared secret stored in environment variables" but research R1 found Better Auth uses
asymmetric JWKS instead. The JWKS approach is stronger (no secret sharing) and satisfies
the spirit of the principle. Constitution update recommended.

## Project Structure

### Documentation (this feature)

```text
specs/002-auth-jwt-security/
├── plan.md              # This file
├── research.md          # Phase 0 output — 7 research decisions
├── data-model.md        # Phase 1 output — Better Auth + Task entity relationships
├── quickstart.md        # Phase 1 output — Auth setup and verification guide
├── contracts/
│   └── auth-endpoints.md # Phase 1 output — API route changes and error contracts
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── main.py              # FastAPI app — updated CORS for frontend origin
├── database.py          # Async engine (unchanged)
├── models.py            # SQLModel Task model (unchanged)
├── auth.py              # NEW: JWKS fetcher + JWT verification dependency
├── routers/
│   └── todos.py         # UPDATED: /api/todos routes with JWT auth dependency
├── requirements.txt     # UPDATED: add PyJWT, cryptography, httpx
├── .env.example         # UPDATED: add BETTER_AUTH_URL
└── .env                 # Local secrets (gitignored)

frontend/
├── package.json         # Next.js app with better-auth dependency
├── .env.local           # BETTER_AUTH_SECRET, DATABASE_URL (gitignored)
├── src/
│   ├── lib/
│   │   └── auth.ts      # Better Auth server config with JWT plugin
│   ├── lib/
│   │   └── auth-client.ts # Better Auth client instance
│   ├── app/
│   │   ├── api/auth/[...all]/route.ts  # Better Auth API handler
│   │   ├── (auth)/
│   │   │   ├── signin/page.tsx   # Sign-in page
│   │   │   └── signup/page.tsx   # Sign-up page
│   │   └── (protected)/
│   │       └── layout.tsx        # Auth-guarded layout
│   └── middleware.ts    # Redirect unauthenticated users
└── next.config.ts
```

**Structure Decision**: Web application with `frontend/` (Next.js) and `backend/`
(FastAPI). Better Auth runs inside Next.js and manages its own database tables in
the same Neon PostgreSQL instance. The backend does NOT import or depend on Better
Auth — it only fetches the JWKS public key to verify tokens.

## Key Design Decisions

### D1: JWKS Asymmetric Verification, Not Shared Secret (Research R1)

Better Auth's JWT plugin uses asymmetric key pairs (EdDSA Ed25519) and exposes a
JWKS endpoint at `/api/auth/jwks`. The backend fetches the public key from this
endpoint to verify tokens. This eliminates the need for a shared secret between
services. The constitution's reference to "shared secret" is superseded by this
stronger approach.

**Trade-off**: Requires the backend to fetch the JWKS endpoint (adds a network
dependency). Mitigated by caching the public key and only refreshing on `kid` mismatch.

### D2: Token Retrieval via getSession() Header (Research R2)

The frontend obtains the JWT from the `set-auth-jwt` response header when calling
`authClient.getSession()`. This is Better Auth's recommended approach. The token
is stored in memory and attached to API requests as `Authorization: Bearer <token>`.

### D3: PyJWT with cryptography for Backend Verification (Research R3)

The backend uses `PyJWT` with the `cryptography` package to verify JWTs against
the JWKS public key. `PyJWT` is the most widely-used Python JWT library and
supports EdDSA (Ed25519) via `cryptography`.

### D4: Minimal JWT Payload (Research R4)

JWT payload includes only `sub` (user ID), `email`, `iat`, and `exp`. This
minimizes token size and limits PII exposure while providing the backend with
the user identity needed for data scoping.

### D5: FastAPI Dependency Injection for Auth (Research R6)

JWT verification is implemented as a FastAPI dependency (`Depends(get_current_user)`),
not middleware. This is idiomatic FastAPI, allows per-route opt-in, and supports
easy testing via dependency overrides.

### D6: Route Transition — Breaking Change from Feature 001 (Research R7)

API routes change from `/api/users/{user_id}/todos` to `/api/todos`. The `user_id`
is extracted from the JWT `sub` claim. This is a breaking change from feature 001
but is necessary: having `user_id` in both the URL and the token creates a
security risk (mismatch) and a confusing API design.

## API Endpoint Summary

### Backend (FastAPI) — After Auth Integration

| Method | Path                    | Auth     | Status | Description       |
|--------|-------------------------|----------|--------|-------------------|
| POST   | /api/todos              | Required | 201    | Create task       |
| GET    | /api/todos              | Required | 200    | List user's tasks |
| GET    | /api/todos/{task_id}    | Required | 200    | Get single task   |
| PATCH  | /api/todos/{task_id}    | Required | 200    | Update task       |
| DELETE | /api/todos/{task_id}    | Required | 204    | Delete task       |

Error responses: 401 (not authenticated / invalid token), 404 (not found / not owner),
422 (validation), 500 (server error).

### Frontend (Better Auth — auto-generated)

| Method | Path                        | Description                   |
|--------|-----------------------------|-------------------------------|
| POST   | /api/auth/sign-up/email     | Create account                |
| POST   | /api/auth/sign-in/email     | Sign in                       |
| POST   | /api/auth/sign-out          | Sign out                      |
| GET    | /api/auth/get-session       | Get session + JWT in header   |
| GET    | /api/auth/jwks              | Public keys for verification  |

Full contract: [contracts/auth-endpoints.md](./contracts/auth-endpoints.md)

## Implementation Phases

### Phase 1: Frontend — Better Auth Setup
- Initialize Next.js project in `frontend/`
- Install `better-auth` and configure the JWT plugin
- Configure Better Auth server instance with Neon PostgreSQL
- Run `npx @better-auth/cli migrate` to create auth tables
- Create the API route handler at `/api/auth/[...all]/route.ts`
- Configure JWT payload to include `sub`, `email`, `iat`, `exp`
- Set `BETTER_AUTH_SECRET` in `.env.local`

### Phase 2: Frontend — Auth Pages & Client
- Create the Better Auth client instance (`auth-client.ts`)
- Build sign-up page with email + password form
- Build sign-in page with email + password form
- Implement sign-out functionality
- Add auth middleware to redirect unauthenticated users
- Create protected layout that guards authenticated pages

### Phase 3: Frontend — API Integration
- Create an API client/helper that attaches JWT to requests
- Retrieve JWT from `getSession()` response header (`set-auth-jwt`)
- Store token in memory for use in API calls
- Attach `Authorization: Bearer <token>` header to all backend requests

### Phase 4: Backend — JWT Verification Module
- Add `PyJWT`, `cryptography`, `httpx` to `requirements.txt`
- Create `backend/auth.py` with:
  - JWKS fetcher: fetch public key from `BETTER_AUTH_URL/api/auth/jwks`
  - Key caching: cache public key, refresh on `kid` mismatch
  - `get_current_user` dependency: extract Bearer token, verify with JWKS,
    return `{"user_id": sub, "email": email}`
- Add `BETTER_AUTH_URL` to `.env.example`

### Phase 5: Backend — Route Migration
- Update `routers/todos.py`:
  - Change prefix from `/users/{user_id}/todos` to `/todos`
  - Remove `user_id` path parameter from all endpoints
  - Add `Depends(get_current_user)` to all endpoints
  - Extract `user_id` from the authenticated user dict
- Update `main.py` CORS to allow frontend origin
- Verify all queries still filter by `user_id` (from token, not path)

### Phase 6: Integration Testing & Verification
- Start both frontend and backend servers
- Test sign-up flow → verify account creation
- Test sign-in flow → verify JWT issuance
- Test authenticated API call → verify user-scoped data access
- Test with missing token → verify 401 response
- Test with expired/tampered token → verify 401 response
- Test cross-user isolation → verify user A cannot access user B's tasks
- Test sign-out → verify subsequent requests rejected

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| JWKS instead of shared secret | Better Auth natively uses asymmetric keys | Shared secret not supported by Better Auth JWT plugin |

## Artifacts Generated

| Artifact | Path | Status |
|----------|------|--------|
| Research | specs/002-auth-jwt-security/research.md | Complete (7 decisions) |
| Data Model | specs/002-auth-jwt-security/data-model.md | Complete |
| Auth Contracts | specs/002-auth-jwt-security/contracts/auth-endpoints.md | Complete |
| Quickstart | specs/002-auth-jwt-security/quickstart.md | Complete |
| Plan | specs/002-auth-jwt-security/plan.md | Complete (this file) |
