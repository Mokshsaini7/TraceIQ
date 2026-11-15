"""Service layer coordinating bug submissions, file attachments, and automated diagnosis triggers.
"""

from typing import List, Optional, Tuple
from fastapi import UploadFile
from sqlalchemy.orm import Session
from bugdiag.models.submission import BugSubmission, BugAttachment
from bugdiag.schemas.submission import BugSubmissionCreate
from bugdiag.repositories.submission_repo import SubmissionRepository
from bugdiag.file_processing.sanitizer import FileProcessingService
from bugdiag.core.logging import get_logger

logger = get_logger("services.submission")

class SubmissionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SubmissionRepository(db)
        self.file_service = FileProcessingService()

    def create_submission(self, data: BugSubmissionCreate) -> BugSubmission:
        submission = BugSubmission(
            title=data.title,
            description=data.description,
            stack_trace=data.stack_trace,
            error_logs=data.error_logs,
            programming_language=data.programming_language,
            framework=data.framework,
            environment_info=data.environment_info,
            severity=data.severity,
            priority=data.priority,
            reproduction_steps=data.reproduction_steps,
            expected_behavior=data.expected_behavior,
            actual_behavior=data.actual_behavior,
            status="pending"
        )
        created = self.repo.create(submission)
        logger.info(f"Created bug submission {created.id}: {created.title}")

        # Diagnosis is triggered explicitly by the client after all attachments have
        # been uploaded. This ensures the agents can inspect attachment contents.

        # Refresh
        return self.repo.get_by_id(created.id)

    async def add_attachment_to_submission(self, submission_id: str, file: UploadFile) -> BugAttachment:
        submission = self.repo.get_by_id(submission_id)
        if not submission:
            raise ValueError(f"Submission {submission_id} does not exist.")

        filename, file_path, file_size, file_hash = await self.file_service.save_upload_file(file)

        attachment = BugAttachment(
            submission_id=submission_id,
            filename=filename,
            original_filename=file.filename or filename,
            file_path=file_path,
            file_size=file_size,
            content_type=file.content_type or "text/plain",
            file_hash=file_hash
        )
        return self.repo.add_attachment(attachment)

    def get_submission(self, submission_id: str) -> Optional[BugSubmission]:
        return self.repo.get_by_id(submission_id)

    def list_submissions(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        priority: Optional[str] = None,
        language: Optional[str] = None,
        search_query: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[int, List[BugSubmission]]:
        skip = (page - 1) * page_size
        return self.repo.list(
            skip=skip,
            limit=page_size,
            status=status,
            severity=severity,
            priority=priority,
            language=language,
            search_query=search_query,
            sort_by=sort_by,
            sort_order=sort_order
        )
