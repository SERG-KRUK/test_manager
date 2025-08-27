"""Модуль с тестами для API эндпоинтов управления задачами."""

from uuid import UUID

import pytest

from app.models import TaskStatus


@pytest.mark.asyncio
class TestTaskAPI:
    """Класс тестов для API эндпоинтов задач."""

    @pytest.fixture(autouse=True)
    async def setup(self, async_client):
        """Фикстура настройки тестового окружения."""
        self.client = async_client
        self.test_task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "status": TaskStatus.CREATED.value
        }

    async def test_create_task_api(self):
        """Тест создания задачи через API."""
        response = await self.client.post("/tasks/", json=self.test_task_data)

        assert response.status_code == 201
        data = response.json()

        assert data["title"] == self.test_task_data["title"]
        assert data["description"] == self.test_task_data["description"]
        assert data["status"] == self.test_task_data["status"]
        assert UUID(data["uuid"])

    async def test_get_task_api(self):
        """Тест получения задачи по UUID через API."""
        create_response = await self.client.post(
            "/tasks/", json=self.test_task_data)
        task_uuid = create_response.json()["uuid"]

        response = await self.client.get(f"/tasks/{task_uuid}")

        assert response.status_code == 200
        data = response.json()
        assert data["uuid"] == task_uuid
        assert data["title"] == self.test_task_data["title"]

    async def test_get_tasks_list_api(self):
        """Тест получения списка задач с пагинацией через API."""
        for i in range(3):
            task_data = {**self.test_task_data, "title": f"Task {i}"}
            await self.client.post("/tasks/", json=task_data)

        response = await self.client.get("/tasks/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("uuid" in task for task in data)

    async def test_update_task_api(self):
        """Тест обновления задачи через API."""
        create_response = await self.client.post(
            "/tasks/", json=self.test_task_data)
        task_uuid = create_response.json()["uuid"]

        update_data = {
            "title": "Updated Task",
            "status": TaskStatus.IN_PROGRESS.value
        }

        response = await self.client.put(
            f"/tasks/{task_uuid}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["status"] == update_data["status"]

    async def test_delete_task_api(self):
        """Тест удаления задачи через API."""
        create_response = await self.client.post(
            "/tasks/", json=self.test_task_data)
        task_uuid = create_response.json()["uuid"]

        response = await self.client.delete(f"/tasks/{task_uuid}")

        assert response.status_code == 204

        get_response = await self.client.get(f"/tasks/{task_uuid}")
        assert get_response.status_code == 404

    async def test_invalid_status_transition_api(self):
        """Тест невалидного перехода статуса через API."""
        create_response = await self.client.post(
            "/tasks/", json=self.test_task_data)
        task_uuid = create_response.json()["uuid"]

        update_data = {"status": TaskStatus.COMPLETED.value}
        response = await self.client.put(
            f"/tasks/{task_uuid}", json=update_data)

        assert response.status_code == 400


@pytest.mark.asyncio
class TestTaskValidationAPI:
    """Класс тестов для валидации данных задач в API."""

    @pytest.mark.parametrize("invalid_data,expected_status", [
        ({"title": ""}, 422),  # Empty title
        ({"title": "x" * 256}, 422),  # Title too long
        ({"status": "invalid_status"}, 422),  # Invalid status
    ])
    async def test_invalid_task_creation(self, async_client,
                                         invalid_data, expected_status):
        """Тест создания задачи с невалидными данными через API."""
        response = await async_client.post("/tasks/", json=invalid_data)
        assert response.status_code == expected_status
