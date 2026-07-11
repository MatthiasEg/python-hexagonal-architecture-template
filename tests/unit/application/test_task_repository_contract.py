import pytest

from app.application.ports.output.task_repository import TaskRepository
from app.infrastructure.db.repositories.task_repository import PostgresTaskRepository
from tests.support.in_memory_task_repository import InMemoryTaskRepository


@pytest.mark.parametrize("adapter", [PostgresTaskRepository, InMemoryTaskRepository])
def test_adapter_is_a_task_repository(adapter: type) -> None:
    assert issubclass(adapter, TaskRepository)
