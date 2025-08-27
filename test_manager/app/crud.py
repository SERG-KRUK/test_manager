"""CRUD операций с задачами."""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from uuid import UUID
from app import models, schemas


class TaskCRUD:
    """Класс для CRUD операций с задачами."""

    def __init__(self, db: Session):
        """Инициализация класса TaskCRUD."""
        self.db = db

    async def create_task(self, task: schemas.TaskCreate) -> models.Task:
        """Создает новую задачу в базе данных."""
        db_task = models.Task(**task.dict())
        self.db.add(db_task)
        await self.db.commit()
        await self.db.refresh(db_task)
        return db_task

    async def get_task(self, task_uuid: UUID) -> models.Task:
        """Получает задачу по UUID."""
        result = await self.db.execute(
            select(models.Task).where(models.Task.uuid == task_uuid)
        )
        return result.scalar_one_or_none()

    async def get_tasks(
            self, skip: int = 0, limit: int = 100) -> list[models.Task]:
        """Получает список задач с пагинацией."""
        result = await self.db.execute(
            select(models.Task).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def update_task(
            self, task_uuid: UUID,
            task_update: schemas.TaskUpdate) -> Optional[models.Task]:
        """Обновляет существующую задачу."""
        db_task = await self.get_task(task_uuid)
        if not db_task:
            return None

        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)

        self.db.add(db_task)
        await self.db.commit()
        await self.db.refresh(db_task)
        return db_task

    async def delete_task(self, task_uuid: UUID) -> bool:
        """Удаляет задачу по UUID."""
        db_task = await self.get_task(task_uuid)
        if not db_task:
            return False

        await self.db.delete(db_task)
        await self.db.commit()
        return True
