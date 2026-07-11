"""FastAPI application factory and composition root."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.infrastructure.config import Settings, get_settings
from app.infrastructure.db.engine import create_async_engine_from_settings, create_session_factory
from app.infrastructure.observability.logging import configure_logging
from app.infrastructure.observability.telemetry import configure_telemetry, instrument_app
from app.infrastructure.web.controllers import health, tasks
from app.infrastructure.web.exception_handlers import register_exception_handlers
from app.infrastructure.web.middleware.request_logging import RequestLoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Manage application startup and shutdown."""
    settings: Settings = app.state.settings

    # Startup: initialise DB engine if configured
    has_database = settings.database_url is not None and bool(settings.database_url.get_secret_value())
    if has_database:
        engine = create_async_engine_from_settings(settings)
        app.state.db_engine = engine
        app.state.db_session_factory = create_session_factory(engine)
        logger.bind(pool_size=settings.database_pool_size).info("database_connected")

    else:
        app.state.db_engine = None
        app.state.db_session_factory = None
        logger.bind(reason="no database_url configured").info("database_skipped")

    yield

    # Shutdown
    if app.state.db_engine is not None:
        await app.state.db_engine.dispose()
        logger.info("database_disconnected")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        settings: Optional settings override (useful for testing).
                  If not provided, uses the global settings singleton.
    """
    if settings is None:
        settings = get_settings()

    configure_logging(settings)
    configure_telemetry(settings)

    # Disable Swagger UI in production
    docs_url = None if settings.is_production else "/docs"
    redoc_url = None if settings.is_production else "/redoc"
    openapi_url = None if settings.is_production else "/openapi.json"

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        lifespan=lifespan,
    )

    # Store settings in app state for access in routes
    app.state.settings = settings

    # Exception handlers
    register_exception_handlers(app)

    # Middleware (outermost first)
    if settings.feature_request_logging:
        app.add_middleware(RequestLoggingMiddleware)  # type: ignore[arg-type]  # ty: Starlette _MiddlewareFactory ParamSpec

    # Configure CORS middleware if origins are specified
    # CORS fields are typed as str (not list) because pydantic-settings
    # tries to JSON-decode list types, which fails on plain env values like "*".
    cors_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,  # type: ignore[arg-type]  # ty: Starlette _MiddlewareFactory ParamSpec
            allow_origins=cors_origins,
            allow_credentials=settings.cors_allow_credentials,
            allow_methods=[m.strip() for m in settings.cors_allow_methods.split(",") if m.strip()],
            allow_headers=[h.strip() for h in settings.cors_allow_headers.split(",") if h.strip()],
        )

    instrument_app(app)
    app.include_router(health.router)
    app.include_router(tasks.router)

    return app
