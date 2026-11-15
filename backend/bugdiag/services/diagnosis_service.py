"""Service layer managing diagnosis reports and agent pipeline re-triggers.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from bugdiag.models.diagnosis import DiagnosisReport, AgentExecutionLog
from bugdiag.repositories.diagnosis_repo import DiagnosisRepository
from bugdiag.agents.orchestrator import AgentOrchestrator
from bugdiag.core.logging import get_logger

logger = get_logger("services.diagnosis")

class DiagnosisService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DiagnosisRepository(db)
        self.orchestrator = AgentOrchestrator(db)

    def get_report_by_submission(self, submission_id: str) -> Optional[DiagnosisReport]:
        return self.repo.get_by_submission_id(submission_id)

    def trigger_diagnosis(self, submission_id: str, force_reanalysis: bool = False) -> DiagnosisReport:
        existing = self.repo.get_by_submission_id(submission_id)
        if existing and not force_reanalysis and existing.status == "completed":
            return existing
        return self.orchestrator.run_pipeline(submission_id)

    def get_execution_logs(self, submission_id: str) -> List[AgentExecutionLog]:
        return self.repo.list_execution_logs(submission_id)
