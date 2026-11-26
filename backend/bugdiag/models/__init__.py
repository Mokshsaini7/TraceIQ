"""ORM Models registry for BugDiag.
"""

from bugdiag.models.base import Base, VectorType, TimestampMixin
from bugdiag.models.submission import BugSubmission, BugAttachment
from bugdiag.models.knowledge_base import (
    Dataset,
    IngestionJob,
    HistoricalDefect,
    DefectChunk,
    EmbeddingRecord
)
from bugdiag.models.diagnosis import DiagnosisReport, AgentExecutionLog

__all__ = [
    "Base",
    "VectorType",
    "TimestampMixin",
    "BugSubmission",
    "BugAttachment",
    "Dataset",
    "IngestionJob",
    "HistoricalDefect",
    "DefectChunk",
    "EmbeddingRecord",
    "DiagnosisReport",
    "AgentExecutionLog"
]
