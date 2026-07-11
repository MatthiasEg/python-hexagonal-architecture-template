from app.domain.task import Task
from tests.support.in_memory_task_repository import InMemoryTaskRepository


async def test_save_get_list_delete_roundtrip() -> None:
    repo = InMemoryTaskRepository()
    task = Task(title="a")

    saved = await repo.save(task)
    assert await repo.get_by_id(saved.id) == saved
    assert await repo.list_all() == [saved]

    assert await repo.delete(saved.id) is True
    assert await repo.get_by_id(saved.id) is None
    assert await repo.delete(saved.id) is False
