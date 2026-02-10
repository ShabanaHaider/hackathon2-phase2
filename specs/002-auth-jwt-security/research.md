# Research: Authentication & JWT Security Integration

**Feature**: `002-auth-jwt-security`
**Date**: 2026-01-28

## R1: Better Auth JWT Mechanism — JWKS, Not Shared Secret

**Decision**: Use Better Auth's JWT plugin with asymmetric key verification
via JWKS endpoint, not a symmetric shared secret.

**Rationale**: Better Auth generates asymmetric key pairs (EdDSA Ed25519 by
default) and exposes a JWKS endpoint at `/api/auth/jwks`. The backend fetches
the public key from this endpoint to verify tokens. This eliminates the need
to share a secret between frontend and backend, improving security posture.

**Alternatives considered**:
- Symmetric HMAC secret: Simpler but requires sharing a secret between both
  services; Better Auth does not natively support this for JWT.
- Session-based verification via API call: Requires the backend to call
  Better Auth's session endpoint for every request; adds latency and coupling.

**Impact on spec**: The spec assumed a "shared secret" for signing/verification.
The actual mechanism is asymmetric (JWKS). The constitutional principle
(FR-013: "shared secret stored in environment variables") is superseded by
JWKS — no shared secret is needed. The BETTER_AUTH_URL environment variable
is needed instead, pointing to the frontend's auth endpoint.

## R2: Token Retrieval Strategy

**Decision**: Use `authClient.getSession()` with the `set-auth-jwt` response
header to obtain the JWT on the frontend, then store it for use in API calls.

**Rationale**: Better Auth's JWT plugin returns a JWT in the `set-auth-jwt`
header when `getSession()` is called. This is the recommended approach per
the official docs. The `authClient.token()` method is an alternative but
requires an additional API call.

**Alternatives considered**:
- `authClient.token()`: Dedicated endpoint, but requires a separate call.
- Cookie-based sessions: Would require the backend to proxy via the frontend;
  not suitable for cross-origin API calls to a Python backend.

## R3: Backend JWT Verification — python-jose with JWKS

**Decision**: Use `python-jose` (or `PyJWT` with `cryptography`) to verify
JWTs on the FastAPI backend. Fetch the public key from Better Auth's JWKS
endpoint and cache it.

**Rationale**: The backend needs to verify JWTs without calling the frontend.
JWKS-based verification is stateless and standard. The public key can be
cached and only refreshed when a new `kid` is encountered.

**Alternatives considered**:
- `PyJWT` + `cryptography`: Equally viable; `PyJWT` is more widely used.
  **Selected**: Use `PyJWT` with `cryptography` for broader ecosystem support.
- Call Better Auth's session API from backend: Adds latency, coupling,
  and defeats the purpose of stateless JWT verification.

## R4: JWT Payload Structure

**Decision**: Configure Better Auth's `definePayload` to include `sub`
(user ID), `email`, `iat`, and `exp`. Keep the payload minimal.

**Rationale**: The backend only needs the user ID to scope data access
(matching the existing `user_id` field on tasks). Email is included for
logging/debugging. Standard JWT claims (`sub`, `iat`, `exp`) follow RFC 7519.

**Alternatives considered**:
- Full user object in payload: Default Better Auth behavior; too much data,
  larger tokens, potential PII exposure.
- User ID only: Minimal but loses email for debugging context.

## R5: Token Expiration Duration

**Decision**: 15 minutes (Better Auth default), with session-based refresh
handled by Better Auth on the frontend.

**Rationale**: Short-lived tokens limit the window for token theft. Better
Auth's session management handles refreshing transparently. The backend
only verifies; it never issues or refreshes tokens.

**Alternatives considered**:
- 1 hour: Fewer refreshes but larger theft window.
- 5 minutes: More secure but may cause friction with frequent refreshes.

## R6: FastAPI Dependency Injection vs Middleware

**Decision**: Use FastAPI dependency injection (`Depends`) for JWT
verification, not middleware.

**Rationale**: Dependency injection is idiomatic FastAPI (Constitution
Principle IV). It allows per-route opt-in, clear function signatures,
and testability via dependency overrides. Middleware would apply globally
and require exclusion logic for public routes.

**Alternatives considered**:
- Global middleware: Simpler for "protect everything" but harder to
  exclude public routes (health checks, docs).

## R7: Route Transition — user_id from Token, Not Path

**Decision**: Modify the todos router to extract `user_id` from the JWT
token instead of the URL path. The path changes from
`/api/users/{user_id}/todos` to `/api/todos` with user identity derived
from the token.

**Rationale**: With authentication, the user_id in the URL is redundant and
creates a security risk (URL user_id could differ from token user_id). The
authenticated user's identity should be the sole source of truth.

**Alternatives considered**:
- Keep `user_id` in path and validate against token: Extra validation step,
  confusing API design — why put identity in the URL if it's in the token?
- Keep `user_id` in path, ignore token: Defeats the purpose of authentication.

**Impact**: This is a breaking change to the API from feature 001. The
existing endpoints must be updated. The frontend will call `/api/todos`
and the backend will extract `user_id` from the JWT.
