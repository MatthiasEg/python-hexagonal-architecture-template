"""Health and readiness probe endpoints."""

from fastapi import APIRouter, Request
from loguru import logger
from sqlalchemy import text

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "healthy"}


@router.get("/health/live")
async def liveness_probe() -> dict[str, str]:
    """Liveness probe for the container runtime.

    Returns 200 if the application is running.
    Used by the orchestrator (Kubernetes, etc.) to decide whether to restart the container.
    """
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness_probe(request: Request) -> dict[str, str]:
    """Readiness probe for the container runtime.

    Returns 200 if the application is ready to accept traffic.
    Checks database connectivity when configured.
    """
    settings = request.app.state.settings
    result: dict[str, str] = {
        "status": "ready",
        "environment": settings.environment.value,
        "version": settings.app_version,
    }

    # Probe database if configured
    session_factory = getattr(request.app.state, "db_session_factory", None)
    if session_factory is not None:
        try:
            async with session_factory() as session:
                await session.execute(text("SELECT 1"))
            result["database"] = "connected"
        except Exception:
            logger.exception("readiness_db_check_failed")
            result["database"] = "unavailable"
            result["status"] = "degraded"

    return result
