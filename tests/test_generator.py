"""
Integration tests for quiz generation.
"""

from src.services.generator import QuizGenerator


def test_quiz_generation(
    sample_request,
) -> None:
    """
    Verify end-to-end quiz generation.
    """

    generator = QuizGenerator()

    quiz = generator.generate(
        sample_request,
    )

    assert quiz.sport == "Cricket"

    assert quiz.difficulty == "Easy"

    assert len(quiz.questions) == 5

    for question in quiz.questions:

        assert len(question.options) == 4

        assert question.explanation