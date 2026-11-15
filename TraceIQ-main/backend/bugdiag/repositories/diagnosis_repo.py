"""Repository for diagnosis reports and agent execution logs.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from bugdiag.models.diagnosis import DiagnosisReport, AgentExecutionLog

class DiagnosisRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_or_update_report(
        self,
        submission_id: str,
        triage_result: Optional[dict] = None,
        log_analysis_result: Optional[dict] = None,
        root_cause_result: Optional[dict] = None,
        duplicate_detection_result: Optional[dict] = None,
        remediation_result: Optional[dict] = None,
        overall_confidence: float = 0.0,
        status: str = "completed",
        error_message: Optional[str] = None
    ) -> DiagnosisReport:
        report = self.get_by_submission_id(submission_id)
        if not report:
            report = DiagnosisReport(
                submission_id=submission_id,
                triage_result=triage_result,
                log_analysis_result=log_analysis_result,
                root_cause_result=root_cause_result,
                duplicate_detection_result=duplicate_detection_result,
                remediation_result=remediation_result,
                overall_confidence=overall_confidence,
                status=status,
                error_message=error_message
            )
            self.db.add(report)
        else:
            if triage_result is not None:
                report.triage_result = triage_result
            if log_analysis_result is not None:
                report.log_analysis_result = log_analysis_result
            if root_cause_result is not None:
                report.root_cause_result = root_cause_result
            if duplicate_detection_result is not None:
                report.duplicate_detection_result = duplicate_detection_result
            if remediation_result is not None:
                report.remediation_result = remediation_result
            report.overall_confidence = overall_confidence
            report.status = status
            report.error_message = error_message
            if status == "failed":
                # Do not leave old successful findings visible on a failed re-run.
                report.triage_result = None
                report.log_analysis_result = None
                report.root_cause_result = None
                report.duplicate_detection_result = None
                report.remediation_result = None

        self.db.commit()
        self.db.refresh(report)
        return report

    def get_by_submission_id(self, submission_id: str) -> Optional[DiagnosisReport]:
        return self.db.query(DiagnosisReport).filter(DiagnosisReport.submission_id == submission_id).first()

    def log_agent_execution(
        self,
        submission_id: str,
        agent_name: str,
        status: str,
        input_payload: Optional[dict] = None,
        output_payload: Optional[dict] = None,
        execution_time_ms: float = 0.0,
        error_message: Optional[str] = None
    ) -> AgentExecutionLog:
        log = AgentExecutionLog(
            submission_id=submission_id,
            agent_name=agent_name,
            status=status,
            input_payload=input_payload,
            output_payload=output_payload,
            execution_time_ms=execution_time_ms,
            error_message=error_message
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def list_execution_logs(self, submission_id: str) -> List[AgentExecutionLog]:
        return (
            self.db.query(AgentExecutionLog)
            .filter(AgentExecutionLog.submission_id == submission_id)
            .order_by(AgentExecutionLog.created_at.asc())
            .all()
        )
