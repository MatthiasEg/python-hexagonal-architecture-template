"""Property-based API fuzzing.

Schemathesis reads the OpenAPI schema FastAPI generates and drives every operation
with generated inputs, asserting the API never returns a 5xx (server error). This
catches whole classes of edge-case crashes without hand-writing cases. The run is
derandomized so an agent gets the same pass/fail on every invocation.
"""

import pytest
import schemathesis
from hypothesis import settings
from schemathesis.checks import not_a_server_error
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.infrastructure.config import Environment, Settings
from app.infrastructure.db.dependencies import get_db_session
from app.infrastructure.db.engine import ensure_async_url
from app.infrastructure.web.app import create_app


def _schema(database_url: str) -> schemathesis.BaseSchema:
    """Build the app against the test database and load its OpenAPI schema."""
    settings_ = Settings(
        environment=Environment.LOCAL,
        debug=True,
        database_url=database_url,
        feature_request_logging=False,
    )
    app = create_app(settings=settings_)
    engine = create_async_engine(ensure_async_url(database_url), poolclass=NullPool)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def _session():
        async with factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = _session
    return schemathesis.openapi.from_asgi("/openapi.json", app)


@pytest.fixture
def api_schema(database_url: str) -> schemathesis.BaseSchema:
    """Expose the OpenAPI schema (bound to the test DB) to schemathesis."""
    return _schema(database_url)


# `from_fixture` lets the schema depend on the session-scoped `database_url` fixture.
schema = schemathesis.pytest.from_fixture("api_schema")


@schema.parametrize()
@settings(max_examples=20, deadline=None, derandomize=True)
def test_api_never_returns_server_error(case: schemathesis.Case) -> None:
    """Every generated request against every endpoint must avoid a 5xx response."""
    case.call_and_validate(checks=[not_a_server_error])
