"""
Quiz generation service.
"""

from __future__ import annotations

from pydantic import ValidationError

from src.logger import logger, log_execution_time
from src.models import QuizRequest, QuizResponse
from src.services.gemini import GeminiService
from src.services.retrieval import RetrievalService
from src.services.search import WebSearchService
from src.templates.prompt_builder import PromptBuilder


class QuizGenerator:
    """
    Coordinates the complete quiz generation workflow.
    """

    def __init__(
        self,
        retrieval_service: RetrievalService | None = None,
        web_search_service: WebSearchService | None = None,
        prompt_builder: PromptBuilder | None = None,
        gemini_service: GeminiService | None = None,
    ) -> None:

        self.retrieval = (
            retrieval_service
            if retrieval_service is not None
            else RetrievalService()
        )

        self.web_search = (
            web_search_service
            if web_search_service is not None
            else WebSearchService()
        )

        self.prompt_builder = (
            prompt_builder
            if prompt_builder is not None
            else PromptBuilder()
        )

        self.gemini = (
            gemini_service
            if gemini_service is not None
            else GeminiService()
        )

    # ======================================================
    # Public API
    # ======================================================

    @log_execution_time("Quiz Generation")
    def generate(
        self,
        request: QuizRequest,
    ) -> QuizResponse:
        """
        Generate a quiz from the user's request.
        """

        logger.info(
            f"Generating {request.difficulty} "
            f"{request.sport} quiz..."
        )

        # ---------------------------------------------
        # Retrieve local knowledge
        # ---------------------------------------------

        retrieved_docs = self.retrieval.retrieve(
            query = (
                f"Generate {request.number_of_questions} "
                f"{request.difficulty.lower()} level "
                f"multiple choice questions about "
                f"{request.sport}"
            ),
            sport=request.sport,
        )

        # ---------------------------------------------
        # Retrieve web knowledge
        # ---------------------------------------------

        web_results = self.web_search.search(
            query=(
                f"{request.sport} "
                f"{request.difficulty}"
            )
        )

        # ---------------------------------------------
        # Build prompt
        # ---------------------------------------------

        prompt = self.prompt_builder.build(
            request=request,
            retrieved_docs=retrieved_docs,
            web_results=web_results,
        )

        # ---------------------------------------------
        # Gemini
        # ---------------------------------------------

        response_json = self.gemini.generate_json(
            system_prompt=prompt.system,
            user_prompt=prompt.user,
        )

        # ---------------------------------------------
        # Validate Response
        # ---------------------------------------------

        quiz = self._validate_response(
            response_json
        )

        logger.success(
            "Quiz generated successfully."
        )

        return quiz

    # ======================================================
    # Helpers
    # ======================================================

    def _validate_response(
        self,
        response: dict,
    ) -> QuizResponse:
        """
        Validate Gemini JSON response.
        """

        try:

            return QuizResponse.model_validate(
                response
            )

        except ValidationError as exc:

            logger.exception(exc)

            raise ValueError(
                "Generated quiz failed validation."
            ) from exc

    def health_check(self) -> bool:
        """
        Verify generator dependencies.
        """

        return (
            self.retrieval.health_check()
            and self.web_search.health_check()
            and self.gemini.health_check()
        )