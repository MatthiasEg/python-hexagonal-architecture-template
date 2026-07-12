"""The SQLAlchemy models and the Alembic migrations must not drift apart.

This is the gate that catches the most common migration mistake: editing a model
and forgetting to generate the matching revision. `alembic check` reflects the
schema of the migrated database and compares it to the models; any pending
autogenerate diff fails the build.
"""

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.util.exc import CommandError

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_models_match_migrations(database_url: str) -> None:  # noqa: ARG001  # fixture ensures DB + migrations are ready
    """`alembic check` reports no pending changes: models and migrations agree.

    If this fails, a model changed without a matching migration. Run
    ``uv run poe db-revision -m "..."``, review the generated DDL, and commit it.
    """
    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    try:
        command.check(config)
    except CommandError as exc:
        pytest.fail(
            f"Models have drifted from the migrations: {exc}. "
            'Generate a revision with `uv run poe db-revision -m "..."` and commit it.'
        )
