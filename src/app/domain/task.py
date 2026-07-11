"""Task domain entity and its status state machine."""

from enum import StrEnum
from typing import Self

from app.domain.entities import Entity
from app.domain.exceptions import InvalidTaskTransitionError


class TaskStatus(StrEnum):
    """Lifecycle states for a Task."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


_ALLOWED_TRANSITIONS: dict[TaskStatus, frozenset[TaskStatus]] = {
    TaskStatus.OPEN: frozenset({TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED}),
    TaskStatus.IN_PROGRESS: frozenset({TaskStatus.DONE, TaskStatus.CANCELLED}),
    TaskStatus.DONE: frozenset(),
    TaskStatus.CANCELLED: frozenset(),
}


class Task(Entity):
    """A unit of work with a constrained status lifecycle."""

    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.OPEN

    def transition_to(self, new_status: TaskStatus) -> Self:
        """Return a copy transitioned to ``new_status``.

        Raises:
            InvalidTaskTransitionError: if the transition is not permitted.
        """
        if new_status not in _ALLOWED_TRANSITIONS[self.status]:
            raise InvalidTaskTransitionError(self.status.value, new_status.value)
        return self.model_copy(update={"status": new_status}).with_updated_at()
