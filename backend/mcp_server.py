"""
MCP Server for Task Tools

A standalone MCP server that exposes task CRUD operations as tools
for AI agents. Uses stdio transport and synchronous SQLModel sessions.

Publishes events to Dapr Pub/Sub after state mutations per
Constitution Principle VII and FR-033.

Server name: todo-task-tools
Transport: stdio
Tools: add_task, list_tasks, update_task, complete_task, delete_task
"""

import logging
import os
import re
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Optional

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from sqlalchemy import create_engine
from sqlmodel import Session, select

from models import Tag, Task, TaskTagLink

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

# Convert async URL format to sync format for psycopg2
# Remove postgresql+asyncpg:// prefix if present
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)

# Clean up query params not supported by psycopg2
DATABASE_URL = re.sub(r"[&?]channel_binding=[^&]*", "", DATABASE_URL)
# sslmode=require is supported by psycopg2, so keep it
DATABASE_URL = re.sub(r"ssl=require", "sslmode=require", DATABASE_URL)

# Dapr configuration
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
PUBSUB_NAME = os.getenv("PUBSUB_NAME", "pubsub-kafka")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"

# Valid enums for input validation
VALID_PRIORITIES = {"low", "medium", "high"}
VALID_RECURRENCE_PATTERNS = {"daily", "weekly", "monthly"}

# Create synchronous engine for MCP server
sync_engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True,
)


@contextmanager
def get_sync_session():
    """Provide a synchronous database session."""
    with Session(sync_engine) as session:
        yield session


def _utcnow() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


def _validate_uuid(task_id: str) -> uuid.UUID | None:
    """Validate and parse a UUID string. Returns None if invalid."""
    try:
        return uuid.UUID(task_id)
    except (ValueError, TypeError):
        return None


# =============================================================================
# Dapr Event Publishing (synchronous) & Tag Resolution
# =============================================================================


def _publish_event(topic: str, data: dict) -> None:
    """Publish an event to Dapr Pub/Sub synchronously. Gracefully degrades."""
    url = f"{DAPR_BASE_URL}/v1.0/publish/{PUBSUB_NAME}/{topic}"
    try:
        response = httpx.post(url, json=data, timeout=5.0)
        response.raise_for_status()
        logger.info("Published to %s: %s", topic, data.get("event_type", "unknown"))
    except httpx.ConnectError:
        logger.warning("Dapr sidecar not available — event not published to %s", topic)
    except Exception as e:
        logger.error("Failed to publish to %s: %s", topic, str(e))


def _build_task_event(event_type: str, user_id: str, task: Task) -> dict:
    """Build a task event dict matching the TaskEvent schema from events.yaml."""
    tag_names = [tag.name for tag in task.tags] if task.tags else []
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "user_id": user_id,
        "task_id": str(task.id),
        "timestamp": _utcnow().isoformat(),
        "version": "1.0",
        "payload": {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "is_completed": task.is_completed,
            "priority": task.priority or "medium",
            "due_at": task.due_at.isoformat() if task.due_at else None,
            "is_recurring": task.is_recurring,
            "recurrence_pattern": task.recurrence_pattern,
            "tags": tag_names,
        },
    }


def _resolve_tags(session: Session, user_id: str, tag_names: list[str]) -> list[Tag]:
    """Resolve tag names to Tag objects, creating new tags as needed (AD-2)."""
    tags = []
    for name in tag_names:
        name = name.strip()
        if not name:
            continue
        existing = session.exec(
            select(Tag).where(Tag.user_id == user_id, Tag.name == name)
        ).first()
        if existing:
            tags.append(existing)
        else:
            new_tag = Tag(name=name, user_id=user_id)
            session.add(new_tag)
            session.flush()
            tags.append(new_tag)
    return tags


# Initialize FastMCP server
mcp = FastMCP("todo-task-tools")


# =============================================================================
# Tool 1: add_task
# =============================================================================


