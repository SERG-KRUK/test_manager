"""Модуль моделей базы данных."""

import enum
import uuid
from sqlalchemy import Column, Enum, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class TaskStatus(str, enum.Enum):
    """Перечисление статусов задачи."""

    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Task(Base):
    """Модель задачи в базе данных."""

    __tablename__ = "tasks"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        Enum(TaskStatus), default=TaskStatus.CREATED, nullable=False)
