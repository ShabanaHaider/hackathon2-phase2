"""
Recurring Task Service - Creates new task instances when recurring tasks are completed.
"""
import logging
import os
from datetime import datetime, timedelta
from typing import Literal, Optional

import httpx
from dateutil.relativedelta import relativedelta
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Environment configuration
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
APP_PORT = int(os.getenv("APP_PORT", "8002"))

# In-memory idempotency tracking (replace with Redis/DB in production)
processed_events: set[str] = set()

app = FastAPI(
    title="Recurring Task Service",
    description="Creates new task instances when recurring tasks are completed",
    version="1.0.0"
)


# Pydantic models matching event schemas
class TaskEventPayload(BaseModel):
    """Full task data at time of event."""
    id: str
    title: str
    description: Optional[str] = None
    is_completed: bool
    priority: Literal["low", "medium", "high"]
    due_at: Optional[datetime] = None
    is_recurring: bool
    recurrence_pattern: Optional[Literal["daily", "weekly", "monthly"]] = None
    tags: list[str] = Field(default_factory=list)


class TaskEvent(BaseModel):
    """Schema for task.completed events from task-events topic."""
    event_id: str = Field(..., description="Unique identifier for idempotent processing")
    event_type: Literal["task.created", "task.updated", "task.completed"]
    user_id: str
    task_id: str
    timestamp: datetime
    version: str = Field(default="1.0")
    payload: TaskEventPayload


class DaprResponse(BaseModel):
    """Standard Dapr event handler response."""
    status: Literal["SUCCESS", "RETRY", "DROP"]


class NewTaskRequest(BaseModel):
    """Request schema for creating a new task via backend API."""
    title: str
    description: Optional[str] = None
    priority: Literal["low", "medium", "high"] = "medium"
    due_at: Optional[datetime] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[Literal["daily", "weekly", "monthly"]] = None
    tag_names: list[str] = Field(default_factory=list)


def calculate_next_due_date(current_due: datetime, pattern: str) -> datetime:
    """Calculate the next due date based on recurrence pattern."""
    if pattern == "daily":
        return current_due + timedelta(days=1)
    elif pattern == "weekly":
        return current_due + timedelta(weeks=1)
    elif pattern == "monthly":
        return current_due + relativedelta(months=1)
    else:
        raise ValueError(f"Unknown recurrence pattern: {pattern}")


async def create_task_via_backend(user_id: str, task_data: NewTaskRequest) -> dict:
    """Create a new task by calling the main backend API via Dapr service invocation."""
    dapr_url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/invoke/backend/method/api/todos"
    direct_url = f"{BACKEND_URL}/api/todos"

    # Dapr invoke: do NOT set dapr-app-id header — Dapr uses the URL path for
    # routing and automatically sets dapr-caller-app-id for the target service.
    dapr_headers = {
        "Content-Type": "application/json",
        "X-User-ID": user_id,
    }

    # Direct call: include dapr-app-id for backend auth (no Dapr sidecar in path).
    direct_headers = {
        "Content-Type": "application/json",
        "X-User-ID": user_id,
        "dapr-app-id": "recurring-task-service",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            logger.info("Attempting to create task via Dapr service invocation")
            response = await client.post(
                dapr_url,
                json=task_data.model_dump(mode="json"),
                headers=dapr_headers,
            )
            response.raise_for_status()
            logger.info("Task created successfully via Dapr")
            return response.json()

        except (httpx.ConnectError, httpx.HTTPStatusError) as e:
            logger.warning("Dapr service invocation failed (%s), falling back to direct call", e)
            response = await client.post(
                direct_url,
                json=task_data.model_dump(mode="json"),
                headers=direct_headers,
            )
            response.raise_for_status()
            logger.info("Task created successfully via direct call")
            return response.json()


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {
        "status": "healthy",
        "service": "recurring-task-service",
        "timestamp": datetime.utcnow().isoformat(),
        "processed_events": len(processed_events)
    }


@app.post("/cron-check-overdue")
async def handle_cron_check_overdue(request: Request):
    """Handle Dapr cron binding invocation to check for overdue tasks."""
    logger.info("Cron binding invoked: check-overdue at %s", datetime.utcnow().isoformat())
    return {"status": "ok"}


@app.post("/events/task-completed", response_model=DaprResponse)
async def handle_task_completed(request: Request):
    """
    Handle incoming Dapr task.completed events from 'task-events' topic.

    When a recurring task is completed, creates a new task instance
    with the next due date calculated based on the recurrence pattern.
    """
    try:
        body = await request.json()
        logger.info("Received task-completed event: %s", body)

        event_data = body.get("data", body)
        event = TaskEvent(**event_data)

        # Only process task.completed events
        if event.event_type != "task.completed":
            logger.info("Ignoring event type: %s", event.event_type)
            return DaprResponse(status="SUCCESS")

        # Check idempotency
        if event.event_id in processed_events:
            logger.info("Event %s already processed, skipping", event.event_id)
            return DaprResponse(status="SUCCESS")

        # Check if task is recurring
        if not event.payload.is_recurring:
            logger.info("Task %s is not recurring, skipping", event.task_id)
            processed_events.add(event.event_id)
            return DaprResponse(status="SUCCESS")

        if not event.payload.recurrence_pattern:
            logger.error("Recurring task %s has no recurrence pattern", event.task_id)
            processed_events.add(event.event_id)
            return DaprResponse(status="DROP")

        if not event.payload.due_at:
            logger.error("Recurring task %s has no due_at date", event.task_id)
            processed_events.add(event.event_id)
            return DaprResponse(status="DROP")

        next_due_at = calculate_next_due_date(
            event.payload.due_at,
            event.payload.recurrence_pattern
        )

        logger.info(
            "Creating next instance of recurring task '%s' with due date %s (pattern: %s)",
            event.payload.title, next_due_at, event.payload.recurrence_pattern
        )

        new_task_data = NewTaskRequest(
            title=event.payload.title,
            description=event.payload.description,
            priority=event.payload.priority,
            due_at=next_due_at,
            is_recurring=True,
            recurrence_pattern=event.payload.recurrence_pattern,
            tag_names=event.payload.tags
        )

        created_task = await create_task_via_backend(event.user_id, new_task_data)

        logger.info(
            "Successfully created recurring task instance. Original: %s, New: %s",
            event.task_id, created_task.get("id", "unknown")
        )

        processed_events.add(event.event_id)
        return DaprResponse(status="SUCCESS")

    except ValueError as e:
        logger.error("Validation error processing task-completed event: %s", e)
        return DaprResponse(status="DROP")

    except httpx.HTTPError as e:
        logger.error("HTTP error creating recurring task: %s", e, exc_info=True)
        return DaprResponse(status="RETRY")

    except Exception as e:
        logger.error("Error processing task-completed event: %s", e, exc_info=True)
        return DaprResponse(status="RETRY")


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Recurring Task Service on port %d", APP_PORT)
    uvicorn.run(app, host="0.0.0.0", port=APP_PORT, log_level="info")