@mcp.tool()
def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    is_recurring: Optional[bool] = None,
    recurrence_pattern: Optional[str] = None,
    tags: Optional[str] = None,
) -> str:
    """
    Create a new task for a user.

    Args:
        user_id: The authenticated user's ID
        title: Task title (1-255 characters)
        description: Optional task description (max 2000 characters)
        priority: Task priority - "low", "medium", or "high" (default: "medium")
        due_date: Optional due date in ISO 8601 format (e.g. "2026-03-01T10:00:00Z")
        is_recurring: Whether task recurs after completion (default: false)
        recurrence_pattern: Recurrence frequency - "daily", "weekly", or "monthly" (required if is_recurring=true)
        tags: Comma-separated tag names (e.g. "work,urgent,project-x")

    Returns:
        Success message with task details, or error message
    """
    # Validate user_id
    if not user_id or not user_id.strip():
        return "Error: user_id is required."

    # Validate title
    title = title.strip() if title else ""
    if not title or len(title) > 255:
        return "Error: Title is required and must be 1-255 characters."

    # Validate description
    if description is not None and len(description) > 2000:
        return "Error: Description must be at most 2000 characters."

    # Validate priority
    effective_priority = "medium"
    if priority is not None:
        priority = priority.strip().lower()
        if priority not in VALID_PRIORITIES:
            return f"Error: Invalid priority '{priority}'. Must be: low, medium, high."
        effective_priority = priority

    # Validate due_date
    parsed_due_at = None
    if due_date is not None:
        try:
            parsed_due_at = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return "Error: Invalid due_date format. Use ISO 8601 (e.g. 2026-03-01T10:00:00Z)."

    # Validate recurrence
    effective_recurring = is_recurring or False
    effective_pattern = None
    if recurrence_pattern is not None:
        recurrence_pattern = recurrence_pattern.strip().lower()
        if recurrence_pattern not in VALID_RECURRENCE_PATTERNS:
            return f"Error: Invalid recurrence_pattern '{recurrence_pattern}'. Must be: daily, weekly, monthly."
        effective_pattern = recurrence_pattern
        effective_recurring = True
    if effective_recurring and not effective_pattern:
        return "Error: recurrence_pattern is required when is_recurring=true."

    # Parse tags
    tag_names = []
    if tags is not None:
        tag_names = [t.strip() for t in tags.split(",") if t.strip()]

    try:
        with get_sync_session() as session:
            task = Task(
                user_id=user_id.strip(),
                title=title,
                description=description,
                priority=effective_priority,
                due_at=parsed_due_at,
                is_recurring=effective_recurring,
                recurrence_pattern=effective_pattern,
            )
            session.add(task)
            session.flush()

            if tag_names:
                task.tags = _resolve_tags(session, user_id.strip(), tag_names)

            session.commit()
            session.refresh(task)

            # Publish task.created event (FR-033, Principle VII)
            _publish_event(
                "task-events",
                _build_task_event("task.created", user_id.strip(), task),
            )

            tag_display = ", ".join(t.name for t in task.tags) if task.tags else "None"
            return (
                f"Task created successfully.\n"
                f"ID: {task.id}\n"
                f"Title: {task.title}\n"
                f"Description: {task.description or 'None'}\n"
                f"Priority: {task.priority}\n"
                f"Due: {task.due_at.isoformat() if task.due_at else 'None'}\n"
                f"Recurring: {task.is_recurring} ({task.recurrence_pattern or 'N/A'})\n"
                f"Tags: {tag_display}\n"
                f"Created: {task.created_at.isoformat()}"
            )
    except Exception:
        return "Error: Failed to create task. Please try again."


# =============================================================================
# Tool 2: list_tasks
# =============================================================================


@mcp.tool()
def list_tasks(user_id: str) -> str:
    """
    List all tasks for a user.

    Args:
        user_id: The authenticated user's ID

    Returns:
        Formatted list of tasks, or message if no tasks found
    """
    # Validate user_id
    if not user_id or not user_id.strip():
        return "Error: user_id is required."

    try:
        with get_sync_session() as session:
            statement = (
                select(Task)
                .where(Task.user_id == user_id.strip())
                .order_by(Task.created_at.desc())
            )
            tasks = session.exec(statement).all()

            if not tasks:
                return "No tasks found for this user."

            lines = [f"Found {len(tasks)} task(s):\n"]
            for i, task in enumerate(tasks, 1):
                status = "DONE" if task.is_completed else "TODO"
                pri = task.priority.upper() if task.priority else "MEDIUM"
                lines.append(f"{i}. [{status}] [{pri}] {task.title} (ID: {task.id})")
                tag_str = ", ".join(t.name for t in task.tags) if task.tags else None
                if tag_str:
                    lines.append(f"   Tags: {tag_str}")
                if task.due_at:
                    lines.append(f"   Due: {task.due_at.isoformat()}")
                if task.is_recurring:
                    lines.append(f"   Recurring: {task.recurrence_pattern}")
                lines.append(f"   Created: {task.created_at.isoformat()}")

            return "\n".join(lines)
    except Exception:
        return "Error: Failed to list tasks. Please try again."


