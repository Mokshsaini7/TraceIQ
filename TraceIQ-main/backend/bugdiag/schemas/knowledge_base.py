"""Pydantic schemas for datasets, historical defects, chunks, and knowledge base stats.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

class DatasetCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=128)
    source: str = Field(..., min_length=2, max_length=64, description="Mozilla | Apache | Eclipse | Kaggle | Custom")
    description: Optional[str] = None
    column_mapping: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional mapping of source dataset headers to BugDiag fields"
    )

class DatasetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    source: str
    description: Optional[str]
    file_path: str
    format: str
    column_mapping: Optional[Dict[str, Any]]
    total_records: int
    status: str
    created_at: datetime
    updated_at: datetime

class IngestionJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dataset_id: str
    total_records: int
    processed_records: int
    failed_records: int
    status: str
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

class HistoricalDefectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source_repo: str
    original_issue_id: str
    title: str
    description: str
    stack_trace: Optional[str]
    comments: Optional[str]
    resolution: Optional[str]
    status: Optional[str]
    programming_language: Optional[str]
    source_url: Optional[str]
    original_created_at: Optional[datetime]
    original_updated_at: Optional[datetime]

class DefectChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    defect_id: str
    chunk_index: int
    chunk_type: str
    content: str
    token_count: int

class KnowledgeBaseStatsResponse(BaseModel):
    total_datasets: int
    total_defects: int
    total_chunks: int
    total_embeddings: int
    by_source: Dict[str, int]
    by_language: Dict[str, int]
    vector_index_status: str
    bm25_index_status: str
