from typing import Any

from app.infrastructure.observability.logger import LoguruLogger


class _SpyLogger:
    """Stands in for loguru's logger to capture delegated calls."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []
        self.bound: dict[str, Any] = {}

    def bind(self, **kwargs: Any) -> "_SpyLogger":
        self.bound = kwargs
        return self

    def debug(self, m: str) -> None:
        self.calls.append(("debug", m))

    def info(self, m: str) -> None:
        self.calls.append(("info", m))

    def warning(self, m: str) -> None:
        self.calls.append(("warning", m))

    def error(self, m: str) -> None:
        self.calls.append(("error", m))

    def exception(self, m: str) -> None:
        self.calls.append(("exception", m))


def test_delegates_all_levels() -> None:
    spy = _SpyLogger()
    log = LoguruLogger(spy)
    log.debug("d")
    log.info("i")
    log.warning("w")
    log.error("e")
    log.exception("x")
    assert spy.calls == [("debug", "d"), ("info", "i"), ("warning", "w"), ("error", "e"), ("exception", "x")]


def test_bind_returns_new_adapter_with_context() -> None:
    spy = _SpyLogger()
    log = LoguruLogger(spy)
    child = log.bind(task_id="123")
    assert isinstance(child, LoguruLogger)
    assert spy.bound == {"task_id": "123"}
