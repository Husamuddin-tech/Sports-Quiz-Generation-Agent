"""
ChromaDB service.

Provides a centralized interface for interacting with the
persistent ChromaDB vector database.

Responsibilities
----------------
- Initialize PersistentClient
- Create/Get collection
- Store documents
- Execute semantic search
- Provide collection utilities
"""

from __future__ import annotations

from typing import Any

import chromadb
from chromadb import Collection
from chromadb.api import ClientAPI

from src.config import CHROMA_DB_PATH
from src.constants import (
    CHROMA_COLLECTION_NAME,
    CHROMA_DISTANCE_FUNCTION,
    DEFAULT_SEARCH_RESULTS,
    DEFAULT_PEEK_RESULTS,
)
from src.exceptions import DatabaseError
from src.logger import logger, log_execution_time
from src.models import RetrievedDocument

Metadata = dict[str, Any]


class ChromaDBService:
    """
    Service responsible for all ChromaDB interactions.
    """

    def __init__(self) -> None:
        self._client: ClientAPI | None = None
        self._collection: Collection | None = None

    # ==========================================================
    # Internal
    # ==========================================================

    def _initialize_client(self) -> ClientAPI:
        """
        Initialize the persistent ChromaDB client.
        """

        if self._client is None:

            logger.info(
                f"Initializing ChromaDB at '{CHROMA_DB_PATH}'."
            )

            try:

                self._client = chromadb.PersistentClient(
                    path=str(CHROMA_DB_PATH)
                )

            except Exception as exc:

                raise DatabaseError(
                    f"Failed to initialize ChromaDB: {exc}"
                ) from exc

            logger.success(
                "ChromaDB client initialized."
            )

        return self._client

    def _get_collection(self) -> Collection:
        """
        Retrieve or create the collection.
        """

        if self._collection is None:

            client = self._initialize_client()

            logger.info(
                f"Loading collection '{CHROMA_COLLECTION_NAME}'."
            )

            try:

                self._collection = (
                    client.get_or_create_collection(
                        name=CHROMA_COLLECTION_NAME,
                        metadata={
                            "hnsw:space": CHROMA_DISTANCE_FUNCTION,
                        },
                    )
                )

            except Exception as exc:

                raise DatabaseError(
                    f"Unable to load collection: {exc}"
                ) from exc

            logger.success(
                f"Collection '{CHROMA_COLLECTION_NAME}' ready."
            )

        return self._collection

    # ==========================================================
    # Public API
    # ==========================================================

    @log_execution_time("Store Documents")
    def add_documents(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[Metadata],
    ) -> None:
        """
        Store documents in the ChromaDB collection.
        """

        self._validate_batch_inputs(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        collection = self._get_collection()

        logger.info(
            f"Adding {len(documents)} document(s) "
            f"to '{CHROMA_COLLECTION_NAME}'."
        )

        try:

            collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=[
                    self._prepare_metadata(metadata)
                    for metadata in metadatas
                ],
            )

            # ChromaDB returns None on successful insertion.

        except Exception as exc:

            raise DatabaseError(
                f"Failed to store documents: {exc}"
            ) from exc

        logger.success(
            f"Stored {len(documents)} document(s) "
            f"in '{CHROMA_COLLECTION_NAME}'."
        )

    # ==========================================================
    # Validation
    # ==========================================================

    def _validate_batch_inputs(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[Metadata],
    ) -> None:
        """
        Validate batch input lengths and contents.
        """

        sizes = {
            len(ids),
            len(documents),
            len(embeddings),
            len(metadatas),
        }

        if len(sizes) != 1:

            raise DatabaseError(
                "Batch sizes do not match."
            )

        if not ids:

            raise DatabaseError(
                "Cannot insert an empty batch."
            )

        seen: set[str] = set()
        duplicate_ids: set[str] = set()

        for doc_id in ids:

            if doc_id in seen:
                duplicate_ids.add(doc_id)

            else:
                seen.add(doc_id)

        if duplicate_ids:

            raise DatabaseError(
                "Duplicate document IDs detected: "
                + ", ".join(sorted(duplicate_ids))
            )

        for document in documents:

            if not document.strip():

                raise DatabaseError(
                    "Document text cannot be empty."
                )

        for embedding in embeddings:

            if not embedding:

                raise DatabaseError(
                    "Embedding cannot be empty."
                )

    def _prepare_metadata(
        self,
        metadata: Metadata | None,
    ) -> Metadata:
        """
        Prepare metadata before storage.

        ChromaDB supports primitive metadata values only.
        """

        if metadata is None:
            return {}

        cleaned: Metadata = {}

        for key, value in metadata.items():

            if value is None:
                continue

            if isinstance(
                value,
                (str, int, float, bool),
            ):

                cleaned[key] = value

            elif isinstance(value, list):

                cleaned[key] = ", ".join(
                    str(item)
                    for item in value
                )

            else:

                cleaned[key] = str(value)

        return cleaned
    
