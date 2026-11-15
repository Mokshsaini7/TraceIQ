"""Schemas for Diagnosis reports and orchestration execution logs.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from bugdiag.schemas.agent import (
    TriageResult,
    LogAnalysisResult,
    RootCauseResult,
    DuplicateDetectionResult,
    RemediationResult
)

class DiagnosisReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    submission_id: str
    triage_result: Optional[TriageResult] = None
    log_analysis_result: Optional[LogAnalysisResult] = None
    root_cause_result: Optional[RootCauseResult] = None
    duplicate_detection_result: Optional[DuplicateDetectionResult] = None
    remediation_result: Optional[RemediationResult] = None
    overall_confidence: float = 0.0
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class DiagnosisTriggerRequest(BaseModel):
    submission_id: str
    force_reanalysis: bool = False

class AgentExecutionLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    submission_id: str
    agent_name: str
    status: str
    input_payload: Optional[Dict[str, Any]] = None
    output_payload: Optional[Dict[str, Any]] = None
    execution_time_ms: float
    error_message: Optional[str] = None
    created_at: datetime
