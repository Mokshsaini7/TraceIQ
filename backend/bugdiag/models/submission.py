"""SQLAlchemy models for bug submissions and uploaded attachments.
"""

import uuid
from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from bugdiag.database.session import Base
from bugdiag.models.base import TimestampMixin

class BugSubmission(Base, TimestampMixin):
    __tablename__ = "bug_submissions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    error_logs = Column(Text, nullable=True)
    programming_language = Column(String(64), nullable=True, index=True)
    framework = Column(String(64), nullable=True, index=True)
    environment_info = Column(Text, nullable=True)
    severity = Column(String(32), default="medium", nullable=False, index=True)
    priority = Column(String(32), default="p2", nullable=False, index=True)
    reproduction_steps = Column(Text, nullable=True)
    expected_behavior = Column(Text, nullable=True)
    actual_behavior = Column(Text, nullable=True)
    status = Column(String(32), default="pending", nullable=False, index=True)

    # Relationships
    attachments = relationship("BugAttachment", back_populates="submission", cascade="all, delete-orphan")
    diagnosis_report = relationship("DiagnosisReport", back_populates="submission", uselist=False, cascade="all, delete-orphan")
    execution_logs = relationship("AgentExecutionLog", back_populates="submission", cascade="all, delete-orphan")

class BugAttachment(Base, TimestampMixin):
    __tablename__ = "bug_attachments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id = Column(String(36), ForeignKey("bug_submissions.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(128), nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)

    # Relationship
    submission = relationship("BugSubmission", back_populates="attachments")
