"""Repository for database operations related to bug submissions and attachments.
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc
from bugdiag.models.submission import BugSubmission, BugAttachment

class SubmissionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, submission: BugSubmission) -> BugSubmission:
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        return submission

    def get_by_id(self, submission_id: str) -> Optional[BugSubmission]:
        return (
            self.db.query(BugSubmission)
            .options(joinedload(BugSubmission.attachments))
            .filter(BugSubmission.id == submission_id)
            .first()
        )

    def list(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        priority: Optional[str] = None,
        language: Optional[str] = None,
        search_query: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[int, List[BugSubmission]]:
        query = self.db.query(BugSubmission).options(joinedload(BugSubmission.attachments))

        if status:
            query = query.filter(BugSubmission.status == status.lower())
        if severity:
            query = query.filter(BugSubmission.severity == severity.lower())
        if priority:
            query = query.filter(BugSubmission.priority == priority.lower())
        if language:
            query = query.filter(BugSubmission.programming_language == language)
        if search_query:
            term = f"%{search_query}%"
            query = query.filter(
                (BugSubmission.title.ilike(term)) | (BugSubmission.description.ilike(term))
            )

        total = query.count()

        allowed_sort = {"created_at", "updated_at", "title", "severity", "priority", "status"}
        sort_col = getattr(BugSubmission, sort_by if sort_by in allowed_sort else "created_at")
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_col))
        else:
            query = query.order_by(desc(sort_col))

        items = query.offset(skip).limit(limit).all()
        return total, items

    def delete(self, submission_id: str) -> bool:
        sub = self.get_by_id(submission_id)
        if not sub:
            return False
        self.db.delete(sub)
        self.db.commit()
        return True

    def update_status(self, submission_id: str, new_status: str) -> Optional[BugSubmission]:
        sub = self.get_by_id(submission_id)
        if sub:
            sub.status = new_status
            self.db.commit()
            self.db.refresh(sub)
        return sub

    def add_attachment(self, attachment: BugAttachment) -> BugAttachment:
        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)
        return attachment

    def get_attachments(self, submission_id: str) -> List[BugAttachment]:
        return (
            self.db.query(BugAttachment)
            .filter(BugAttachment.submission_id == submission_id)
            .all()
        )
