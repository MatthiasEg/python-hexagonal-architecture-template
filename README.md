# FastAPI Hexagonal Template

Production-grade hexagonal-architecture FastAPI template — layer boundaries enforced in CI, built for AI coding agents.

[![CI](https://github.com/MatthiasEg/python-hexagonal-architecture-template/actions/workflows/ci.yml/badge.svg)](https://github.com/MatthiasEg/python-hexagonal-architecture-template/actions/workflows/ci.yml)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Most "clean" or "hexagonal" FastAPI templates draw three layers in a diagram and then let the
domain import the ORM anyway. Here the import direction is a build gate: `uv run poe arch` fails
if any inner layer reaches outward, so the architecture cannot rot silently. That same
discipline — a fixed structure, a canonical example to mirror, one deterministic command that
defines "done" — is what makes the codebase legible to AI coding agents.

**Use this if** you want a backend where the architecture is real and stays real, and you are
happy to add auth, a frontend, or a task queue yourself when you need them.

**Don't use this if** you want a full-stack app out of the box (React, auth, email) — reach for
[full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) — or if
your service is thin CRUD where layered architecture is overhead you won't recoup.

## Quickstart

```bash
uv sync && uv run poe install-hooks
uv run poe check   # lint → types → arch → deps → audit → tests (+coverage, +schemathesis)
uv run poe dev     # dev server at http://localhost:8000
```

A fresh clone is green. Unit tests, linting, type-checking, and the architecture check need
nothing external; integration tests and schemathesis use [testcontainers](https://testcontainers.com/)
to spin up Postgres, so they need Docker.

Requirements: [Python 3.13+](https://www.python.org/), [uv](https://docs.astral.sh/uv/), and
Docker for the integration layer.

## Architecture, and why it's enforced

Hexagonal architecture (ports & adapters), three concentric layers. The one rule: **imports
point inward only.** Outer layers know inner layers; never the reverse.

```
infrastructure/  →  application/  →  domain/
  (outer)            (middle)         (inner, zero framework imports)
```

```
src/app/
├── main.py                 # composition root
├── domain/                 # inner — pure business logic (Entity, Task + status FSM, exceptions)
├── application/            # middle — use cases + ports/{input,output}
└── infrastructure/         # outer — web (FastAPI), db (SQLAlchemy/Alembic), observability, config
```

- **`domain/`** — pure business logic; no framework imports, no I/O. Entities are immutable and
  own their identity and UTC timestamps. The `Task` entity encodes a status state machine
  (`OPEN → IN_PROGRESS → DONE`, plus `CANCELLED`); an illegal transition raises a domain error,
  not an HTTP status.
- **`application/`** — use cases orchestrate domain objects through ports. `ports/input/` are
  driving contracts (what the app can do); `ports/output/` are driven contracts (repository,
  unit of work, logger) that infrastructure implements. Depends on `domain/` only.
- **`infrastructure/`** — every concrete technology: FastAPI controllers and DTOs, the
  SQLAlchemy repository, Alembic migrations, logging, tracing, config.

Convention alone doesn't hold this line — someone imports `sqlalchemy` into a use case "just for
one query" and the boundary is gone. So it's a machine check.
[import-linter](https://import-linter.readthedocs.io/) runs as part of `uv run poe check` and
fails the build on any violation. Add `import sqlalchemy` to a domain module and you get:

```
Hexagonal Architecture KEPT
Application layer: no infrastructure libraries BROKEN
Domain layer: no infrastructure libraries BROKEN

app.domain is not allowed to import sqlalchemy:
-   app.domain.task -> sqlalchemy (l.3)

Contracts: 1 kept, 2 broken.
```

If you need the domain to reach a database or an HTTP client, the dependency is backwards:
define an output port and implement it in `infrastructure/`. That inversion is the point. See
[ADR-0001](docs/adr/0001-enforce-hexagonal-boundaries-with-import-linter.md).

## Adding a feature

New resources mirror the `Task` slice, built domain-outward so each layer compiles against the
one beneath it. The full file-by-file runbook is
[docs/adding-a-feature.md](docs/adding-a-feature.md); the short version:

1. `domain/` — entity + rules + unit test
2. `application/ports/output/` — driven port + in-memory fake + contract test
3. `application/ports/input/` + `use_cases/` — driving ports + use cases (unit-tested, no mocks)
4. `infrastructure/db/` — SQLAlchemy model + migration + Postgres adapter
5. `infrastructure/web/` — DTOs + controller, wired in `app.py`
6. `uv run poe check` until green

Agents get this as a repeatable procedure, not prose: `.claude/skills/add-feature` drives the
runbook and `.claude/skills/check-fix` closes the loop.

## The validation loop

One command is the definition of done, fail-fast cheapest-first:

```
uv run poe check
   → ruff → ty → import-linter → deptry → pip-audit → pytest (+coverage, +schemathesis)
```

| Stage | Tool | Catches |
|---|---|---|
| lint | ruff | style, bugs, security (`S`), complexity (`C90`), docstrings (`D`) |
| typecheck | ty | type errors before runtime |
| arch | import-linter | inward-only boundary violations |
| deps | deptry | unused / missing / misplaced dependencies |
| audit | pip-audit | known CVEs in the dependency tree |
| test | pytest | behavior, with branch coverage (floor enforced), seeded random order, and schemathesis OpenAPI fuzzing |

The loop is deterministic — pinned versions, seeded test order (pytest-randomly), derandomized
fuzzing (schemathesis) — so a re-run gives the same answer and a flaky result is a real bug.
schemathesis already earned its keep here: it caught an unbounded create-task field against a
`String(200)` column that would have returned a 500. Which tools are in the loop, and which were
deliberately left out, is in [ADR-0002](docs/adr/0002-validation-loop-tool-selection.md).

Outside the every-run loop: gitleaks and deptry run as pre-commit hooks, commitizen enforces
Conventional Commits, and Squawk lock-safety-lints migration DDL (`uv run poe migration-lint`).

## Agent-native

Not a slogan — a set of files that let an agent add a feature and verify it unattended:

- **`AGENTS.md`** is the single source of truth (architecture, loop, constraints). `CLAUDE.md`
  imports it; `.github/copilot-instructions.md` and `.cursor/rules/` are thin pointers. No
  duplicated instructions to drift.
- **The `Task` slice** is the worked example an agent mirrors.
- **`uv run poe check`** is a deterministic definition of done an agent can close on its own.
- **`.claude/`** ships a permission allowlist, a `PostToolUse` hook that auto-formats edited
  files, and skills for adding features, closing the loop, and writing migrations.

Details in [docs/agent-native.md](docs/agent-native.md).

## How this compares

| | This template | full-stack-fastapi | fastapi-best-practices | fastapi-clean-example |
|---|---|---|---|---|
| Hexagonal / ports & adapters | Yes | No | N/A (guide) | Yes |
| Boundary **enforced in CI** | Yes (import-linter) | No | No | No (conventions only) |
| Scaffoldable template | Yes | Yes | No | No (example) |
| Agent-native | Yes | No | No | No |
| Full-stack (frontend, auth) | No (by design) | Yes | N/A | No |

The big templates win on breadth and trust; none enforce the boundary. That gap is what this
fills. Longer comparison and honest "when not to use" in
[docs/comparison.md](docs/comparison.md).

## Documentation

- [Architecture](docs/architecture.md) · [Adding a feature](docs/adding-a-feature.md) ·
  [Validation loop](docs/validation-loop.md) · [Agent-native](docs/agent-native.md) ·
  [Comparison](docs/comparison.md) · [FAQ](docs/faq.md)
- [Decision records](docs/adr/README.md) — why the architecture and the loop are the way they are.

Rendered docs site: MkDocs Material, published to GitHub Pages (`uv run poe docs-serve` to
preview locally).

## Configuration

Settings use pydantic-settings in `src/app/infrastructure/config.py`; every variable takes the
`APP_` prefix (e.g. `APP_ENVIRONMENT=local`). See `.env.example` for the full list.

## Contributing

`uv run poe check` is the bar. Conventional Commits, Google-style docstrings, and the layer rule
are enforced — see [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md).

## License

[MIT](LICENSE).
