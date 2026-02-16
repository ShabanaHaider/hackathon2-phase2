import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, Query
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import or_, case, desc, asc

from auth import get_current_user
from database import get_session
from models import Task, Tag, TaskTagLink, TaskCreate, TaskResponse, TaskUpdate, TagResponse
from services.event_publisher import event_publisher

router = APIRouter(prefix="/todos", tags=["todos"])


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# --- US1: Create a New Task ---


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    body: TaskCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Task:
    user_id = current_user["user_id"]
    now = _utcnow()

    # Validate recurrence pattern
    if body.recurrence_pattern is not None and not body.is_recurring:
        raise HTTPException(status_code=422, detail="recurrence_pattern requires is_recurring=True")

    task = Task(
        title=body.title,
        description=body.description,
        priority=body.priority,
        due_at=body.due_at,
        is_recurring=body.is_recurring,
        recurrence_pattern=body.recurrence_pattern,
        user_id=user_id,
        created_at=now,
        updated_at=now,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)

    # Handle tags if provided
    if body.tag_names:
        for tag_name in body.tag_names:
            # Get or create tag
            tag_statement = select(Tag).where(
                Tag.user_id == user_id,
                func.lower(Tag.name) == func.lower(tag_name)
            )
            result = await session.exec(tag_statement)
            tag = result.first()

            if not tag:
                # Create new tag
                tag = Tag(
                    name=tag_name.strip(),
                    user_id=user_id,
                    created_at=now
                )
                session.add(tag)
                await session.commit()
                await session.refresh(tag)

            # Create the relationship
            task_tag_link = TaskTagLink(task_id=task.id, tag_id=tag.id)
            session.add(task_tag_link)

        await session.commit()
        await session.refresh(task)  # Refresh to get the tags

    # Publish event
    task_response = TaskResponse.model_validate(task)
    await event_publisher.publish_task_event("task.created", user_id, task_response)

    return task


# --- US2: List All Tasks for a User ---


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    current_user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    status: Optional[str] = Query(None, description="Filter by status: pending/completed"),
    priority: Optional[str] = Query(None, description="Filter by priority: low/medium/high"),
    tag: Optional[str] = Query(None, description="Filter by tag name"),
    sort_by: Optional[str] = Query(None, description="Sort by field: created_at/due_at/priority/title"),
    sort_order: Optional[str] = Query("asc", description="Sort order: asc/desc"),
    q: Optional[str] = Query(None, description="Search query for title/description/tags"),
) -> list[Task]:
    user_id = current_user["user_id"]

    statement = select(Task).where(Task.user_id == user_id)

    # Track if we've joined the tag tables
    tag_joined = False

    # Apply filters
    if status and status != "all":
        if status == "pending":
            statement = statement.where(Task.is_completed == False)
        elif status == "completed":
            statement = statement.where(Task.is_completed == True)

    if priority:
        statement = statement.where(Task.priority == priority)

    if tag:
        statement = statement.join(TaskTagLink).join(Tag).where(func.lower(Tag.name) == func.lower(tag))
        tag_joined = True

    # Apply search
    if q:
        search_term = f"%{q}%"
        if not tag_joined:
            statement = statement.outerjoin(TaskTagLink).outerjoin(Tag)
        statement = statement.where(
            or_(
                Task.title.ilike(search_term),
                Task.description.ilike(search_term),
                Tag.name.ilike(search_term),
            )
        ).distinct()

    # Priority sort uses numeric mapping: high=1, medium=2, low=3
    priority_order = case(
        (Task.priority == "high", 1),
        (Task.priority == "medium", 2),
        (Task.priority == "low", 3),
        else_=2,
    )

    # Apply sorting
    if sort_by:
        order_fn = desc if sort_order == "desc" else asc
        if sort_by == "created_at":
            statement = statement.order_by(order_fn(Task.created_at))
        elif sort_by == "due_at":
            statement = statement.order_by(order_fn(Task.due_at).nulls_last())
        elif sort_by == "priority":
            statement = statement.order_by(order_fn(priority_order))
        elif sort_by == "title":
            statement = statement.order_by(order_fn(Task.title))
    else:
        statement = statement.order_by(Task.created_at.desc())

    results = await session.exec(statement)
    return list(results.unique().all())


# --- US3: View a Single Task ---


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    current_user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Task:
    user_id = current_user["user_id"]
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.exec(statement)
    task = result.first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# --- US4: Update an Existing Task ---


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    body: TaskUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Task:
    user_id = current_user["user_id"]
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.exec(statement)
    task = result.first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = body.model_dump(exclude_unset=True)
    tag_names = update_data.pop("tag_names", None)

    # Validate recurrence pattern
    if "recurrence_pattern" in update_data and update_data["recurrence_pattern"] is not None:
        if not update_data.get("is_recurring", task.is_recurring):
            raise HTTPException(status_code=422, detail="recurrence_pattern requires is_recurring=True")

    for key, value in update_data.items():
        setattr(task, key, value)

    # Auto-manage completed_at based on is_completed toggle
    if "is_completed" in update_data:
        if task.is_completed:
            task.completed_at = _utcnow()
        else:
            task.completed_at = None

    task.updated_at = _utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    # Handle tags if tag_names was explicitly provided
    if tag_names is not None:
        # Remove existing tag associations
        delete_stmt = select(TaskTagLink).where(TaskTagLink.task_id == task.id)
        existing_links = await session.exec(delete_stmt)
        for link in existing_links:
            await session.delete(link)

        # Add new tag associations
        if tag_names:
            now = _utcnow()
            for tag_name in tag_names:
                # Get or create tag
                tag_statement = select(Tag).where(
                    Tag.user_id == user_id,
                    func.lower(Tag.name) == func.lower(tag_name)
                )
                result = await session.exec(tag_statement)
                tag = result.first()

                if not tag:
                    # Create new tag
                    tag = Tag(
                        name=tag_name.strip(),
                        user_id=user_id,
                        created_at=now
                    )
                    session.add(tag)
                    await session.commit()
                    await session.refresh(tag)

                # Create the relationship
                task_tag_link = TaskTagLink(task_id=task.id, tag_id=tag.id)
                session.add(task_tag_link)

        await session.commit()
        await session.refresh(task)  # Refresh to get the tags

    # Publish event — use task.completed if is_completed changed to True
    task_response = TaskResponse.model_validate(task)
    if "is_completed" in update_data and task.is_completed:
        event_type = "task.completed"
    else:
        event_type = "task.updated"
    await event_publisher.publish_task_event(event_type, user_id, task_response)

    return task


# --- US5: Delete a Task ---


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: uuid.UUID,
    current_user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Response:
    user_id = current_user["user_id"]
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.exec(statement)
    task = result.first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task_title = task.title
    task_id_val = task.id
    await session.delete(task)
    await session.commit()

    # Publish delete event
    await event_publisher.publish_task_deleted_event(user_id, task_id_val, task_title)

    return Response(status_code=204)
