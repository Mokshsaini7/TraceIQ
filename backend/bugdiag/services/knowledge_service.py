"""Service coordinating knowledge base dataset imports and statistics.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from fastapi import UploadFile
from sqlalchemy.orm import Session
from bugdiag.models.knowledge_base import Dataset, IngestionJob
from bugdiag.schemas.knowledge_base import DatasetCreate
from bugdiag.repositories.knowledge_repo import KnowledgeRepository
from bugdiag.file_processing.sanitizer import FileProcessingService
from bugdiag.ingestion.pipeline import IngestionPipeline
from bugdiag.core.logging import get_logger

logger = get_logger("services.knowledge")

class KnowledgeService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = KnowledgeRepository(db)
        self.file_service = FileProcessingService()

    async def register_dataset_file(self, file: UploadFile, metadata: DatasetCreate) -> Dataset:
        filename, file_path, file_size, file_hash = await self.file_service.save_upload_file(file)
        fmt = Path(filename).suffix.lstrip(".").lower()
        if fmt not in ["json", "csv"]:
            fmt = "json"

        dataset = Dataset(
            name=metadata.name,
            source=metadata.source,
            description=metadata.description,
            file_path=file_path,
            format=fmt,
            column_mapping=metadata.column_mapping,
            status="uploaded"
        )
        created = self.repo.create_dataset(dataset)

        # Trigger ingestion synchronously or via runner
        pipeline = IngestionPipeline(self.db)
        pipeline.run_ingestion(created.id)

        return self.repo.get_dataset_by_id(created.id)

    def import_local_path(
        self,
        name: str,
        source: str,
        file_path: str,
        format_type: str,
        description: Optional[str] = None,
        column_mapping: Optional[dict] = None
    ) -> Dataset:
        dataset = Dataset(
            name=name,
            source=source,
            description=description,
            file_path=file_path,
            format=format_type,
            column_mapping=column_mapping,
            status="uploaded"
        )
        created = self.repo.create_dataset(dataset)
        pipeline = IngestionPipeline(self.db)
        pipeline.run_ingestion(created.id)
        return self.repo.get_dataset_by_id(created.id)

    def get_stats(self) -> Dict[str, Any]:
        return self.repo.get_stats()

    def list_datasets(self, page: int = 1, page_size: int = 20) -> Tuple[int, List[Dataset]]:
        skip = (page - 1) * page_size
        return self.repo.list_datasets(skip=skip, limit=page_size)

    def list_ingestion_jobs(self, dataset_id: Optional[str] = None) -> List[IngestionJob]:
        return self.repo.list_ingestion_jobs(dataset_id=dataset_id)
