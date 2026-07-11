"""Postgres adapter implementing the TaskRepository output port."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.output.task_repository import TaskRepository
from app.domain.task import Task, TaskStatus
from app.infrastructure.db.models.task import TaskModel


def _to_domain(row: TaskModel) -> Task:
    """Map an ORM row to a domain Task."""
    return Task(
        id=row.id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        title=row.title,
        description=row.description,
        status=TaskStatus(row.status),
    )


class PostgresTaskRepository(TaskRepository):
    """Persists Task aggregates in Postgres via SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: UUID) -> Task | None:
        row = await self._session.get(TaskModel, entity_id)
        return _to_domain(row) if row is not None else None

    async def save(self, entity: Task) -> Task:
        row = await self._session.get(TaskModel, entity.id)
        if row is None:
            row = TaskModel(
                id=entity.id,
                title=entity.title,
                description=entity.description,
                status=entity.status.value,
            )
            self._session.add(row)
        else:
            row.title = entity.title
            row.description = entity.description
            row.status = entity.status.value
        await self._session.flush()
        await self._session.refresh(row)
        return _to_domain(row)

    async def delete(self, entity_id: UUID) -> bool:
        row = await self._session.get(TaskModel, entity_id)
        if row is None:
            return False
        await self._session.delete(row)
        await self._session.flush()
        return True

    async def list_all(self) -> list[Task]:
        result = await self._session.execute(select(TaskModel))
        return [_to_domain(row) for row in result.scalars().all()]
