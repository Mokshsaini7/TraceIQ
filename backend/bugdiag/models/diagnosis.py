"""SQLAlchemy models for diagnosis reports and agent execution logs.
"""

import uuid
from sqlalchemy import Column, String, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from bugdiag.database.session import Base
from bugdiag.models.base import TimestampMixin

class DiagnosisReport(Base, TimestampMixin):
    __tablename__ = "diagnosis_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id = Column(String(36), ForeignKey("bug_submissions.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # 5-Agent Outputs
    triage_result = Column(JSON, nullable=True)
    log_analysis_result = Column(JSON, nullable=True)
    root_cause_result = Column(JSON, nullable=True)
    duplicate_detection_result = Column(JSON, nullable=True)
    remediation_result = Column(JSON, nullable=True)
    
    overall_confidence = Column(Float, default=0.0, nullable=False)
    status = Column(String(32), default="processing", nullable=False, index=True)  # processing, completed, failed
    error_message = Column(Text, nullable=True)

    # Relationships
    submission = relationship("BugSubmission", back_populates="diagnosis_report")

class AgentExecutionLog(Base, TimestampMixin):
    __tablename__ = "agent_execution_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id = Column(String(36), ForeignKey("bug_submissions.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String(64), nullable=False, index=True)
    status = Column(String(32), default="started", nullable=False, index=True)  # started, completed, failed
    input_payload = Column(JSON, nullable=True)
    output_payload = Column(JSON, nullable=True)
    execution_time_ms = Column(Float, default=0.0, nullable=False)
    error_message = Column(Text, nullable=True)

    # Relationships
    submission = relationship("BugSubmission", back_populates="execution_logs")
