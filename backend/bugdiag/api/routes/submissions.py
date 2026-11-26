"""Bug Submission API endpoints.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from bugdiag.database.session import get_db
from bugdiag.schemas.submission import (
    BugSubmissionCreate,
    BugSubmissionResponse,
    BugSubmissionListResponse,
    BugAttachmentResponse
)
from bugdiag.services.submission_service import SubmissionService

router = APIRouter(prefix="/submissions", tags=["Bug Submissions"])

@router.post("", response_model=BugSubmissionResponse, status_code=status.HTTP_201_CREATED)
def create_submission(payload: BugSubmissionCreate, db: Session = Depends(get_db)):
    service = SubmissionService(db)
    submission = service.create_submission(payload)
    return submission

@router.get("", response_model=BugSubmissionListResponse)
def list_submissions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db)
):
    service = SubmissionService(db)
    total, items = service.list_submissions(
        page=page,
        page_size=page_size,
        status=status,
        severity=severity,
        priority=priority,
        language=language,
        search_query=search,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }

@router.get("/{submission_id}", response_model=BugSubmissionResponse)
def get_submission_details(submission_id: str, db: Session = Depends(get_db)):
    service = SubmissionService(db)
    sub = service.get_submission(submission_id)
    if not sub:
        raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found.")
    return sub

@router.post("/{submission_id}/attachments", response_model=BugAttachmentResponse)
async def upload_attachment(
    submission_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    service = SubmissionService(db)
    try:
        attachment = await service.add_attachment_to_submission(submission_id, file)
        return attachment
    except ValueError as val_err:
        raise HTTPException(status_code=404, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_submission(submission_id: str, db: Session = Depends(get_db)):
    from bugdiag.repositories.submission_repo import SubmissionRepository
    if not SubmissionRepository(db).delete(submission_id):
        raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found.")


@router.get("/{submission_id}/context")
def get_submission_agent_context(submission_id: str, db: Session = Depends(get_db)):
    """Return the versioned intake-agent handoff payload for downstream agents."""
    service = SubmissionService(db)
    submission = service.get_submission(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found.")
    context = submission.analysis_context
    if not context:
        raise HTTPException(status_code=404, detail="Agent context is not available for this submission.")
    return {
        "schema_version": context.schema_version,
        "orchestration_status": context.orchestration_status,
        "triage_status": context.triage_status,
        "log_analysis_status": context.log_analysis_status,
        "triage_output": context.triage_output,
        "log_analysis_output": context.log_analysis_output,
        "combined_context": context.combined_context,
        "errors": context.errors,
    }