# =============================================================================
# Tool 3: update_task
# =============================================================================


@mcp.tool()
def update_task(
    user_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    is_recurring: Optional[bool] = None,
    recurrence_pattern: Optional[str] = None,
    tags: Optional[str] = None,
) -> str:
    """
    Update fields of an existing task.

    Args:
        user_id: The authenticated user's ID
        task_id: UUID of the task to update
        title: New title (1-255 characters)
        description: New description (max 2000 characters)
        priority: New priority - "low", "medium", or "high"
        due_date: New due date in ISO 8601 format, or "none" to clear
        is_recurring: Whether task recurs after completion
        recurrence_pattern: Recurrence frequency - "daily", "weekly", "monthly", or "none" to clear
        tags: Comma-separated tag names to replace current tags, or "none" to clear all

    Returns:
        Success message with updated task details, or error message
    """
    # Validate user_id
    if not user_id or not user_id.strip():
        return "Error: user_id is required."

    # Validate task_id
    parsed_id = _validate_uuid(task_id)
    if parsed_id is None:
        return "Error: Invalid task_id format."

    # Check if at least one field is provided
    has_updates = any(
        v is not None
        for v in [title, description, priority, due_date, is_recurring, recurrence_pattern, tags]
    )
    if not has_updates:
        return "Error: No fields to update. Provide at least one field."

    # Validate title if provided
    if title is not None:
        title = title.strip() if title else ""
        if not title or len(title) > 255:
            return "Error: Title must be 1-255 characters."

    # Validate description if provided
    if description is not None and len(description) > 2000:
        return "Error: Description must be at most 2000 characters."

    # Validate priority if provided
    if priority is not None:
        priority = priority.strip().lower()
        if priority not in VALID_PRIORITIES:
            return f"Error: Invalid priority '{priority}'. Must be: low, medium, high."

    # Validate due_date if provided
    parsed_due_at = None
    clear_due = False
    if due_date is not None:
        if due_date.strip().lower() == "none":
            clear_due = True
        else:
            try:
                parsed_due_at = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                return "Error: Invalid due_date format. Use ISO 8601 or 'none' to clear."

    # Validate recurrence_pattern if provided
    clear_recurrence = False
    if recurrence_pattern is not None:
        if recurrence_pattern.strip().lower() == "none":
            clear_recurrence = True
        else:
            recurrence_pattern = recurrence_pattern.strip().lower()
            if recurrence_pattern not in VALID_RECURRENCE_PATTERNS:
                return f"Error: Invalid recurrence_pattern '{recurrence_pattern}'. Must be: daily, weekly, monthly."

    try:
        with get_sync_session() as session:
            statement = select(Task).where(
                Task.id == parsed_id,
                Task.user_id == user_id.strip(),
            )
            task = session.exec(statement).first()

            if not task:
                return "Error: Task not found."

            # Update fields
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if priority is not None:
                task.priority = priority
            if clear_due:
                task.due_at = None
            elif parsed_due_at is not None:
                task.due_at = parsed_due_at
            if is_recurring is not None:
                task.is_recurring = is_recurring
            if clear_recurrence:
                task.recurrence_pattern = None
                task.is_recurring = False
            elif recurrence_pattern is not None:
                task.recurrence_pattern = recurrence_pattern
                task.is_recurring = True
            if tags is not None:
                if tags.strip().lower() == "none":
                    task.tags = []
                else:
                    tag_names = [t.strip() for t in tags.split(",") if t.strip()]
                    task.tags = _resolve_tags(session, user_id.strip(), tag_names)

            task.updated_at = _utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)

            # Publish task.updated event (FR-033, Principle VII)
            _publish_event(
                "task-events",
                _build_task_event("task.updated", user_id.strip(), task),
            )

            tag_display = ", ".join(t.name for t in task.tags) if task.tags else "None"
            return (
                f"Task updated successfully.\n"
                f"ID: {task.id}\n"
                f"Title: {task.title}\n"
                f"Description: {task.description or 'None'}\n"
                f"Priority: {task.priority}\n"
                f"Due: {task.due_at.isoformat() if task.due_at else 'None'}\n"
                f"Recurring: {task.is_recurring} ({task.recurrence_pattern or 'N/A'})\n"
                f"Tags: {tag_display}\n"
                f"Updated: {task.updated_at.isoformat()}"
            )
    except Exception:
        return "Error: Failed to update task. Please try again."


