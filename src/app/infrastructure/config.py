"""Application configuration with environment-based settings."""

from enum import StrEnum, auto
from functools import lru_cache
from typing import Annotated

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Application environment."""

    LOCAL = auto()
    DEV = auto()
    PROD = auto()


class LogFormat(StrEnum):
    """Log output format."""

    TEXT = auto()
    JSON = auto()


class Settings(BaseSettings):
    """Application settings with environment variable support.

    All settings can be overridden via environment variables with the
    ``APP_`` prefix (e.g. ``APP_ENVIRONMENT=local``).
    """

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Core ---
    app_name: str = "fastapi-hexagonal-template"
    app_version: str = "0.1.0"
    environment: Environment = Environment.LOCAL
    debug: bool = False

    # --- Server ---
    host: str = "0.0.0.0"  # noqa: S104  # binds all interfaces in containers; override via APP_HOST
    port: int = 8000

    # --- Logging ---
    log_level: Annotated[str, Field(pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")] = "INFO"
    log_format: LogFormat = LogFormat.TEXT

    # --- CORS ---
    # Typed as str because pydantic-settings JSON-decodes list types,
    # which fails on plain env values like "" or "*".
    cors_origins: str = ""
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "*"
    cors_allow_headers: str = "*"

    # --- Database ---
    database_url: SecretStr | None = None
    database_pool_size: int = 5
    database_pool_max_overflow: int = 10

    # --- Feature flags ---
    feature_detailed_errors: bool = True
    feature_request_logging: bool = True

    @field_validator("log_level", mode="before")
    @classmethod
    def uppercase_log_level(cls, v: str) -> str:
        """Ensure log level is uppercase."""
        return v.upper() if isinstance(v, str) else v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PROD

    @property
    def is_development(self) -> bool:
        """Check if running in a development environment (local or dev)."""
        return self.environment in (Environment.LOCAL, Environment.DEV)


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings singleton."""
    return Settings()
