"""Core configuration management for BugDiag using Pydantic Settings.
"""

from functools import lru_cache
from typing import List, Union
from typing import Annotated
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, NoDecode
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Application
    APP_NAME: str = "TraceIQ"
    APP_ENV: str = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = ""  # Reserved for a future signed-session/JWT implementation; never ship a default secret.

    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./bugdiag_local.db",
        description="SQLAlchemy Database URL. Supports PostgreSQL with pgvector and SQLite fallback."
    )

    # Embeddings & Vector
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    EMBEDDING_DEVICE: str = "cpu"
    EMBEDDING_BATCH_SIZE: int = 32

    # RAG & Retrieval
    BM25_K1: float = 1.5
    BM25_B: float = 0.75
    RRF_K: int = 60
    DEFAULT_TOP_K: int = 5
    MAX_TOP_K: int = 20
    SIMILARITY_THRESHOLD: float = 0.78

    # Seed datasets directory (override in Docker via DATASETS_DIR)
    DATASETS_DIR: str = ""

    # File Processing & Uploads
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: str = ".txt,.log,.json,.csv,.md,.py,.java,.js,.ts,.tsx,.jsx,.xml,.yaml,.yml"

    # CORS
    # Accepts a JSON list or a comma-separated string (e.g. from docker-compose)
    CORS_ORIGINS: Annotated[List[str], NoDecode] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:4173",
        "http://127.0.0.1:4173"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_cors(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                import json
                return json.loads(v)
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    # Optional LLM refinement (grounded-citation rule is always enforced)
    ANTHROPIC_API_KEY: str = ""
    LLM_MODEL: str = "claude-sonnet-4-5"
    LLM_TIMEOUT_SECONDS: float = 30.0

    @property
    def allowed_extensions_set(self) -> set[str]:
        return {ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",") if ext.strip()}

@lru_cache()
def get_settings() -> Settings:
    return Settings()
