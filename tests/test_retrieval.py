"""
Integration tests for semantic retrieval.
"""

from src.services.retrieval import RetrievalService


def test_retrieve_documents() -> None:
    """
    Verify semantic retrieval.
    """

    retrieval = RetrievalService()

    docs = retrieval.retrieve(
        query="Virat Kohli batting",
        sport="Cricket",
        top_k=3,
    )

    assert len(docs) > 0

    assert docs[0].content

    assert docs[0].similarity_score >= 0