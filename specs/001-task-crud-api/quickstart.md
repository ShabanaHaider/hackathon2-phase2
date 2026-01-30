# Quickstart: Task CRUD API

**Feature Branch**: `001-task-crud-api`
**Date**: 2026-01-27

## Prerequisites

- Python 3.11+
- Neon PostgreSQL database with connection string
- `pip` or `uv` for dependency management

## Setup

1. **Clone and checkout branch**:

   ```bash
   git checkout 001-task-crud-api
   ```

2. **Create virtual environment and install dependencies**:

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate   # Linux/Mac
   # .venv\Scripts\activate    # Windows
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:

   ```bash
   cp .env.example .env
   # Edit .env with your Neon PostgreSQL connection string
   ```

   Required variables:

   ```text
   DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require
   ```

4. **Start the server**:

   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

5. **Verify**: Open `http://localhost:8000/docs` for interactive API docs.

## Quick Test

```bash
# Create a task
curl -X POST http://localhost:8000/api/users/user-1/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "My first task", "description": "Test description"}'

# List tasks for user
curl http://localhost:8000/api/users/user-1/todos

# Get a single task (replace TASK_ID with actual UUID)
curl http://localhost:8000/api/users/user-1/todos/TASK_ID

# Update a task
curl -X PATCH http://localhost:8000/api/users/user-1/todos/TASK_ID \
  -H "Content-Type: application/json" \
  -d '{"is_completed": true}'

# Delete a task
curl -X DELETE http://localhost:8000/api/users/user-1/todos/TASK_ID
```

## Verification Checklist

- [ ] POST returns 201 with created task including UUID id
- [ ] GET list returns only tasks for the specified user_id
- [ ] GET single returns 404 for non-existent or other user's task
- [ ] PATCH updates only specified fields, returns 200
- [ ] PATCH with is_completed=true sets completed_at timestamp
- [ ] DELETE returns 204 with no body
- [ ] DELETE returns 404 for non-existent or other user's task
- [ ] POST with empty title returns 422
- [ ] Data persists after server restart
