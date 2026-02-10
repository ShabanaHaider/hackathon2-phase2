import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auth import get_current_user
from database import get_session
from models import (
    Conversation,
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
    Message,
    MessageCreate,
    MessageResponse,
)

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
