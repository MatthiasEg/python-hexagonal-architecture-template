"""Domain exceptions — pure business-level error hierarchy.

All exception types represent domain-level failure categories that are
independent of infrastructure technology choices.
"""


class DomainError(Exception):
    """Base exception for all domain-level errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class EntityNotFoundError(DomainError):
    """Raised when a requested entity does not exist."""

    def __init__(self, entity_type: str, entity_id: str) -> None:
        super().__init__(f"{entity_type} with id '{entity_id}' not found")


class ValidationError(DomainError):
    """Raised when domain validation rules are violated."""


class InvalidTaskTransitionError(DomainError):
    """Raised when a Task status transition violates the lifecycle rules."""

    def __init__(self, current: str, requested: str) -> None:
        super().__init__(f"cannot transition task from '{current}' to '{requested}'")
