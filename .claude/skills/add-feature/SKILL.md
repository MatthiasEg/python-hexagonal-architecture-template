---
name: add-feature
description: Use when adding a new resource or use case to this FastAPI hexagonal template. Drives the domain-outward runbook that mirrors the Task slice and ends at a green validation loop.
---

# Add a feature

Add a new resource (or use case) by mirroring the canonical `Task` slice, building from the
domain outward so each layer compiles against the one beneath it.

## Steps

Follow `docs/adding-a-feature.md` in order. Do not skip ahead a layer; each depends on the
one before it.

1. **Domain** (`src/app/domain/<name>.py`): entity (extend `Entity`) and any state machine
   or invariants. Pure: no framework imports. Add domain exceptions in
   `src/app/domain/exceptions.py`. Write the unit test for the invariants first.
2. **Output port** (`src/app/application/ports/output/<name>_repository.py`): the driven
   contract the use cases need. Add an in-memory fake in `tests/support/` and a contract test
   asserting adapters satisfy the port.
3. **Input ports + use cases** (`ports/input/<name>_ports.py`,
   `use_cases/<name>_use_cases.py`): one use case per operation. Mutating use cases take
   `(repository, uow, logger)` and call `await uow.commit()`. Unit-test each with the
   in-memory repo, no mocks.
4. **Persistence** (`db/models/<name>.py` + Alembic migration via the `add-migration` skill;
   `db/repositories/<name>_repository.py`).
5. **API edge** (`web/schemas/<name>.py` DTOs, `web/controllers/<name>.py` router). Bound DTO
   fields to the DB column limits so bad input is rejected at the edge, not in the database.
   Wire the router in `web/app.py`.
6. **Tests**: integration (repository against Postgres via testcontainers; API via ASGI).

## Definition of done

Run the `check-fix` skill (or `uv run poe check` directly) and iterate until green. The
feature is not done until the full loop passes and coverage stays above the floor. Commit
with a Conventional Commit message (`feat(<layer>): ...`).
