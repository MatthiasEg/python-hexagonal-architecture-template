# FastAPI Hexagonal Template

Production-grade hexagonal-architecture FastAPI template with layer boundaries enforced in CI,
built for AI coding agents.

Most "clean" or "hexagonal" FastAPI templates draw three layers in a diagram and then let the
domain import the ORM anyway. Here the import direction is a build gate: `uv run poe arch`
fails if any inner layer reaches outward, so the architecture cannot rot silently. The same
discipline makes the codebase legible to AI coding agents: a fixed structure, a canonical
example to mirror, and one deterministic command that defines "done".

- **[Architecture](architecture.md)**: the three layers, the inward-only rule, and how it is
  enforced.
- **[Adding a feature](adding-a-feature.md)**: the domain-outward runbook, mirroring the
  `Task` slice.
- **[Validation loop](validation-loop.md)**: the one command, what each tool catches, and
  why these and not others.
- **[Agent-native](agent-native.md)**: `AGENTS.md`, the `.claude/` assets, and the
  determinism contract.
- **[Comparison](comparison.md)**: how this differs from the popular FastAPI templates.
- **[FAQ](faq.md)**: the questions people actually ask.

## Quickstart

```bash
uv sync && uv run poe install-hooks
uv run poe check   # lint → types → arch → deps → audit → tests (+coverage, +schemathesis)
uv run poe dev     # dev server at http://localhost:8000
```

Integration tests and schemathesis need Docker (testcontainers spins up Postgres). Everything
else runs without it.

## Stack

Python 3.13 · FastAPI · uv · async SQLAlchemy 2.0 + asyncpg · Alembic · Postgres · pydantic v2
· loguru · OpenTelemetry. Boundaries enforced with import-linter; fuzzed with schemathesis.

The source lives at
[github.com/MatthiasEg/python-hexagonal-architecture-template](https://github.com/MatthiasEg/python-hexagonal-architecture-template).
Use the green "Use this template" button to start a repo from it.
