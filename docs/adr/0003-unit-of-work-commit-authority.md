# ADR-0003: The UnitOfWork is the sole commit authority

- **Status:** Accepted
- **Date:** 2026-07-05

## Context

Something has to own the transaction boundary. Two obvious candidates: the request-scoped
database session (commit on the way out of the request), or an explicit unit-of-work the use
case drives. If both commit — or if the session auto-commits *and* a use case commits — you get
partial writes, double commits, and behavior that depends on middleware ordering. The
application layer must not import SQLAlchemy, so the boundary has to be expressed as a port.

## Decision

Commits go through one path only: the `UnitOfWork` output port
(`application/ports/output/unit_of_work.py`), implemented by `SqlAlchemyUnitOfWork` in
infrastructure. Concretely:

- `get_db_session` yields a session and **does not commit** — it only rolls back on an
  exception and closes.
- A mutating use case takes `(repository, uow, logger)` and calls `await uow.commit()`
  explicitly after its writes.
- Read use cases take only the repository and never commit.
- Repositories `add`/`flush` but never `commit`.

## Alternatives considered

- **Session commits at end of request** (a common FastAPI pattern). Simple, but it hides the
  boundary in middleware, commits even when the use case wanted to abort, and couples
  transactionality to the web layer — invisible to the domain and to tests. Rejected.
- **Repository commits per write.** Destroys atomicity across multiple writes in one use case
  and makes "save two things or neither" impossible. Rejected.
- **No unit of work; rely on autocommit.** Non-deterministic and untestable. Rejected.

## Consequences

- Transaction boundaries are explicit and visible in the use case, and unit-testable with a
  fake unit of work (`tests/support/fake_unit_of_work.py`) — no database required.
- Slightly more ceremony: mutating use cases carry a third dependency. This is intentional; the
  boundary is a first-class thing, not an accident of framework config.
- The application layer stays free of SQLAlchemy — the commit contract is a port.
