# Quickstart: Todo Web Frontend Application

**Feature Branch**: `003-todo-web-frontend`
**Date**: 2026-01-28

## Prerequisites

- Node.js 18+ and npm
- Backend API running at `http://localhost:8000` (Feature 001)
- Better Auth configured and migrated (Feature 002)
- Frontend Next.js project initialized in `frontend/`

## Setup

1. **Navigate to frontend directory**:

   ```bash
   cd frontend
   ```

2. **Install dependencies** (if not already):

   ```bash
   npm install
   ```

3. **Configure environment variables**:

   ```bash
   # frontend/.env.local
   BETTER_AUTH_SECRET=<your-secret>
   DATABASE_URL=<neon-postgresql-url>
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Start the development server**:

   ```bash
   npm run dev
   ```

   Frontend available at `http://localhost:3000`.

5. **Start the backend** (in separate terminal):

   ```bash
   cd /path/to/project
   source backend/.venv/bin/activate
   uvicorn backend.main:app --reload --port 8000
   ```

## Verification Checklist

### Authentication Flow

- [ ] Navigate to `/` without being signed in → redirected to `/signin`
- [ ] Navigate to `/signup` → sign-up form loads
- [ ] Create account with valid email and password (8+ chars) → redirected to dashboard
- [ ] Sign out → redirected to `/signin`
- [ ] Sign in with existing credentials → dashboard loads
- [ ] Sign in with wrong password → shows "Invalid credentials" error
- [ ] Sign up with duplicate email → shows appropriate error

### Task CRUD Operations

- [ ] Dashboard shows empty state when user has no tasks
- [ ] Create a task with title only → task appears in list
- [ ] Create a task with title and description → both visible
- [ ] Attempt to create task with empty title → validation error shown
- [ ] Click complete checkbox → task marked as complete (visual indicator)
- [ ] Click complete checkbox again → task returns to incomplete
- [ ] Edit task title → change persists after save
- [ ] Edit task description → change persists after save
- [ ] Delete task → confirmation prompt appears
- [ ] Confirm delete → task removed from list
- [ ] Cancel delete → task remains in list

### User Isolation

- [ ] Create tasks as User A
- [ ] Sign out and sign in as User B
- [ ] User B sees only their own tasks (or empty state)
- [ ] User B cannot see User A's tasks

### Responsive Design

- [ ] Dashboard layout works on mobile (320px width)
- [ ] Dashboard layout works on tablet (768px width)
- [ ] Dashboard layout works on desktop (1920px width)
- [ ] Forms are usable on touch devices

### Error Handling

- [ ] Stop backend → API calls show error message with retry option
- [ ] Network timeout → loading indicator, then error state
- [ ] 404 on task operation → "Task not found" message

### Loading States

- [ ] Dashboard shows loading indicator while fetching tasks
- [ ] Create form shows loading state during submission
- [ ] Complete toggle shows loading state during API call
- [ ] Delete shows loading state during API call

## Quick Test Script

```bash
# 1. Start both servers
# Terminal 1 (Backend):
cd /path/to/project && source backend/.venv/bin/activate
uvicorn backend.main:app --reload --port 8000

# Terminal 2 (Frontend):
cd /path/to/project/frontend
npm run dev

# 2. Open browser to http://localhost:3000
# 3. Create account via /signup
# 4. Create a few tasks
# 5. Mark some complete
# 6. Edit one task
# 7. Delete one task
# 8. Sign out and sign in again
# 9. Verify tasks persist
```

## Common Issues

### "Not authenticated" on API calls

- Verify Better Auth is properly configured
- Check that JWT is being attached to requests
- Confirm CORS is allowing credentials from frontend origin

### Tasks not loading

- Verify backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` is set correctly
- Check browser console for CORS errors

### Sign-in redirect loop

- Clear cookies and try again
- Verify Better Auth database tables exist
- Check session cookie is being set
