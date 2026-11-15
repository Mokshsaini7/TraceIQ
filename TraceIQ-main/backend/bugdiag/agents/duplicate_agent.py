"""Duplicate Detection Agent: Evaluates historical defect reports using semantic and keyword hybrid matching
to detect duplicate bugs and compute calibrated duplicate likelihood.
"""

from typing import Any, Dict, List
from bugdiag.schemas.agent import DuplicateDetectionResult, DuplicateMatch
from bugdiag.core.logging import get_logger
from bugdiag.core.config import get_settings

logger = get_logger("agents.duplicate")

class DuplicateDetectionAgent:
    """Duplicate detection agent identifying possible duplicate bug submissions."""

    def __init__(self):
        self.threshold = get_settings().SIMILARITY_THRESHOLD

    def analyze(self, retrieved_candidates: List[Dict[str, Any]]) -> DuplicateDetectionResult:
        matches: List[DuplicateMatch] = []
        highest_score = 0.0

        for candidate in retrieved_candidates:
            score = float(candidate.get("similarity_score", 0.0))
            if score > highest_score:
                highest_score = score

            matches.append(DuplicateMatch(
                defect_id=candidate["defect_id"],
                source_repo=candidate["source_repo"],
                original_issue_id=candidate["original_issue_id"],
                title=candidate["title"],
                similarity_score=score,
                retrieval_method=candidate.get("retrieval_method", "hybrid_rrf")
            ))

        is_dup = highest_score >= self.threshold

        logger.info(f"Duplicate detection completed: is_duplicate={is_dup}, highest_score={highest_score}")
        return DuplicateDetectionResult(
            is_duplicate=is_dup,
            highest_similarity=round(highest_score, 4),
            potential_duplicates=matches
        )
