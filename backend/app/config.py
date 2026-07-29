"""
Mithrava Agriculture Platform - Application Configuration

Production-grade settings loaded from environment variables / .env file.
Uses pydantic-settings for validation, type coercion, and documentation.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import json


class Settings(BaseSettings):
    """Application settings with validation and defaults.

    All settings can be overridden via environment variables or a .env file
    in the project root. Field names are case-sensitive and must match exactly.
    """

    # ── Environment ────────────────────────────────────────────────────
    ENVIRONMENT: str = Field(
        default="development",
        description="Runtime environment: development, staging, production",
    )
    DEBUG: bool = Field(default=True, description="Enable debug mode and verbose logging")

    # ── Authentication / JWT ───────────────────────────────────────────
    SECRET_KEY: str = Field(
        default="change-me-in-production",
        description="HMAC secret for JWT signing. MUST be changed in production.",
    )
    ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=15, description="Access token lifetime in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, description="Refresh token lifetime in days"
    )

    # ── Database ───────────────────────────────────────────────────────
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://mithrava:mithrava@localhost:5432/mithrava",
        description="Async PostgreSQL connection string (asyncpg driver)",
    )
    DATABASE_URL_SYNC: str = Field(
        default="postgresql://mithrava:mithrava@localhost:5432/mithrava",
        description="Sync PostgreSQL connection string (psycopg2 driver, for migrations)",
    )

    # ── Redis ──────────────────────────────────────────────────────────
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for caching and rate limiting",
    )

    # ── CORS ───────────────────────────────────────────────────────────
    CORS_ORIGINS: str = Field(
        default='["http://localhost:3000"]',
        description='JSON-encoded list of allowed CORS origins',
    )

    # ── Google Gemini (primary LLM) ────────────────────────────────────
    GEMINI_API_KEY: str = Field(
        default="", description="Google Gemini API key (primary LLM provider)"
    )
    GEMINI_MODEL: str = Field(
        default="gemini-2.0-flash", description="Gemini chat completion model"
    )
    GEMINI_VISION_MODEL: str = Field(
        default="gemini-2.0-flash", description="Gemini vision model"
    )
    GEMINI_EMBEDDING_MODEL: str = Field(
        default="text-embedding-004",
        description="Gemini embedding model",
    )

    # ── Ollama (local LLM) ────────────────────────────────────────────
    OLLAMA_URL: str = Field(
        default="http://localhost:11434", description="Ollama server base URL"
    )
    OLLAMA_MODEL: str = Field(
        default="llama3.1", description="Ollama model identifier"
    )

    # ── Weather ────────────────────────────────────────────────────────
    OPENWEATHER_API_KEY: str = Field(
        default="", description="OpenWeatherMap API key for weather data"
    )
    # Backward compat alias — some env files use this name
    OPENWEATHERMAP_API_KEY: str = Field(
        default="", description="(Deprecated) Use OPENWEATHER_API_KEY instead"
    )

    # ── AWS (S3 Storage) ───────────────────────────────────────────────
    AWS_ACCESS_KEY_ID: str = Field(default="", description="AWS IAM access key ID")
    AWS_SECRET_ACCESS_KEY: str = Field(
        default="", description="AWS IAM secret access key"
    )
    AWS_BUCKET_NAME: str = Field(
        default="mithrava-storage", description="S3 bucket name for file uploads"
    )
    AWS_REGION: str = Field(
        default="ap-south-1", description="AWS region (Mumbai, closest to India)"
    )

    # ── Google OAuth ───────────────────────────────────────────────────
    GOOGLE_CLIENT_ID: str = Field(default="", description="Google OAuth 2.0 client ID")
    GOOGLE_CLIENT_SECRET: str = Field(
        default="", description="Google OAuth 2.0 client secret"
    )

    # ── OpenAI (fallback LLM, optional) ────────────────────────────────
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key (optional fallback)")
    OPENAI_MODEL: str = Field(
        default="gpt-4o-mini", description="OpenAI chat completion model"
    )
    OPENAI_EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model (1536 dimensions)",
    )

    # ── Firebase / Push Notifications ──────────────────────────────────
    FIREBASE_CREDENTIALS_PATH: str = Field(
        default="firebase-service-account.json",
        description="Path to Firebase service account JSON for FCM push notifications",
    )

    # ── Rate Limiting ──────────────────────────────────────────────────
    RATE_LIMIT_GENERAL: int = Field(
        default=100, description="Max requests per window for general endpoints"
    )
    RATE_LIMIT_AI: int = Field(
        default=10, description="Max requests per window for AI endpoints"
    )
    RATE_LIMIT_WINDOW: int = Field(
        default=60, description="Rate limit window duration in seconds"
    )

    # ── Logging ────────────────────────────────────────────────────────
    LOG_LEVEL: str = Field(
        default="INFO", description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
    LOG_FORMAT: str = Field(
        default="json", description="Log output format: json or text"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS JSON string into a list of origin URLs."""
        return json.loads(self.CORS_ORIGINS)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
