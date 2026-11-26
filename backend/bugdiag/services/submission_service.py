"""Service layer coordinating bug submissions, file attachments, and automated diagnosis triggers.
"""

from typing import List, Optional, Tuple
from fastapi import UploadFile
from sqlalchemy.orm import Session
from bugdiag.models.submission import BugSubmission, BugAttachment, BugAnalysisContext
from bugdiag.schemas.submission import BugSubmissionCreate
from bugdiag.repositories.submission_repo import SubmissionRepository
from bugdiag.file_processing.sanitizer import FileProcessingService
from bugdiag.core.logging import get_logger
from bugdiag.agents.triage_agent import TriageAgent
from bugdiag.agents.log_analysis_agent import LogAnalysisAgent
import time

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

        # Run the two intake agents immediately on every new submission. They are
        # deliberately isolated: one agent failing must not discard the other result.
        # Uploaded attachments are handled by the later full diagnosis pipeline.
        triage_output = None
        log_output = None
        triage_status = "pending"
        log_status = "pending"
        errors = []
        triage_started = time.perf_counter()
        try:
            triage = TriageAgent().analyze(
                title=created.title, description=created.description,
                stack_trace=created.stack_trace, error_logs=created.error_logs,
                language_hint=created.programming_language, framework_hint=created.framework,
                user_severity=created.severity, user_priority=created.priority,
                reproduction_steps=created.reproduction_steps, environment_info=created.environment_info,
                expected_behavior=created.expected_behavior, actual_behavior=created.actual_behavior
            )
            triage_output = triage.model_dump(mode="json")
            triage_status = "completed"
        except Exception as exc:
            triage_status = "failed"
            errors.append(f"TriageAgent: {type(exc).__name__}: {str(exc)[:500]}")
            logger.exception("Intake TriageAgent failed for submission %s", created.id)

        try:
            log_result = LogAnalysisAgent().analyze(created.stack_trace, created.error_logs)
            log_output = log_result.model_dump(mode="json")
            log_status = "completed" if (created.stack_trace or created.error_logs) else "incomplete"
        except Exception as exc:
            log_status = "failed"
            errors.append(f"LogAnalysisAgent: {type(exc).__name__}: {str(exc)[:500]}")
            logger.exception("Intake LogAnalysisAgent failed for submission %s", created.id)

        combined = {
            "schema_version": "1.0", "submission_id": created.id,
            "bug": {"title": created.title, "description": created.description,
                    "stack_trace": created.stack_trace, "error_logs": created.error_logs,
                    "programming_language": created.programming_language, "framework": created.framework},
            "triage": triage_output, "log_analysis": log_output,
            "agent_status": {"triage": triage_status, "log_analysis": log_status},
            "downstream_ready": bool(triage_output and log_output),
        }
        overall = "completed" if triage_status == "completed" and log_status == "completed" else (
            "partial" if triage_output or log_output else "failed")
        try:
            context = BugAnalysisContext(
                submission_id=created.id, schema_version="1.0",
                orchestration_status=overall, triage_status=triage_status,
                log_analysis_status=log_status, triage_output=triage_output,
                log_analysis_output=log_output, combined_context=combined, errors=errors
            )
            self.db.add(context)
            self.db.commit()
        except Exception:
            self.db.rollback()
            logger.exception("Could not persist intake context for submission %s", created.id)
            # Preserve the submission; report orchestration persistence failure.
            try:
                self.db.add(BugAnalysisContext(
                    submission_id=created.id, schema_version="1.0",
                    orchestration_status="failed", triage_status=triage_status,
                    log_analysis_status=log_status, triage_output=triage_output,
                    log_analysis_output=log_output, combined_context=combined,
                    errors=errors + ["Could not persist combined agent context."]
                ))
                self.db.commit()
            except Exception:
                self.db.rollback()
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
