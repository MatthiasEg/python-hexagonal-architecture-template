from fastapi.testclient import TestClient

from app.infrastructure.config import Environment, Settings
from app.infrastructure.web.app import create_app


def test_create_app_serves_health() -> None:
    settings = Settings(environment=Environment.LOCAL, feature_request_logging=False)
    with TestClient(create_app(settings=settings)) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
