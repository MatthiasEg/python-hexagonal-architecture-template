"""The Task DTOs reject input the database cannot store.

schemathesis found that a NUL byte in a string field passes DTO validation and then
crashes with a 500 in PostgreSQL. These tests pin the edge-validation fix so the
regression cannot come back regardless of what the fuzzer happens to generate.
"""

import pytest
from pydantic import ValidationError

from app.infrastructure.web.schemas.task import TaskCreateRequest


def test_rejects_null_byte_in_title() -> None:
    """A NUL byte in the title is a 422 at the edge, not a 500 in the database."""
    with pytest.raises(ValidationError):
        TaskCreateRequest(title="bad\x00title")


def test_rejects_null_byte_in_description() -> None:
    """A NUL byte in the description is rejected the same way."""
    with pytest.raises(ValidationError):
        TaskCreateRequest(title="ok", description="bad\x00description")


def test_accepts_ordinary_text() -> None:
    """Normal input still validates."""
    request = TaskCreateRequest(title="Write the runbook", description="mirror the Task slice")
    assert request.title == "Write the runbook"
