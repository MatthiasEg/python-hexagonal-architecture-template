"""Loguru-backed implementation of the LoggerPort."""

from __future__ import annotations

from typing import Any

from loguru import logger as loguru_logger

from app.application.ports.output.logger import LoggerPort


class LoguruLogger(LoggerPort):
    """Delegates structured logging to loguru, preserving bound context."""

    def __init__(self, _logger: Any = None) -> None:  # noqa: ANN401  # injected loguru logger has no clean public type
        self._logger = _logger or loguru_logger

    def bind(self, **kwargs: Any) -> LoguruLogger:  # noqa: ANN401  # structured context is arbitrary key-values
        """Return a new adapter with the given key-value pairs bound as context."""
        return LoguruLogger(self._logger.bind(**kwargs))

    def debug(self, message: str) -> None:
        """Log a debug message."""
        self._logger.debug(message)

    def info(self, message: str) -> None:
        """Log an informational message."""
        self._logger.info(message)

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self._logger.warning(message)

    def error(self, message: str) -> None:
        """Log an error message."""
        self._logger.error(message)

    def exception(self, message: str) -> None:
        """Log an error message with exception traceback."""
        self._logger.exception(message)
