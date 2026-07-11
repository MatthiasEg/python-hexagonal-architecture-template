"""Port for transactional unit-of-work boundaries.

Allows use cases to signal persistence checkpoints without coupling
to any specific database or ORM technology.
"""

from abc import ABC, abstractmethod


class UnitOfWork(ABC):
    """Marks a transactional boundary for persisted changes."""

    @abstractmethod
    async def commit(self) -> None:
        """Persist all changes made since the last commit."""
        ...
