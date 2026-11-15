"""Base models, common mixins, and custom vector types for BugDiag.
"""

import json
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import DateTime, Column, TypeDecorator, Text
from bugdiag.database.session import Base

try:
    from pgvector.sqlalchemy import Vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False

class VectorType(TypeDecorator):
    """Platform-resilient vector column type.
    Uses pgvector's Vector type when running on PostgreSQL with pgvector,
    and falls back to JSON-serialized float list on SQLite.
    """
    impl = Text
    cache_ok = True

    def __init__(self, dimension: int = 384, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dimension = dimension

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql" and HAS_PGVECTOR:
            return dialect.type_descriptor(Vector(self.dimension))
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value: Optional[List[float]], dialect):
        if value is None:
            return None
        if dialect.name == "postgresql" and HAS_PGVECTOR:
            return value
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, list):
            return value
        try:
            return json.loads(value)
        except Exception:
            return []

def get_utc_now():
    return datetime.now(timezone.utc)

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)
