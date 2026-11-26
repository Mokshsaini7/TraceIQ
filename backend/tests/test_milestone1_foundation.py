"""Milestone 1 acceptance tests for seeded defect ingestion and indexing."""
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bugdiag.database.session import Base
from bugdiag.ingestion.pipeline import IngestionPipeline
from bugdiag.models.knowledge_base import Dataset, HistoricalDefect, DefectChunk, EmbeddingRecord

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASETS = [
    ("Mozilla", "mozilla_defects_sample.json", "json"),
    ("Apache", "apache_defects_sample.csv", "csv"),
    ("Eclipse", "eclipse_defects_sample.json", "json"),
]


class FakeEmbeddingModel:
    model_name = "test-embedding-model"

    def encode_batch(self, texts):
        return [[1.0] + [0.0] * 383 for _ in texts]


@pytest.fixture

def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_seed_datasets_parse_and_ingest_without_row_failures(db_session, monkeypatch):
    monkeypatch.setattr("bugdiag.ingestion.pipeline.get_embedding_model", lambda: FakeEmbeddingModel())
    expected_total = 0

    for source, filename, fmt in DATASETS:
        path = PROJECT_ROOT / "datasets" / "raw" / filename
        assert path.is_file(), f"Missing seeded dataset: {path}"

        pipeline = IngestionPipeline(db_session)
        records = pipeline.parse_dataset_records(str(path), fmt)
        assert records, f"Dataset {filename} is empty"
        expected_total += len(records)

        dataset = Dataset(
            name=f"{source} seeded test dataset",
            source=source,
            file_path=str(path),
            format=fmt,
            status="uploaded",
        )
        db_session.add(dataset)
        db_session.commit()

        job = pipeline.run_ingestion(dataset.id)
        db_session.refresh(job)
        assert job.status == "completed"
        assert job.processed_records == len(records)
        assert job.failed_records == 0

    assert db_session.query(HistoricalDefect).count() == expected_total
    assert db_session.query(DefectChunk).count() >= expected_total
    assert db_session.query(EmbeddingRecord).count() == db_session.query(DefectChunk).count()


def test_seeded_dataset_count_is_documented_and_nonzero():
    total = 0
    for _, filename, fmt in DATASETS:
        path = PROJECT_ROOT / "datasets" / "raw" / filename
        if fmt == "json":
            import json
            total += len(json.loads(path.read_text(encoding="utf-8")))
        else:
            import csv
            with path.open(encoding="utf-8-sig", newline="") as handle:
                total += sum(1 for _ in csv.DictReader(handle))
    assert total == 10
