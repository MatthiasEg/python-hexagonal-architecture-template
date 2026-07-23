# The toolchain

This project ships a deliberately large set of tools, but none of it is decoration. Each tool
earns its place by catching one specific class of mistake, and they are arranged so you feel
them at the right moment: as you type, when you commit, when you push, and on a schedule. The
goal is simple. A mistake should be caught by a machine, close to where you made it, rather than
by a reviewer or by a user in production.

One idea runs through all of it: **the earlier and more deterministic the check, the cheaper the
fix.** A formatting nit fixed on save never reaches a diff. A broken architecture boundary caught
by `uv run poe arch` never reaches `main`. A dependency CVE caught in CI never reaches a release.
If you only remember one thing, remember that the tools are layered by *when* they run, and each
layer is cheap because the previous one already narrowed the problem.

## At a glance

| Tool | What it does for you | When it runs |
|---|---|---|
| **uv** | Installs Python, dependencies, and tools from one pinned lockfile | Setup, and under everything |
| **poe** | Names the commands so you type `poe check`, not a paragraph of flags | Always |
| **ruff** | Formats code and flags bugs, security issues, and complexity | On save, commit, `poe check` |
| **ty** | Checks types before the code runs | `poe check` |
| **import-linter** | Fails the build if a layer imports the wrong direction | `poe check`, commit |
| **deptry** | Finds unused, missing, or misplaced dependencies | `poe check`, commit |
| **pip-audit** | Scans dependencies for known security vulnerabilities | `poe check` |
| **pytest** (+coverage, +randomly, +schemathesis) | Runs the tests and measures how well they cover the code | `poe check` |
| **testcontainers** | Spins up a real Postgres for integration tests | `poe check` (needs Docker) |
| **Alembic** (+`alembic check`) | Manages DB migrations and catches a forgotten one | `poe check`, on demand |
| **Squawk** | Warns when a migration would lock a production table | On migration change, CI |
| **OpenAPI snapshot** | Fails if the public API surface changes unexpectedly | `poe check` |
| **gitleaks** | Blocks commits that contain secrets | Commit, CI |
| **Semgrep** | Enforces project rules that import-linter cannot express | Commit, CI |
| **commitizen** | Enforces a consistent, machine-readable commit format | Commit |
| **zizmor** | Audits the CI workflows themselves for security holes | CI |
| **diff-cover** | Requires the lines you changed in a PR to be tested | CI (pull requests) |
| **mutmut** | Checks whether the tests actually assert, not just run | Nightly |
| **Dependabot** | Opens PRs to keep dependencies and actions current | Weekly |

The rest of this page explains each group and, more usefully, *why it helps you write better
code*.

## Foundation

**uv** is the package and environment manager. It installs the right Python, resolves every
dependency, and records exact versions in `uv.lock`, which is committed. Because the lockfile is
pinned, everyone (and every CI run, and every AI agent) builds from the same versions, so "works
on my machine" stops being a category of bug. `uv sync` is the only setup step.

**Python 3.13** is the runtime. Modern typing and performance, nothing exotic.

**poe** (poethepoet) is the task runner. It gives commands readable names in `pyproject.toml`, so
the whole team runs `uv run poe check` instead of memorizing a long chain of flags. It is the
front door to everything below.

## While you edit

**ruff format** is an opinionated formatter (think Black, but faster and part of the same tool as
the linter). Formatting is not a matter of taste you argue about in review here; it is applied
automatically. If you use Claude Code, a hook runs `ruff format` and `ruff check --fix` on every
file you edit, so formatting and trivial fixes are done before you even look. That keeps review
focused on logic instead of whitespace.

## The one command: `uv run poe check`

This is the definition of done. It runs the checks fail-fast and cheapest-first, so the fastest
feedback comes first and a slow stage never runs against code that already failed a quick one:

```
ruff -> ty -> import-linter -> deptry -> pip-audit -> pytest (+coverage, +schemathesis, +drift gates)
```

Everything in it is deterministic (pinned versions, seeded test order), so a re-run gives the
same answer. A green `poe check` is a promise you can trust. Here is what each stage buys you.

**ruff (lint)** is one fast tool wearing many hats. In plain terms it catches:

- *Bugs and dead weight*: likely mistakes (flake8-bugbear), needless complexity in comprehensions
  and returns, and commented-out code that should be deleted.
- *Security*: the same checks the `bandit` tool is known for (`S`), for example flagging unsafe
  defaults, so a separate security linter is not needed.
- *Complexity*: a hard cap on how convoluted a single function may get (`C90`, max complexity 8).
  When you exceed it, the fix is to split the function, which is exactly the nudge you want. This
  is the main guardrail against code slowly sprawling out of hand.
- *Correctness for this stack*: blocking calls inside async code (`ASYNC`), naive datetimes that
  cause timezone bugs (`DTZ`), and FastAPI-specific misuse (`FAST`).
- *Consistency*: import order, naming, docstrings on public symbols (`D`), and the presence of
  type hints on every function (`ANN`). It also bans a bare `# noqa`, so you cannot silence a
  warning without naming which one and why.

Consistency sounds cosmetic, but it is what lets a newcomer or an agent read any file in the repo
and find the same shapes in the same places.

**ty** is the type checker (from the makers of ruff and uv, so it is fast). It catches the
"wrong shape" errors, like passing the wrong type or forgetting a `None` case, before the code
ever runs. Paired with `ANN` above, one tool ensures types are *present* and the other ensures
they are *correct*, which are two different mistakes.

