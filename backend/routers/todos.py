import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auth import get_current_user
from database import get_session
from models import Task, TaskCreate, TaskResponse, TaskUpdate

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
    task = Task(
        title=body.title,
        description=body.description,
        user_id=user_id,
        created_at=now,
        updated_at=now,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


# --- US2: List All Tasks for a User ---


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    current_user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[Task]:
    user_id = current_user["user_id"]
    statement = select(Task).where(Task.user_id == user_id)
    results = await session.exec(statement)
    return list(results.all())


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

    await session.delete(task)
    await session.commit()
    return Response(status_code=204)
