"""In-memory TaskRepository for fast, DB-free tests (demonstrates port swapping)."""

from uuid import UUID

from app.application.ports.output.task_repository import TaskRepository
from app.domain.task import Task


class InMemoryTaskRepository(TaskRepository):
    """Stores Task aggregates in a dict as a drop-in for the Postgres adapter."""

    def __init__(self) -> None:
        self._store: dict[UUID, Task] = {}

    async def get_by_id(self, entity_id: UUID) -> Task | None:
        return self._store.get(entity_id)

    async def save(self, entity: Task) -> Task:
        self._store[entity.id] = entity
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        return self._store.pop(entity_id, None) is not None

    async def list_all(self) -> list[Task]:
        return list(self._store.values())
