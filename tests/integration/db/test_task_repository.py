from app.domain.task import Task, TaskStatus
from app.infrastructure.db.repositories.task_repository import PostgresTaskRepository


async def test_save_and_get(db_session) -> None:
    repo = PostgresTaskRepository(db_session)
    saved = await repo.save(Task(title="persist me", description="d"))

    fetched = await repo.get_by_id(saved.id)
    assert fetched is not None
    assert fetched.title == "persist me"
    assert fetched.description == "d"
    assert fetched.status is TaskStatus.OPEN


async def test_save_updates_existing(db_session) -> None:
    repo = PostgresTaskRepository(db_session)
    saved = await repo.save(Task(title="t"))
    updated = await repo.save(saved.transition_to(TaskStatus.IN_PROGRESS))

    fetched = await repo.get_by_id(updated.id)
    assert fetched is not None
    assert fetched.status is TaskStatus.IN_PROGRESS


async def test_list_and_delete(db_session) -> None:
    repo = PostgresTaskRepository(db_session)
    a = await repo.save(Task(title="a"))
    await repo.save(Task(title="b"))
    assert len(await repo.list_all()) == 2

    assert await repo.delete(a.id) is True
    assert await repo.get_by_id(a.id) is None
    assert len(await repo.list_all()) == 1
