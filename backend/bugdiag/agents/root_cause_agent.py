"""Evidence-first root cause analysis. Outputs hypotheses, not proven causes."""

from typing import Any, Dict, List
from bugdiag.schemas.agent import RootCauseResult, HistoricalMatchReference, TriageResult, LogAnalysisResult
from bugdiag.core.logging import get_logger
from bugdiag.core.config import get_settings

logger = get_logger("agents.root_cause")
class RootCauseAgent:
    """Build cautious hypotheses from parsed evidence and relevant historical records."""

    def __init__(self):
        self.historical_strong_threshold = get_settings().SIMILARITY_THRESHOLD

    def analyze(self, title: str, description: str, triage: TriageResult,
                log_analysis: LogAnalysisResult, similar_defects: List[Dict[str, Any]]) -> RootCauseResult:
        matches: List[HistoricalMatchReference] = []
        for d in similar_defects[:3]:
            matches.append(HistoricalMatchReference(
                defect_id=str(d.get("defect_id", "")), source_repo=str(d.get("source_repo", "Unknown")),
                original_issue_id=str(d.get("original_issue_id", "Unknown")), title=str(d.get("title", "Untitled")),
                similarity_score=float(d.get("similarity_score", 0.0)), resolution=d.get("resolution"),
                url=d.get("source_url")))

        evidence: List[str] = []
        category = triage.category
        exc = log_analysis.exception_type
        frames = log_analysis.stack_frames
        if exc:
            evidence.append(f"The log parser found exception type: {exc}.")
        if log_analysis.error_message:
            evidence.append(f"Exception message: {log_analysis.error_message[:300]}")
        if frames:
            f = frames[0]
            evidence.append(f"First parsed stack frame: {f.file}" + (f":{f.line}" if f.line else "") + (f" in {f.function}" if f.function else ""))
        evidence.append(f"Triage category is {category}; this is a keyword-based classification, not proof of cause.")

        hypotheses = {
            "NullPointer": ("Possible null or missing-value access", "The report contains terms commonly linked to null or missing-value errors. Confirm the exact failing expression and value at the reported stack frame."),
            "Memory": ("Possible memory or resource exhaustion", "The report contains memory-related terms. Check memory usage, allocation size, retained objects, and resource cleanup around the failure."),
            "Concurrency": ("Possible concurrency or synchronization issue", "The report contains concurrency-related terms. Check shared state, lock ordering, thread ownership, and race conditions."),
            "IndexOutOfBounds": ("Possible invalid collection or buffer index", "The report contains index or bounds-related terms. Check the index value, collection length, and boundary conditions."),
            "Network": ("Possible network or connection failure", "The report contains network-related terms. Check endpoint availability, DNS, timeouts, TLS, proxy settings, and response codes."),
            "Configuration": ("Possible configuration or dependency problem", "The report contains configuration-related terms. Check required settings, installed packages, paths, and runtime versions."),
        }
        root_cause, explanation = hypotheses.get(category, (
            "Cause not yet established",
            "The available report does not contain enough specific evidence to identify a reliable root cause. Add the full error message, stack trace, reproduction steps, and affected code context."))

        # Confidence is deliberately conservative. It measures evidence coverage for this
        # hypothesis; it is not a statistically calibrated probability.
        confidence = 0.20
        if exc: confidence += 0.15
        if frames: confidence += 0.25
        if log_analysis.error_message: confidence += 0.10
        if len(description.strip()) >= 80: confidence += 0.05
        strong_matches = [m for m in matches if m.similarity_score >= self.historical_strong_threshold]
        if strong_matches:
            evidence.append(f"{len(strong_matches)} historical record(s) met the configured {self.historical_strong_threshold:.0%} relevance threshold. They are supporting references, not proof that this bug has the same cause.")
            confidence += 0.10
        elif matches:
            evidence.append("Historical records were retrieved, but none met the threshold for a strong match. Treat them as low-confidence leads only.")
        if not frames:
            evidence.append("No source file and line number could be confirmed from the supplied logs.")
        confidence = min(0.80, confidence)
        logger.info("Root cause hypothesis created (evidence score %.2f)", confidence)
        return RootCauseResult(identified_root_cause=root_cause, explanation=explanation,
            confidence=round(confidence, 2), supporting_evidence=evidence, historical_matches=matches)
