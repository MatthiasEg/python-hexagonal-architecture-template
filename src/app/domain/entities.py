"""Domain entities — pure business objects with no infrastructure dependencies."""

from abc import ABC
from datetime import UTC, datetime
from typing import Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class Entity(BaseModel, ABC):
    """Abstract base for all domain entities with identity and timestamps."""

    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def with_updated_at(self) -> Self:
        """Return a copy with ``updated_at`` refreshed to now (UTC)."""
        return self.model_copy(update={"updated_at": datetime.now(UTC)})
