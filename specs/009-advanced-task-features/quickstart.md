# Quickstart: Intermediate and Advanced Todo Features

**Feature**: 009-advanced-task-features
**Date**: 2026-02-13

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- Dapr CLI installed
- Access to Neon PostgreSQL database
- Kafka cluster (or local Kafka via Docker)

## Environment Setup

### 1. Backend Environment

Create/update `backend/.env`:

```bash
# Existing variables
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
BETTER_AUTH_SECRET=your-jwt-secret

# New variables for Phase V
DAPR_HTTP_PORT=3500
PUBSUB_NAME=pubsub-kafka
```

### 2. Dapr Components

Create `dapr/components/pubsub-kafka.yaml`:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "localhost:9092"  # Or your Kafka broker
    - name: consumerGroup
      value: "todo-app"
    - name: authType
      value: "none"  # Use "password" for secured Kafka
```

### 3. Start Local Kafka (Development)

```bash
docker-compose -f docker-compose.kafka.yml up -d
```

Or use existing Kafka cluster.

## Database Migration

### Run Migration

```bash
cd backend

# Option 1: Alembic migration (if configured)
alembic upgrade head

# Option 2: Direct SQL execution
psql $DATABASE_URL -f migrations/009_advanced_task_features.sql
```

### Verify Schema

```sql
-- Check new columns on tasks table
\d tasks

-- Check new tables
\d tags
\d task_tags
```

## Running the Application

### Backend with Dapr

```bash
cd backend

# Start with Dapr sidecar
dapr run --app-id backend \
         --app-port 8000 \
         --dapr-http-port 3500 \
         --components-path ../dapr/components \
         -- uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Recurring Task Service (when implemented)

```bash
cd services/recurring-task-service

dapr run --app-id recurring-service \
         --app-port 8001 \
         --dapr-http-port 3501 \
         --components-path ../../dapr/components \
         -- uvicorn main:app --host 0.0.0.0 --port 8001
```

## API Usage Examples

### Create Task with Priority and Tags

```bash
curl -X POST http://localhost:8000/api/todos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Quarterly review",
    "description": "Prepare Q1 slides",
    "priority": "high",
    "due_at": "2026-02-20T10:00:00Z",
    "tag_names": ["work", "presentations"]
  }'
```

### List Tasks with Filtering

```bash
# Filter by priority
curl "http://localhost:8000/api/todos?priority=high" \
  -H "Authorization: Bearer $TOKEN"

# Filter by tag
curl "http://localhost:8000/api/todos?tag=work" \
  -H "Authorization: Bearer $TOKEN"

# Filter by status
curl "http://localhost:8000/api/todos?status=pending" \
  -H "Authorization: Bearer $TOKEN"

# Combined filters
curl "http://localhost:8000/api/todos?status=pending&priority=high&tag=work" \
  -H "Authorization: Bearer $TOKEN"
```

### Sort Tasks

```bash
# Sort by due date (ascending, nulls last)
curl "http://localhost:8000/api/todos?sort_by=due_at&sort_order=asc" \
  -H "Authorization: Bearer $TOKEN"

# Sort by priority (high first)
curl "http://localhost:8000/api/todos?sort_by=priority&sort_order=desc" \
  -H "Authorization: Bearer $TOKEN"
```

### Search Tasks

```bash
# Search in title, description, and tags
curl "http://localhost:8000/api/todos?q=meeting" \
  -H "Authorization: Bearer $TOKEN"
```

### Create Recurring Task

```bash
curl -X POST http://localhost:8000/api/todos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Daily standup",
    "priority": "medium",
    "due_at": "2026-02-14T09:00:00Z",
    "is_recurring": true,
    "recurrence_pattern": "daily",
    "tag_names": ["meetings"]
  }'
```

### Manage Tags

```bash
# List all tags
curl http://localhost:8000/api/tags \
  -H "Authorization: Bearer $TOKEN"

# Create a tag
curl -X POST http://localhost:8000/api/tags \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "urgent"}'

# Delete a tag
curl -X DELETE http://localhost:8000/api/tags/{tag_id} \
  -H "Authorization: Bearer $TOKEN"
```

## Testing

### Backend Tests

```bash
cd backend
pytest tests/test_todos_extended.py -v
pytest tests/test_tags.py -v
pytest tests/test_events.py -v
```

### Event Publishing Test

```bash
# Subscribe to task-events topic (in another terminal)
dapr publish --pubsub pubsub-kafka --topic task-events --data '{"test": true}'

# Check Kafka consumer
kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic task-events --from-beginning
```

## Troubleshooting

### Dapr Not Starting

```bash
# Check Dapr is installed
dapr --version

# Initialize Dapr (if not done)
dapr init

# Check component files
dapr components -k
```

### Database Connection Issues

```bash
# Test database connection
psql $DATABASE_URL -c "SELECT 1"

# Check migrations applied
psql $DATABASE_URL -c "\d tasks"
```

### Kafka Connection Issues

```bash
# Check Kafka is running
docker ps | grep kafka

# Test Kafka connectivity
kafka-topics --bootstrap-server localhost:9092 --list
```

## Validation Checklist

- [ ] Backend starts with Dapr sidecar
- [ ] Database migration successful (new columns and tables exist)
- [ ] Can create task with priority, tags, due_at
- [ ] Filtering by status, priority, tag works
- [ ] Sorting by created_at, due_at, priority, title works
- [ ] Search returns matching tasks
- [ ] Tags are user-scoped (can't see other users' tags)
- [ ] Events published to Kafka on task mutations
- [ ] Recurring Task Service processes task.completed events
- [ ] Frontend displays priority badges and tags
- [ ] Frontend filter/sort controls work
