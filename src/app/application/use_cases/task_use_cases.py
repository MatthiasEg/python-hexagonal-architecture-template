"""Use cases orchestrating the Task aggregate via its output ports.

Mutating use cases depend on three driven ports: a ``TaskRepository`` for
persistence, a ``UnitOfWork`` for the transactional boundary, and a
``LoggerPort`` for structured logging, none of which couple the application
layer to a concrete framework.
"""

from uuid import UUID

from app.application.ports.input.task_ports import (
    CreateTaskUseCase,
    GetTaskUseCase,
    ListTasksUseCase,
    TransitionTaskUseCase,
)
from app.application.ports.output.logger import LoggerPort
from app.application.ports.output.task_repository import TaskRepository
from app.application.ports.output.unit_of_work import UnitOfWork
from app.domain.exceptions import EntityNotFoundError
from app.domain.task import Task, TaskStatus


class CreateTask(CreateTaskUseCase):
    """Persist a new task in the OPEN state and commit the transaction."""

    def __init__(self, tasks: TaskRepository, uow: UnitOfWork, logger: LoggerPort) -> None:
        self._tasks = tasks
        self._uow = uow
        self._logger = logger

    async def execute(self, title: str, description: str) -> Task:
        task = await self._tasks.save(Task(title=title, description=description))
        await self._uow.commit()
        self._logger.bind(task_id=str(task.id)).info("task_created")
        return task


class GetTask(GetTaskUseCase):
    """Fetch a task or raise if it does not exist."""

    def __init__(self, tasks: TaskRepository) -> None:
        self._tasks = tasks

    async def execute(self, task_id: UUID) -> Task:
        task = await self._tasks.get_by_id(task_id)
        if task is None:
            raise EntityNotFoundError("Task", str(task_id))
        return task


class ListTasks(ListTasksUseCase):
    """Return all tasks."""

    def __init__(self, tasks: TaskRepository) -> None:
        self._tasks = tasks

    async def execute(self) -> list[Task]:
        return await self._tasks.list_all()


class TransitionTask(TransitionTaskUseCase):
    """Move a task to a new status, enforcing the lifecycle rules, then commit."""

    def __init__(self, tasks: TaskRepository, uow: UnitOfWork, logger: LoggerPort) -> None:
        self._tasks = tasks
        self._uow = uow
        self._logger = logger

    async def execute(self, task_id: UUID, new_status: TaskStatus) -> Task:
        task = await self._tasks.get_by_id(task_id)
        if task is None:
            raise EntityNotFoundError("Task", str(task_id))
        updated = await self._tasks.save(task.transition_to(new_status))
        await self._uow.commit()
        self._logger.bind(task_id=str(updated.id), status=updated.status.value).info("task_transitioned")
        return updated
