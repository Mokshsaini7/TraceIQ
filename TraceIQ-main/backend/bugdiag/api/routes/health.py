"""Health and readiness checks with honest dependency status."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from bugdiag.database.session import get_db
from bugdiag.core.config import get_settings
from bugdiag.embeddings.factory import get_embedding_model

router = APIRouter(prefix="/health", tags=["Health & System"])

@router.get("")
def health_check(db: Session = Depends(get_db)):
    settings = get_settings()
    db_status, db_dialect, db_error = "healthy", "unknown", None
    try:
        bind = db.get_bind()
        with bind.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_dialect = bind.dialect.name
    except Exception as exc:
        db_status, db_error = "unhealthy", str(exc)[:300]

    configured_dialect = "postgresql" if settings.DATABASE_URL.startswith(("postgresql", "postgres")) else "sqlite" if settings.DATABASE_URL.startswith("sqlite") else "other"
    if db_status == "healthy" and db_dialect != configured_dialect:
        db_status = "degraded"
        db_error = f"Configured database is {configured_dialect}, but the application is using {db_dialect} (fallback)."

    embedding_status = "not_checked"
    embedding_mode = "unknown"
    embedding_reason = None
    try:
        model = get_embedding_model()
        if getattr(model, "using_fallback", False):
            embedding_status = "degraded"
            embedding_mode = "deterministic_hash_fallback (not semantic)"
            embedding_reason = getattr(model, "fallback_reason", None)
        else:
            embedding_status = "healthy"
            embedding_mode = "sentence_transformers"
    except Exception as exc:
        embedding_status, embedding_reason = "unhealthy", str(exc)[:300]

    overall = "healthy" if db_status == "healthy" and embedding_status == "healthy" else "degraded"
    return {
        "status": overall, "app_name": settings.APP_NAME, "environment": settings.APP_ENV,
        "database": {"status": db_status, "configured_dialect": configured_dialect, "dialect": db_dialect, "error": db_error},
        "embeddings": {"status": embedding_status, "mode": embedding_mode,
                       "model_name": getattr(locals().get("model", None), "model_name", settings.EMBEDDING_MODEL),
                       "dimension": getattr(locals().get("model", None), "dimension", settings.EMBEDDING_DIMENSION),
                       "fallback_reason": embedding_reason},
        "llm_enabled": bool(settings.ANTHROPIC_API_KEY), "version": "0.2.0"
    }
