"""Strict schemas for the 5-Agent Architecture in BugDiag.
"""

from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

class TriageReasoning(BaseModel):
    severity_reason: str = "Assessment reason was not provided by this legacy result."
    priority_reason: str = "Assessment reason was not provided by this legacy result."
    component_reason: str = "Component evidence was not available in this legacy result."
    evidence: List[str] = Field(default_factory=list)


class TriageResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: str = Field(..., description="Evidence-based bug category")
    severity: Literal["critical", "high", "medium", "low"]
    priority: Literal["p1", "p2", "p3", "p4"]
    affected_component: str = Field("Unknown", description="Most likely affected module, or Unknown")
    programming_language: str
    framework: Optional[str] = None
    confidence_score: float = Field(0.0, ge=0.0, le=1.0)
    reasoning: TriageReasoning = Field(default_factory=TriageReasoning)
    missing_information: List[str] = Field(default_factory=list)
    completeness_score: float = Field(..., ge=0.0, le=1.0)

class StackFrameInfo(BaseModel):
    file: str
    line: Optional[int] = None
    function: Optional[str] = None
    class_name: Optional[str] = None
    code_context: Optional[str] = None


class FailurePoint(BaseModel):
    file: Optional[str] = None
    class_name: Optional[str] = None
    method: Optional[str] = None
    line: Optional[int] = None


class LogAnalysisResult(BaseModel):
    """Stable, machine-readable forensic result emitted by LogAnalysisAgent."""
    has_stack_trace: bool
    detected_format: str = "unknown"
    frame_count: int = Field(0, ge=0)
    analysis_summary: Optional[str] = None
    exception_type: Optional[str] = None
    error_message: Optional[str] = None
    stack_frames: List[StackFrameInfo] = Field(default_factory=list)
    suspect_files: List[str] = Field(default_factory=list)
    technical_evidence: List[str] = Field(default_factory=list)
    failure_point: Optional[FailurePoint] = None
    code_path: List[StackFrameInfo] = Field(default_factory=list)
    confidence_score: float = Field(0.0, ge=0.0, le=1.0)

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