# =============================================================================
# Tool 4: complete_task
# =============================================================================


@mcp.tool()
def complete_task(user_id: str, task_id: str) -> str:
    """
    Toggle the completion status of a task.

    Args:
        user_id: The authenticated user's ID
        task_id: UUID of the task to complete/uncomplete

    Returns:
        Success message with task status, or error message
    """
    # Validate user_id
    if not user_id or not user_id.strip():
        return "Error: user_id is required."

    # Validate task_id
    parsed_id = _validate_uuid(task_id)
    if parsed_id is None:
        return "Error: Invalid task_id format."

    try:
        with get_sync_session() as session:
            statement = select(Task).where(
                Task.id == parsed_id,
                Task.user_id == user_id.strip(),
            )
            task = session.exec(statement).first()

            if not task:
                return "Error: Task not found."

            # Toggle completion status
            if task.is_completed:
                task.is_completed = False
                task.completed_at = None
                result_msg = "Task marked as incomplete."
            else:
                task.is_completed = True
                task.completed_at = _utcnow()
                result_msg = "Task marked as completed."

            task.updated_at = _utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)

            # Publish event: task.completed or task.updated (FR-033, Principle VII)
            event_type = "task.completed" if task.is_completed else "task.updated"
            _publish_event(
                "task-events",
                _build_task_event(event_type, user_id.strip(), task),
            )

            if task.is_completed:
                return (
                    f"{result_msg}\n"
                    f"ID: {task.id}\n"
                    f"Title: {task.title}\n"
                    f"Completed: {task.completed_at.isoformat()}"
                )
            else:
                return f"{result_msg}\n" f"ID: {task.id}\n" f"Title: {task.title}"
    except Exception:
        return "Error: Failed to update task. Please try again."


# =============================================================================
# Tool 5: delete_task
# =============================================================================


@mcp.tool()
def delete_task(user_id: str, task_id: str) -> str:
    """
    Permanently delete a task.

    Args:
        user_id: The authenticated user's ID
        task_id: UUID of the task to delete

    Returns:
        Success message, or error message
    """
    # Validate user_id
    if not user_id or not user_id.strip():
        return "Error: user_id is required."

    # Validate task_id
    parsed_id = _validate_uuid(task_id)
    if parsed_id is None:
        return "Error: Invalid task_id format."

    try:
        with get_sync_session() as session:
            statement = select(Task).where(
                Task.id == parsed_id,
                Task.user_id == user_id.strip(),
            )
            task = session.exec(statement).first()

            if not task:
                return "Error: Task not found."

            task_title = task.title
            task_id_val = task.id
            session.delete(task)
            session.commit()

            # Publish task.deleted event (FR-033, Principle VII)
            _publish_event(
                "task-events",
                {
                    "event_id": str(uuid.uuid4()),
                    "event_type": "task.deleted",
                    "user_id": user_id.strip(),
                    "task_id": str(task_id_val),
                    "timestamp": _utcnow().isoformat(),
                    "version": "1.0",
                    "payload": {"title": task_title},
                },
            )

            return (
                f"Task deleted successfully.\n"
                f"ID: {task_id_val}\n"
                f"Title: {task_title}"
            )
    except Exception:
        return "Error: Failed to delete task. Please try again."


# =============================================================================
# Main entry point
# =============================================================================

if __name__ == "__main__":
    mcp.run()
