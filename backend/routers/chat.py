"""
Stateless Chat API Endpoint (Spec 7)

Provides a user-scoped chat endpoint that orchestrates conversation persistence
and AI agent execution. The endpoint is completely stateless - all context is
reconstructed from the database on each request.

Endpoint: POST /api/{user_id}/chat
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auth import get_current_user
from database import get_session
from models import (
    Conversation,
    Message,
    MessageResponse,
    UserChatRequest,
    UserChatResponse,
    ToolCallInfo,
)
from agent import run_agent, format_message_history

router = APIRouter(tags=["chat"])


def _utcnow() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


# --- T008: User ID Validation ---


def validate_user_id(user_id: str, current_user: dict[str, Any]) -> None:
    """
    Validate that the URL user_id matches the authenticated user.

    Raises:
        HTTPException: 403 if user_id doesn't match JWT user
    """
    jwt_user_id = current_user.get("user_id")
    if user_id != jwt_user_id:
        raise HTTPException(
            status_code=403,
            detail="User ID mismatch"
        )


# --- T009: Get or Create Conversation ---


async def get_or_create_conversation(
    user_id: str,
    session: AsyncSession,
) -> Conversation:
    """
    Get the user's conversation or create one if it doesn't exist.

    Single conversation per user model - query by user_id, create if not found.

    Args:
        user_id: The authenticated user's ID
        session: Database session

    Returns:
        Conversation: The user's conversation (existing or newly created)
    """
    statement = select(Conversation).where(Conversation.user_id == user_id)
    result = await session.exec(statement)
    conversation = result.first()

    if conversation is None:
        now = _utcnow()
        conversation = Conversation(
            user_id=user_id,
            title="Task Assistant",
            created_at=now,
            updated_at=now,
        )
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)

    return conversation


# --- T010: Load Message History ---


async def load_message_history(
    conversation_id: uuid.UUID,
    session: AsyncSession,
    limit: int = 20,
) -> list[Message]:
    """
    Load the last N messages from a conversation for agent context.

    Args:
        conversation_id: The conversation's UUID
        session: Database session
        limit: Maximum number of messages to load (default 20)

    Returns:
        List of messages in chronological order (oldest first)
    """
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    result = await session.exec(statement)
    messages = list(result.all())
    # Reverse to chronological order
    return list(reversed(messages))


# --- Main Chat Endpoint (T007, T011-T014) ---


@router.post("/{user_id}/chat", response_model=UserChatResponse)
async def chat_with_agent(
    user_id: str,
    body: UserChatRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserChatResponse:
    """
    Send a message to the AI agent and receive a response.

    This endpoint:
    1. Validates the authenticated user matches the URL user_id
    2. Gets or creates a conversation for the user
    3. Loads the last 20 messages for context
    4. Persists the user's message (before agent call for data integrity)
    5. Invokes the AI agent with message and history
    6. Persists the agent's response
    7. Returns both messages and any tool calls

    Args:
        user_id: User ID from URL path (must match JWT user)
        body: Request body containing the user's message
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        UserChatResponse with user_message, assistant_message, and tool_calls

    Raises:
        HTTPException: 403 if user_id mismatch, 500 on agent failure
    """
    # T008: Validate user_id matches JWT
    validate_user_id(user_id, current_user)

    # T009: Get or create conversation
    conversation = await get_or_create_conversation(user_id, session)

    # T010: Load message history
    history_messages = await load_message_history(conversation.id, session)
    message_history = format_message_history(history_messages)

    now = _utcnow()

    # T011: Persist user message BEFORE agent call (data integrity)
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=body.message,
        created_at=now,
    )
    session.add(user_message)

    # Update conversation timestamp
    conversation.updated_at = now
    session.add(conversation)

    # Commit user message first (survives agent failure)
    await session.commit()
    await session.refresh(user_message)

    # T012: Invoke agent with message history
    try:
        agent_result = await run_agent(
            user_id=user_id,
            message=body.message,
            message_history=message_history,
        )

        # Handle both old (string) and new (tuple) return formats
        if isinstance(agent_result, tuple):
            agent_response, tool_calls = agent_result
        else:
            agent_response = agent_result
            tool_calls = None

    except Exception as e:
        # Agent failed but user message is preserved
        raise HTTPException(
            status_code=500,
            detail={
                "error": "AI agent error",
                "message": str(e),
                "user_message": MessageResponse.model_validate(user_message).model_dump(),
            }
        )

    # T013: Persist assistant message
    assistant_now = _utcnow()
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=agent_response,
        created_at=assistant_now,
    )
    session.add(assistant_message)

    # Update conversation timestamp
    conversation.updated_at = assistant_now
    session.add(conversation)

    await session.commit()
    await session.refresh(assistant_message)

    # T014: Assemble response
    return UserChatResponse(
        user_message=MessageResponse.model_validate(user_message),
        assistant_message=MessageResponse.model_validate(assistant_message),
        tool_calls=tool_calls,
    )
