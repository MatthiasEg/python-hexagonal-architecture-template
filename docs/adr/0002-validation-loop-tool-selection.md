# ADR-0002: Validation-loop tool selection and exclusions

- **Status:** Accepted
- **Date:** 2026-07-05

## Context

The template is built so an AI agent can add a feature and verify it without a human. That
requires one deterministic command that catches the mistakes agents actually make, and it
requires *restraint*, because every extra tool is latency, a new failure mode, and another
thing to keep from going stale. The temptation is to add every linter in existence; the
discipline is to add only those that catch a distinct, real class of defect.

## Decision

`uv run poe check` runs, fail-fast cheapest-first:

```
ruff → ty → import-linter → deptry → pip-audit → pytest (+coverage, +schemathesis)
```

Each earns its place by catching something the others do not:

- **ruff**: lint + format + import order + security (`S`) + complexity (`C90`, `max-complexity`
  8) + docstrings (`D`) + annotation presence (`ANN`) + async correctness (`ASYNC`) +
  timezone-safe datetimes (`DTZ`) + FastAPI rules (`FAST`) + exception, return, naming, and
  antipattern groups (`TRY`, `RET`, `N`, `PIE`, `PERF`, `FURB`, ...). One fast tool; folding
  bandit-style checks into `S` removes a separate dependency. `ANN` matters specifically for
  agents: `ty` checks that types are *correct*, `ANN` checks they are *present*, and the two
  failure modes (omitted vs wrong annotation) need different gates.
- **ty**: static types. Catches the wrong-shape errors before runtime.
- **import-linter**: the architecture boundary (see ADR-0001). Nothing else checks this.
- **deptry**: unused / missing / misplaced dependencies. Keeps the dependency set honest as
  the code churns.
- **pip-audit**: known CVEs in the dependency tree (PyPA/OSV).
- **pytest** with **coverage** (branch, floor enforced), **pytest-randomly** (seeded random
  order surfaces fixture coupling), and **schemathesis** (property-fuzzes the OpenAPI schema
  in-process, asserting no endpoint returns a 5xx). schemathesis is derandomized so a run is
  reproducible. Two more gates ride in the test suite: **`alembic check`** fails if a model
  changed without a matching migration (the "agent forgot the migration" mistake), and an
  **OpenAPI snapshot** test fails if the public API surface drifts from the committed
  `tests/snapshots/openapi.json` (regenerate deliberately with `uv run poe openapi-snapshot`).

Determinism is a hard requirement: pinned versions (`uv.lock`), a seeded test order, and
derandomized fuzzing mean an agent gets identical pass/fail on re-run.

Separately (not in the every-run loop): **gitleaks** and **deptry** run as pre-commit hooks,
**commitizen** enforces Conventional Commits at commit-msg time, and **Squawk**
(`uv run poe migration-lint`) lock-safety-lints migration DDL. Run it when migrations change,
not on every check, because it needs the `squawk` binary and only applies to schema changes.
In CI, **zizmor** audits the workflow YAML itself (injection, over-broad permissions, unpinned
actions), and every action is pinned to a commit SHA so a moved tag cannot change what runs.

## Alternatives considered and excluded, with reasons

- **standalone bandit**: redundant with ruff's `S` rules.
- **radon / xenon**: complexity is covered by ruff `C90` with a `max-complexity` threshold.
- **vulture as a gate**: high false-positive rate on a template with intentionally-unused
  extension points; noise would train agents to ignore the gate.
- **mutmut / cosmic-ray (mutation testing)**: valuable but slow; belongs in a nightly job,
  not the inner loop. Out of scope for v1.
- **safety / detect-secrets**: overlap with pip-audit and gitleaks respectively.
- **SBOM generation, sqlfluff**: SBOM is a release concern (there is no published artifact to
  attest); Squawk already covers migration safety better than sqlfluff, whose SQL-text linting
  has almost nothing to lint against Alembic's Python DSL.

A 2026 survey of enforcement tooling reconsidered the following and kept them out of the
baseline (documented here so they are not re-litigated):

- **Tach** (module-boundary enforcer): its one net-new capability over import-linter is
  public-interface enforcement, which pays off only once a layer holds several modules. A
  recipe for larger forks, not a second boundary tool for a one-slice template.
- **beartype / typeguard / deal / CrossHair** (runtime types and design-by-contract): the
  immutable entities that raise typed domain exceptions already are design-by-contract, and
  `ty` + pydantic cover the boundaries. CrossHair is also solver-based and nondeterministic.
- **generic Semgrep / CodeQL / Snyk SAST**: redundant with ruff `S` + pip-audit + gitleaks at
  this size. A narrow, hand-written Semgrep rule to enforce a project convention (e.g. "commit
  only through the UnitOfWork") is worth revisiting, but a generic scanner is noise.
- **Atlas**: replaces Alembic and leans on a cloud service; `alembic check` gives the drift
  gate we wanted without the framework swap.
- **mutation testing (mutmut) and diff-cover**: genuinely useful, but as a nightly job and a
  PR-level gate respectively, not the inner loop; a good next step, out of scope here.

## Consequences

- One command is the contract. An agent (or CI) has a single, deterministic definition of done.
- The loop stays fast enough to run on every change because slow/periodic checks (mutation,
  SBOM, migration-lint) are deliberately kept out of it.
- pip-audit advisory drift can turn CI red without a code change. The response is
  `uv lock --upgrade`, or an allowlist entry with a written reason, never silently dropping
  the gate.
