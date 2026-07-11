# Agent-native

"Agent-native" is not a marketing word here. It is a set of concrete files that let an AI
coding agent add a feature and verify it without a human in the loop. Three things make that
work: a single source of truth, a canonical example to mirror, and a deterministic definition
of done.

## Single source of truth

[`AGENTS.md`](https://github.com/MatthiasEg/python-hexagonal-architecture-template/blob/main/AGENTS.md)
at the repo root holds the rules: the architecture, the validation loop, how to add a feature,
and the off-limits constraints. Everything else points at it instead of duplicating it.
`CLAUDE.md` imports it with `@AGENTS.md`, and `.github/copilot-instructions.md` and
`.cursor/rules/` are thin pointers. Duplicated instructions drift; a single file does not.

## A canonical example

The `Task` slice is the pattern an agent copies. It exercises every layer: a domain entity
with a state machine, input and output ports, use cases, a Postgres adapter and an in-memory
fake, DTOs and a controller, and tests at each layer. The runbook in
[Adding a feature](adding-a-feature.md) walks the slice domain-outward, file by file, so an
agent adds a second resource by mirroring it rather than inventing a shape.

## A deterministic definition of done

`uv run poe check` is the contract (see [Validation loop](validation-loop.md)). Because it is
deterministic, an agent can run it, read the first failing stage, fix the root cause, and
re-run until green, with the same result a human would get. Nothing about "done" is left to
judgment.

## Claude Code assets

The `.claude/` directory ships working assets, not just docs:

- **`settings.json`**: a permission allowlist that pre-approves `uv run poe *`,
  `uv run pytest *`, read-only git, and common read tooling, plus a `PostToolUse` hook that
  runs `ruff format` and `ruff check --fix` on each edited Python file. Formatting is applied
  automatically, so it never becomes a review comment.
- **Skills** (`.claude/skills/`): `add-feature` drives the runbook, `check-fix` closes the
  validation loop, and `add-migration` autogenerates and lock-safety-lints an Alembic revision.

None of this is Claude-specific in spirit. The `AGENTS.md` contract works for any agent. The
`.claude/` assets are just the concrete wiring for one of them.

## Design decisions

Non-obvious choices live as ADRs in
[`docs/adr/`](adr/README.md). An agent (or a human) changing the architecture reads them first,
because they record not just what was decided but which alternatives were rejected and why,
which is what stops a decision being silently reversed.
