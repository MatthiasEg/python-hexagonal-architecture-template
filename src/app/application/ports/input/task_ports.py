"""Input (driving) ports for Task operations."""

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.task import Task, TaskStatus


class CreateTaskUseCase(ABC):
    """Create a new task."""

    @abstractmethod
    async def execute(self, title: str, description: str) -> Task: ...


class GetTaskUseCase(ABC):
    """Fetch a task by id."""

    @abstractmethod
    async def execute(self, task_id: UUID) -> Task: ...


class ListTasksUseCase(ABC):
    """List all tasks."""

    @abstractmethod
    async def execute(self) -> list[Task]: ...


class TransitionTaskUseCase(ABC):
    """Move a task to a new status."""

    @abstractmethod
    async def execute(self, task_id: UUID, new_status: TaskStatus) -> Task: ...
