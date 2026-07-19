"""
Application-wide constants.

This module centralizes all constants used across the application,
making the codebase easier to maintain and reducing hardcoded values.
"""

from typing import Final

# ==========================================================
# Application
# ==========================================================

APP_NAME: Final[str] = "AI-Powered Sports Quiz Generation Agent"

APP_VERSION: Final[str] = "1.0.0"

PAGE_TITLE: Final[str] = APP_NAME

PAGE_ICON: Final[str] = "🏆"

# ==========================================================
# Supported Sports
# ==========================================================

SUPPORTED_SPORTS: Final[list[str]] = [
    "Cricket",
    "Football",
    "Basketball",
    "Tennis",
    "Badminton",
    "Formula 1",
    "Olympics",
]

# ==========================================================
# Difficulty Levels
# ==========================================================

SUPPORTED_DIFFICULTIES: Final[list[str]] = [
    "Easy",
    "Medium",
    "Hard",
]

# ==========================================================
# Quiz Configuration
# ==========================================================

DEFAULT_QUESTION_COUNT: Final[int] = 5

MIN_QUESTION_COUNT: Final[int] = 4

MAX_QUESTION_COUNT: Final[int] = 5

OPTIONS_PER_QUESTION: Final[int] = 4

# ==========================================================
# ChromaDB
# ==========================================================

CHROMA_COLLECTION_NAME: Final[str] = "sports_knowledge"

DOCUMENT_SOURCE: Final[str] = "sports_facts"

# ==========================================================
# Retrieval
# ==========================================================

DEFAULT_SEARCH_RESULTS: Final[int] = 3

DEFAULT_VECTOR_RESULTS: Final[int] = 3

# ==========================================================
# Embedding Model
# ==========================================================

EMBEDDING_MODEL_NAME: Final[str] = "all-MiniLM-L6-v2"

# ==========================================================
# Logging
# ==========================================================

LOG_FORMAT: Final[str] = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

LOG_FILE_NAME: Final[str] = "logs/app.log"

# ==========================================================
# LLM
# ==========================================================

SYSTEM_ROLE: Final[str] = (
    "You are an expert sports quiz generator."
)

# ==========================================================
# JSON Keys
# ==========================================================

QUESTION_KEY: Final[str] = "question"

OPTIONS_KEY: Final[str] = "options"

ANSWER_KEY: Final[str] = "answer"

EXPLANATION_KEY: Final[str] = "explanation"

SPORT_KEY: Final[str] = "sport"

DIFFICULTY_KEY: Final[str] = "difficulty"