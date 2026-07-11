---
name: check-fix
description: Use to close the validation loop — run `uv run poe check`, parse the first failing stage, fix the root cause, and re-run until the whole loop is green.
---

# Close the validation loop

`uv run poe check` runs the stages fail-fast, cheapest-first. Fix the **first** failing stage,
then re-run the whole loop — a later stage's output is meaningless until the earlier ones pass.

## Loop

1. Run `uv run poe check`.
2. Identify the failing stage from the output and fix the root cause — never weaken the gate:

   | Stage | Tool | Typical fix |
   |---|---|---|
   | lint | ruff | `uv run poe format`, then address remaining `ruff check` findings by hand. Do not blanket-`# noqa`; justify any suppression inline. |
   | typecheck | ty | Add/adjust type hints; fix the actual type error. |
   | arch | import-linter | An inner layer imported outward. Invert with an output port — do not relax the contract. |
   | deps | deptry | Remove an unused dep, or `uv add` a missing one, or move it between groups. |
   | audit | pip-audit | `uv lock --upgrade` to a patched version; allowlist only with a written reason. |
   | test | pytest | Fix the code or the test. A coverage failure means add tests, not lower `fail_under`. |

3. Re-run `uv run poe check`. Repeat until green.

## Notes

- Integration tests and schemathesis need Docker (testcontainers). If Docker is down, say so
  rather than skipping them silently.
- The loop is deterministic — a flaky result is a real bug (test order coupling, unseeded
  randomness, wall-clock assertion), not noise. Track it down.
- `uv run poe test-quick` is faster for iterating on a single failure; finish with the full
  `uv run poe check`.
