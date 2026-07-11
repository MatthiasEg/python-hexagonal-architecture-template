"""Persistence port for the Task aggregate."""

from abc import abstractmethod

from app.application.ports.output.repository import Repository
from app.domain.task import Task


class TaskRepository(Repository[Task]):
    """Output port for storing and retrieving Task aggregates."""

    @abstractmethod
    async def list_all(self) -> list[Task]:
        """Return all tasks."""
        ...