# ==========================================================
# Search
# ==========================================================

    @log_execution_time("Semantic Search")
    def search(
        self,
        query_embedding: list[float],
        top_k: int = DEFAULT_SEARCH_RESULTS,
        filters: Metadata | None = None,
    ) -> list[RetrievedDocument]:
        """
        Perform semantic similarity search.

        Parameters
        ----------
        query_embedding:
            Embedding vector of the query.

        top_k:
            Number of documents to retrieve.

        filters:
            Optional metadata filters.

        Returns
        -------
        list[RetrievedDocument]
        """

        if not query_embedding:

            raise DatabaseError(
                "Query embedding cannot be empty."
            )

        collection = self._get_collection()

        logger.info(
            f"Searching '{CHROMA_COLLECTION_NAME}' "
            f"(top_k={top_k})"
        )

        try:

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filters,
                include=[
                    "documents",
                    "metadatas",
                    "distances",
                ],
            )

        except Exception as exc:

            raise DatabaseError(
                f"Search failed: {exc}"
            ) from exc

        retrieved = self._convert_results(results)

        logger.success(
            f"Retrieved {len(retrieved)} document(s)."
        )

        return retrieved

    def _convert_results(
        self,
        results: dict[str, Any],
    ) -> list[RetrievedDocument]:
        """
        Convert raw ChromaDB output into RetrievedDocument objects.
        """

        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        retrieved: list[RetrievedDocument] = []

        for doc_id, content, metadata, distance in zip(
            ids,
            documents,
            metadatas,
            distances,
        ):

            similarity = max(
                0.0,
                1.0 - float(distance),
            )

            retrieved.append(
                RetrievedDocument(
                    id=doc_id,
                    content=content,
                    metadata=metadata or {},
                    similarity_score=similarity,
                )
            )

        return retrieved

# ==========================================================
# Collection Utilities
# ==========================================================

    def count(self) -> int:
        """
        Return the number of stored documents.
        """

        collection = self._get_collection()

        try:

            return collection.count()

        except Exception as exc:

            raise DatabaseError(
                f"Unable to count documents: {exc}"
            ) from exc


    def peek(
        self,
        limit: int = DEFAULT_PEEK_RESULTS,
    ) -> dict[str, Any]:
        """
        Preview stored documents.
        """

        collection = self._get_collection()

        try:

            return collection.peek(limit=limit)

        except Exception as exc:

            raise DatabaseError(
                f"Unable to peek collection: {exc}"
            ) from exc


    @log_execution_time("Reset Collection")
    def reset_collection(self) -> None:
        """
        Delete and recreate the collection.

        Intended for development/testing.
        """

        client = self._initialize_client()

        logger.warning(
            f"Resetting '{CHROMA_COLLECTION_NAME}'."
        )

        try:

            client.delete_collection(
                CHROMA_COLLECTION_NAME
            )

        except Exception:
            pass

        self._collection = None

        self._get_collection()

        logger.success(
            "Collection reset completed."
        )

    