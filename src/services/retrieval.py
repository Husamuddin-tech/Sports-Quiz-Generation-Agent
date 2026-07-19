"""
Semantic retrieval service for the sports knowledge base.
"""

from __future__ import annotations

from src.constants import DEFAULT_SEARCH_RESULTS
from src.exceptions import DatabaseError, EmbeddingError
from src.logger import logger, log_execution_time
from src.models import RetrievedDocument
from src.services.database import ChromaDBService
from src.services.embeddings import EmbeddingService


class RetrievalService:
    """
    Performs semantic retrieval from the knowledge base.
    """

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        database: ChromaDBService | None = None,
    ) -> None:
        """
        Initialize retrieval service.

        Parameters
        ----------
        embedding_service:
            Embedding service instance.

        database:
            ChromaDB service instance.
        """

        self.embedding_service = (
            embedding_service
            if embedding_service is not None
            else EmbeddingService()
        )

        self.database = (
            database
            if database is not None
            else ChromaDBService()
        )

    # ======================================================
    # Public API
    # ======================================================

    @log_execution_time("Knowledge Retrieval")
    def retrieve(
        self,
        query: str,
        *,
        sport: str | None = None,
        top_k: int = DEFAULT_SEARCH_RESULTS,
    ) -> list[RetrievedDocument]:
        """
        Retrieve the most relevant knowledge documents.

        Parameters
        ----------
        query:
            User query.

        sport:
            Optional sport filter.

        top_k:
            Number of documents to retrieve.

        Returns
        -------
        list[RetrievedDocument]
        """

        query = query.strip()

        if not query:
            raise ValueError(
                "Query cannot be empty."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        logger.info(
            f"Retrieving knowledge "
            f"(sport={sport}, top_k={top_k})"
        )

        query_embedding = self._embed_query(query)

        filters = self._build_filters(sport)

        results = self.database.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters,
        )

        results = self._rerank_results(results)

        logger.success(
            f"Retrieved {len(results)} document(s)."
        )

        return results

    # ======================================================
    # Internal Helpers
    # ======================================================

    def _embed_query(
        self,
        query: str,
    ) -> list[float]:
        """
        Generate an embedding for the user query.
        """

        try:
            return self.embedding_service.embed_text(
                query
            )

        except EmbeddingError:
            raise

        except Exception as exc:
            raise EmbeddingError(
                f"Failed to embed query: {exc}"
            ) from exc

    def _build_filters(
        self,
        sport: str | None,
    ) -> dict[str, str] | None:
        """
        Build Chroma metadata filters.
        """

        if not sport:
            return None

        return {
            "sport": sport,
        }

    def _rerank_results(
        self,
        results: list[RetrievedDocument],
    ) -> list[RetrievedDocument]:
        """
        Placeholder for future reranking.

        Currently returns semantic search results
        unchanged.
        """

        return sorted(
            results,
            key=lambda doc: doc.similarity_score,
            reverse=True,
        )

    # ======================================================
    # Convenience Methods
    # ======================================================

    def retrieve_by_sport(
        self,
        sport: str,
        query: str,
        *,
        top_k: int = DEFAULT_SEARCH_RESULTS,
    ) -> list[RetrievedDocument]:
        """
        Retrieve documents for a specific sport.
        """

        return self.retrieve(
            query=query,
            sport=sport,
            top_k=top_k,
        )

    def health_check(self) -> bool:
        """
        Verify that the retrieval pipeline is operational.
        """

        try:

            self.database.count()

            return True

        except DatabaseError:

            return False