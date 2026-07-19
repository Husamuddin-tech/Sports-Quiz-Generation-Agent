"""
Custom exceptions for the AI-Powered Sports Quiz Generation Agent.

Having application-specific exceptions makes error handling cleaner,
improves debugging, and allows us to catch different failure types
without relying on generic exceptions.
"""


class SportsQuizError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str = "An unexpected application error occurred."):
        self.message = message
        super().__init__(self.message)


# ==========================================================
# Configuration
# ==========================================================


class ConfigurationError(SportsQuizError):
    """Raised when application configuration is invalid."""


# ==========================================================
# Retrieval
# ==========================================================


class DatabaseError(SportsQuizError):
    """Raised when ChromaDB operations fail."""


class EmbeddingError(SportsQuizError):
    """Raised when embedding generation fails."""


class SearchError(SportsQuizError):
    """Raised when web search fails."""


class RetrievalError(SportsQuizError):
    """Raised when retrieval pipeline fails."""


# ==========================================================
# LLM
# ==========================================================


class LLMError(SportsQuizError):
    """Raised when the Gemini API returns an error."""


class PromptError(SportsQuizError):
    """Raised when prompt construction fails."""


class ParsingError(SportsQuizError):
    """Raised when the LLM response cannot be parsed."""


class ValidationError(SportsQuizError):
    """Raised when generated quiz data fails validation."""


class DatasetValidationError(SportsQuizError):
    """Raised when the curated knowledge base is invalid."""


class QuizGenerationError(SportsQuizError):
    """Raised when quiz generation fails."""

class LLMError(Exception):
    """Base exception for LLM-related errors."""


class LLMGenerationError(LLMError):
    """Raised when the LLM fails to generate a response."""


class LLMResponseError(LLMError):
    """Raised when the LLM returns an invalid or empty response."""


# ==========================================================
# UI
# ==========================================================


class UserInputError(SportsQuizError):
    """Raised when user input is invalid."""

