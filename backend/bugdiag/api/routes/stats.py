"""Aggregated dashboard statistics."""

from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from bugdiag.database.session import get_db
from bugdiag.models.submission import BugSubmission
from bugdiag.models.diagnosis import DiagnosisReport
from bugdiag.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/stats", tags=["Dashboard Stats"])


@router.get("/dashboard")
def dashboard_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(BugSubmission.id)).scalar() or 0
    by_status = dict(db.query(BugSubmission.status, func.count()).group_by(BugSubmission.status).all())
    by_severity = dict(db.query(BugSubmission.severity, func.count()).group_by(BugSubmission.severity).all())
    reports = db.query(DiagnosisReport).filter(DiagnosisReport.status == "completed").all()
    avg_conf = round(sum(r.overall_confidence for r in reports) / len(reports), 3) if reports else 0.0
    dup_count = sum(1 for r in reports if (r.duplicate_detection_result or {}).get("is_duplicate"))
    categories = Counter((r.triage_result or {}).get("category", "Unknown") for r in reports)
    return {
        "total_submissions": total,
        "by_status": by_status,
        "by_severity": by_severity,
        "completed_diagnoses": len(reports),
        "average_confidence": avg_conf,
        "duplicates_detected": dup_count,
        "by_category": dict(categories),
        "knowledge_base": KnowledgeService(db).get_stats(),
    }
