# ADR-0001: Enforce hexagonal boundaries in CI with import-linter

- **Status:** Accepted
- **Date:** 2026-07-01

## Context

Hexagonal architecture only pays off if the dependency rule — imports point inward only —
actually holds. In practice it erodes: someone imports `SQLAlchemy` into a use case "just for
this one query", a domain model grows a `fastapi` import for a validation helper, and within a
few months the "clean" architecture is a three-tier app with extra folders. Convention and
code review do not catch this reliably, especially with AI agents generating code fast.

The whole selling point of this template is that the architecture is real. That claim needs a
machine check, not a diagram.

## Decision

We enforce the layer boundaries in CI with [import-linter](https://import-linter.readthedocs.io/).
The contracts live in `pyproject.toml` under `[tool.importlinter]` and run as
`uv run poe arch`, which is part of `uv run poe check`. Three contracts:

1. A **layers** contract ordering `app.infrastructure` → `app.application` → `app.domain`, so
   no inner layer may import an outer one.
2. A **forbidden** contract barring `app.application` from importing infrastructure libraries
   (`sqlalchemy`, `fastapi`, `loguru`, `alembic`, `starlette`, …).
3. The same forbidden contract for `app.domain`.

Any violation fails the build.

## Alternatives considered

- **Folder conventions + code review only** (what most "clean architecture" example repos do,
  e.g. `fastapi-clean-example`). Free, but unenforced — it degrades exactly when the team is
  moving fast, which is when you need it. Rejected: an unenforced boundary is a comment.
- **`ruff` custom rules / `flake8-import-restrictions`.** Ruff has no first-class layered-
  architecture contract, and the import-restriction plugins are less expressive than
  import-linter's layered + forbidden contract model. Rejected on expressiveness.
- **Runtime dependency injection framework that structurally prevents wrong imports.** Heavier,
  changes the programming model, and still does not stop a stray `import`. Rejected as
  over-engineering for the goal.

## Consequences

- The architecture cannot rot silently; a bad import is a red build, not a slow decay.
- Contributors must invert dependencies properly (define an output port, implement it in
  infrastructure) instead of reaching across a layer. That is the intended friction.
- The forbidden-module lists need updating when a genuinely new infrastructure library is
  added — a small, deliberate maintenance cost, and a useful checkpoint.
