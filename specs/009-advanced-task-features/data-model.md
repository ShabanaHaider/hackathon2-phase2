# Data Model: Intermediate and Advanced Todo Features

**Feature**: 009-advanced-task-features
**Date**: 2026-02-13

## Entity Relationship Diagram

```text
┌─────────────────────────────────────────────────────────────┐
│                          Task                                │
│─────────────────────────────────────────────────────────────│
│ id: UUID (PK)                                               │
│ title: VARCHAR(255) NOT NULL                                │
│ description: TEXT                                           │
│ is_completed: BOOLEAN DEFAULT FALSE                         │
│ completed_at: TIMESTAMPTZ                                   │
│ created_at: TIMESTAMPTZ NOT NULL                            │
│ updated_at: TIMESTAMPTZ NOT NULL                            │
│ user_id: VARCHAR(255) NOT NULL (indexed)                    │
│ ─────────── NEW FIELDS ───────────                          │
│ priority: VARCHAR(10) DEFAULT 'medium' (indexed)            │
│ due_at: TIMESTAMPTZ (indexed)                               │
│ is_recurring: BOOLEAN DEFAULT FALSE                         │
│ recurrence_pattern: VARCHAR(20)                             │
└─────────────────────────────────────────────────────────────┘
        │
        │ many-to-many
        ▼
┌───────────────────┐       ┌───────────────────┐
│     TaskTag       │       │       Tag         │
│───────────────────│       │───────────────────│
│ task_id: UUID (FK)│──────▶│ id: UUID (PK)     │
│ tag_id: UUID (FK) │       │ name: VARCHAR(50) │
│ (composite PK)    │       │ user_id: VARCHAR  │
└───────────────────┘       │ created_at: TS    │
                            └───────────────────┘
```

## Entity Definitions

### Task (Extended)

Extends existing Task model with new fields.

| Field | Type | Constraints | Default | Notes |
|-------|------|-------------|---------|-------|
| id | UUID | PK | uuid4() | Existing |
| title | VARCHAR(255) | NOT NULL | - | Existing |
| description | TEXT | NULLABLE | NULL | Existing |
| is_completed | BOOLEAN | NOT NULL | FALSE | Existing |
| completed_at | TIMESTAMPTZ | NULLABLE | NULL | Existing |
| created_at | TIMESTAMPTZ | NOT NULL | now() | Existing |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | Existing |
| user_id | VARCHAR(255) | NOT NULL, INDEX | - | Existing |
| **priority** | VARCHAR(10) | NOT NULL, INDEX | 'medium' | NEW: low/medium/high |
| **due_at** | TIMESTAMPTZ | NULLABLE, INDEX | NULL | NEW: Optional deadline |
| **is_recurring** | BOOLEAN | NOT NULL | FALSE | NEW: Recurrence flag |
| **recurrence_pattern** | VARCHAR(20) | NULLABLE | NULL | NEW: daily/weekly/monthly |

**Indexes**:
- `ix_tasks_user_id` (existing)
- `ix_tasks_priority` (new)
- `ix_tasks_due_at` (new)
- `ix_tasks_user_id_priority` (new composite)
- `ix_tasks_user_id_due_at` (new composite)

**Validation Rules**:
- priority MUST be one of: 'low', 'medium', 'high'
- recurrence_pattern MUST be one of: 'daily', 'weekly', 'monthly' (or NULL)
- recurrence_pattern can only be set if is_recurring is TRUE
- due_at MUST be stored in UTC

### Tag (New)

Represents a user-specific category/label.

| Field | Type | Constraints | Default | Notes |
|-------|------|-------------|---------|-------|
| id | UUID | PK | uuid4() | |
| name | VARCHAR(50) | NOT NULL | - | Case-insensitive unique per user |
| user_id | VARCHAR(255) | NOT NULL, INDEX | - | Owner of the tag |
| created_at | TIMESTAMPTZ | NOT NULL | now() | |

**Indexes**:
- `ix_tags_user_id` (for user-scoped queries)
- `uq_tags_user_id_name` (unique constraint: user_id + LOWER(name))

**Validation Rules**:
- name MUST be 1-50 characters
- name MUST be unique per user (case-insensitive)
- name MUST NOT contain leading/trailing whitespace

### TaskTag (New - Link Table)

Join table for many-to-many Task ↔ Tag relationship.

| Field | Type | Constraints | Default | Notes |
|-------|------|-------------|---------|-------|
| task_id | UUID | PK, FK → tasks.id | - | ON DELETE CASCADE |
| tag_id | UUID | PK, FK → tags.id | - | ON DELETE CASCADE |

**Indexes**:
- Composite primary key on (task_id, tag_id)
- `ix_task_tags_tag_id` (for reverse lookups)

**Cascade Behavior**:
- Deleting a Task removes all its TaskTag associations
- Deleting a Tag removes all its TaskTag associations

## SQLModel Definitions

### Priority Enum

```python
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class RecurrencePattern(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
```

### Task Model (Extended)

```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    is_completed: bool = Field(default=False)
    completed_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    user_id: str = Field(index=True, max_length=255)

    # --- NEW FIELDS ---
    priority: str = Field(default="medium", max_length=10, index=True)
    due_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, index=True)
    )
    is_recurring: bool = Field(default=False)
    recurrence_pattern: Optional[str] = Field(default=None, max_length=20)

    # --- RELATIONSHIPS ---
    tags: list["Tag"] = Relationship(
        back_populates="tasks",
        link_model=TaskTagLink,
        sa_relationship_kwargs={"lazy": "selectin"}
    )
```

