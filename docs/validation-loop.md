# The validation loop

One command is the definition of done:

```bash
uv run poe check
```

It runs the stages fail-fast, cheapest-first, so the fastest feedback comes first and an
expensive stage never runs against code that already failed a cheap one:

```
ruff → ty → import-linter → deptry → pip-audit → pytest (+coverage, +schemathesis)
```

## What each stage catches

| Stage | Tool | Catches |
|---|---|---|
| lint | ruff | style, imports, bugs (bugbear), security (`S`), complexity (`C90`), docstrings (`D`), annotation presence (`ANN`), async correctness (`ASYNC`), naive datetimes (`DTZ`), FastAPI misuse (`FAST`), and exception/return/naming antipatterns |
| typecheck | ty | type errors, before runtime |
| arch | import-linter | any inward-only boundary violation |
| deps | deptry | unused, missing, or misplaced dependencies |
| audit | pip-audit | known CVEs in the dependency tree (PyPA/OSV) |
| test | pytest | behavior, with branch **coverage** (floor enforced), seeded random order (**pytest-randomly**), OpenAPI **schemathesis** fuzzing, a **migration-drift** gate (`alembic check`), and an **OpenAPI-snapshot** gate |

Each earns its place by catching a class of defect the others miss. Two of the test-suite gates
target mistakes an agent makes often: `alembic check` fails when a model changed without a
matching migration, and the OpenAPI snapshot fails when the public API surface drifts from the
committed `tests/snapshots/openapi.json` (regenerate deliberately with
`uv run poe openapi-snapshot`). The reasoning, and the tools deliberately left out (standalone
bandit, radon/xenon, vulture, Tach, beartype, generic SAST, mutation testing, SBOM, diff-cover),
is recorded in [ADR-0002](adr/0002-validation-loop-tool-selection.md).

## Determinism

An agent must get the same pass/fail every time, or the loop is useless as a definition of
done. Three things guarantee that:

- **Pinned versions**: `uv.lock` fixes every dependency and tool.
- **Seeded test order**: pytest-randomly shuffles with a recorded seed, so order-coupling
  surfaces reproducibly rather than flaking intermittently.
- **Derandomized fuzzing**: schemathesis runs with a fixed strategy, so the property tests are
  reproducible.

A flaky result is therefore a real bug (an unseeded random, a wall-clock assertion, a network
call in a test), not noise to retry away.

## schemathesis

schemathesis reads the OpenAPI schema FastAPI generates and drives every operation with
generated inputs, asserting the API never returns a 5xx. It runs in-process against the ASGI
app, wired to a testcontainers Postgres. This caught a real bug in this template: a create-task
DTO with no length bound against a `String(200)` column would have 500'd on oversized input.
The fix is to bound the DTO field, and that is the pattern to copy: reject bad input at the edge
with a 422, never let it reach the database.

## Outside the every-run loop

Some checks are valuable but do not belong in the inner loop:

- **gitleaks** (secret scan) and **deptry** run as pre-commit hooks.
- **commitizen** enforces Conventional Commits at commit-msg time.
- **Squawk** lock-safety-lints migration DDL via `uv run poe migration-lint`. Run it when
  migrations change, since it needs the `squawk` binary and only applies to schema changes.
- **zizmor** audits the GitHub Actions workflows themselves for injection, over-broad
  permissions, and unpinned actions. It runs in CI, where every action is also pinned to a
  commit SHA so a moved tag cannot silently change what the pipeline runs.

CI (`.github/workflows/ci.yml`) runs the full `uv run poe check` against a Postgres service,
plus the gitleaks, migration-safety, and workflow-security (zizmor) jobs.
