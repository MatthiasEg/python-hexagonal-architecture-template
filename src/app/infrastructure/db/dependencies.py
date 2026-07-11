"""FastAPI dependencies for database session management and port wiring."""

from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession]:
    """Yield an async database session, rolling back on error.

    Transaction commits are owned by the application layer via the ``UnitOfWork``
    port (see ``SqlAlchemyUnitOfWork``), not by this request-scoped dependency.
    """
    session_factory = request.app.state.db_session_factory
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
