"""API DTOs for the Task resource."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator, BaseModel, Field

from app.domain.task import Task, TaskStatus


def _no_null_bytes(value: str) -> str:
    """Reject NUL bytes, which a PostgreSQL text column cannot store.

    Without this, a title or description containing a NUL byte passes DTO
    validation and only fails deep in the database with a 500. Rejecting it here
    turns it into a 422 at the edge, the same reason ``title`` is length-bounded.
    """
    if "\x00" in value:
        raise ValueError("must not contain null bytes")
    return value


NonNullStr = Annotated[str, AfterValidator(_no_null_bytes)]


class TaskCreateRequest(BaseModel):
    """Request body for creating a task."""

    # max_length matches the ``tasks.title`` column (String(200)) so oversized
    # input is rejected at the edge (422) instead of failing in the database.
    title: Annotated[NonNullStr, Field(min_length=1, max_length=200)]
    description: NonNullStr = ""


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
