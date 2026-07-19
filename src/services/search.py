"""
DuckDuckGo web search service.
"""

from __future__ import annotations

from ddgs import DDGS

from src.logger import logger, log_execution_time
from src.models import SearchResult


class WebSearchService:
    """
    Performs live web searches using DuckDuckGo.
    """

    def __init__(
        self,
        max_results: int = 5,
    ) -> None:
        self.max_results = max_results

    # ======================================================
    # Public API
    # ======================================================

    @log_execution_time("Web Search")
    def search(
        self,
        query: str,
        *,
        max_results: int | None = None,
    ) -> list[SearchResult]:
        """
        Perform a web search.

        Parameters
        ----------
        query:
            Search query.

        max_results:
            Maximum number of results.

        Returns
        -------
        list[SearchResult]
        """

        query = query.strip()

        if not query:
            raise ValueError(
                "Search query cannot be empty."
            )

        limit = max_results or self.max_results

        logger.info(
            f"Searching DuckDuckGo: {query}"
        )

        try:

            with DDGS() as ddgs:

                raw_results = list(
                    ddgs.text(
                        query,
                        max_results=limit,
                    )
                )

        except Exception as exc:

            logger.exception(exc)

            return []

        results = self._convert_results(
            raw_results
        )

        logger.success(
            f"Retrieved {len(results)} web result(s)."
        )

        return results

    # ======================================================
    # Helpers
    # ======================================================

    def _convert_results(
        self,
        raw_results: list[dict],
    ) -> list[SearchResult]:
        """
        Convert DDGS output into SearchResult objects.
        """

        seen: set[str] = set()

        converted: list[SearchResult] = []

        for result in raw_results:

            url = result.get("href", "")

            if url in seen:
                continue

            seen.add(url)

            converted.append(
                SearchResult(
                    title=result.get("title", ""),
                    snippet=result.get("body", ""),
                    source=url,
                )
            )

        return converted

    # ======================================================
    # Convenience Methods
    # ======================================================

    def health_check(self) -> bool:
        """
        Verify that web search is operational.
        """

        try:

            self.search(
                "sports",
                max_results=1,
            )

            return True

        except Exception:

            return False