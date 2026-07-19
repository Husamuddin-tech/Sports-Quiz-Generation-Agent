"""
Pydantic models used throughout the application.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from datetime import datetime, date


# ==========================================================
# Quiz Request
# ==========================================================


class QuizRequest(BaseModel):
    """User request for quiz generation."""

    sport: str = Field(..., min_length=2)

    difficulty: Literal["Easy", "Medium", "Hard"]

    number_of_questions: int = Field(
        default=5,
        ge=4,
        le=5,
    )


# ==========================================================
# Search Result
# ==========================================================


class SearchResult(BaseModel):
    """Represents a single web search result."""

    title: str

    snippet: str

    source: str


# ==========================================================
# Retrieved Context
# ==========================================================


class RetrievedDocument(BaseModel):
    """Document retrieved from ChromaDB."""

    content: str

    source: str

    similarity_score: float


# ==========================================================
# Quiz Option
# ==========================================================


class QuizOption(BaseModel):
    """Represents one MCQ option."""

    label: Literal["A", "B", "C", "D"]

    text: str


# ==========================================================
# Quiz Question
# ==========================================================


class QuizQuestion(BaseModel):
    """Represents a single quiz question."""

    question: str

    options: list[QuizOption]

    correct_answer: Literal["A", "B", "C", "D"]

    explanation: str


# ==========================================================
# Quiz Response
# ==========================================================


class QuizResponse(BaseModel):
    """Complete quiz."""

    sport: str

    difficulty: str

    questions: list[QuizQuestion]

    sources: list[str] = []

    generated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )


class KnowledgeSource(BaseModel):
    """Metadata describing the origin of a knowledge record."""

    type: str
    name: str
    license: str
    verified: bool



class SportsKnowledge(BaseModel):
    """Represents one curated knowledge record."""

    id: str

    sport: str

    topic: str

    title: str

    content: str

    keywords: list[str]

    question_types: list[str]

    difficulty: list[str]

    version: str

    last_updated: date

    source: KnowledgeSource

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )



