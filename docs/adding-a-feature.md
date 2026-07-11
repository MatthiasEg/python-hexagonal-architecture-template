# Adding a feature

This is the worked runbook an agent (or a human) follows to add a resource. It mirrors the
`Task` slice — the canonical example in the repo — building from the domain outward so every
layer compiles against the one beneath it. Substitute your resource name for `Task`
throughout.

The order matters: each step depends only on the steps above it, so you can run the relevant
tests after each one instead of discovering a design mistake at the API layer.

Worked example resource: a `Note` with a `title`, `body`, and an `archived` flag.

## 0. Where each layer lives

```
src/app/domain/                         # 1. entity + rules (pure)
src/app/application/ports/output/        # 2. driven port (what the app needs)
src/app/application/ports/input/         # 3. driving ports (what the app can do)
src/app/application/use_cases/           # 4. use cases
src/app/infrastructure/db/models/        # 5. SQLAlchemy model + migration
src/app/infrastructure/db/repositories/  # 6. Postgres adapter
src/app/infrastructure/web/schemas/      # 7. API DTOs
src/app/infrastructure/web/controllers/  # 7. router
tests/                                    # tests at each layer as you go
```

## 1. Domain — the entity and its rules

`src/app/domain/note.py`. Extend `Entity` (gives you `id`, `created_at`, `updated_at`,
immutability, and `with_updated_at()`). Encode behavior and invariants here — a state machine,
a validation rule, a computed property. Keep it pure: no imports outside `app.domain`.

Model the `Task` slice: `src/app/domain/task.py` shows a `StrEnum` status with an explicit
`_ALLOWED_TRANSITIONS` table and a `transition_to()` method that raises a domain exception on
an illegal move. Add any new domain exception to `src/app/domain/exceptions.py` (subclass the
existing `DomainError` / `ValidationError` / `EntityNotFoundError`).

Test first: `tests/unit/domain/test_note.py`. Assert the legal operations and that each
illegal one raises. No mocks, no I/O.

## 2. Output port — what the application needs

`src/app/application/ports/output/note_repository.py`. Define the persistence contract the use
cases depend on, e.g. `save`, `get_by_id`, `list_all`. Mirror
`ports/output/task_repository.py`. This is an abstract contract (ABC) — infrastructure
implements it; the application never imports the concrete adapter.

Provide a test double now: `tests/support/in_memory_note_repository.py`, a dict-backed
implementation of the port. Add a contract test
(`tests/unit/application/test_note_repository_contract.py`) asserting both the in-memory and
Postgres adapters satisfy the port — this is what keeps the swappable-adapter promise honest.

## 3. Input ports — what the application can do

`src/app/application/ports/input/note_ports.py`. One abstract use-case class per operation
(`CreateNoteUseCase`, `GetNoteUseCase`, …), each with an `async def execute(...)`. Mirror
`ports/input/task_ports.py`. Controllers depend on these abstractions, not on the concrete use
cases.

## 4. Use cases — orchestration

`src/app/application/use_cases/note_use_cases.py`. Implement each input port. A use case
orchestrates domain objects through the output ports and does nothing framework-specific.

Mutating use cases (create, update, transition) take three driven ports —
`(repository, uow, logger)` — and call `await uow.commit()` explicitly after the write, then
log. Read use cases take only the repository. Copy the shape from
`use_cases/task_use_cases.py`. Raise `EntityNotFoundError` when a lookup misses.

Unit-test each use case with the in-memory repository and the fakes in `tests/support/`
(`fake_unit_of_work.py`, `fake_logger.py`) — zero mocks. See
`tests/unit/application/test_task_use_cases.py`.

## 5. Persistence — model and migration

`src/app/infrastructure/db/models/note.py`. The SQLAlchemy model, mapping the entity to the
`notes` table. Mirror `db/models/task.py`. Match column limits to what the domain allows
(e.g. `String(200)` for a bounded title).

Generate the migration with the `add-migration` skill (or `uv run poe db-revision -m "add
notes"`), **read the generated DDL**, then lint it with `uv run poe migration-lint`.

## 6. Repository adapter — the driven side

`src/app/infrastructure/db/repositories/note_repository.py`. `PostgresNoteRepository`
implements the output port against an `AsyncSession`. It maps rows to domain entities and back;
it does **not** commit — the `UnitOfWork` owns commits. Mirror
`db/repositories/task_repository.py`.

Integration test: `tests/integration/db/test_note_repository.py`, against real Postgres via
testcontainers.

## 7. API edge — DTOs and controller

`src/app/infrastructure/web/schemas/note.py`. Request/response Pydantic DTOs with explicit
`from_domain()` mapping. **Bound the fields to the DB column limits** (`Field(min_length=1,
max_length=200)`), so oversized input is rejected at the edge with a 422 instead of failing in
the database with a 500 — schemathesis will catch you if you forget.

`src/app/infrastructure/web/controllers/note.py`. An `APIRouter` wiring HTTP to the use cases.
The controller constructs the adapter, unit of work, and logger via FastAPI `Depends` and calls
the use case. Mirror `controllers/tasks.py`. Register the router in
`src/app/infrastructure/web/app.py` (`app.include_router(note.router)`).

Integration test: `tests/integration/web/test_note_api.py`, driving the ASGI app.

## 8. Close the loop

```bash
uv run poe check
```

Iterate (see the `check-fix` skill) until every stage is green and coverage stays above the
floor. Then commit — one Conventional Commit per layer reads well in history, or one
`feat: add Note resource` if you prefer a single commit.

## Why this order

Building domain-first means the compiler and the unit tests validate your design before you
write a line of SQL or HTTP. If you find yourself wanting the domain to import a database
session or an HTTP client, stop — the dependency is backwards. Define an output port and push
the concrete dependency out to `infrastructure/`. That inversion is the whole point of the
architecture, and `uv run poe arch` will fail the build if you skip it.
