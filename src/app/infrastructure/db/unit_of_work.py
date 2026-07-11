"""SQLAlchemy-backed implementation of the UnitOfWork port."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.output.unit_of_work import UnitOfWork


class SqlAlchemyUnitOfWork(UnitOfWork):
    """Wraps an async SQLAlchemy session to provide commit boundaries."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        """Persist all changes made since the last commit."""
        await self._session.commit()
