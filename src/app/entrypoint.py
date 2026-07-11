"""Application entrypoint: configure logging first, run migrations, then start uvicorn.

Running everything from a single Python entrypoint lets us install the loguru
intercept handler *before* any library (uvicorn reloader, alembic) emits log
records, producing fully unified log output across all components.
"""

from __future__ import annotations

import uvicorn
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig

from app.infrastructure.config import Environment, get_settings
from app.infrastructure.observability.logging import configure_logging


def main() -> None:
    """Configure logging, run pending migrations, and start the ASGI server."""
    settings = get_settings()
    configure_logging(settings)

    if settings.database_url and settings.database_url.get_secret_value():
        alembic_cfg = AlembicConfig("alembic.ini")
        alembic_command.upgrade(alembic_cfg, "head")

    # log_config=None tells uvicorn not to call logging.config.dictConfig(),
    # so our intercept handler installed above stays in place for the reloader
    # process; the worker subprocess reinstalls it via create_app() → configure_logging().
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        log_config=None,
        reload=settings.environment == Environment.LOCAL,
    )


if __name__ == "__main__":
    main()
