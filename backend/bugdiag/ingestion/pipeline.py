"""Historical defect ingestion and indexing pipeline.
Executes Import -> Cleaning -> Normalization -> Deduplication -> Chunking -> Embedding Generation -> Storage.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
from sqlalchemy.orm import Session

from bugdiag.core.logging import get_logger
from bugdiag.core.config import get_settings
from bugdiag.embeddings.factory import get_embedding_model
from bugdiag.ingestion.cleaner import clean_text, normalize_stack_trace, compute_content_hash
from bugdiag.ingestion.chunker import DefectChunker
from bugdiag.models.knowledge_base import (
    Dataset,
    IngestionJob,
    HistoricalDefect,
    DefectChunk,
    EmbeddingRecord
)
from bugdiag.repositories.knowledge_repo import KnowledgeRepository

logger = get_logger("ingestion.pipeline")

# Canonical default mappings for popular open source repositories
DEFAULT_MOZILLA_MAPPING = {
    "source_repo": "product",
    "original_issue_id": "bug_id",
    "title": "summary",
    "description": "description",
    "stack_trace": "stack_trace",
    "comments": "comments",
    "resolution": "resolution",
    "status": "status",
    "programming_language": "language",
    "source_url": "url",
    "created_date": "creation_time",
    "updated_date": "last_change_time"
}

DEFAULT_APACHE_MAPPING = {
    "source_repo": "project_key",
    "original_issue_id": "issue_key",
    "title": "summary",
    "description": "description",
    "stack_trace": "environment_log",
    "comments": "comment_log",
    "resolution": "resolution",
    "status": "status",
    "programming_language": "language",
    "source_url": "link",
    "created_date": "created",
    "updated_date": "updated"
}

DEFAULT_ECLIPSE_MAPPING = {
    "source_repo": "product",
    "original_issue_id": "id",
    "title": "summary",
    "description": "description",
    "stack_trace": "stack_trace",
    "comments": "comments",
    "resolution": "resolution",
    "status": "status",
    "programming_language": "language",
    "source_url": "url",
    "created_date": "creation_ts",
    "updated_date": "delta_ts"
}

class IngestionPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.repo = KnowledgeRepository(db)
        self.settings = get_settings()
        self.embedding_model = get_embedding_model()
        self.chunker = DefectChunker()

    def _infer_mapping(self, source: str, user_mapping: Optional[Dict[str, str]]) -> Dict[str, str]:
        mapping = {}
        src_lower = source.lower()
        if "mozilla" in src_lower:
            mapping.update(DEFAULT_MOZILLA_MAPPING)
        elif "apache" in src_lower:
            mapping.update(DEFAULT_APACHE_MAPPING)
        elif "eclipse" in src_lower:
            mapping.update(DEFAULT_ECLIPSE_MAPPING)

        if user_mapping:
            mapping.update(user_mapping)
        return mapping

    def parse_dataset_records(self, file_path: str, fmt: str) -> List[Dict[str, Any]]:
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Dataset file not found at: {file_path}")

        if fmt.lower() == "json":
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    # Handle common wrappers like {"bugs": [...]}
                    for k, v in data.items():
                        if isinstance(v, list):
                            return v
                    return [data]
                return []
        elif fmt.lower() == "csv":
            df = pd.read_csv(path, dtype=str)
            df = df.fillna("")
            return df.to_dict(orient="records")
        else:
            raise ValueError(f"Unsupported dataset format: {fmt}. Must be JSON or CSV.")

    def run_ingestion(self, dataset_id: str) -> IngestionJob:
        dataset = self.repo.get_dataset_by_id(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found.")

        job = IngestionJob(
            dataset_id=dataset_id,
            total_records=0,
            processed_records=0,
            failed_records=0,
            status="running"
        )
        self.repo.create_ingestion_job(job)

        try:
            records = self.parse_dataset_records(dataset.file_path, dataset.format)
            job.total_records = len(records)
            self.db.commit()

            mapping = self._infer_mapping(dataset.source, dataset.column_mapping)
            processed_count = 0
            failed_count = 0

            for row in records:
                try:
                    # Field extraction with configurable mapping
                    repo_src = str(row.get(mapping.get("source_repo", "source_repo"), dataset.source) or dataset.source).strip()
                    issue_id = str(row.get(mapping.get("original_issue_id", "original_issue_id"), f"AUTO-{uuid.uuid4().hex[:8]}")).strip()
                    raw_title = str(row.get(mapping.get("title", "title"), "")).strip()
                    raw_desc = str(row.get(mapping.get("description", "description"), "")).strip()

                    if not raw_title and not raw_desc:
                        failed_count += 1
                        continue

                    title = clean_text(raw_title) or "Untitled Defect"
                    description = clean_text(raw_desc) or title
                    stack_trace = normalize_stack_trace(str(row.get(mapping.get("stack_trace", "stack_trace"), "") or ""))
                    comments = clean_text(str(row.get(mapping.get("comments", "comments"), "") or "")) or None
                    resolution = clean_text(str(row.get(mapping.get("resolution", "resolution"), "") or "")) or None
                    status_val = clean_text(str(row.get(mapping.get("status", "status"), "") or "")) or None
                    language = clean_text(str(row.get(mapping.get("programming_language", "language"), "") or "")) or None
                    source_url = str(row.get(mapping.get("source_url", "source_url"), "") or "").strip() or None

                    # Deduplication check
                    content_hash = compute_content_hash(repo_src, issue_id, title, description)
                    existing = self.repo.get_defect_by_hash(content_hash)
                    if existing:
                        logger.info(f"Skipping duplicate defect record: {repo_src} / {issue_id}")
                        processed_count += 1
                        continue

                    # Parse timestamps if present
                    c_date = None
                    created_raw = row.get(mapping.get("created_date", "created_date"))
                    if created_raw:
                        try:
                            c_date = pd.to_datetime(created_raw).to_pydatetime()
                        except Exception:
                            c_date = None

                    u_date = None
                    updated_raw = row.get(mapping.get("updated_date", "updated_date"))
                    if updated_raw:
                        try:
                            u_date = pd.to_datetime(updated_raw).to_pydatetime()
                        except Exception:
                            u_date = None

                    defect = HistoricalDefect(
                        dataset_id=dataset.id,
                        source_repo=repo_src,
                        original_issue_id=issue_id,
                        title=title,
                        description=description,
                        stack_trace=stack_trace,
                        comments=comments,
                        resolution=resolution,
                        status=status_val,
                        programming_language=language,
                        source_url=source_url,
                        content_hash=content_hash,
                        original_created_at=c_date,
                        original_updated_at=u_date
                    )
                    self.db.add(defect)
                    self.db.flush()

                    # Chunking
                    chunk_dicts = self.chunker.chunk_defect(
                        title=title,
                        description=description,
                        stack_trace=stack_trace,
                        resolution=resolution
                    )

                    chunk_objects = []
                    chunk_texts = []
                    for c_dict in chunk_dicts:
                        chunk_obj = DefectChunk(
                            defect_id=defect.id,
                            chunk_index=c_dict["chunk_index"],
                            chunk_type=c_dict["chunk_type"],
                            content=c_dict["content"],
                            token_count=c_dict["token_count"]
                        )
                        chunk_objects.append(chunk_obj)
                        chunk_texts.append(c_dict["content"])

                    self.db.add_all(chunk_objects)
                    self.db.flush()

                    # Embedding Generation
                    embeddings = self.embedding_model.encode_batch(chunk_texts)
                    embedding_records = []
                    for chunk_obj, emb_vec in zip(chunk_objects, embeddings):
                        emb_rec = EmbeddingRecord(
                            chunk_id=chunk_obj.id,
                            model_name=self.embedding_model.model_name,
                            dimension=len(emb_vec),
                            vector=emb_vec
                        )
                        embedding_records.append(emb_rec)

                    self.db.add_all(embedding_records)
                    self.db.commit()
                    processed_count += 1

                except Exception as row_err:
                    self.db.rollback()
                    logger.error(f"Error processing row in dataset {dataset_id}: {row_err}")
                    failed_count += 1

            self.repo.update_ingestion_job(
                job_id=job.id,
                status="completed",
                processed=processed_count,
                failed=failed_count
            )
            self.repo.update_dataset_status(dataset_id, "completed", total_records=processed_count)
            logger.info(f"Ingestion completed for {dataset.name}: {processed_count} processed, {failed_count} failed.")

        except Exception as e:
            logger.error(f"Ingestion job failed for {dataset_id}: {e}")
            self.repo.update_ingestion_job(
                job_id=job.id,
                status="failed",
                error_msg=str(e)
            )
            self.repo.update_dataset_status(dataset_id, "failed")

        return job
