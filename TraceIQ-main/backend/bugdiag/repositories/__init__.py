"""Repositories registry for BugDiag.
"""

from bugdiag.repositories.submission_repo import SubmissionRepository
from bugdiag.repositories.knowledge_repo import KnowledgeRepository
from bugdiag.repositories.diagnosis_repo import DiagnosisRepository

__all__ = [
    "SubmissionRepository",
    "KnowledgeRepository",
    "DiagnosisRepository"
]
