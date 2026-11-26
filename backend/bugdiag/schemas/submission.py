"""Pydantic schemas for bug submissions and attachments.
"""

from datetime import datetime
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class BugAttachmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    submission_id: str
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    content_type: str
    file_hash: str
    created_at: datetime

class BugSubmissionCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=255, description="Brief summary of the bug")
    description: str = Field(..., min_length=10, description="Detailed problem statement and behavior")
    stack_trace: Optional[str] = Field(None, description="Raw stack trace or exception output")
    error_logs: Optional[str] = Field(None, description="Relevant application or console logs")
    programming_language: Optional[str] = Field(None, description="Primary language, e.g. Python, Java, C++")
    framework: Optional[str] = Field(None, description="Framework, e.g. FastAPI, Spring, React")
    environment_info: Optional[str] = Field(None, description="OS, architecture, runtime versions")
    severity: Literal["critical", "high", "medium", "low"] = Field("medium", description="Reporter-suggested severity; agent independently reassesses")
    priority: Literal["p1", "p2", "p3", "p4"] = Field("p3", description="Reporter-suggested priority; agent independently reassesses")
    reproduction_steps: Optional[str] = Field(None, description="Step-by-step reproduction instructions")
    expected_behavior: Optional[str] = Field(None, description="What was expected to happen")
    actual_behavior: Optional[str] = Field(None, description="What actually happened")


class BugAnalysisContextResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    schema_version: str
    orchestration_status: str
    triage_status: str
    log_analysis_status: str
    triage_output: Optional[Dict[str, Any]] = None
    log_analysis_output: Optional[Dict[str, Any]] = None
    combined_context: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)

class BugSubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    stack_trace: Optional[str]
    error_logs: Optional[str]
    programming_language: Optional[str]
    framework: Optional[str]
    environment_info: Optional[str]
    severity: str
    priority: str
    reproduction_steps: Optional[str]
    expected_behavior: Optional[str]
    actual_behavior: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    attachments: List[BugAttachmentResponse] = []
    analysis_context: Optional[BugAnalysisContextResponse] = None

class BugSubmissionListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[BugSubmissionResponse]
