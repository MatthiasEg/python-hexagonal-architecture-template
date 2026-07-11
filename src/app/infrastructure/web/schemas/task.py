"""API DTOs for the Task resource."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.task import Task, TaskStatus


class TaskCreateRequest(BaseModel):
    """Request body for creating a task."""

    # max_length matches the ``tasks.title`` column (String(200)) so oversized
    # input is rejected at the edge (422) instead of failing in the database.
    title: str = Field(min_length=1, max_length=200)
    description: str = ""


class TaskTransitionRequest(BaseModel):
    """Request body for transitioning a task's status."""

    status: TaskStatus


class TaskResponse(BaseModel):
    """Task representation returned by the API."""

    id: UUID
    title: str
    description: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, task: Task) -> "TaskResponse":
        """Build a response DTO from a domain Task."""
        return cls(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
