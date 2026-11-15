"""Strict schemas for the 5-Agent Architecture in BugDiag.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class TriageResult(BaseModel):
    category: str = Field(..., description="Bug classification category, e.g. Memory, Concurrency, NullPointer, Network")
    severity: str = Field(..., description="Assessed severity level")
    priority: str = Field(..., description="Assessed priority level")
    programming_language: str = Field(..., description="Detected programming language")
    framework: Optional[str] = Field(None, description="Detected or confirmed framework")
    missing_information: List[str] = Field(default_factory=list, description="List of missing fields or reproduction details")
    completeness_score: float = Field(..., ge=0.0, le=1.0, description="Completeness score from 0.0 to 1.0")

class StackFrameInfo(BaseModel):
    file: str
    line: Optional[int] = None
    function: Optional[str] = None
    code_context: Optional[str] = None

class LogAnalysisResult(BaseModel):
    has_stack_trace: bool
    exception_type: Optional[str] = None
    error_message: Optional[str] = None
    stack_frames: List[StackFrameInfo] = Field(default_factory=list)
    suspect_files: List[str] = Field(default_factory=list)
    technical_evidence: List[str] = Field(default_factory=list)

class HistoricalMatchReference(BaseModel):
    defect_id: str
    source_repo: str
    original_issue_id: str
    title: str
    similarity_score: float
    resolution: Optional[str] = None
    url: Optional[str] = None

class RootCauseResult(BaseModel):
    identified_root_cause: str
    explanation: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    supporting_evidence: List[str] = Field(default_factory=list)
    historical_matches: List[HistoricalMatchReference] = Field(default_factory=list)

class DuplicateMatch(BaseModel):
    defect_id: str
    source_repo: str
    original_issue_id: str
    title: str
    similarity_score: float
    retrieval_method: str  # semantic | bm25 | hybrid_rrf

class DuplicateDetectionResult(BaseModel):
    is_duplicate: bool
    highest_similarity: float
    potential_duplicates: List[DuplicateMatch] = Field(default_factory=list)

class FixRecommendation(BaseModel):
    title: str
    description: str
    diff_snippet: Optional[str] = None
    is_verified_from_history: bool = False
    source_defect_id: Optional[str] = None

class RemediationResult(BaseModel):
    verified_fixes: List[FixRecommendation] = Field(default_factory=list)
    suggested_fixes: List[FixRecommendation] = Field(default_factory=list)
    rationale: str
    historical_references: List[HistoricalMatchReference] = Field(default_factory=list)
