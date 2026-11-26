"""Knowledge Base dataset management, import, and statistics endpoints.
"""

import os
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from bugdiag.database.session import get_db
from bugdiag.schemas.knowledge_base import (
    DatasetResponse,
    IngestionJobResponse,
    KnowledgeBaseStatsResponse,
    DatasetCreate
)
from bugdiag.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge-base", tags=["Knowledge Base"])

@router.get("/stats", response_model=KnowledgeBaseStatsResponse)
def get_knowledge_base_stats(db: Session = Depends(get_db)):
    service = KnowledgeService(db)
    return service.get_stats()

@router.get("/datasets", response_model=List[DatasetResponse])
def list_datasets(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1),
    db: Session = Depends(get_db)
):
    service = KnowledgeService(db)
    total, items = service.list_datasets(page=page, page_size=page_size)
    return items

@router.post("/datasets", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    name: str = Form(...),
    source: str = Form(...),
    description: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    service = KnowledgeService(db)
    metadata = DatasetCreate(
        name=name,
        source=source,
        description=description
    )
    dataset = await service.register_dataset_file(file, metadata)
    return dataset

@router.post("/import-default")
def import_default_datasets(db: Session = Depends(get_db)):
    """Imports default authentic historical defect datasets from Mozilla, Apache, and Eclipse."""
    service = KnowledgeService(db)
    # Check project datasets directory
    from bugdiag.core.config import get_settings
    _s = get_settings()
    raw_dir = Path(_s.DATASETS_DIR) if _s.DATASETS_DIR else Path(__file__).resolve().parents[4] / "datasets" / "raw"

    imported = []
    defaults = [
        ("Mozilla Defect Repository Sample", "Mozilla", raw_dir / "mozilla_defects_sample.json", "json", "Authentic Bugzilla crash and rendering defect records"),
        ("Apache Project Defect Benchmark", "Apache", raw_dir / "apache_defects_sample.csv", "csv", "Authentic Jira defects from Spark, Lucene, Kafka, Hadoop"),
        ("Eclipse Platform Defect Archive", "Eclipse", raw_dir / "eclipse_defects_sample.json", "json", "Authentic Eclipse Bugzilla JDT and SWT defect reports")
    ]

    for name, src, path, fmt, desc in defaults:
        if path.is_file():
            ds = service.import_local_path(
                name=name,
                source=src,
                file_path=str(path),
                format_type=fmt,
                description=desc
            )
            imported.append(ds.name)

    stats = service.get_stats()
    return {
        "message": f"Successfully imported {len(imported)} benchmark datasets into knowledge base.",
        "imported_datasets": imported,
        "current_stats": stats
    }

@router.get("/jobs", response_model=List[IngestionJobResponse])
def list_ingestion_jobs(
    dataset_id: str = Query(None),
    db: Session = Depends(get_db)
):
    service = KnowledgeService(db)
    return service.list_ingestion_jobs(dataset_id=dataset_id)
