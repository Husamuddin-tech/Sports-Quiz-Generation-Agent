"""
Application configuration.

Loads environment variables from the .env file and exposes them
through a strongly typed Settings object.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ==========================================================
# Project Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_DB_PATH = BASE_DIR / "chroma_db"

DATA_DIR = BASE_DIR / "data" / "sports"

# ==========================================================
# Settings
# ==========================================================


class Settings(BaseSettings):
    """Application settings."""

    # ==========================
    # Gemini
    # ==========================

    gemini_api_key: str = Field(
        ...,
        alias="GEMINI_API_KEY",
    )

    model_name: str = Field(
        default="gemini-2.5-flash",
        alias="MODEL_NAME",
    )

    temperature: float = Field(
        default=0.4,
        ge=0.0,
        le=2.0,
        alias="TEMPERATURE",
    )

    max_output_tokens: int = Field(
        default=4096,
        gt=0,
        alias="MAX_OUTPUT_TOKENS",
    )

    top_p: float = Field(
        default=0.95,
        alias="TOP_P",
    )

    top_k: int = Field(
        default=40,
        alias="TOP_K",
    )

    # ==========================
    # Retrieval
    # ==========================

    top_k_results: int = Field(
        default=5,
        ge=1,
        le=20,
        alias="TOP_K_RESULTS",
    )

    # ==========================
    # Embeddings
    # ==========================

    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        alias="EMBEDDING_MODEL",
    )

    # ==========================
    # Logging
    # ==========================

    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings."""

    return Settings()


settings = get_settings()