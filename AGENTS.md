# AGENTS.md

Single source of truth for coding agents (and humans) working in this repository.
`CLAUDE.md`, `.github/copilot-instructions.md`, and `.cursor/rules/` all point here. Do not
duplicate rules; change them in this file.

## What this project is

A hexagonal-architecture (ports and adapters) FastAPI backend template. Layer boundaries are
enforced in CI by import-linter, so the architecture cannot silently rot. Python 3.13, uv, async
SQLAlchemy + Alembic + Postgres. The `Task` resource is the canonical vertical slice; mirror it
when adding a feature.

## The one command

```bash
uv run poe check
```

Runs the full validation loop, fail-fast and cheapest-first:

```
ruff -> ty -> import-linter -> deptry -> pip-audit -> pytest (+coverage, +schemathesis)
```

A change is not done until `uv run poe check` is green. Integration tests and schemathesis need
Docker (testcontainers spins up Postgres). This loop is deterministic: pinned tool versions
(`uv.lock`), seeded test order (pytest-randomly), and derandomized fuzzing (schemathesis) mean
the same input yields the same pass/fail on every run. Do not add nondeterminism (wall-clock
assertions, network calls, unseeded randomness) to tests.

## Architecture rules (enforced)

Imports point inward only. Outer layers know inner layers; the reverse never happens.

```
infrastructure/  ->  application/  ->  domain/
  (outer)             (middle)          (inner, zero framework imports)
```

- **`src/app/domain/`** is pure business logic. No imports from `application/` or
  `infrastructure/`; no FastAPI, SQLAlchemy, loguru, pydantic-settings. Entities are immutable;
  rule violations raise domain exceptions, not HTTP errors.
- **`src/app/application/`** is where use cases orchestrate domain objects. `ports/input/` are
  driving contracts (what the app can do); `ports/output/` are driven contracts (what the app
  needs: repositories, unit of work, logger). It depends on `domain/` only and imports no infra
  libraries (see the forbidden-module lists in `pyproject.toml`).
- **`src/app/infrastructure/`** holds every concrete technology: FastAPI controllers/DTOs,
  SQLAlchemy repositories, Alembic migrations, logging, telemetry, config. It implements the
  output ports.

`uv run poe arch` fails the build on any inward-only violation. If you need the domain to reach
a database or an HTTP client, you have the dependency backwards: define an output port in
`application/ports/output/` and implement it in `infrastructure/`.

The `UnitOfWork` is the sole commit authority; `get_db_session` does not commit. Mutating use
cases take `(repository, uow, logger)` and call `await uow.commit()` explicitly. See
[ADR-0003](docs/adr/0003-unit-of-work-commit-authority.md).

## Adding a feature

Follow [docs/adding-a-feature.md](docs/adding-a-feature.md), an ordered, file-by-file runbook
that mirrors the `Task` slice from the domain outward and ends at a green `uv run poe check`. The
`Task` slice files, in dependency order:

1. `src/app/domain/task.py`: entity + `TaskStatus` state machine
2. `src/app/application/ports/output/task_repository.py`: driven port
3. `src/app/application/ports/input/task_ports.py`: driving ports
4. `src/app/application/use_cases/task_use_cases.py`: use cases
5. `src/app/infrastructure/db/models/task.py` + migration: persistence model
6. `src/app/infrastructure/db/repositories/task_repository.py`: Postgres adapter
7. `src/app/infrastructure/web/schemas/task.py` + `controllers/tasks.py`: API edge
8. tests at every layer (unit domain FSM, use cases with in-memory repo, contract test,
   integration repo + API)

## Commands

| Command | Purpose |
|---|---|
| `uv run poe check` | Full validation loop (see above). Run before declaring done. |
| `uv run poe test-quick` | pytest without coverage, for fast iteration |
| `uv run poe format` | `ruff format` |
| `uv run poe lint` | `ruff check src tests` |
| `uv run poe typecheck` | `ty check src` |
| `uv run poe arch` | import-linter boundary check |
| `uv run poe dev` | dev server (uvicorn --reload) |
| `uv run poe db-revision -m "msg"` | autogenerate an Alembic migration |
| `uv run poe migration-lint` | Squawk lock-safety lint on migration DDL |

## Constraints (off-limits)

- **Do not break the layer rule** to make something compile. Fix the dependency direction.
- **Do not edit `uv.lock` by hand.** Change dependencies via `uv add` / `uv remove`, then commit
  the regenerated lock.
- **Do not weaken the gates to pass**: not the coverage floor (`fail_under` in `pyproject.toml`),
  not the ruff rules, not the import-linter contracts. If a gate is wrong, change it deliberately
  in one commit and say why.
- **Do not add auth, rate-limiting, a task queue, or an LLM adapter to the baseline.** They are
  explicit non-goals; document them as recipes instead.
- **Conventional Commits** are enforced by commitizen (`type: subject`, e.g. `feat(domain): ...`,
  `fix: ...`, `test: ...`, `docs: ...`, `refactor: ...`, `chore: ...`).
- Every public module, class, and function needs a Google-style docstring (ruff `D`).
- Line length 120. Type hints on all functions and variables.

## Where design decisions live

Architecture Decision Records are in [docs/adr/](docs/adr/). Read them before changing the
architecture or the validation loop. They record what was decided and, more usefully, what was
rejected and why.
