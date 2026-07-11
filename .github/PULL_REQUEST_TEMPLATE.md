## What & why

<!-- What does this change and why? Link any relevant issue or ADR. -->

## Checklist

- [ ] `uv run poe check` is green (lint, types, arch, deps, audit, tests + coverage + schemathesis)
- [ ] New/changed behavior is covered by tests
- [ ] Layer boundaries respected (no inward-only violation; `uv run poe arch` passes)
- [ ] Conventional Commit messages
- [ ] ADR added/updated if this changes the architecture or the validation loop
- [ ] Docs updated if user-facing behavior changed
