"""Модуль с тестами для CRUD операций и валидации задач."""

from uuid import UUID

import pytest

from app import schemas, crud
from app.models import TaskStatus


@pytest.mark.asyncio
class TestTaskCRUD:
    """Класс тестов для CRUD операций с задачами."""

    @pytest.fixture(autouse=True)
    async def setup(self, test_db, async_client):
        """Фикстура настройки тестового окружения."""
        self.client = async_client
        self.test_task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "status": TaskStatus.CREATED
        }

    @pytest.mark.order(1)
    async def test_create_task(self):
        """Тест создания новой задачи."""
        response = await self.client.post("/tasks/", json=self.test_task_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == self.test_task_data["title"]
        assert data["description"] == self.test_task_data["description"]
        assert data["status"] == self.test_task_data["status"]
        assert UUID(data["uuid"])

    @pytest.mark.order(2)
    async def test_get_task(self):
        """Тест получения задачи по UUID."""
        create_response = await self.client.post(
            "/tasks/", json=self.test_task_data)
        task_uuid = create_response.json()["uuid"]

        response = await self.client.get(f"/tasks/{task_uuid}")
        assert response.status_code == 200
        data = response.json()
        assert data["uuid"] == task_uuid
        assert data["title"] == self.test_task_data["title"]

    @pytest.mark.order(3)
    async def test_get_nonexistent_task(self):
        """Тест получения несуществующей задачи."""
        response = await self.client.get(
            "/tasks/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    @pytest.mark.order(4)
    async def test_get_tasks_list(self):
        """Тест получения списка задач."""
        for i in range(3):
            task_data = {**self.test_task_data, "title": f"Task {i}"}
            await self.client.post("/tasks/", json=task_data)

        response = await self.client.get("/tasks/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("uuid" in task for task in data)

    @pytest.mark.order(5)
    async def test_update_task(self):
        """Тест обновления задачи."""
        create_response = await self.client.post(
            "/tasks/", json=self.test_task_data)
        task_uuid = create_response.json()["uuid"]

        update_data = {
            "title": "Updated Task",
            "status": TaskStatus.IN_PROGRESS
        }

        response = await self.client.put(
            f"/tasks/{task_uuid}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["status"] == update_data["status"]

    @pytest.mark.order(6)
    async def test_invalid_status_transition(self):
        """Тест невалидного перехода статуса."""
        create_response = await self.client.post(
            "/tasks/", json=self.test_task_data)
        task_uuid = create_response.json()["uuid"]

        update_data = {"status": TaskStatus.COMPLETED}
        response = await self.client.put(
            f"/tasks/{task_uuid}", json=update_data)
        assert response.status_code == 400

    @pytest.mark.order(7)
    async def test_delete_task(self):
        """Тест удаления задачи."""
        create_response = await self.client.post(
            "/tasks/", json=self.test_task_data)
        task_uuid = create_response.json()["uuid"]
        response = await self.client.delete(f"/tasks/{task_uuid}")
        assert response.status_code == 204

        get_response = await self.client.get(f"/tasks/{task_uuid}")
        assert get_response.status_code == 404


@pytest.mark.asyncio
class TestTaskValidation:
    """Класс тестов для валидации данных задач."""

    @pytest.mark.parametrize("invalid_data", [
        {"title": ""},  # Empty title
        {"title": "x" * 256},  # Title too long
    ])
    async def test_invalid_task_creation(self, async_client, invalid_data):
        """Тест создания задачи с невалидными данными."""
        response = await async_client.post("/tasks/", json=invalid_data)
        assert response.status_code == 422
