"""OpenTelemetry tracing configuration."""

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider

from app.infrastructure.config import Settings


def configure_telemetry(settings: Settings) -> None:
    """Configure OpenTelemetry with trace/span ID propagation.

    Sets up TracerProvider with service resource so trace IDs propagate
    into loguru. An actual exporter (e.g. OTLP) can be added later.
    """
    resource = Resource.create({"service.name": settings.app_name})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)


def instrument_app(app: FastAPI) -> None:
    """Instrument a FastAPI app with OpenTelemetry."""
    FastAPIInstrumentor.instrument_app(app)
