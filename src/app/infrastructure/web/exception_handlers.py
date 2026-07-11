"""Structured exception handlers mapping domain errors to HTTP responses."""

from typing import cast

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.domain.exceptions import DomainError, EntityNotFoundError, ValidationError
from app.infrastructure.web.schemas.error import ErrorResponse


def _error_response(status_code: int, error: str, detail: str) -> JSONResponse:
    """Build a JSON error response with the standard ``ErrorResponse`` shape."""
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(error=error, detail=detail, status_code=status_code).model_dump(),
    )


async def entity_not_found_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Map an :class:`EntityNotFoundError` to a 404 response."""
    error = cast("EntityNotFoundError", exc)
    logger.bind(detail=error.message).warning("entity_not_found")
    return _error_response(404, "Not Found", error.message)


async def validation_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Map a domain :class:`ValidationError` to a 422 response."""
    error = cast("ValidationError", exc)
    logger.bind(detail=error.message).warning("validation_error")
    return _error_response(422, "Validation Error", error.message)


async def domain_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Map any other :class:`DomainError` to a 400 response."""
    error = cast("DomainError", exc)
    logger.bind(detail=error.message).warning("domain_error")
    return _error_response(400, "Bad Request", error.message)


async def http_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Map a Starlette ``HTTPException`` to a structured error response."""
    error = cast("StarletteHTTPException", exc)
    detail = error.detail if isinstance(error.detail, str) else str(error.detail)
    logger.bind(status_code=error.status_code, detail=detail).warning("http_exception")
    return _error_response(error.status_code, "HTTP Error", detail)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Map any uncaught exception to a 500 response, hiding details unless enabled."""
    logger.opt(exception=exc).error("unhandled_exception")
    settings = request.app.state.settings
    detail = str(exc) if settings.feature_detailed_errors else "Internal Server Error"
    return _error_response(500, "Internal Server Error", detail)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the app."""
    # More specific handlers first — FastAPI matches most-specific exception type
    app.add_exception_handler(EntityNotFoundError, entity_not_found_handler)
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
