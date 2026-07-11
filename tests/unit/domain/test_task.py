import pytest

from app.domain.exceptions import InvalidTaskTransitionError
from app.domain.task import Task, TaskStatus


def test_new_task_defaults_to_open() -> None:
    task = Task(title="write plan")
    assert task.status is TaskStatus.OPEN
    assert task.description == ""


def test_legal_transition_returns_updated_copy() -> None:
    task = Task(title="write plan")
    moved = task.transition_to(TaskStatus.IN_PROGRESS)
    assert moved.status is TaskStatus.IN_PROGRESS
    assert moved.id == task.id
    assert task.status is TaskStatus.OPEN  # original unchanged (immutable)


@pytest.mark.parametrize(
    ("start", "target"),
    [
        (TaskStatus.OPEN, TaskStatus.DONE),
        (TaskStatus.DONE, TaskStatus.IN_PROGRESS),
        (TaskStatus.CANCELLED, TaskStatus.OPEN),
    ],
)
def test_illegal_transition_raises(start: TaskStatus, target: TaskStatus) -> None:
    task = Task(title="x", status=start)
    with pytest.raises(InvalidTaskTransitionError):
        task.transition_to(target)
