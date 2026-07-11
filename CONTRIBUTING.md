# Contributing

Thanks for considering a contribution. This repository is a template, so the bar is a little
different from a normal app: every change has to keep the example clean enough that people copy
it as a reference. Read `AGENTS.md` first; it is the source of truth for the architecture and
the validation loop.

## Setup

```bash
uv sync && uv run poe install-hooks
```

Integration tests and schemathesis need Docker (testcontainers spins up Postgres).

## The rules

- **The architecture is enforced.** Imports point inward only
  (`infrastructure → application → domain`); `uv run poe arch` fails the build otherwise. If
  you need to cross a boundary, invert it with an output port. See
  `docs/adding-a-feature.md` and [ADR-0001](docs/adr/0001-enforce-hexagonal-boundaries-with-import-linter.md).
- **A change is done only when `uv run poe check` is green** (lint, types, arch, deps, audit,
  tests + coverage + schemathesis). Do not weaken a gate to pass; if a gate is genuinely wrong,
  change it deliberately in its own commit and explain why.
- **Conventional Commits**, enforced by commitizen: `type(scope): subject`
  (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`, and so on).
- **Google-style docstrings** on public symbols, type hints everywhere, line length 120.
- New resources mirror the `Task` slice. Follow the runbook rather than inventing a new shape.

## Adding a dependency

Use `uv add` / `uv add --group dev` and commit the regenerated `uv.lock`. Never edit the lock by
hand. A new dependency should earn its place. Prefer the standard library first, and note in
the PR why the dependency is needed.

## Architectural changes

If your change alters the architecture or the validation loop, add or update an ADR in
`docs/adr/`. The point of an ADR is to record the rejected alternatives so the decision is not
silently reversed later.

## Pull requests

Keep them focused. Describe what changed and why, link any relevant ADR, and confirm
`uv run poe check` is green. CI runs the same loop on a Postgres service, plus gitleaks and
migration lock-safety.
