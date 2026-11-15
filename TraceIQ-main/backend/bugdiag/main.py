"""BugDiag FastAPI Application Entrypoint.
Production-minded, asynchronous, modular backend for defect diagnosis.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

from bugdiag.core.config import get_settings
from bugdiag.core.logging import setup_logging, get_logger
from bugdiag.database.session import init_db, SessionLocal
from bugdiag.services.knowledge_service import KnowledgeService
from bugdiag.api.routes import (
    health_router,
    submissions_router,
    diagnosis_router,
    knowledge_router,
    search_router,
    system_router,
    stats_router
)

setup_logging()
logger = get_logger("main")
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB tables & seed initial sample knowledge base if empty
    logger.info("Initializing BugDiag database schema...")
    try:
        init_db()
        db = SessionLocal()
        try:
            k_service = KnowledgeService(db)
            stats = k_service.get_stats()
            if stats["total_defects"] == 0:
                logger.info("Knowledge base is empty. Auto-ingesting authentic benchmark datasets...")
                raw_dir = Path(settings.DATASETS_DIR) if settings.DATASETS_DIR else Path(__file__).resolve().parent.parent.parent / "datasets" / "raw"
                defaults = [
                    ("Mozilla Defect Repository Sample", "Mozilla", raw_dir / "mozilla_defects_sample.json", "json"),
                    ("Apache Project Defect Benchmark", "Apache", raw_dir / "apache_defects_sample.csv", "csv"),
                    ("Eclipse Platform Defect Archive", "Eclipse", raw_dir / "eclipse_defects_sample.json", "json")
                ]
                for name, src, path, fmt in defaults:
                    if path.is_file():
                        logger.info(f"Auto-ingesting {name} from {path}...")
                        k_service.import_local_path(
                            name=name,
                            source=src,
                            file_path=str(path),
                            format_type=fmt
                        )
                logger.info("Auto-ingestion of default benchmark datasets completed successfully.")
        finally:
            db.close()
    except Exception as e:
        logger.exception("Application startup initialization failed.")
        # In production, starting without a working persistent database can make
        # writes fail or hide an operational outage behind a healthy web process.
        if settings.APP_ENV.lower() in {"production", "prod"}:
            raise

    yield

    # Shutdown
    logger.info("Shutting down BugDiag backend...")

app = FastAPI(
    title=settings.APP_NAME,
    description="TraceIQ — Intelligent Bug Diagnosis and Fix Recommendation Platform",
    version="0.2.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers under API V1 prefix
api_prefix = settings.API_V1_PREFIX
app.include_router(health_router, prefix=api_prefix)
app.include_router(submissions_router, prefix=api_prefix)
app.include_router(diagnosis_router, prefix=api_prefix)
app.include_router(knowledge_router, prefix=api_prefix)
app.include_router(search_router, prefix=api_prefix)
app.include_router(system_router, prefix=api_prefix)
app.include_router(stats_router, prefix=api_prefix)

@app.get("/")
def root():
    return {
        "message": "Welcome to TraceIQ API — Intelligent Bug Diagnosis Platform",
        "milestone": "Milestone 1 — Foundation & Bug Understanding",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health"
    }
