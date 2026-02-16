# Research: Intermediate and Advanced Todo Features

**Feature**: 009-advanced-task-features
**Date**: 2026-02-13

## Research Topics

### 1. Dapr Pub/Sub Patterns for FastAPI

**Decision**: Use `dapr` Python SDK with HTTP client for publishing events

**Rationale**:
- Dapr provides language-agnostic Pub/Sub via HTTP/gRPC sidecar
- Python SDK (`dapr`) offers clean abstraction over HTTP calls
- No direct Kafka client needed in application code
- Supports multiple message brokers (Kafka, Redis, RabbitMQ) via component swap

**Implementation Pattern**:
```python
from dapr.clients import DaprClient

async def publish_event(topic: str, data: dict):
    with DaprClient() as client:
        client.publish_event(
            pubsub_name="pubsub-kafka",
            topic_name=topic,
            data=json.dumps(data),
            data_content_type="application/json"
        )
```

**Alternatives Considered**:
- Direct Kafka client (aiokafka): Rejected per Constitution Principle IV
- Redis Pub/Sub: Less durable; Kafka preferred for event sourcing
- HTTP webhooks: Synchronous; doesn't scale for event-driven architecture

### 2. SQLModel Many-to-Many Relationships

**Decision**: Use SQLModel with explicit link table and relationship definitions

**Rationale**:
- SQLModel supports SQLAlchemy-style relationships
- Link table (TaskTag) allows clean many-to-many mapping
- Can add metadata to relationship (e.g., created_at on association)

**Implementation Pattern**:
```python
class TaskTagLink(SQLModel, table=True):
    __tablename__ = "task_tags"
    task_id: uuid.UUID = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tags.id", primary_key=True)

class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=50, index=True)
    user_id: str = Field(index=True, max_length=255)
    tasks: list["Task"] = Relationship(back_populates="tags", link_model=TaskTagLink)

class Task(SQLModel, table=True):  # Extended
    # ... existing fields ...
    tags: list["Tag"] = Relationship(back_populates="tasks", link_model=TaskTagLink)
```

**Alternatives Considered**:
- JSON array column for tags: Rejected; loses relational integrity, harder to query
- Separate tags table without link: Rejected; doesn't support many-to-many

### 3. PostgreSQL Search Performance (ILIKE)

**Decision**: Use ILIKE with indexed columns for 10,000-item scale

**Rationale**:
- ILIKE is case-insensitive pattern matching in PostgreSQL
- Performance acceptable for task lists up to 10,000 items per user
- Spec explicitly excludes full-text search (out of scope)
- Can add GIN index on tsvector if needed later

**Implementation Pattern**:
```python
# Single field search
statement = select(Task).where(
    Task.user_id == user_id,
    Task.title.ilike(f"%{search_term}%")
)

# Multi-field OR search
from sqlalchemy import or_
statement = select(Task).where(
    Task.user_id == user_id,
    or_(
        Task.title.ilike(f"%{search_term}%"),
        Task.description.ilike(f"%{search_term}%")
    )
)
```

**Performance Notes**:
- ILIKE without leading wildcard can use B-tree index
- Leading wildcard (`%term`) requires sequential scan or trigram index
- For 10,000 tasks, sequential scan is acceptable (<100ms)

**Alternatives Considered**:
- PostgreSQL full-text search (tsvector): Out of scope per spec
- Elasticsearch: Overkill for current scale; adds operational complexity
- Application-level filtering: Rejected; moves too much data over wire

### 4. Recurring Task Scheduling Strategies

**Decision**: Event-driven regeneration on task completion

**Rationale**:
- Task completion triggers event to `task-events` topic
- Recurring Task Service subscribes and creates next occurrence
- No polling or scheduled jobs needed
- Scales horizontally with multiple service instances

**Event Flow**:
1. User completes task → Backend publishes `task.completed` event
2. Recurring Task Service receives event
3. If `is_recurring=true`, service creates new task via backend API
4. New task published as `task.created` event

**Implementation Pattern**:
```python
# Event payload
{
    "event_id": "uuid",
    "event_type": "task.completed",
    "user_id": "user123",
    "task_id": "uuid",
    "timestamp": "2026-02-13T10:00:00Z",
    "version": "1.0",
    "payload": {
        "is_recurring": true,
        "recurrence_pattern": "daily",
        "due_at": "2026-02-14T10:00:00Z",
        "title": "Daily standup",
        "priority": "high",
        "tags": ["work", "meetings"]
    }
}
```

**Alternatives Considered**:
- Cron job polling: Rejected; doesn't scale, introduces lag
- Database trigger: Rejected; couples regeneration to DB layer
- Dapr Jobs API: Could supplement for time-based reminders; overkill for completion-triggered recurrence

### 5. Priority Enum Implementation

**Decision**: String enum with validation at Pydantic layer

**Rationale**:
- Python Enum provides type safety
- String storage allows easy database queries and sorting
- Pydantic validates on input

**Implementation Pattern**:
```python
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(SQLModel, table=True):
    priority: str = Field(default="medium", max_length=10)

class TaskCreate(BaseModel):
    priority: Priority = Priority.MEDIUM
```

**Alternatives Considered**:
- Integer priority (1-3): Less readable in API responses
- PostgreSQL ENUM type: Harder to migrate; string is more flexible

### 6. Due Date and Reminder Architecture

**Decision**: Store due_at in UTC; publish reminder events based on configurable offset

**Rationale**:
- UTC storage prevents timezone confusion
- Frontend converts to user's local timezone for display
- Reminder events published via Dapr; consumed by Notification Service

**Reminder Flow**:
1. Task with due_at created/updated → Schedule reminder
2. At reminder time, publish to `reminders` topic
3. Notification Service receives and dispatches notification

**Note**: Per spec assumption, reminder timing is at due_at (no configurable offset in v1).

### 7. Idempotent Event Handling

**Decision**: Use event_id for deduplication in consumers

**Rationale**:
- At-least-once delivery may cause duplicate events
- Consumers track processed event_ids in database
- Prevents duplicate recurring task creation

**Implementation Pattern**:
```python
# In recurring task service
async def handle_task_completed(event: dict):
    event_id = event["event_id"]

    # Check if already processed
    if await is_event_processed(event_id):
        return  # Skip duplicate

    # Process event
    await create_next_occurrence(event)

    # Mark as processed
    await mark_event_processed(event_id)
```

## Summary

| Topic | Decision | Key Trade-off |
|-------|----------|---------------|
| Pub/Sub | Dapr HTTP API | Latency vs. portability |
| Many-to-many | SQLModel link table | Complexity vs. query flexibility |
| Search | ILIKE pattern matching | No relevance scoring vs. simplicity |
| Recurring | Event-driven regeneration | Eventual consistency vs. scalability |
| Priority | String enum | Storage overhead vs. readability |
| Reminders | Event-driven notification | Distributed system complexity vs. scalability |
| Idempotency | Event ID deduplication | State tracking vs. correctness |

All research items resolved. Ready for Phase 1 design.
