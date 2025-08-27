"""Модуль с API эндпоинтами для управления задачами."""

from uuid import UUID
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas, models, crud, permissions
from app.database import get_db


app = FastAPI(
    title="Task Manager API",
    description="CRUD API for managing tasks",
    version="1.0.0"
)


@app.post("/tasks/", response_model=schemas.Task,
          status_code=status.HTTP_201_CREATED)
async def create_task(
    task: schemas.TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создает новую задачу."""
    task_crud = crud.TaskCRUD(db)
    return await task_crud.create_task(task)


@app.get("/tasks/", response_model=List[schemas.Task])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Получает список задач с пагинацией."""
    task_crud = crud.TaskCRUD(db)
    tasks = await task_crud.get_tasks(skip, limit)
    return tasks


@app.get("/tasks/{task_uuid}", response_model=schemas.Task)
async def get_task(
    task_uuid: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Получает задачу по UUID."""
    task_crud = crud.TaskCRUD(db)
    task = await task_crud.get_task(task_uuid)
    permissions.TaskPermissions.check_task_exists(task)
    return task


@app.put("/tasks/{task_uuid}", response_model=schemas.Task)
async def update_task(
    task_uuid: UUID,
    task_update: schemas.TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновляет существующую задачу."""
    task_crud = crud.TaskCRUD(db)

    existing_task = await task_crud.get_task(task_uuid)
    permissions.TaskPermissions.check_task_exists(existing_task)

    if task_update.status and existing_task.status != task_update.status:
        permissions.TaskPermissions.validate_status_transition(
            existing_task.status, task_update.status
        )

    updated_task = await task_crud.update_task(task_uuid, task_update)
    return updated_task


@app.delete("/tasks/{task_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_uuid: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Удаляет задачу по UUID."""
    task_crud = crud.TaskCRUD(db)

    existing_task = await task_crud.get_task(task_uuid)
    permissions.TaskPermissions.check_task_exists(existing_task)

    success = await task_crud.delete_task(task_uuid)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task"
        )
