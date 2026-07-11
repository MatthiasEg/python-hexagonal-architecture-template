import uuid

import pytest

from app.application.use_cases.task_use_cases import CreateTask, GetTask, ListTasks, TransitionTask
from app.domain.exceptions import EntityNotFoundError, InvalidTaskTransitionError
from app.domain.task import TaskStatus
from tests.support.fake_logger import FakeLogger
from tests.support.fake_unit_of_work import FakeUnitOfWork
from tests.support.in_memory_task_repository import InMemoryTaskRepository


async def test_create_commits_and_logs() -> None:
    repo = InMemoryTaskRepository()
    uow = FakeUnitOfWork()
    logger = FakeLogger()
    created = await CreateTask(repo, uow, logger).execute("plan", "write it")
    fetched = await GetTask(repo).execute(created.id)
    assert fetched.title == "plan"
    assert fetched.description == "write it"
    assert fetched.status is TaskStatus.OPEN
    assert uow.commits == 1
    assert ("info", "task_created", {"task_id": str(created.id)}) in logger.records


async def test_get_missing_raises() -> None:
    repo = InMemoryTaskRepository()
    with pytest.raises(EntityNotFoundError):
        await GetTask(repo).execute(uuid.uuid4())


async def test_list_returns_all() -> None:
    repo = InMemoryTaskRepository()
    uow = FakeUnitOfWork()
    logger = FakeLogger()
    await CreateTask(repo, uow, logger).execute("a", "")
    await CreateTask(repo, uow, logger).execute("b", "")
    assert len(await ListTasks(repo).execute()) == 2


async def test_transition_commits_logs_and_persists() -> None:
    repo = InMemoryTaskRepository()
    uow = FakeUnitOfWork()
    logger = FakeLogger()
    created = await CreateTask(repo, uow, logger).execute("a", "")
    moved = await TransitionTask(repo, uow, logger).execute(created.id, TaskStatus.IN_PROGRESS)
    assert moved.status is TaskStatus.IN_PROGRESS
    assert (await GetTask(repo).execute(created.id)).status is TaskStatus.IN_PROGRESS
    assert uow.commits == 2  # one for the create, one for the transition
    assert ("info", "task_transitioned", {"task_id": str(created.id), "status": "in_progress"}) in logger.records


async def test_transition_illegal_raises() -> None:
    repo = InMemoryTaskRepository()
    uow = FakeUnitOfWork()
    logger = FakeLogger()
    created = await CreateTask(repo, uow, logger).execute("a", "")
    with pytest.raises(InvalidTaskTransitionError):
        await TransitionTask(repo, uow, logger).execute(created.id, TaskStatus.DONE)


async def test_transition_missing_raises() -> None:
    repo = InMemoryTaskRepository()
    uow = FakeUnitOfWork()
    logger = FakeLogger()
    with pytest.raises(EntityNotFoundError):
        await TransitionTask(repo, uow, logger).execute(uuid.uuid4(), TaskStatus.IN_PROGRESS)
