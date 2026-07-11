"""In-memory UnitOfWork test double that records commits."""

from app.application.ports.output.unit_of_work import UnitOfWork


class FakeUnitOfWork(UnitOfWork):
    """Counts commits so unit tests can assert the transaction boundary fired."""

    def __init__(self) -> None:
        self.commits = 0

    async def commit(self) -> None:
        self.commits += 1