**import-linter** enforces the architecture. The project is built in three layers
(`infrastructure -> application -> domain`) and imports may only point inward. This tool fails the
build the instant an inner layer reaches outward, for example if the pure domain tries to import
SQLAlchemy. Diagrams rot; a build gate does not. This is the single check that keeps the
architecture real over time. See [Architecture](architecture.md) and
[ADR-0001](adr/0001-enforce-hexagonal-boundaries-with-import-linter.md).

**deptry** keeps the dependency list honest: it flags a package you declared but never use, one
you use but forgot to declare, or one that is in the wrong group. Dependency drift is a slow leak,
and this plugs it.

**pip-audit** scans your dependency tree against public vulnerability databases and fails if a
known CVE is present. When it fires, the fix is to upgrade to a patched version, so security
updates become part of normal work instead of a special project.

**pytest and its plugins** run the tests and, more importantly, measure their quality:

- *coverage* fails the build if overall branch coverage drops below a floor (80%), so new code
  arrives with tests.
- *pytest-randomly* runs the tests in a seeded random order, which surfaces hidden coupling
  between tests (a test that only passes because another ran first) reproducibly instead of as a
  once-a-month flake.
- *testcontainers* starts a throwaway real Postgres for the integration tests, so the database
  code is tested against the actual database, not a mock. This needs Docker.
- *schemathesis* reads the API's OpenAPI schema and throws generated inputs at every endpoint,
  asserting none of them cause a server error. It already caught a real bug here: an unbounded
  input that would have crashed on an oversized value.
- *`alembic check`* fails if you changed a database model but forgot to create the migration, one
  of the most common and most annoying mistakes to discover late.
- *the OpenAPI snapshot* fails if the public API surface changed without you intending it, so an
  accidental breaking change to the contract cannot slip through silently.

## When you commit

Git hooks (installed with `uv run poe install-hooks`) run a fast subset before a commit is even
created:

- **ruff**, **import-linter**, and **deptry** run again, so the cheap checks catch you at commit
  time, not just in `poe check`.
- **gitleaks** scans the change for secrets (API keys, tokens, private keys) and blocks the commit
  if it finds one. A leaked secret in git history is expensive to clean up; this stops it at the
  door.
- **Semgrep** enforces project conventions that import-linter structurally cannot see, because it
  reads *how code is called*, not just what it imports. The first such rule enforces that database
  commits go only through the UnitOfWork (see
  [ADR-0003](adr/0003-unit-of-work-commit-authority.md)); a stray `session.commit()` elsewhere is
  rejected.
- **commitizen** checks the commit *message* follows the Conventional Commits format
  (`feat: ...`, `fix: ...`). That keeps history readable and lets tooling generate changelogs
  later.

## When you open a pull request

Continuous integration (GitHub Actions) re-runs the full `uv run poe check` against a real
Postgres service, so nothing depends on a developer's machine. Alongside it:

- **Squawk** lints the SQL your migrations would emit and warns when an operation would take a
  heavy lock on a live table, the kind of migration that causes downtime. It runs when migrations
  change.
- **zizmor** audits the workflow files themselves for security problems (script injection,
  over-broad permissions, unpinned actions), because the CI configuration is code too, and every
  GitHub Action is pinned to an exact commit so a moved tag cannot change what runs.
- **diff-cover** looks only at the lines you changed and requires them to be well tested (90%),
  which catches untested new code that would otherwise hide under a passing repo-wide average.

## Nightly

**mutmut** runs mutation testing on the business logic. It makes small changes to your code (flip
a comparison, drop a line) and checks whether the tests notice. A test suite can have high
coverage and still assert almost nothing; mutation testing is the honest measure of whether the
tests would actually catch a regression. It runs nightly rather than on every change because it
is slow, and surviving mutants are a to-do list, not a blocking failure.

## Kept current

**Dependabot** opens weekly pull requests to update Python dependencies, GitHub Actions, and the
Docker base image. This matters because a security scan is only as good as it is fresh: pinned
versions and a scanner with nothing new to update would slowly rot. Every update PR runs the full
`poe check` before it can merge, so staying current is safe by default.

## The application stack it all guards

The tooling protects a small, conventional runtime stack:

- **FastAPI** and **uvicorn** for the web layer and the server.
- **async SQLAlchemy 2.0** with **asyncpg** and **Alembic** for the database and migrations.
- **pydantic v2** for request/response models and **pydantic-settings** for configuration.
- **loguru** for structured logging and **OpenTelemetry** for tracing.

## For AI coding agents

The same tools that help humans are what make this codebase safe for AI agents to work in: a fixed
structure to mirror, and one deterministic command to verify against. `AGENTS.md` is the single
set of rules, and the `.claude/` directory ships an auto-formatting hook and task-specific skills.
See [Agent-native](agent-native.md).

## Why so much tooling?

Because each layer is cheap only because the one before it already did its job. Formatting never
reaches review, so review is about logic. The architecture boundary is a build error, so it never
becomes a slow decay. Coverage and mutation testing together mean tests are both present and
meaningful. And because every check is deterministic and named behind one command, "is this done?"
has a real answer, whether it is a new contributor or an AI agent asking. That is what lets the
project move fast without the code getting worse.
