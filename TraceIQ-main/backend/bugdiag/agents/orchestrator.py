"""Agent Orchestrator: Executes the 5-Agent Pipeline with structured execution logging.
Workflow:
Bug Submission -> Validation -> Preprocessing -> Triage Agent -> Log Analysis Agent -> Knowledge Retrieval -> Root Cause Agent -> Duplicate Detection Agent -> Remediation Agent -> Diagnosis Report.
"""

import time
from typing import Any, Dict, List
from sqlalchemy.orm import Session
from bugdiag.core.logging import get_logger
from bugdiag.repositories.submission_repo import SubmissionRepository
from bugdiag.repositories.diagnosis_repo import DiagnosisRepository
from bugdiag.retrieval.hybrid import HybridRetriever
from bugdiag.agents.triage_agent import TriageAgent
from bugdiag.agents.log_analysis_agent import LogAnalysisAgent
from bugdiag.agents.root_cause_agent import RootCauseAgent
from bugdiag.agents.duplicate_agent import DuplicateDetectionAgent
from bugdiag.agents.remediation_agent import RemediationAgent
from bugdiag.llm import LLMEnhancer
from bugdiag.models.diagnosis import DiagnosisReport
from bugdiag.file_processing.parser import read_file_safely

logger = get_logger("agents.orchestrator")

class AgentOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.submission_repo = SubmissionRepository(db)
        self.diagnosis_repo = DiagnosisRepository(db)
        self.retriever = HybridRetriever(db)

        # 5 Agents initialization
        self.triage_agent = TriageAgent()
        self.log_analysis_agent = LogAnalysisAgent()
        self.root_cause_agent = RootCauseAgent()
        self.duplicate_agent = DuplicateDetectionAgent()
        self.remediation_agent = RemediationAgent()
        self.llm = LLMEnhancer()

    def run_pipeline(self, submission_id: str) -> DiagnosisReport:
        submission = self.submission_repo.get_by_id(submission_id)
        if not submission:
            raise ValueError(f"Submission {submission_id} not found.")

        logger.info(f"Initiating 5-Agent Diagnosis Pipeline for Submission {submission_id}: '{submission.title}'")
        self.submission_repo.update_status(submission_id, "analyzing")

        try:
            # 1. Preprocessing & Attachment Content Extraction
            combined_logs = submission.error_logs or ""
            if submission.attachments:
                for att in submission.attachments:
                    # Safely read text/log attachment without execution
                    file_text = read_file_safely(att.file_path, max_chars=10000)
                    if file_text:
                        combined_logs += f"\n--- Attachment [{att.original_filename}] ---\n{file_text}"

            # 2. Agent 1: Triage Agent
            t0 = time.perf_counter()
            triage_res = self.triage_agent.analyze(
                title=submission.title,
                description=submission.description,
                stack_trace=submission.stack_trace,
                error_logs=combined_logs,
                language_hint=submission.programming_language,
                framework_hint=submission.framework,
                user_severity=submission.severity,
                user_priority=submission.priority,
                reproduction_steps=submission.reproduction_steps
            )
            triage_ms = (time.perf_counter() - t0) * 1000
            self.diagnosis_repo.log_agent_execution(
                submission_id=submission_id,
                agent_name="TriageAgent",
                status="completed",
                input_payload={"title": submission.title, "language_hint": submission.programming_language},
                output_payload=triage_res.model_dump(),
                execution_time_ms=round(triage_ms, 2)
            )

            # 3. Agent 2: Log Analysis Agent
            t0 = time.perf_counter()
            log_res = self.log_analysis_agent.analyze(
                stack_trace=submission.stack_trace,
                error_logs=combined_logs
            )
            log_ms = (time.perf_counter() - t0) * 1000
            self.diagnosis_repo.log_agent_execution(
                submission_id=submission_id,
                agent_name="LogAnalysisAgent",
                status="completed",
                input_payload={"has_stack_trace": bool(submission.stack_trace)},
                output_payload=log_res.model_dump(),
                execution_time_ms=round(log_ms, 2)
            )

            # 4. Knowledge Retrieval (Hybrid RRF Search)
            search_query = f"{submission.title} {log_res.exception_type or ''} {submission.description[:200]}"
            similar_defects = self.retriever.search(
                query=search_query,
                method="hybrid",
                top_k=5,
                language_filter=triage_res.programming_language if triage_res.programming_language != "General" else None
            )

            # 5. Agent 3: Root Cause Agent
            t0 = time.perf_counter()
            root_cause_res = self.root_cause_agent.analyze(
                title=submission.title,
                description=submission.description,
                triage=triage_res,
                log_analysis=log_res,
                similar_defects=similar_defects
            )
            root_cause_res = self.llm.refine_root_cause(
                submission.title, submission.description, submission.stack_trace,
                root_cause_res, similar_defects
            )
            rc_ms = (time.perf_counter() - t0) * 1000
            self.diagnosis_repo.log_agent_execution(
                submission_id=submission_id,
                agent_name="RootCauseAgent",
                status="completed",
                input_payload={"category": triage_res.category, "exception": log_res.exception_type},
                output_payload=root_cause_res.model_dump(),
                execution_time_ms=round(rc_ms, 2)
            )

            # 6. Agent 4: Duplicate Detection Agent
            t0 = time.perf_counter()
            duplicate_res = self.duplicate_agent.analyze(similar_defects)
            dup_ms = (time.perf_counter() - t0) * 1000
            self.diagnosis_repo.log_agent_execution(
                submission_id=submission_id,
                agent_name="DuplicateDetectionAgent",
                status="completed",
                input_payload={"candidate_count": len(similar_defects)},
                output_payload=duplicate_res.model_dump(),
                execution_time_ms=round(dup_ms, 2)
            )

            # 7. Agent 5: Remediation Agent
            t0 = time.perf_counter()
            remediation_res = self.remediation_agent.analyze(
                triage=triage_res,
                log_analysis=log_res,
                root_cause=root_cause_res,
                similar_defects=similar_defects
            )
            rem_ms = (time.perf_counter() - t0) * 1000
            self.diagnosis_repo.log_agent_execution(
                submission_id=submission_id,
                agent_name="RemediationAgent",
                status="completed",
                input_payload={"historical_matches_count": len(similar_defects)},
                output_payload=remediation_res.model_dump(),
                execution_time_ms=round(rem_ms, 2)
            )

            # 8. Overall Confidence Synthesis
            # A report with missing logs or weak evidence must not receive a high score
            # merely because its form is complete. This is an evidence-coverage score,
            # not a statistically calibrated probability.
            overall_confidence = round(min(0.80, max(0.0,
                root_cause_res.confidence * 0.70 +
                triage_res.completeness_score * 0.15 +
                (0.15 if log_res.stack_frames else 0.05 if log_res.exception_type else 0.0)
            )), 2)

            # 9. Final Diagnosis Report Persistence
            report = self.diagnosis_repo.create_or_update_report(
                submission_id=submission_id,
                triage_result=triage_res.model_dump(),
                log_analysis_result=log_res.model_dump(),
                root_cause_result=root_cause_res.model_dump(),
                duplicate_detection_result=duplicate_res.model_dump(),
                remediation_result=remediation_res.model_dump(),
                overall_confidence=overall_confidence,
                status="completed"
            )

            self.submission_repo.update_status(submission_id, "analyzed")
            logger.info(f"Diagnosis Report successfully generated for submission {submission_id} (Confidence: {overall_confidence}).")
            return report

        except Exception as e:
            logger.error(f"Pipeline execution error for submission {submission_id}: {e}", exc_info=True)
            report = self.diagnosis_repo.create_or_update_report(
                submission_id=submission_id,
                overall_confidence=0.0,
                status="failed",
                error_message=str(e)
            )
            self.submission_repo.update_status(submission_id, "failed")
            try:
                self.diagnosis_repo.log_agent_execution(
                    submission_id=submission_id,
                    agent_name="DiagnosisPipeline",
                    status="failed",
                    input_payload={"submission_id": submission_id},
                    output_payload=None,
                    execution_time_ms=0.0,
                    error_message=str(e)[:1000]
                )
            except Exception:
                logger.exception("Could not save pipeline failure telemetry for %s", submission_id)
            return report
