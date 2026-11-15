"""SQLAlchemy models for datasets, ingestion jobs, historical defects, chunks, and embeddings.
"""

import uuid
from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from bugdiag.database.session import Base
from bugdiag.models.base import TimestampMixin, VectorType

class Dataset(Base, TimestampMixin):
    __tablename__ = "datasets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(128), nullable=False, index=True)
    source = Column(String(64), nullable=False, index=True)  # Mozilla, Apache, Eclipse, Kaggle, etc.
    description = Column(Text, nullable=True)
    file_path = Column(String(512), nullable=False)
    format = Column(String(16), nullable=False)  # csv, json
    column_mapping = Column(JSON, nullable=True)
    total_records = Column(Integer, default=0, nullable=False)
    status = Column(String(32), default="uploaded", nullable=False, index=True)  # uploaded, processing, completed, failed

    # Relationships
    ingestion_jobs = relationship("IngestionJob", back_populates="dataset", cascade="all, delete-orphan")
    defects = relationship("HistoricalDefect", back_populates="dataset", cascade="all, delete-orphan")

class IngestionJob(Base, TimestampMixin):
    __tablename__ = "ingestion_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    total_records = Column(Integer, default=0, nullable=False)
    processed_records = Column(Integer, default=0, nullable=False)
    failed_records = Column(Integer, default=0, nullable=False)
    status = Column(String(32), default="pending", nullable=False, index=True)  # pending, running, completed, failed
    error_message = Column(Text, nullable=True)

    # Relationships
    dataset = relationship("Dataset", back_populates="ingestion_jobs")

class HistoricalDefect(Base, TimestampMixin):
    __tablename__ = "historical_defects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String(36), ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True, index=True)
    source_repo = Column(String(64), nullable=False, index=True)
    original_issue_id = Column(String(64), nullable=False, index=True)
    title = Column(String(512), nullable=False, index=True)
    description = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    comments = Column(Text, nullable=True)
    resolution = Column(String(64), nullable=True, index=True)
    status = Column(String(64), nullable=True, index=True)
    programming_language = Column(String(64), nullable=True, index=True)
    source_url = Column(String(512), nullable=True)
    content_hash = Column(String(64), nullable=False, index=True)  # SHA-256 for exact deduplication
    original_created_at = Column(DateTime(timezone=True), nullable=True)
    original_updated_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    dataset = relationship("Dataset", back_populates="defects")
    chunks = relationship("DefectChunk", back_populates="defect", cascade="all, delete-orphan")

class DefectChunk(Base, TimestampMixin):
    __tablename__ = "defect_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    defect_id = Column(String(36), ForeignKey("historical_defects.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    chunk_type = Column(String(32), default="mixed", nullable=False)  # summary, stack_trace, resolution, mixed
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0, nullable=False)

    # Relationships
    defect = relationship("HistoricalDefect", back_populates="chunks")
    embedding = relationship("EmbeddingRecord", back_populates="chunk", uselist=False, cascade="all, delete-orphan")

class EmbeddingRecord(Base, TimestampMixin):
    __tablename__ = "embeddings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chunk_id = Column(String(36), ForeignKey("defect_chunks.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    model_name = Column(String(128), default="all-MiniLM-L6-v2", nullable=False, index=True)
    dimension = Column(Integer, default=384, nullable=False)
    vector = Column(VectorType(dimension=384), nullable=False)

    # Relationships
    chunk = relationship("DefectChunk", back_populates="embedding")
