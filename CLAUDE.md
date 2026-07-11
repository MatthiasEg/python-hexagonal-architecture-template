# CLAUDE.md

The project rules live in one place to avoid drift. Read them there:

@AGENTS.md

## Claude Code notes

Everything above (architecture, the validation loop, how to add a feature, constraints) is
imported from `AGENTS.md` and applies here verbatim. The notes below are Claude-Code-specific
and do not belong in the tool-agnostic `AGENTS.md`.

- **Skills** (`.claude/skills/`): `add-feature` drives the runbook in
  `docs/adding-a-feature.md`; `check-fix` runs `uv run poe check`, parses failures, fixes,
  and re-runs until green; `add-migration` autogenerates an Alembic revision and reviews it
  with Squawk. Prefer these over ad-hoc steps.
- **Hooks** (`.claude/settings.json`): a `PostToolUse` hook runs `ruff format` and
  `ruff check --fix` on any Python file you edit, so formatting is applied automatically
  after each edit — you do not need to think about it.
- **Permissions**: the allowlist pre-approves `uv run poe *`, `uv run pytest *`, read-only
  git, and common read tooling. Anything outside it will prompt.
- After a feature, run `uv run poe check` and do not report the work as complete until it is
  green.
