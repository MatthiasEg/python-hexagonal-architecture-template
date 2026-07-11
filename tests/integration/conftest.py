"""Integration test fixtures.

Postgres is provided in two ways:
- **CI:** ``APP_DATABASE_URL`` is pre-set by a Postgres service container —
  no Docker daemon needed in the test runner.
- **Local dev:** when the env var is absent, testcontainers spins up a
  Postgres container automatically (requires a running Docker daemon).
"""

import os
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

import app.infrastructure.db.models  # noqa: F401  # register models on Base.metadata
from app.infrastructure.config import Environment, Settings
from app.infrastructure.db.base import Base
from app.infrastructure.db.dependencies import get_db_session
from app.infrastructure.db.engine import ensure_async_url
from app.infrastructure.web.app import create_app

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def database_url() -> Generator[str]:
    """Provide a Postgres connection URL for integration tests.

    If ``APP_DATABASE_URL`` is already set (e.g. in CI), use it directly.
    Otherwise, start a throwaway Postgres container via testcontainers.
    """
    env_url = os.environ.get("APP_DATABASE_URL")

    if env_url:
        # CI path: strip the asyncpg driver so ensure_async_url re-adds it uniformly.
        yield env_url.replace("+asyncpg", "")
    else:
        with PostgresContainer("postgres:17-alpine") as container:
            url = container.get_connection_url().replace("+psycopg2", "")
            old = os.environ.get("APP_DATABASE_URL")
            os.environ["APP_DATABASE_URL"] = url
            yield url
            if old is None:
                os.environ.pop("APP_DATABASE_URL", None)
            else:
                os.environ["APP_DATABASE_URL"] = old


@pytest.fixture(scope="session", autouse=True)
def _run_migrations(database_url: str) -> None:  # noqa: ARG001
    alembic_cfg = Config(str(PROJECT_ROOT / "alembic.ini"))
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(autouse=True)
async def _clean_tables(database_url: str) -> AsyncGenerator[None]:
    yield
    tables = [t.name for t in reversed(Base.metadata.sorted_tables)]
    if not tables:
        return
    engine = create_async_engine(ensure_async_url(database_url))
    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE {', '.join(tables)} CASCADE"))
    await engine.dispose()


@pytest.fixture
async def db_session(database_url: str) -> AsyncGenerator[AsyncSession]:
    engine = create_async_engine(ensure_async_url(database_url))
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


@pytest.fixture
async def api_client(database_url: str) -> AsyncGenerator[AsyncClient]:
    """Async HTTP client wired to the real app and database."""
    settings = Settings(
        environment=Environment.LOCAL,
        debug=True,
        database_url=database_url,
        feature_request_logging=False,
        feature_detailed_errors=True,
    )
    app = create_app(settings=settings)
    engine = create_async_engine(ensure_async_url(database_url))
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def _test_db_session() -> AsyncGenerator[AsyncSession]:
        async with factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = _test_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    await engine.dispose()
