"""Error response schema for structured API errors."""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response returned by all exception handlers."""

    error: str
    detail: str
    status_code: int
