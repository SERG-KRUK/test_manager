"""Модуль проверки прав доступа и валидации для задач."""

from fastapi import HTTPException, status


class TaskPermissions:
    """Класс для проверки прав доступа и валидации операций с задачами."""

    @staticmethod
    def check_task_exists(task):
        """Проверяет существование задачи."""
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

    @staticmethod
    def validate_status_transition(current_status, new_status):
        """Валидирует переход между статусами задачи."""
        valid_transitions = {
            "created": ["in_progress", "completed"],
            "in_progress": ["completed"],
            "completed": ["in_progress"]
        }

        if new_status not in valid_transitions.get(current_status, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot transition from {current_status} to {new_status}"
            )
