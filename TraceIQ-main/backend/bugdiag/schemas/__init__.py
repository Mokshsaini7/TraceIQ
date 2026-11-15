"""Schemas registry for BugDiag.
"""

from bugdiag.schemas.submission import (
    BugSubmissionCreate,
    BugSubmissionResponse,
    BugSubmissionListResponse,
    BugAttachmentResponse
)
from bugdiag.schemas.knowledge_base import (
    DatasetCreate,
    DatasetResponse,
    IngestionJobResponse,
    HistoricalDefectResponse,
    DefectChunkResponse,
    KnowledgeBaseStatsResponse
)
from bugdiag.schemas.agent import (
    TriageResult,
    LogAnalysisResult,
    RootCauseResult,
    DuplicateDetectionResult,
    RemediationResult,
    FixRecommendation,
    HistoricalMatchReference
)
from bugdiag.schemas.diagnosis import (
    DiagnosisReportResponse,
    DiagnosisTriggerRequest,
    AgentExecutionLogResponse
)
from bugdiag.schemas.retrieval import (
    SearchQueryRequest,
    SearchResultItem,
    SearchResponse,
    EvaluationMetricsResponse
)

__all__ = [
    "BugSubmissionCreate",
    "BugSubmissionResponse",
    "BugSubmissionListResponse",
    "BugAttachmentResponse",
    "DatasetCreate",
    "DatasetResponse",
    "IngestionJobResponse",
    "HistoricalDefectResponse",
    "DefectChunkResponse",
    "KnowledgeBaseStatsResponse",
    "TriageResult",
    "LogAnalysisResult",
    "RootCauseResult",
    "DuplicateDetectionResult",
    "RemediationResult",
    "FixRecommendation",
    "HistoricalMatchReference",
    "DiagnosisReportResponse",
    "DiagnosisTriggerRequest",
    "AgentExecutionLogResponse",
    "SearchQueryRequest",
    "SearchResultItem",
    "SearchResponse",
    "EvaluationMetricsResponse"
]
