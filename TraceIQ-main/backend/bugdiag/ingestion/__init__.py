"""Ingestion module initialization.
"""

from bugdiag.ingestion.cleaner import clean_text, normalize_stack_trace, compute_content_hash
from bugdiag.ingestion.chunker import DefectChunker
from bugdiag.ingestion.pipeline import IngestionPipeline

__all__ = [
    "clean_text",
    "normalize_stack_trace",
    "compute_content_hash",
    "DefectChunker",
    "IngestionPipeline"
]
