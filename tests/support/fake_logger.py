"""In-memory LoggerPort test double that records emitted log records."""

from typing import Any

from app.application.ports.output.logger import LoggerPort


class FakeLogger(LoggerPort):
    """Records (level, message, bound-context) tuples for assertions.

    ``bind`` returns a child sharing the same record sink, mirroring loguru.
    """

    def __init__(
        self,
        context: dict[str, Any] | None = None,
        sink: list[tuple[str, str, dict[str, Any]]] | None = None,
    ) -> None:
        self._context = context or {}
        self.records: list[tuple[str, str, dict[str, Any]]] = sink if sink is not None else []

    def bind(self, **kwargs: Any) -> "FakeLogger":
        return FakeLogger({**self._context, **kwargs}, self.records)

    def _log(self, level: str, message: str) -> None:
        self.records.append((level, message, self._context))

    def debug(self, message: str) -> None:
        self._log("debug", message)

    def info(self, message: str) -> None:
        self._log("info", message)

    def warning(self, message: str) -> None:
        self._log("warning", message)

    def error(self, message: str) -> None:
        self._log("error", message)

    def exception(self, message: str) -> None:
        self._log("exception", message)
