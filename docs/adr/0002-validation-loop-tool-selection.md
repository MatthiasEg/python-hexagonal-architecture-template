# ADR-0002: Validation-loop tool selection and exclusions

- **Status:** Accepted
- **Date:** 2026-07-05

## Context

The template is built so an AI agent can add a feature and verify it without a human. That
requires one deterministic command that catches the mistakes agents actually make — and it
requires *restraint*, because every extra tool is latency, a new failure mode, and another
thing to keep from going stale. The temptation is to add every linter in existence; the
discipline is to add only those that catch a distinct, real class of defect.

## Decision

`uv run poe check` runs, fail-fast cheapest-first:

```
ruff → ty → import-linter → deptry → pip-audit → pytest (+coverage, +schemathesis)
```

Each earns its place by catching something the others do not:

- **ruff** — lint + format + import order + security (`S`) + complexity (`C90`) + docstrings
  (`D`). One fast tool; folding bandit-style checks into `S` removes a separate dependency.
- **ty** — static types. Catches the wrong-shape errors before runtime.
- **import-linter** — the architecture boundary (see ADR-0001). Nothing else checks this.
- **deptry** — unused / missing / misplaced dependencies. Keeps the dependency set honest as
  the code churns.
- **pip-audit** — known CVEs in the dependency tree (PyPA/OSV).
- **pytest** with **coverage** (branch, floor enforced), **pytest-randomly** (seeded random
  order surfaces fixture coupling), and **schemathesis** (property-fuzzes the OpenAPI schema
  in-process, asserting no endpoint returns a 5xx). schemathesis is derandomized so a run is
  reproducible.

Determinism is a hard requirement: pinned versions (`uv.lock`), a seeded test order, and
derandomized fuzzing mean an agent gets identical pass/fail on re-run.

Separately (not in the every-run loop): **gitleaks** and **deptry** run as pre-commit hooks,
**commitizen** enforces Conventional Commits at commit-msg time, and **Squawk**
(`uv run poe migration-lint`) lock-safety-lints migration DDL — run when migrations change,
not on every check, because it needs the `squawk` binary and only applies to schema changes.

## Alternatives considered — excluded, with reasons

- **standalone bandit** — redundant with ruff's `S` rules.
- **radon / xenon** — complexity is covered by ruff `C90` with a `max-complexity` threshold.
- **vulture as a gate** — high false-positive rate on a template with intentionally-unused
  extension points; noise would train agents to ignore the gate.
- **mutmut / cosmic-ray (mutation testing)** — valuable but slow; belongs in a nightly job,
  not the inner loop. Out of scope for v1.
- **safety / detect-secrets** — overlap with pip-audit and gitleaks respectively.
- **SBOM generation, diff-cover, sqlfluff** — SBOM is a release concern; diff-cover fights the
  absolute coverage floor; Squawk already covers migration safety better than sqlfluff.

## Consequences

- One command is the contract. An agent (or CI) has a single, deterministic definition of done.
- The loop stays fast enough to run on every change because slow/periodic checks (mutation,
  SBOM, migration-lint) are deliberately kept out of it.
- pip-audit advisory drift can turn CI red without a code change. The response is
  `uv lock --upgrade`, or an allowlist entry with a written reason — never silently dropping
  the gate.
