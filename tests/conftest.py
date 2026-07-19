"""
Pytest fixtures.
"""

from __future__ import annotations

import pytest

from src.models import QuizRequest


@pytest.fixture
def sample_request() -> QuizRequest:
    return QuizRequest(
        sport="Cricket",
        difficulty="Easy",
        number_of_questions=5,
    )