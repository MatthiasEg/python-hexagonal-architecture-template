"""The public API surface is snapshot-gated against accidental drift.

FastAPI generates the OpenAPI schema from the routes and DTOs. Committing a
snapshot turns any change to that surface into an explicit, reviewable diff: an
agent that alters an endpoint or a response shape must consciously regenerate the
snapshot, rather than changing the public contract silently.
"""

import json
from pathlib import Path

from app.infrastructure.config import Environment, Settings
from app.infrastructure.web.app import create_app

SNAPSHOT = Path(__file__).resolve().parents[1] / "snapshots" / "openapi.json"


def test_openapi_schema_matches_snapshot() -> None:
    """The generated OpenAPI schema equals the committed snapshot.

    If this fails after an intentional API change, regenerate the snapshot with
    ``uv run poe openapi-snapshot`` and commit it.
    """
    app = create_app(settings=Settings(environment=Environment.LOCAL, database_url=None))
    current = app.openapi()
    expected = json.loads(SNAPSHOT.read_text())
    assert current == expected, (
        "OpenAPI schema drifted. Run `uv run poe openapi-snapshot` if the change is intentional."
    )
