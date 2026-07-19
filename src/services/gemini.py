"""
Gemini LLM service.
"""

from __future__ import annotations

import json

from google import genai
from google.genai import types

from src.config import settings
from src.constants import (
    DEFAULT_MAX_OUTPUT_TOKENS,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_K,
    DEFAULT_TOP_P,
)
from src.logger import logger, log_execution_time


class GeminiService:
    """
    Wrapper around the Google Gemini API.
    """

    def __init__(
        self,
        *,
        model: str | None = None,
    ) -> None:

        self.model = model or settings.model_name

        self.client = genai.Client(
            api_key=settings.gemini_api_key,
        )

    # ======================================================
    # Public API
    # ======================================================

    @log_execution_time("Gemini Generation")
    def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """
        Generate text from Gemini.

        Parameters
        ----------
        system_prompt:
            System instructions.

        user_prompt:
            User prompt.

        Returns
        -------
        str
        """

        logger.info(
            f"Generating response using {self.model}"
        )

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=DEFAULT_TEMPERATURE,
            top_p=DEFAULT_TOP_P,
            top_k=DEFAULT_TOP_K,
            max_output_tokens=DEFAULT_MAX_OUTPUT_TOKENS,
            response_mime_type="application/json",
        )

        # print(f"Using Gemini model: {self.model}")

        response = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=config,
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        logger.success("Generation completed.")

        return response.text.strip()

    # ======================================================
    # Helpers
    # ======================================================

    def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> dict:
        """
        Generate and parse a JSON response from Gemini.
        """
        response = self.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        try:
            return json.loads(response)

        except json.JSONDecodeError as exc:
            logger.exception(exc)
            raise ValueError(
                "Gemini returned invalid JSON."
            ) from exc
    def health_check(self) -> bool:
        """
        Verify that the Gemini service is reachable and the configured model
        can generate a response.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents="Health check",
            )

            if response.text:
                logger.info("Gemini health check passed.")
                return True

            logger.warning("Gemini health check returned an empty response.")
            return False

        except Exception as exc:
            logger.exception(f"Gemini health check failed: {exc}")
            return False