# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A production-grade, AI-agent-native FastAPI backend template built on hexagonal architecture (ports & adapters), with layer boundaries enforced in CI. Python 3.13, FastAPI, uv for package management.

## Commands

```bash
uv sync && uv run poe install-hooks  # Initial setup (installs pre-commit + commit-msg hooks)
uv run poe dev                        # Dev server (uvicorn --reload)
uv run poe check                      # Full loop: lint → typecheck → arch → deps → audit → test
uv run poe lint                       # Ruff linter (incl. security S, complexity C90, docstrings D)
uv run poe typecheck                  # ty type checker
uv run poe arch                       # Import-linter (hexagonal enforcement)
uv run poe deps                       # deptry — unused/missing/transitive dependencies
uv run poe audit                      # pip-audit — dependency CVE scan
uv run poe test                       # pytest + coverage (enforces fail_under; incl. schemathesis fuzzing)
uv run poe test-quick                 # pytest without coverage (fast iteration)
uv run poe test-parallel              # pytest -n auto (xdist) for larger suites
uv run poe format                     # Ruff formatter
uv run poe migration-lint             # Squawk lock-safety lint on migration DDL (needs `squawk` on PATH)
```

Run a single test: `uv run pytest tests/unit/domain/test_task.py -k test_name`

## Architecture

Hexagonal Architecture (Ports & Adapters) under `src/app/`. Imports flow **inward only** — enforced by import-linter (`uv run poe arch`):

```
infrastructure/  →  application/  →  domain/
  (outer)            (middle)        (inner, no deps)
```

- **domain/** — Pure business logic, zero imports from other layers. Pydantic models in `entities.py`, custom errors in `exceptions.py`.
- **application/** — Use cases orchestrate domain logic. `ports/input/` defines what the app can do (implemented by use cases). `ports/output/` defines what the app needs (implemented by infrastructure, e.g., repositories).
- **infrastructure/** — External adapters. `web/controllers/` for FastAPI routes, `web/schemas/` for API DTOs, `db/repositories/` for data access.

Composition root: `src/app/main.py` → `infrastructure/web/app.py` (`create_app()`).

## Configuration

Settings via pydantic-settings in `src/app/infrastructure/config.py`. All env vars use the `APP_` prefix (e.g., `APP_ENVIRONMENT=local`). See `.env.example` for all options.

## Testing

Tests in `tests/` with `unit/`, `integration/`, `e2e/` subdirectories. Uses pytest-asyncio with `asyncio_mode = "auto"`.

**Coverage** — configured in `pyproject.toml` under `[tool.coverage.*]`. Branch coverage enabled, threshold enforced via `fail_under` (currently 80%). Adjust the threshold in `[tool.coverage.report]`.

Ensure tests are successful after implementing a new feature.

## Code Style
- Ruff with line length 120. Key rules: isort, bugbear, pyupgrade, simplify, pathlib enforcement. First-party package: `app`.
- Generate production-grade Python code following these principles: use type hints on all functions and variables, write pure functions with clear single responsibilities, and prefer immutability and functional patterns over stateful mutations.
- Apply Clean Architecture separation: keep I/O at the edges, business logic in the core, and never mix concerns across layers.
- Always include comprehensive docstrings (Google style), meaningful variable names, and handle all edge cases explicitly; no silent failures or bare excepts.
- Prefer stdlib solutions before third-party; when dependencies are needed, pin versions and document why each is required.
- Write code that is immediately testable: no hidden globals, no hard-coded config, dependency-injected, and structured so unit tests require zero mocking of internals.
