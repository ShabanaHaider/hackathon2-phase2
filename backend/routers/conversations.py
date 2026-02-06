import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auth import get_current_user
from database import get_session
from models import (
    ChatRequest,
    ChatResponse,
    Conversation,
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
    Message,
    MessageCreate,
    MessageResponse,
)
from agent import run_agent, format_message_history

router = APIRouter(prefix="/conversations", tags=["conversations"])


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# --- US1: Create a New Conversation ---


@router.post("", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    body: ConversationCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Conversation:
    user_id = current_user["user_id"]
    now = _utcnow()
    conversation = Conversation(
        title=body.title,
        user_id=user_id,
        created_at=now,
        updated_at=now,
    )
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation


# --- US1: List All Conversations for a User ---


@router.get("", response_model=list[ConversationResponse])
async def list_conversations(
    current_user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[Conversation]:
    user_id = current_user["user_id"]
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    results = await session.exec(statement)
    return list(results.all())


# --- US1: Get a Single Conversation ---


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: uuid.UUID,
    current_user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Conversation:
    user_id = current_user["user_id"]
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id,
    )
    result = await session.exec(statement)
    conversation = result.first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


# --- US3: Update a Conversation ---


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: uuid.UUID,
    body: ConversationUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Conversation:
    user_id = current_user["user_id"]
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id,
    )
    result = await session.exec(statement)
    conversation = result.first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(conversation, key, value)

    conversation.updated_at = _utcnow()

    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation


# --- US3: Delete a Conversation ---


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: uuid.UUID,
    current_user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Response:
    user_id = current_user["user_id"]
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id,
    )
    result = await session.exec(statement)
    conversation = result.first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await session.delete(conversation)
    await session.commit()
    return Response(status_code=204)


# --- US2: Create a Message in a Conversation ---


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=201,
)
async def create_message(
    conversation_id: uuid.UUID,
    body: MessageCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Message:
    user_id = current_user["user_id"]

    # Verify conversation exists and belongs to the user
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id,
    )
    result = await session.exec(statement)
    conversation = result.first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    now = _utcnow()

    message = Message(
        conversation_id=conversation_id,
        role=body.role,
        content=body.content,
        created_at=now,
    )
    session.add(message)

    # Update conversation's updated_at to bubble it up in list ordering
    conversation.updated_at = now
    session.add(conversation)

    await session.commit()
    await session.refresh(message)
    return message


# --- US2: List Messages for a Conversation ---


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
async def list_messages(
    conversation_id: uuid.UUID,
    current_user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[Message]:
    user_id = current_user["user_id"]

    # Verify conversation exists and belongs to the user
    conv_statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id,
    )
    conv_result = await session.exec(conv_statement)
    conversation = conv_result.first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Retrieve messages in chronological order
    msg_statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    msg_result = await session.exec(msg_statement)
    return list(msg_result.all())


# --- AI Agent Chat Endpoint ---


@router.post(
    "/{conversation_id}/chat",
    response_model=ChatResponse,
    status_code=200,
)
async def chat_with_agent(
    conversation_id: uuid.UUID,
    body: ChatRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ChatResponse:
    """
    Send a message to the AI agent and receive a response.

    This endpoint:
    1. Verifies the conversation belongs to the user
    2. Loads the last 20 messages for context
    3. Saves the user's message
    4. Invokes the AI agent with the message and context
    5. Saves the agent's response
    6. Returns both messages
    """
    user_id = current_user["user_id"]

    # Verify conversation exists and belongs to the user
    conv_statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id,
    )
    conv_result = await session.exec(conv_statement)
    conversation = conv_result.first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    now = _utcnow()

    # Load message history (last 20 messages for context)
    history_statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(20)
    )
    history_result = await session.exec(history_statement)
    history_messages = list(reversed(history_result.all()))

    # Format history for the agent
    message_history = format_message_history(history_messages)

    # Save user message
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=body.message,
        created_at=now,
    )
    session.add(user_message)

    # Update conversation timestamp
    conversation.updated_at = now
    session.add(conversation)

    # Commit user message first (so it's persisted even if agent fails)
    await session.commit()
    await session.refresh(user_message)

    # Run the AI agent
    agent_response = await run_agent(
        user_id=user_id,
        message=body.message,
        message_history=message_history,
    )

    # Save assistant message
    assistant_now = _utcnow()
    assistant_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=agent_response,
        created_at=assistant_now,
    )
    session.add(assistant_message)

    # Update conversation timestamp again
    conversation.updated_at = assistant_now
    session.add(conversation)

    await session.commit()
    await session.refresh(assistant_message)

    return ChatResponse(
        user_message=MessageResponse.model_validate(user_message),
        assistant_message=MessageResponse.model_validate(assistant_message),
    )
