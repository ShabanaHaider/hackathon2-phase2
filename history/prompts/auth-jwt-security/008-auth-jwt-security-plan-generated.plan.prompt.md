---
id: 008
title: Auth JWT Security Plan Generated
stage: plan
date: 2026-01-28
surface: agent
model: claude-opus-4-5-20251101
feature: auth-jwt-security
branch: 002-auth-jwt-security
user: user
command: /sp.plan
labels: ["plan", "authentication", "jwt", "better-auth", "jwks", "fastapi"]
links:
  spec: specs/002-auth-jwt-security/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-auth-jwt-security/plan.md
  - specs/002-auth-jwt-security/research.md
  - specs/002-auth-jwt-security/data-model.md
  - specs/002-auth-jwt-security/contracts/auth-endpoints.md
  - specs/002-auth-jwt-security/quickstart.md
tests:
---

## Prompt

/sp.plan

Constitution alignment: This plan must enforce the constitution's security, statelessness, and environment-based secret management rules.

Create:
- Better Auth JWT configuration
- Frontend token handling strategy
- FastAPI JWT verification middleware
- User identity extraction mechanism

Decisions needing documentation:
- JWT payload structure
- Token expiration duration
- Middleware vs dependency-based verification
- Source of truth for user identity

Testing strategy:
- Valid token access
- Missing token rejection
- Expired token rejection
- User ID mismatch handling

Technical phases:
1. Enable JWT plugin in Better Auth
2. Configure shared secret in both services
3. Implement FastAPI JWT verification
4. Protect all task-related routes
5. Validate security behavior

## Response snapshot

Generated implementation plan at `specs/002-auth-jwt-security/plan.md` on branch `002-auth-jwt-security`.

**Phase 0 (Research)**: 7 research decisions (R1–R7) documented in `research.md`.
Critical finding: Better Auth uses JWKS asymmetric keys (EdDSA Ed25519), NOT shared symmetric secrets. This supersedes the spec/constitution assumption about shared secrets.

**Phase 1 (Design)**: Created `data-model.md` (Better Auth tables + Task relationship), `contracts/auth-endpoints.md` (API route transition from `/api/users/{user_id}/todos` to `/api/todos`, error contracts), and `quickstart.md` (setup guide for both frontend and backend).

**Plan**: 6 implementation phases covering frontend Better Auth setup, auth pages, API integration, backend JWT verification module, route migration, and integration testing. 6 key design decisions (D1–D6) documented.

Constitution check: All 6 principles PASS. Principle II/VI updated — JWKS replaces shared secret (stronger security posture).

## Outcome

- Impact: Architectural plan established for authentication and JWT security integration with Better Auth JWKS
- Tests: N/A (plan phase, no code)
- Files: specs/002-auth-jwt-security/plan.md, research.md, data-model.md, contracts/auth-endpoints.md, quickstart.md
- Next prompts: /sp.tasks to generate implementation tasks, or /sp.adr to document JWKS decision
- Reflection: Research phase revealed a significant architecture difference (JWKS vs shared secret) that changes the implementation approach. The plan documents this clearly and recommends a constitution update.

## Evaluation notes (flywheel)

- Failure modes observed: Initial spec assumed shared symmetric secret; research corrected this to JWKS asymmetric verification
- Graders run and results (PASS/FAIL): Constitution check all PASS (6/6 principles)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
