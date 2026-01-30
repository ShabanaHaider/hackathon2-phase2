# Quickstart: Authentication & JWT Security Integration

**Feature Branch**: `002-auth-jwt-security`
**Date**: 2026-01-28

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Neon PostgreSQL database (same instance as feature 001)
- Feature 001 (Task CRUD API) already implemented and working

## Setup — Frontend (Better Auth)

1. **Initialize the frontend**:

   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment variables**:

   ```bash
   cp .env.example .env.local
   ```

   Required variables in `.env.local`:

   ```text
   BETTER_AUTH_SECRET=<generate-a-random-secret>
   DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Run Better Auth migrations** (creates auth tables in Neon):

   ```bash
   npx @better-auth/cli migrate
   ```

4. **Start the frontend dev server**:

   ```bash
   npm run dev
   ```

   Frontend available at `http://localhost:3000`.

## Setup — Backend (JWT Verification)

1. **Install updated dependencies**:

   ```bash
   cd backend
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Update environment variables**:

   Add to `backend/.env`:

   ```text
   BETTER_AUTH_URL=http://localhost:3000
   ```

3. **Start the backend server**:

   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

## Quick Test

### 1. Create an account

Navigate to `http://localhost:3000/signup` and create an account with email
and password.

### 2. Sign in

Navigate to `http://localhost:3000/signin` and sign in with your credentials.

### 3. Test authenticated API call

```bash
# Get a JWT token (after signing in via the frontend, retrieve from session)
# The frontend handles this automatically. For manual testing:

# Test with valid token
curl http://localhost:8000/api/todos \
  -H "Authorization: Bearer <your-jwt-token>"

# Create a task with valid token
curl -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{"title": "My authenticated task"}'
```

### 4. Test rejection scenarios

```bash
# Missing token — expect 401
curl http://localhost:8000/api/todos

# Invalid token — expect 401
curl http://localhost:8000/api/todos \
  -H "Authorization: Bearer invalid-token-here"

# Expired token — expect 401
# (Wait 15+ minutes after token issuance, or use a pre-expired token)
```

## Verification Checklist

### Authentication Flow
- [ ] Sign-up creates account and signs user in immediately
- [ ] Sign-in with valid credentials issues a JWT token
- [ ] Sign-in with wrong password returns generic error
- [ ] Duplicate email signup is rejected

### Backend JWT Verification
- [ ] Request with valid JWT returns user-scoped data (200)
- [ ] Request without Authorization header returns 401
- [ ] Request with invalid/tampered token returns 401
- [ ] Request with expired token returns 401

### User Data Isolation
- [ ] User A's tasks are not visible to User B
- [ ] User A cannot modify User B's tasks (404)
- [ ] User A cannot delete User B's tasks (404)

### Route Transition
- [ ] Old routes (`/api/users/{user_id}/todos`) no longer exist
- [ ] New routes (`/api/todos`) work with JWT authentication

### Frontend Integration
- [ ] Frontend attaches JWT to all API requests automatically
- [ ] Sign-out clears session and subsequent API calls fail with 401
- [ ] Unauthenticated users are redirected to sign-in page

## JWKS Verification (Manual)

To verify the JWKS endpoint is working:

```bash
# Fetch public keys from Better Auth
curl http://localhost:3000/api/auth/jwks
```

Expected response: JSON with `keys` array containing the public key(s) used
for JWT verification.
