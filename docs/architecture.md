# Architecture

Hexagonal architecture (ports & adapters), organized as three concentric layers. The one rule:
**imports point inward only.** Outer layers know about inner layers; never the reverse.

```
infrastructure/  →  application/  →  domain/
  (outer)            (middle)         (inner, zero framework imports)
```

```
src/app/
├── main.py                          # composition root
├── domain/                          # inner — pure business logic
│   ├── entities.py                  # Entity base (id, UTC timestamps, immutable)
│   ├── task.py                      # Task entity + status state machine
│   └── exceptions.py                # domain errors
├── application/                     # middle — use cases + ports
│   ├── use_cases/                   # orchestrate domain objects
│   └── ports/
│       ├── input/                   # driving ports (what the app can do)
│       └── output/                  # driven ports (repository, unit of work, logger)
└── infrastructure/                  # outer — frameworks & drivers
    ├── web/                         # FastAPI controllers, DTO schemas, middleware
    ├── db/                          # SQLAlchemy engine, repositories, Alembic migrations
    ├── observability/               # loguru + OpenTelemetry
    └── config.py                    # pydantic-settings
```

## The layers

**`domain/`** — pure business logic. No imports from `application/` or `infrastructure/`, no
FastAPI, SQLAlchemy, loguru, or pydantic-settings. Entities are immutable (frozen Pydantic
models) and own their identity and UTC timestamps
([ADR-0004](adr/0004-utc-timestamps-owned-by-the-domain.md)). Business-rule violations raise
domain exceptions, not HTTP status codes. The `Task` entity encodes a status state machine —
`OPEN → IN_PROGRESS → DONE` (plus `CANCELLED`) — with an explicit allowed-transitions table;
an illegal move raises `InvalidTaskTransitionError`.

**`application/`** — use cases, one per operation, orchestrating domain objects through ports.
`ports/input/` are the driving contracts a controller calls; `ports/output/` are the driven
contracts (repository, unit of work, logger) that infrastructure implements. This layer
depends on `domain/` only and imports no infrastructure library — the forbidden-module list in
`pyproject.toml` makes that a build rule. Mutating use cases take `(repository, uow, logger)`
and commit through the unit of work
([ADR-0003](adr/0003-unit-of-work-commit-authority.md)).

**`infrastructure/`** — every concrete technology choice: FastAPI controllers and DTO schemas,
the SQLAlchemy repository and Alembic migrations, logging and tracing, configuration. It
implements the output ports defined in `application/`.

## Why enforce it in CI

Convention erodes. Someone imports `sqlalchemy` into a use case "just for this one query", a
domain model grows a `fastapi` import for a validation helper, and within a few months the
clean architecture is a three-tier app with extra folders. Code review does not catch this
reliably — least of all when an AI agent is generating code quickly.

So the boundary is a machine check. [import-linter](https://import-linter.readthedocs.io/) runs
as `uv run poe arch` (part of `uv run poe check`) with three contracts: a layered contract
ordering the three packages, and forbidden-import contracts barring the domain and application
layers from infrastructure libraries. A violation fails the build. See
[ADR-0001](adr/0001-enforce-hexagonal-boundaries-with-import-linter.md) for the decision and
the alternatives that were rejected.

If you find yourself wanting the domain to reach a database or an HTTP client, the dependency
is backwards: define an output port in `application/ports/output/` and implement it in
`infrastructure/`. That inversion is the point.
