"""HTTP controller for the Task resource."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.task_use_cases import CreateTask, GetTask, ListTasks, TransitionTask
from app.infrastructure.db.dependencies import get_db_session
from app.infrastructure.db.repositories.task_repository import PostgresTaskRepository
from app.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.observability.logger import LoguruLogger
from app.infrastructure.web.schemas.task import TaskCreateRequest, TaskResponse, TaskTransitionRequest

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


def _repository(session: SessionDep) -> PostgresTaskRepository:
    return PostgresTaskRepository(session)


def _unit_of_work(session: SessionDep) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session)


def _logger() -> LoguruLogger:
    return LoguruLogger()


RepositoryDep = Annotated[PostgresTaskRepository, Depends(_repository)]
UnitOfWorkDep = Annotated[SqlAlchemyUnitOfWork, Depends(_unit_of_work)]
LoggerDep = Annotated[LoguruLogger, Depends(_logger)]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(
    body: TaskCreateRequest, repository: RepositoryDep, uow: UnitOfWorkDep, logger: LoggerDep
) -> TaskResponse:
    """Create a new task."""
    task = await CreateTask(repository, uow, logger).execute(body.title, body.description)
    return TaskResponse.from_domain(task)


@router.get("/{task_id}")
async def get_task(task_id: UUID, repository: RepositoryDep) -> TaskResponse:
    """Fetch a single task by id."""
    task = await GetTask(repository).execute(task_id)
    return TaskResponse.from_domain(task)


@router.get("")
async def list_tasks(repository: RepositoryDep) -> list[TaskResponse]:
    """List all tasks."""
    tasks = await ListTasks(repository).execute()
    return [TaskResponse.from_domain(task) for task in tasks]


@router.post("/{task_id}/transition")
async def transition_task(
    task_id: UUID, body: TaskTransitionRequest, repository: RepositoryDep, uow: UnitOfWorkDep, logger: LoggerDep
) -> TaskResponse:
    """Move a task to a new status."""
    task = await TransitionTask(repository, uow, logger).execute(task_id, body.status)
    return TaskResponse.from_domain(task)
