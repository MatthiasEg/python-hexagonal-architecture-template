"""Async SQLAlchemy engine and session factory."""

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.infrastructure.config import Settings


def ensure_async_url(url: str) -> str:
    """Convert postgresql:// to postgresql+asyncpg:// if needed."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def create_async_engine_from_settings(settings: Settings) -> AsyncEngine:
    """Create an async SQLAlchemy engine from application settings."""
    if settings.database_url is None:
        msg = "database_url is required to create an engine"
        raise ValueError(msg)

    url = ensure_async_url(settings.database_url.get_secret_value())

    return create_async_engine(
        url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_pool_max_overflow,
        echo=settings.debug,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create an async session factory bound to the given engine."""
    return async_sessionmaker(engine, expire_on_commit=False)
