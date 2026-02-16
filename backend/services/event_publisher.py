"""Dapr-based event publisher service for task events.

Publishes events via Dapr HTTP API to Kafka topics.
Gracefully degrades if Dapr sidecar is not available.
"""

import logging
import os
import uuid
from datetime import datetime, timezone

import httpx

from models import (
    TaskResponse,
    TaskEvent,
    TaskEventPayload,
    TaskDeletedEvent,
    TaskDeletedPayload,
    ReminderEvent,
    ReminderEventPayload,
)

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
PUBSUB_NAME = os.getenv("PUBSUB_NAME", "pubsub-kafka")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EventPublisher:
    """Service to publish task events via Dapr HTTP API."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=5.0)
        return self._client

    async def _publish(self, topic: str, data: dict) -> None:
        """Publish data to a Dapr pubsub topic."""
        url = f"{DAPR_BASE_URL}/v1.0/publish/{PUBSUB_NAME}/{topic}"
        try:
            client = await self._get_client()
            response = await client.post(url, json=data)
            response.raise_for_status()
            logger.info("Published to %s: %s", topic, data.get("event_type", "unknown"))
        except httpx.ConnectError:
            logger.warning("Dapr sidecar not available — event not published to %s", topic)
        except Exception as e:
            logger.error("Failed to publish to %s: %s", topic, str(e))

    async def publish_task_event(
        self,
        event_type: str,
        user_id: str,
        task_response: TaskResponse,
    ) -> None:
        """Publish a task event to the 'task-events' topic."""
        payload = TaskEventPayload(
            id=task_response.id,
            title=task_response.title,
            description=task_response.description,
            is_completed=task_response.is_completed,
            priority=task_response.priority,
            due_at=task_response.due_at,
            is_recurring=task_response.is_recurring,
            recurrence_pattern=task_response.recurrence_pattern,
            tags=[tag.name for tag in task_response.tags] if task_response.tags else [],
        )
        event = TaskEvent(
            event_type=event_type,
            user_id=user_id,
            task_id=task_response.id,
            payload=payload,
        )
        await self._publish("task-events", event.model_dump(mode="json"))

    async def publish_task_deleted_event(
        self,
        user_id: str,
        task_id: uuid.UUID,
        task_title: str,
    ) -> None:
        """Publish a task.deleted event to the 'task-events' topic."""
        event = TaskDeletedEvent(
            user_id=user_id,
            task_id=task_id,
            payload=TaskDeletedPayload(title=task_title),
        )
        await self._publish("task-events", event.model_dump(mode="json"))

    async def publish_reminder_event(
        self,
        user_id: str,
        task_response: TaskResponse,
        reminder_time: datetime,
    ) -> None:
        """Publish a reminder event to the 'reminders' topic."""
        if not task_response.due_at:
            return
        event = ReminderEvent(
            user_id=user_id,
            task_id=task_response.id,
            payload=ReminderEventPayload(
                title=task_response.title,
                due_at=task_response.due_at,
                priority=task_response.priority,
            ),
        )
        await self._publish("reminders", event.model_dump(mode="json"))

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# Global instance
event_publisher = EventPublisher()
