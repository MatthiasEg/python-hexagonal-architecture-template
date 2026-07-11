# Copilot instructions

The authoritative rules for this repository live in [`AGENTS.md`](../AGENTS.md). Read it
first and follow it. Key points, in short:

- Hexagonal architecture. Imports point inward only:
  `infrastructure/ → application/ → domain/`. `domain/` imports no frameworks. The boundary
  is enforced by import-linter (`uv run poe arch`). Do not violate it to make code compile;
  fix the dependency direction instead.
- Mirror the `Task` slice when adding a feature. Follow `docs/adding-a-feature.md`.
- A change is done only when `uv run poe check` is green.
- Conventional Commits (`type: subject`). Google-style docstrings on all public symbols.
  Line length 120. Type hints everywhere.
