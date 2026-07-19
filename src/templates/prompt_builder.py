"""
Prompt builder for quiz generation.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.models import (
    QuizRequest,
    RetrievedDocument,
    SearchResult,
)


# ==========================================================
# Prompt Container
# ==========================================================


@dataclass(slots=True)
class Prompt:
    """
    Structured prompt for LLMs.
    """

    system: str

    user: str

    @property
    def full_prompt(self) -> str:
        """Return complete prompt."""

        return f"{self.system}\n\n{self.user}"


# ==========================================================
# Prompt Builder
# ==========================================================


class PromptBuilder:
    """
    Builds prompts for Gemini.
    """

    # ------------------------------------------------------

    def build(
        self,
        *,
        request: QuizRequest,
        retrieved_docs: list[RetrievedDocument],
        web_results: list[SearchResult],
    ) -> Prompt:
        """
        Build the complete prompt.
        """

        system = self._build_system_prompt()

        sections = [
            self._build_request_section(request),
            self._build_local_context(retrieved_docs),
            self._build_web_context(web_results),
            self._build_rules(),
            self._build_output_format(),
        ]

        user = "\n\n".join(
            section
            for section in sections
            if section.strip()
        )

        return Prompt(
            system=system,
            user=user,
        )

    # ------------------------------------------------------

    def _build_system_prompt(self) -> str:
        """
        System instructions.
        """

        return """
You are an expert sports quiz generation assistant.

Your task is to create engaging, accurate, educational multiple-choice quizzes.

Use the provided local knowledge first.

Use web search only when it adds useful context.

Never invent facts.

Every question must have exactly four options.

Only one option may be correct.

Provide a concise explanation for every answer.

Return ONLY valid JSON.
""".strip()

    # ------------------------------------------------------

    def _build_request_section(
        self,
        request: QuizRequest,
    ) -> str:

        return f"""
# USER REQUEST

Sport:
{request.sport}

Difficulty:
{request.difficulty}

Number of Questions:
{request.number_of_questions}
""".strip()

    # ------------------------------------------------------

    def _build_local_context(
        self,
        docs: list[RetrievedDocument],
    ) -> str:

        if not docs:

            return """
# LOCAL KNOWLEDGE

No local knowledge available.
""".strip()

        lines = ["# LOCAL KNOWLEDGE"]

        for index, doc in enumerate(docs, start=1):

            lines.append(
                f"""
Document {index}

Content:
{doc.content}

Metadata:
{doc.metadata}

Similarity:
{doc.similarity_score:.3f}
""".strip()
            )

        return "\n\n".join(lines)

    # ------------------------------------------------------

    def _build_web_context(
        self,
        results: list[SearchResult],
    ) -> str:

        if not results:

            return """
# WEB SEARCH

No web search results available.
""".strip()

        lines = ["# WEB SEARCH"]

        for index, result in enumerate(
            results,
            start=1,
        ):

            lines.append(
                f"""
Result {index}

Title:
{result.title}

Summary:
{result.snippet}

Source:
{result.source}
""".strip()
            )

        return "\n\n".join(lines)

    # ------------------------------------------------------

    def _build_rules(self) -> str:

        return """
# QUIZ RULES

Generate questions only about the requested sport.

Match the requested difficulty.

Avoid duplicate questions.

Use only information supported by the provided context.

Do not mention that context was provided.

Questions should test understanding instead of memorization whenever possible.

Explanations should be concise and factually accurate.
""".strip()

    # ------------------------------------------------------

    def _build_output_format(self) -> str:

        return """
# OUTPUT FORMAT

Return ONLY valid JSON.

{
  "sport": "...",
  "difficulty": "...",
  "questions": [
    {
      "question": "...",
      "options": [
        {
          "label": "A",
          "text": "..."
        },
        {
          "label": "B",
          "text": "..."
        },
        {
          "label": "C",
          "text": "..."
        },
        {
          "label": "D",
          "text": "..."
        }
      ],
      "correct_answer": "A",
      "explanation": "..."
    }
  ]
}
""".strip()