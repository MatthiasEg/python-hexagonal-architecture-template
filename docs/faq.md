# FAQ

## Is this actually hexagonal, or just three folders?

Actually hexagonal, and the build proves it. import-linter runs as `uv run poe arch` with a
layered contract and forbidden-import contracts; if the domain or application layer imports an
infrastructure library, the build fails. Try it: add `import sqlalchemy` to a domain module and
run `uv run poe check`.

## What is the difference between ports and adapters here?

A **port** is an interface owned by the application: `ports/input/` are driving ports (what the
app can do, called by controllers), `ports/output/` are driven ports (what the app needs, such
as a repository, a unit of work, or a logger). An **adapter** is a concrete implementation in
`infrastructure/`: `PostgresTaskRepository` is an adapter for the `TaskRepository` output port.
The application depends on the port; the adapter is wired in at the edge.

## Why uv instead of Poetry or pip-tools?

Speed and a single tool for Python versions, virtualenvs, dependency resolution, and locking.
The lockfile is committed; CI installs with `uv sync --frozen` for reproducible builds. If you
prefer another manager, the dependency metadata is standard `pyproject.toml`.

## Do I need Docker?

Only for integration tests and schemathesis, which use testcontainers to spin up Postgres. Unit
tests, linting, type-checking, and the architecture check need nothing external. In CI a
Postgres service container is provided instead, via `APP_DATABASE_URL`.

## How do I add authentication?

It is a deliberate non-goal of the baseline, so you add it as an adapter. Define the security
contract as an input/output port, implement it in `infrastructure/web/` (dependency,
middleware, or a driven port to an identity provider), and keep the domain unaware of it. The
point of the architecture is that cross-cutting concerns like auth attach at the edge without
touching business logic.

## Can an AI agent really add a feature on its own?

That is the design goal. Give the agent `AGENTS.md` and `docs/adding-a-feature.md`, and it
mirrors the `Task` slice from the domain outward, then closes `uv run poe check`, a
deterministic command, until it is green. The determinism is what makes unattended
verification possible; see [Agent-native](agent-native.md).

## Why is the coverage floor only 80%?

It is a floor, not a target: the gate that fails CI, set where it catches real regressions
without forcing tests for trivial glue. The `Task` slice itself is covered far above that.
Raise `fail_under` in `pyproject.toml` if your project warrants a stricter floor.

## How do I change the architecture rules?

Deliberately, in one commit, with an ADR. The contracts live in `pyproject.toml` under
`[tool.importlinter]`. If you are relaxing a boundary, write down why in `docs/adr/` first.
The rejected-alternatives section is what stops the decision being undone later by someone who
never saw the tradeoff.
