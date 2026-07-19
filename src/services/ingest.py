"""
Knowledge base ingestion pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.constants import EMBEDDING_BATCH_SIZE
from src.logger import logger, log_execution_time
from src.models import SportsKnowledge
from src.services.database import ChromaDBService
from src.services.embeddings import EmbeddingService
from src.services.validator import DatasetValidator
from src.config import DATA_DIR



# ==========================================================
# Ingestion Summary
# ==========================================================


@dataclass(slots=True)
class IngestionSummary:
    """Summary of an ingestion run."""

    total_records: int
    stored_records: int
    skipped_records: int


# ==========================================================
# Knowledge Ingestion Service
# ==========================================================


class KnowledgeIngestionService:
    """
    Loads, validates, embeds, and stores
    sports knowledge into ChromaDB.
    """

    def __init__(self) -> None:
        self.validator = DatasetValidator()
        self.embedding_service = EmbeddingService()
        self.database = ChromaDBService()

    # ======================================================
    # Public API
    # ======================================================

    @log_execution_time("Knowledge Ingestion")
    def ingest(
        self,
        *,
        reset_database: bool = False,
    ) -> IngestionSummary:
        """
        Build the vector database.

        Parameters
        ----------
        reset_database:
            Whether to recreate the collection.

        Returns
        -------
        IngestionSummary
        """

        if reset_database:
            logger.warning("Resetting existing database...")
            self.database.reset_collection()

        logger.info("Loading and validating dataset...")

        records = self._load_records()

        logger.success(
            f"Loaded {len(records)} validated record(s)."
        )

        total = len(records)

        if total == 0:
            return IngestionSummary(
                total_records=0,
                stored_records=0,
                skipped_records=0,
            )

        stored = 0

        for batch in self._split_batches(records):

            self._store_batch(batch)

            stored += len(batch)

        logger.success(
            f"Ingestion complete. Stored {stored} documents."
        )

        return IngestionSummary(
            total_records=total,
            stored_records=stored,
            skipped_records=total - stored,
        )

    # ======================================================
    # Internal Helpers
    # ======================================================

    def _load_records(
        self,
    ) -> list[SportsKnowledge]:
        """
        Load and validate dataset.
        """

        return self.validator.load_and_validate(DATA_DIR)
    
    def _build_document(
        self,
        record: SportsKnowledge,
    ) -> str:
        """
        Build searchable text for embeddings.
        """

        keywords = ", ".join(record.keywords)

        question_types = ", ".join(
            record.question_types
        )

        difficulties = ", ".join(
            record.difficulty
        )

        return f"""
Sport: {record.sport}

Topic: {record.topic}

Title: {record.title}

Content:
{record.content}

Keywords:
{keywords}

Question Types:
{question_types}

Difficulty:
{difficulties}
""".strip()

    def _build_metadata(
        self,
        record: SportsKnowledge,
    ) -> dict[str, Any]:
        """
        Convert record metadata into
        Chroma-compatible metadata.
        """

        return {
            "id": record.id,
            "sport": record.sport,
            "topic": record.topic,
            "title": record.title,
            "difficulty": ",".join(record.difficulty),
            "keywords": ",".join(record.keywords),
            "question_types": ",".join(
                record.question_types
            ),
            "version": record.version,
            "last_updated": str(
                record.last_updated
            ),
            "source_name": record.source.name,
            "source_type": record.source.type,
            "verified": str(
                record.source.verified
            ),
        }

    def _store_batch(
        self,
        records: list[SportsKnowledge],
    ) -> None:
        """
        Generate embeddings and store one batch.
        """

        ids = [record.id for record in records]

        documents = [
            self._build_document(record)
            for record in records
        ]

        metadatas = [
            self._build_metadata(record)
            for record in records
        ]

        embeddings = (
            self.embedding_service.embed_batch(
                documents
            )
        )

        self.database.add_documents(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        logger.info(
            f"Stored batch of {len(records)} document(s)."
        )

    def _split_batches(
        self,
        records: list[SportsKnowledge],
    ):
        """
        Yield batches of records.
        """

        for start in range(
            0,
            len(records),
            EMBEDDING_BATCH_SIZE,
        ):
            yield records[
                start : start + EMBEDDING_BATCH_SIZE
            ]