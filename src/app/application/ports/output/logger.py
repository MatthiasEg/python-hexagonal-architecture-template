"""Port for structured logging with contextual binding."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LoggerPort(ABC):
    """Structured logger that supports contextual key-value binding.

    Use ``bind()`` to attach context (e.g. record_id) that appears on every
    subsequent log line from the returned instance.
    """

    @abstractmethod
    def bind(self, **kwargs: Any) -> LoggerPort:  # noqa: ANN401  # structured context is arbitrary key-values
        """Return a new logger with the given key-value pairs bound as context."""
        ...

    @abstractmethod
    def debug(self, message: str) -> None:
        """Log a debug message."""
        ...

    @abstractmethod
    def info(self, message: str) -> None:
        """Log an informational message."""
        ...

    @abstractmethod
    def warning(self, message: str) -> None:
        """Log a warning message."""
        ...

    @abstractmethod
    def error(self, message: str) -> None:
        """Log an error message."""
        ...

    @abstractmethod
    def exception(self, message: str) -> None:
        """Log an error message with exception traceback."""
        ...
