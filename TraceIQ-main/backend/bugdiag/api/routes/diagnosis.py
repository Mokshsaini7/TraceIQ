"""Diagnosis reports and 5-agent execution inspection endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from bugdiag.database.session import get_db
from bugdiag.schemas.diagnosis import (
    DiagnosisReportResponse,
    DiagnosisTriggerRequest,
    AgentExecutionLogResponse
)
from bugdiag.services.diagnosis_service import DiagnosisService

router = APIRouter(prefix="/diagnosis", tags=["Agent Diagnosis"])

@router.get("/{submission_id}", response_model=DiagnosisReportResponse)
def get_diagnosis_report(submission_id: str, db: Session = Depends(get_db)):
    service = DiagnosisService(db)
    report = service.get_report_by_submission(submission_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No diagnosis report found for submission {submission_id}."
        )
    return report

@router.post("/trigger", response_model=DiagnosisReportResponse)
def trigger_diagnosis_pipeline(payload: DiagnosisTriggerRequest, db: Session = Depends(get_db)):
    service = DiagnosisService(db)
    try:
        report = service.trigger_diagnosis(
            submission_id=payload.submission_id,
            force_reanalysis=payload.force_reanalysis
        )
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{submission_id}/logs", response_model=List[AgentExecutionLogResponse])
def get_agent_execution_logs(submission_id: str, db: Session = Depends(get_db)):
    service = DiagnosisService(db)
    logs = service.get_execution_logs(submission_id)
    return logs
