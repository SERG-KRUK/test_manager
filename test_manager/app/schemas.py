"""Модуль Pydantic схем для валидации данных задач."""

from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Перечисление допустимых статусов задачи."""

    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskBase(BaseModel):
    """Базовая схема задачи с общими полями."""

    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.CREATED


class TaskCreate(TaskBase):
    """Схема для создания новой задачи."""

    pass


class TaskUpdate(BaseModel):
    """Схема для обновления существующей задачи."""

    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None


class Task(TaskBase):
    """Схема ответа с данными задачи."""

    uuid: UUID

    class Config:
        """Конфигурация Pydantic модели."""

        from_attributes = True
