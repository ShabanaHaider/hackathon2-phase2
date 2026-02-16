import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field as PydanticField
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from auth import get_current_user
from database import get_session
from models import Tag, TagResponse

router = APIRouter(prefix="/tags", tags=["tags"])


class TagCreateRequest(BaseModel):
    name: str = PydanticField(min_length=1, max_length=50)


@router.get("", response_model=list[TagResponse])
async def list_tags(
    current_user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[Tag]:
    user_id = current_user["user_id"]
    statement = select(Tag).where(Tag.user_id == user_id).order_by(Tag.name)
    results = await session.exec(statement)
    return list(results.all())


@router.post("", response_model=TagResponse, status_code=201)
async def create_tag(
    body: TagCreateRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Tag:
    user_id = current_user["user_id"]

    # Check if tag already exists (case-insensitive)
    statement = select(Tag).where(
        Tag.user_id == user_id,
        func.lower(Tag.name) == func.lower(body.name.strip()),
    )
    result = await session.exec(statement)
    existing = result.first()
    if existing:
        raise HTTPException(status_code=409, detail="Tag already exists")

    tag = Tag(name=body.name.strip(), user_id=user_id)
    session.add(tag)
    await session.commit()
    await session.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: uuid.UUID,
    current_user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Response:
    user_id = current_user["user_id"]
    statement = select(Tag).where(Tag.id == tag_id, Tag.user_id == user_id)
    result = await session.exec(statement)
    tag = result.first()
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    await session.delete(tag)
    await session.commit()
    return Response(status_code=204)
