"""
Notification Service - Handles task reminders and notifications via Dapr Pub/Sub.
"""
import logging
import os
from datetime import datetime
from typing import Literal, Optional

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
APP_PORT = int(os.getenv("APP_PORT", "8001"))

# In-memory idempotency tracking (replace with Redis/DB in production)
processed_events: set[str] = set()

app = FastAPI(
    title="Notification Service",
    description="Handles task reminders and user notifications",
    version="1.0.0"
)


# Pydantic models matching event schemas
class ReminderEventPayload(BaseModel):
    """Payload for reminder.due events."""
    title: str
    due_at: datetime
    priority: Literal["low", "medium", "high"]


class ReminderEvent(BaseModel):
    """Schema for reminder.due events from reminders topic."""
    event_id: str = Field(..., description="Unique identifier for idempotent processing")
    event_type: Literal["reminder.due"]
    user_id: str
    task_id: str
    timestamp: datetime
    version: str = Field(default="1.0")
    payload: ReminderEventPayload


class NotificationEventPayload(BaseModel):
    """Payload for notification.request events."""
    notification_type: Literal["reminder", "recurring_created"]
    title: str
    message: str
    task_id: Optional[str] = None


class NotificationEvent(BaseModel):
    """Schema for notification.request events from notifications topic."""
    event_id: str = Field(..., description="Unique identifier for idempotent processing")
    event_type: Literal["notification.request"]
    user_id: str
    timestamp: datetime
    version: str = Field(default="1.0")
    payload: NotificationEventPayload


class DaprResponse(BaseModel):
    """Standard Dapr event handler response."""
    status: Literal["SUCCESS", "RETRY", "DROP"]


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {
        "status": "healthy",
        "service": "notification-service",
        "timestamp": datetime.utcnow().isoformat(),
        "processed_events": len(processed_events)
    }


@app.post("/events/reminder-due", response_model=DaprResponse)
async def handle_reminder_due(request: Request):
    """
    Handle incoming Dapr reminder.due events from 'reminders' topic.

    Validates ReminderEvent schema, logs the reminder (stub for real notification),
    and returns acknowledgment to Dapr.
    """
    try:
        body = await request.json()
        logger.info("Received reminder event: %s", body)

        # Extract event data (handle both CloudEvents wrapper and raw event)
        event_data = body.get("data", body)

        # Validate against schema
        event = ReminderEvent(**event_data)

        # Check idempotency
        if event.event_id in processed_events:
            logger.info("Event %s already processed, skipping", event.event_id)
            return DaprResponse(status="SUCCESS")

        # Process the reminder (stub implementation)
        logger.info(
            "REMINDER: User %s - Task '%s' (ID: %s) due at %s. Priority: %s",
            event.user_id, event.payload.title, event.task_id,
            event.payload.due_at, event.payload.priority
        )

        # Mark as processed
        processed_events.add(event.event_id)

        return DaprResponse(status="SUCCESS")

    except ValueError as e:
        logger.error("Validation error processing reminder event: %s", e)
        return DaprResponse(status="DROP")

    except Exception as e:
        logger.error("Error processing reminder event: %s", e, exc_info=True)
        return DaprResponse(status="RETRY")


@app.post("/events/notification", response_model=DaprResponse)
async def handle_notification(request: Request):
    """
    Handle incoming Dapr notification.request events from 'notifications' topic.

    Validates NotificationEvent schema, logs the notification,
    and returns acknowledgment to Dapr.
    """
    try:
        body = await request.json()
        logger.info("Received notification event: %s", body)

        # Extract event data (handle both CloudEvents wrapper and raw event)
        event_data = body.get("data", body)

        # Validate against schema
        event = NotificationEvent(**event_data)

        # Check idempotency
        if event.event_id in processed_events:
            logger.info("Event %s already processed, skipping", event.event_id)
            return DaprResponse(status="SUCCESS")

        # Process the notification (stub implementation)
        logger.info(
            "NOTIFICATION: User %s - Type: %s Title: '%s' Message: '%s' Task ID: %s",
            event.user_id, event.payload.notification_type,
            event.payload.title, event.payload.message,
            event.payload.task_id or "N/A"
        )

        # Mark as processed
        processed_events.add(event.event_id)

        return DaprResponse(status="SUCCESS")

    except ValueError as e:
        logger.error("Validation error processing notification event: %s", e)
        return DaprResponse(status="DROP")

    except Exception as e:
        logger.error("Error processing notification event: %s", e, exc_info=True)
        return DaprResponse(status="RETRY")


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Notification Service on port %d", APP_PORT)
    uvicorn.run(app, host="0.0.0.0", port=APP_PORT, log_level="info")
