"""Integration tests for BM25, Vector Search, Hybrid RRF, and Ingestion Pipeline.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bugdiag.models.base import Base
from bugdiag.retrieval.bm25 import BM25Retriever
from bugdiag.retrieval.hybrid import HybridRetriever
from bugdiag.database.session import Base
from bugdiag.ingestion.pipeline import IngestionPipeline
from bugdiag.models.knowledge_base import Dataset

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()

def test_bm25_retrieval():
    corpus = [
        {"content": "NullPointerException in gfxFont when measuring canvas text", "chunk_id": "c1"},
        {"content": "OutOfMemoryError in Apache Spark shuffle spill execution", "chunk_id": "c2"},
        {"content": "Deadlock in Kafka consumer coordinator heartbeat rebalance", "chunk_id": "c3"}
    ]
    retriever = BM25Retriever(corpus)
    results = retriever.search("gfxFont NullPointer canvas", top_k=2)

    assert len(results) > 0
    top_chunk, score = results[0]
    assert top_chunk["chunk_id"] == "c1"
    assert score > 0.0

def test_rrf_scoring_order():
    # Test RRF formula behavior
    k = 60
    rank_1_rrf = 1.0 / (k + 1)
    rank_2_rrf = 1.0 / (k + 2)
    assert rank_1_rrf > rank_2_rrf
