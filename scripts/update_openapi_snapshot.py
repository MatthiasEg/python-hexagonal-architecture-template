"""Regenerate the committed OpenAPI snapshot.

Run via `uv run poe openapi-snapshot` after an intentional change to the API
surface. The snapshot is asserted against in tests/unit/test_openapi_snapshot.py,
so any unintended drift fails the build until it is reviewed and regenerated here.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from app.infrastructure.config import Environment, Settings
from app.infrastructure.web.app import create_app

SNAPSHOT = Path(__file__).resolve().parents[1] / "tests" / "snapshots" / "openapi.json"


def main() -> None:
    """Write the current OpenAPI schema to the committed snapshot file."""
    app = create_app(settings=Settings(environment=Environment.LOCAL, database_url=None))
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n")
    print(f"wrote {SNAPSHOT}")


if __name__ == "__main__":
    main()
