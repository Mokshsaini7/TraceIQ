"""Pydantic schemas for semantic search, BM25 keyword matching, hybrid RRF, and evaluation metrics.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class SearchQueryRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Search query string")
    method: str = Field("hybrid", description="semantic | bm25 | hybrid")
    top_k: int = Field(5, ge=1, le=25, description="Number of results to return")
    source_filter: Optional[str] = Field(None, description="Filter by source repo (Mozilla, Apache, Eclipse, etc.)")
    language_filter: Optional[str] = Field(None, description="Filter by programming language")

class SearchResultItem(BaseModel):
    defect_id: str
    original_issue_id: str
    source_repo: str
    title: str
    description: str
    stack_trace: Optional[str] = None
    resolution: Optional[str] = None
    status: Optional[str] = None
    programming_language: Optional[str] = None
    similarity_score: float
    source_url: Optional[str] = None
    retrieval_method: str
    matched_chunk: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    method: str
    total_results: int
    execution_time_ms: float
    results: List[SearchResultItem]

class EvaluationMetricsResponse(BaseModel):
    dataset_name: str
    sample_queries_evaluated: int
    precision_at_k: Dict[str, float]
    recall_at_k: Dict[str, float]
    mrr: float
    comparison_by_method: Dict[str, Dict[str, float]]
    timestamp: str
