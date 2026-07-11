"""Generic persistence port shared by all entity repositories."""

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities import Entity


class Repository[E: Entity](ABC):
    """Output port for basic CRUD persistence of a domain entity type ``E``."""

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> E | None: ...

    @abstractmethod
    async def save(self, entity: E) -> E: ...

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool: ...