### Tag Model

```python
class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_tags_user_id_name"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=50, index=True)
    user_id: str = Field(index=True, max_length=255)
    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    # --- RELATIONSHIPS ---
    tasks: list["Task"] = Relationship(
        back_populates="tags",
        link_model=TaskTagLink
    )
```

### TaskTagLink Model

```python
class TaskTagLink(SQLModel, table=True):
    __tablename__ = "task_tags"

    task_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("tasks.id", ondelete="CASCADE"),
            primary_key=True
        )
    )
    tag_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("tags.id", ondelete="CASCADE"),
            primary_key=True
        )
    )
```

## Request/Response Schemas

### TaskCreate (Extended)

```python
class TaskCreate(BaseModel):
    title: str = PydanticField(min_length=1, max_length=255)
    description: Optional[str] = PydanticField(default=None, max_length=2000)
    priority: Priority = Priority.MEDIUM
    due_at: Optional[datetime] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[RecurrencePattern] = None
    tag_names: Optional[list[str]] = PydanticField(default=None, max_length=10)

    @validator("recurrence_pattern")
    def validate_recurrence(cls, v, values):
        if v is not None and not values.get("is_recurring"):
            raise ValueError("recurrence_pattern requires is_recurring=True")
        return v
```

### TaskUpdate (Extended)

```python
class TaskUpdate(BaseModel):
    title: Optional[str] = PydanticField(default=None, min_length=1, max_length=255)
    description: Optional[str] = PydanticField(default=None, max_length=2000)
    is_completed: Optional[bool] = None
    priority: Optional[Priority] = None
    due_at: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    tag_names: Optional[list[str]] = None
```

### TaskResponse (Extended)

```python
class TagResponse(BaseModel):
    id: uuid.UUID
    name: str

    model_config = {"from_attributes": True}

class TaskResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str]
    is_completed: bool
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    user_id: str
    priority: str
    due_at: Optional[datetime]
    is_recurring: bool
    recurrence_pattern: Optional[str]
    tags: list[TagResponse] = []

    model_config = {"from_attributes": True}
```

### Tag Schemas

```python
class TagCreate(BaseModel):
    name: str = PydanticField(min_length=1, max_length=50)

class TagResponse(BaseModel):
    id: uuid.UUID
    name: str
    user_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
```

## Event Schemas

### TaskEvent

Published to `task-events` topic on task mutations.

```python
class TaskEventPayload(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str]
    is_completed: bool
    priority: str
    due_at: Optional[datetime]
    is_recurring: bool
    recurrence_pattern: Optional[str]
    tags: list[str]  # Tag names for easier processing

class TaskEvent(BaseModel):
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_type: str  # task.created, task.updated, task.completed, task.deleted
    user_id: str
    task_id: uuid.UUID
    timestamp: datetime = Field(default_factory=_utcnow)
    version: str = "1.0"
    payload: TaskEventPayload
```

### ReminderEvent

Published to `reminders` topic when task due date approaches.

```python
class ReminderEvent(BaseModel):
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_type: str = "reminder.due"
    user_id: str
    task_id: uuid.UUID
    timestamp: datetime = Field(default_factory=_utcnow)
    version: str = "1.0"
    payload: dict  # Contains task title, due_at, priority
```

## Database Migration

Migration script to add new columns and tables:

```sql
-- Add new columns to tasks table
ALTER TABLE tasks
ADD COLUMN priority VARCHAR(10) NOT NULL DEFAULT 'medium',
ADD COLUMN due_at TIMESTAMPTZ,
ADD COLUMN is_recurring BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN recurrence_pattern VARCHAR(20);

-- Create indexes
CREATE INDEX ix_tasks_priority ON tasks(priority);
CREATE INDEX ix_tasks_due_at ON tasks(due_at);
CREATE INDEX ix_tasks_user_id_priority ON tasks(user_id, priority);
CREATE INDEX ix_tasks_user_id_due_at ON tasks(user_id, due_at);

-- Create tags table
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_tags_user_id ON tags(user_id);
CREATE UNIQUE INDEX uq_tags_user_id_name ON tags(user_id, LOWER(name));

-- Create task_tags link table
CREATE TABLE task_tags (
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);

CREATE INDEX ix_task_tags_tag_id ON task_tags(tag_id);
```

## Query Patterns

### Filter by Priority

```python
statement = select(Task).where(
    Task.user_id == user_id,
    Task.priority == priority
)
```

### Filter by Tag

```python
statement = (
    select(Task)
    .join(TaskTagLink)
    .join(Tag)
    .where(Task.user_id == user_id, Tag.name == tag_name)
)
```

### Sort by Due Date (nulls last)

```python
from sqlalchemy import nullslast

statement = (
    select(Task)
    .where(Task.user_id == user_id)
    .order_by(nullslast(Task.due_at.asc()))
)
```

### Search Across Fields

```python
from sqlalchemy import or_

search_term = f"%{query}%"
statement = (
    select(Task)
    .outerjoin(TaskTagLink)
    .outerjoin(Tag)
    .where(
        Task.user_id == user_id,
        or_(
            Task.title.ilike(search_term),
            Task.description.ilike(search_term),
            Tag.name.ilike(search_term)
        )
    )
    .distinct()
)
```
