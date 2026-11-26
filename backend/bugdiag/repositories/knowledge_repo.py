"""Repository for dataset management, historical defects, chunks, and embeddings.
"""

from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from bugdiag.models.knowledge_base import (
    Dataset,
    IngestionJob,
    HistoricalDefect,
    DefectChunk,
    EmbeddingRecord
)

class KnowledgeRepository:
    def __init__(self, db: Session):
        self.db = db

    # Datasets
    def create_dataset(self, dataset: Dataset) -> Dataset:
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)
        return dataset

    def get_dataset_by_id(self, dataset_id: str) -> Optional[Dataset]:
        return self.db.query(Dataset).filter(Dataset.id == dataset_id).first()

    def list_datasets(self, skip: int = 0, limit: int = 50) -> Tuple[int, List[Dataset]]:
        query = self.db.query(Dataset)
        total = query.count()
        items = query.order_by(desc(Dataset.created_at)).offset(skip).limit(limit).all()
        return total, items

    def update_dataset_status(self, dataset_id: str, status: str, total_records: Optional[int] = None) -> Optional[Dataset]:
        ds = self.get_dataset_by_id(dataset_id)
        if ds:
            ds.status = status
            if total_records is not None:
                ds.total_records = total_records
            self.db.commit()
            self.db.refresh(ds)
        return ds

    # Ingestion Jobs
    def create_ingestion_job(self, job: IngestionJob) -> IngestionJob:
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def update_ingestion_job(
        self,
        job_id: str,
        status: str,
        processed: int = 0,
        failed: int = 0,
        error_msg: Optional[str] = None
    ) -> Optional[IngestionJob]:
        job = self.db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if job:
            job.status = status
            job.processed_records = processed
            job.failed_records = failed
            if error_msg:
                job.error_message = error_msg
            self.db.commit()
            self.db.refresh(job)
        return job

    def list_ingestion_jobs(self, dataset_id: Optional[str] = None) -> List[IngestionJob]:
        q = self.db.query(IngestionJob)
        if dataset_id:
            q = q.filter(IngestionJob.dataset_id == dataset_id)
        return q.order_by(desc(IngestionJob.created_at)).all()

    # Historical Defects
    def get_defect_by_hash(self, content_hash: str) -> Optional[HistoricalDefect]:
        return self.db.query(HistoricalDefect).filter(HistoricalDefect.content_hash == content_hash).first()

    def create_defect(self, defect: HistoricalDefect) -> HistoricalDefect:
        self.db.add(defect)
        self.db.commit()
        self.db.refresh(defect)
        return defect

    def bulk_create_defects(self, defects: List[HistoricalDefect]) -> List[HistoricalDefect]:
        self.db.add_all(defects)
        self.db.commit()
        for d in defects:
            self.db.refresh(d)
        return defects

    def get_defect_by_id(self, defect_id: str) -> Optional[HistoricalDefect]:
        return self.db.query(HistoricalDefect).filter(HistoricalDefect.id == defect_id).first()

    def list_defects(self, skip: int = 0, limit: int = 50, source: Optional[str] = None) -> Tuple[int, List[HistoricalDefect]]:
        q = self.db.query(HistoricalDefect)
        if source:
            q = q.filter(HistoricalDefect.source_repo.ilike(f"%{source}%"))
        total = q.count()
        items = q.order_by(desc(HistoricalDefect.created_at)).offset(skip).limit(limit).all()
        return total, items

    # Chunks & Embeddings
    def bulk_create_chunks(self, chunks: List[DefectChunk]) -> List[DefectChunk]:
        self.db.add_all(chunks)
        self.db.commit()
        for c in chunks:
            self.db.refresh(c)
        return chunks

    def bulk_create_embeddings(self, embeddings: List[EmbeddingRecord]) -> List[EmbeddingRecord]:
        self.db.add_all(embeddings)
        self.db.commit()
        return embeddings

    def get_all_chunks_with_embeddings(self) -> List[Tuple[DefectChunk, HistoricalDefect, Optional[List[float]], Optional[str]]]:
        chunks = (
            self.db.query(DefectChunk)
            .options(
                joinedload(DefectChunk.defect),
                joinedload(DefectChunk.embedding)
            )
            .all()
        )
        records = []
        for c in chunks:
            if c.defect:
                vec = c.embedding.vector if c.embedding else None
                model_name = c.embedding.model_name if c.embedding else None
                records.append((c, c.defect, vec, model_name))
        return records

    # Statistics
    def get_stats(self) -> Dict[str, Any]:
        total_datasets = self.db.query(func.count(Dataset.id)).scalar() or 0
        total_defects = self.db.query(func.count(HistoricalDefect.id)).scalar() or 0
        total_chunks = self.db.query(func.count(DefectChunk.id)).scalar() or 0
        total_embeddings = self.db.query(func.count(EmbeddingRecord.id)).scalar() or 0

        sources = (
            self.db.query(HistoricalDefect.source_repo, func.count(HistoricalDefect.id))
            .group_by(HistoricalDefect.source_repo)
            .all()
        )
        by_source = {s[0]: s[1] for s in sources if s[0]}

        languages = (
            self.db.query(HistoricalDefect.programming_language, func.count(HistoricalDefect.id))
            .group_by(HistoricalDefect.programming_language)
            .all()
        )
        by_language = {l[0]: l[1] for l in languages if l[0]}

        return {
            "total_datasets": total_datasets,
            "total_defects": total_defects,
            "total_chunks": total_chunks,
            "total_embeddings": total_embeddings,
            "by_source": by_source,
            "by_language": by_language,
            "vector_index_status": "active" if total_embeddings > 0 else "unindexed",
            "bm25_index_status": "ready" if total_chunks > 0 else "unindexed"
        }
