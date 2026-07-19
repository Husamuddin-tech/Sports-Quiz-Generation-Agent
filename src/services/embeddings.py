"""
Embedding service.

This module provides a centralized interface for generating text
embeddings using Sentence Transformers.

Responsibilities:
- Lazy-load the embedding model
- Generate single embeddings
- Generate batch embeddings
- Expose embedding dimension
"""

from __future__ import annotations

from typing import Sequence

from sentence_transformers import SentenceTransformer

from src.constants import (
    EMBEDDING_BATCH_SIZE,
    EMBEDDING_MODEL_NAME,
)
from src.exceptions import EmbeddingError
from src.logger import logger, log_execution_time


class EmbeddingService:
    """
    Service for generating semantic embeddings.

    The underlying SentenceTransformer model is loaded lazily on the
    first request and reused for the lifetime of the application.
    """

    def __init__(self) -> None:
        self._model: SentenceTransformer | None = None

    # ==========================================================
    # Internal
    # ==========================================================

    def _load_model(self) -> SentenceTransformer:
        """
        Lazily load the embedding model.
        """

        if self._model is None:

            logger.info(
                f"Loading embedding model: {EMBEDDING_MODEL_NAME}"
            )

            try:

                self._model = SentenceTransformer(
                    EMBEDDING_MODEL_NAME
                )

            except Exception as exc:
                raise EmbeddingError(
                    f"Unable to load embedding model: {exc}"
                ) from exc

            logger.success(
                f"Embedding model loaded: {EMBEDDING_MODEL_NAME}"
            )

        return self._model

    # ==========================================================
    # Public API
    # ==========================================================

    @property
    def embedding_dimension(self) -> int:
        """
        Return the embedding dimension.

        Returns
        -------
        int
            Embedding vector size.
        """

        model = self._load_model()

        return model.get_sentence_embedding_dimension()

    @log_execution_time("Generate Text Embedding")
    def embed_text(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate an embedding for a single text.
        """

        text = text.strip()

        if not text:
            raise EmbeddingError(
                "Cannot generate an embedding for empty text."
            )

        model = self._load_model()

        try:

            embedding = model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )

            return embedding.tolist()

        except Exception as exc:

            raise EmbeddingError(
                f"Embedding generation failed: {exc}"
            ) from exc

    @log_execution_time("Generate Batch Embeddings")
    def embed_batch(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Parameters
        ----------
        texts:
            Collection of documents.

        Returns
        -------
        list[list[float]]
            Embedding vectors.
        """

        if not texts:
            return []

        model = self._load_model()

        logger.info(
            f"Generating embeddings for {len(texts)} documents."
        )

        try:

            embeddings = model.encode(
                list(texts),
                batch_size=EMBEDDING_BATCH_SIZE,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )

            logger.success(
                f"Generated {len(embeddings)} embeddings."
            )

            return embeddings.tolist()

        except Exception as exc:

            raise EmbeddingError(
                f"Batch embedding generation failed: {exc}"
            ) from exc