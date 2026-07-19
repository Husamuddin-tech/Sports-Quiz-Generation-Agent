"""
Application configuration.

Loads environment variables from the .env file and exposes them
through a strongly typed Settings object.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # ==========================
    # Google Gemini
    # ==========================

    google_api_key: str = Field(
        ...,
        alias="GOOGLE_API_KEY",
        description="Google Gemini API Key",
    )

    model_name: str = Field(
        default="gemini-2.5-flash",
        alias="MODEL_NAME",
    )

    temperature: float = Field(
        default=0.6,
        ge=0.0,
        le=2.0,
        alias="TEMPERATURE",
    )

    max_output_tokens: int = Field(
        default=4096,
        gt=0,
        alias="MAX_OUTPUT_TOKENS",
    )

    # ==========================
    # Retrieval
    # ==========================

    top_k_results: int = Field(
        default=3,
        ge=1,
        le=10,
        alias="TOP_K_RESULTS",
    )

    # ==========================
    # Logging
    # ==========================

    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
    )

    # ==========================
    # ChromaDB
    # ==========================

    chroma_db_path: str = Field(
        default="./chroma_db",
        alias="CHROMA_DB_PATH",
    )

    

    BASE_DIR = Path(__file__).resolve().parent.parent

    CHROMA_DB_PATH = BASE_DIR / "chroma_db"

    # ==========================
    # Embedding Model
    # ==========================

    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        alias="EMBEDDING_MODEL",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.

    The settings are loaded only once during application startup.
    """
    return Settings()


settings = get_settings()