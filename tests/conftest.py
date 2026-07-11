import pytest
from fastapi.testclient import TestClient

from app.infrastructure.config import Environment, Settings
from app.infrastructure.web.app import create_app


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings with safe defaults."""
    return Settings(
        environment=Environment.LOCAL,
        debug=True,
        log_level="DEBUG",
        feature_detailed_errors=True,
        feature_request_logging=False,
    )


@pytest.fixture
def app(test_settings: Settings):
    """Create a FastAPI app instance with test settings."""
    return create_app(settings=test_settings)


@pytest.fixture
def client(app) -> TestClient:
    """Create a test client with the test app."""
    return TestClient(app)
