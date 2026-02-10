"""
MCP Server for Task Tools

A standalone MCP server that exposes task CRUD operations as tools
for AI agents. Uses stdio transport and synchronous SQLModel sessions.

Server name: todo-task-tools
Transport: stdio
Tools: add_task, list_tasks, update_task, complete_task, delete_task
"""

import os
import re
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from sqlalchemy import create_engine
from sqlmodel import Session, select

from models import Task

# Load environment variables
load_dotenv()

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
) -> str:
    """
    Create a new task for a user.

    Args:
        user_id: The authenticated user's ID
        title: Task title (1-255 characters)
        description: Optional task description (max 2000 characters)

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

    try:
        with get_sync_session() as session:
            task = Task(
                user_id=user_id.strip(),
                title=title,
                description=description,
            )
            session.add(task)
            session.commit()
            session.refresh(task)

            return (
                f"Task created successfully.\n"
                f"ID: {task.id}\n"
                f"Title: {task.title}\n"
                f"Description: {task.description or 'None'}\n"
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
                lines.append(f"{i}. [{status}] {task.title} (ID: {task.id})")
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
) -> str:
    """
    Update the title or description of an existing task.

    Args:
        user_id: The authenticated user's ID
        task_id: UUID of the task to update
        title: New title (1-255 characters)
        description: New description (max 2000 characters)

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
    has_title = title is not None
    has_description = description is not None
    if not has_title and not has_description:
        return "Error: No fields to update. Provide title or description."

    # Validate title if provided
    if has_title:
        title = title.strip() if title else ""
        if not title or len(title) > 255:
            return "Error: Title must be 1-255 characters."

    # Validate description if provided
    if has_description and description is not None and len(description) > 2000:
        return "Error: Description must be at most 2000 characters."

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
            if has_title:
                task.title = title
            if has_description:
                task.description = description
            task.updated_at = _utcnow()

            session.add(task)
            session.commit()
            session.refresh(task)

            return (
                f"Task updated successfully.\n"
                f"ID: {task.id}\n"
                f"Title: {task.title}\n"
                f"Description: {task.description or 'None'}\n"
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
            task_id_str = str(task.id)
            session.delete(task)
            session.commit()

            return (
                f"Task deleted successfully.\n" f"ID: {task_id_str}\n" f"Title: {task_title}"
            )
    except Exception:
        return "Error: Failed to delete task. Please try again."


# =============================================================================
# Main entry point
# =============================================================================

if __name__ == "__main__":
    mcp.run()
