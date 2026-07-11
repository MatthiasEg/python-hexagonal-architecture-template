ARG PYTHON_VERSION=3.13
ARG UV_VERSION=0.6.3

FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

# ==============================================================================
# Base stage - shared configuration
# ==============================================================================
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

WORKDIR /app

# ==============================================================================
# Builder stage - install dependencies
# ==============================================================================
FROM base AS builder

COPY --from=uv /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install dependencies first (cached layer)
COPY uv.lock pyproject.toml ./
RUN uv sync --no-install-project --no-dev

# Install the project (non-editable for production)
COPY src/ src/
RUN uv sync --no-dev --no-editable

# ==============================================================================
# Production stage - minimal runtime image
# ==============================================================================
FROM base AS production

ARG BUILD_DATE
ARG VCS_REF

LABEL org.opencontainers.image.title="fastapi-hexagonal-template" \
      org.opencontainers.image.description="Production-grade hexagonal-architecture FastAPI template — enforced in CI, built for AI coding agents." \
      org.opencontainers.image.version="0.1.0" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}"

RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid 1000 --no-create-home app

COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Copy alembic configuration and migrations for deploy-time migrations
COPY --chown=app:app alembic.ini /app/alembic.ini
COPY --chown=app:app src/app/infrastructure/db/migrations/ /app/src/app/infrastructure/db/migrations/

# Production environment defaults
ENV PATH="/app/.venv/bin:$PATH" \
    APP_ENVIRONMENT=prod \
    APP_DEBUG=false \
    APP_LOG_LEVEL=INFO \
    APP_LOG_FORMAT=json \
    APP_FEATURE_DETAILED_ERRORS=false \
    APP_FEATURE_REQUEST_LOGGING=true

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/live')"]

CMD ["python", "-m", "app.entrypoint"]

# ==============================================================================
# Development stage - includes dev dependencies
# ==============================================================================
FROM base AS development

COPY --from=uv /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY uv.lock pyproject.toml ./
RUN uv sync --frozen --no-install-project

COPY src/ src/
COPY alembic.ini /app/alembic.ini
RUN uv sync --frozen

# Development environment defaults
ENV PATH="/app/.venv/bin:$PATH" \
    APP_ENVIRONMENT=local \
    APP_DEBUG=true \
    APP_LOG_LEVEL=DEBUG \
    APP_LOG_FORMAT=text \
    APP_FEATURE_DETAILED_ERRORS=true \
    APP_FEATURE_REQUEST_LOGGING=true

EXPOSE 8000

CMD ["python", "-m", "app.entrypoint"]
