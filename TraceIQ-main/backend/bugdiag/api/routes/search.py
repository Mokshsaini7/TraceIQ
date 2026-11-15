"""Semantic, BM25, and Hybrid historical defect search & evaluation routes.
"""

import time
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from bugdiag.database.session import get_db
from bugdiag.schemas.retrieval import (
    SearchQueryRequest,
    SearchResponse,
    SearchResultItem,
    EvaluationMetricsResponse
)
from bugdiag.retrieval.hybrid import HybridRetriever
from bugdiag.retrieval.evaluation import RetrievalEvaluator

router = APIRouter(prefix="/search", tags=["Semantic Search & Evaluation"])

@router.post("/historical", response_model=SearchResponse)
def search_historical_defects(payload: SearchQueryRequest, db: Session = Depends(get_db)):
    retriever = HybridRetriever(db)
    t0 = time.perf_counter()

    results_data = retriever.search(
        query=payload.query,
        method=payload.method,
        top_k=payload.top_k,
        source_filter=payload.source_filter,
        language_filter=payload.language_filter
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000

    items = [SearchResultItem(**item) for item in results_data]
    return SearchResponse(
        query=payload.query,
        method=payload.method,
        total_results=len(items),
        execution_time_ms=round(elapsed_ms, 2),
        results=items
    )

@router.get("/evaluate", response_model=EvaluationMetricsResponse)
def evaluate_retrieval_performance(db: Session = Depends(get_db)):
    evaluator = RetrievalEvaluator(db)
    metrics = evaluator.evaluate_all(k_values=[1, 3, 5])
    return metrics
