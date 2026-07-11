"""Structured logging configuration using loguru."""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

from loguru import logger
from opentelemetry import trace

from app.infrastructure.config import Environment, Settings

if TYPE_CHECKING:
    import loguru as loguru_module

# Loggers whose access logs are covered by RequestLoggingMiddleware (suppressed to avoid duplicates)
_SUPPRESSED_LOGGERS = ("uvicorn.access",)

# Loggers that configure their own handlers and disable propagation; these must be overridden explicitly
_INTERCEPTED_LOGGERS = ("uvicorn", "uvicorn.error", "uvicorn.access", "alembic")


class _InterceptHandler(logging.Handler):
    """Redirect stdlib logging records to loguru, preserving caller location."""

    def emit(self, record: logging.LogRecord) -> None:
        """Forward a stdlib log record to loguru."""
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Walk up the stack until we leave logging internals to find the true caller.
        frame, depth = logging.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def _otel_patcher(record: loguru_module.Record) -> None:
    """Inject OpenTelemetry trace/span IDs into log records."""
    span = trace.get_current_span()
    ctx = span.get_span_context()
    if ctx and ctx.trace_id:
        record["extra"]["trace_id"] = format(ctx.trace_id, "032x")
        record["extra"]["span_id"] = format(ctx.span_id, "016x")


def configure_logging(settings: Settings) -> None:
    """Configure loguru and redirect all stdlib logging (uvicorn, alembic, …) through it."""
    logger.remove()

    # Configure patcher globally for OTel trace context injection
    logger.configure(patcher=_otel_patcher)

    if settings.environment == Environment.LOCAL:
        logger.add(
            sys.stdout,
            level=settings.log_level,
            format="<green>{time:YYYY-MM-DDTHH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
            "{extra}",
            colorize=True,
            serialize=False,
            backtrace=True,
            diagnose=True,
        )
    else:
        logger.add(
            sys.stdout,
            level=settings.log_level,
            serialize=True,
            backtrace=False,
            diagnose=False,
        )

    # Intercept all stdlib logging → loguru via root logger
    handler = _InterceptHandler()
    logging.root.setLevel(0)
    logging.root.handlers = [handler]

    # Override library loggers that set their own handlers and disable propagation
    for name in _INTERCEPTED_LOGGERS:
        lib_logger = logging.getLogger(name)
        lib_logger.handlers = [handler]
        lib_logger.propagate = False

    # Suppress access logs already covered by RequestLoggingMiddleware
    for name in _SUPPRESSED_LOGGERS:
        logging.getLogger(name).disabled = True
