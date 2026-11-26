"""Evidence-aware remediation notes. No untested patch is presented as verified."""
from typing import Any, Dict, List
from bugdiag.schemas.agent import (RemediationResult, FixRecommendation, HistoricalMatchReference,
    TriageResult, LogAnalysisResult, RootCauseResult)
from bugdiag.core.logging import get_logger

logger = get_logger("agents.remediation")

class RemediationAgent:
    def analyze(self, triage: TriageResult, log_analysis: LogAnalysisResult,
                root_cause: RootCauseResult, similar_defects: List[Dict[str, Any]]) -> RemediationResult:
        historical_refs: List[HistoricalMatchReference] = []
        historical_notes: List[FixRecommendation] = []
        for d in similar_defects:
            resolution = (d.get("resolution") or "").strip()
            ref = HistoricalMatchReference(defect_id=str(d.get("defect_id", "")),
                source_repo=str(d.get("source_repo", "Unknown")),
                original_issue_id=str(d.get("original_issue_id", "Unknown")),
                title=str(d.get("title", "Untitled")),
                similarity_score=float(d.get("similarity_score", 0.0)),
                resolution=resolution or None, url=d.get("source_url"))
            historical_refs.append(ref)
            if resolution and len(resolution) > 10:
                historical_notes.append(FixRecommendation(
                    title=f"Historical resolution note — {ref.source_repo} ({ref.original_issue_id})",
                    description=(resolution + "\n\nThis is text recorded in the source dataset. TraceIQ has not independently checked out, applied, or tested the original patch."),
                    diff_snippet=None, is_verified_from_history=False, source_defect_id=ref.original_issue_id))

        category_guidance = {
            "NullPointer": ("Check for missing or null values", "Inspect the exact variable at the first relevant stack frame. Confirm where it is created, whether a lookup can return no result, and whether input validation is needed."),
            "Memory": ("Check memory use and resource cleanup", "Measure memory near the failure. Look for large allocations, retained references, unbounded queues, and resources that are not closed."),
            "Concurrency": ("Check shared state and thread ordering", "Identify shared data, lock ownership, and the order in which locks are acquired. Reproduce under load before changing synchronization."),
            "IndexOutOfBounds": ("Check index and collection boundaries", "Record the index and collection length at the failure. Check empty collections, off-by-one conditions, and changes between validation and access."),
            "Network": ("Check the network request path", "Verify the target host, DNS, port, TLS, proxy, timeout, and actual response code. Separate connection failures from application errors."),
            "Configuration": ("Check runtime configuration and dependencies", "Compare required environment variables, file paths, installed package versions, and runtime versions with a known working environment."),
        }
        title, detail = category_guidance.get(triage.category, (
            "Collect more evidence before changing code",
            "The current report does not support a safe code change. Capture the full error, stack trace, reproduction steps, environment details, and the code around the failing operation."))
        if log_analysis.stack_frames:
            f = log_analysis.stack_frames[0]
            detail += f" First parsed frame: {f.file}" + (f":{f.line}" if f.line else "") + "."
        else:
            detail += " No usable file-and-line stack frame was parsed."
        suggested = [FixRecommendation(title=title, description=detail, diff_snippet=None,
            is_verified_from_history=False, source_defect_id=None)]
        rationale = (f"TraceIQ found {len(historical_notes)} historical resolution note(s). "
            "These notes are not verified patches. The suggested next step is based on the current triage category and parsed log evidence; review and test it before applying.")
        logger.info("Remediation notes generated: %s historical notes, 1 investigation suggestion", len(historical_notes))
        return RemediationResult(verified_fixes=[], suggested_fixes=historical_notes + suggested,
            rationale=rationale, historical_references=historical_refs)
