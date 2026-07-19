"""
Integration tests for knowledge ingestion.
"""

from src.services.database import ChromaDBService
from src.services.ingest import KnowledgeIngestionService


def test_ingestion_pipeline() -> None:
    """
    Verify that the dataset can be ingested.
    """

    ingestion = KnowledgeIngestionService()

    summary = ingestion.ingest(
        reset_database=True,
    )

    db = ChromaDBService()

    assert summary.total_records > 0

    assert summary.stored_records == summary.total_records

    assert db.count() == summary.total_records