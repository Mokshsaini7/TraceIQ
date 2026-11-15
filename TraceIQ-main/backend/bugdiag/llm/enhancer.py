"""Optional LLM refinement of the Root Cause explanation.

Design:
- Disabled unless ANTHROPIC_API_KEY is set; the heuristic agents always produce a complete report.
- Grounded Citation Rule: the model must cite only defect IDs from the retrieved set. Any
  output citing an unknown ID (or no ID) is rejected and the heuristic text is kept.
- Any network/parse failure falls back silently to the heuristic result.
"""

import re
from typing import Any, Dict, List, Optional

import httpx

from bugdiag.core.config import get_settings
from bugdiag.core.logging import get_logger
from bugdiag.schemas.agent import RootCauseResult

logger = get_logger("llm.enhancer")
_CITE = re.compile(r"\[([A-Za-z0-9_.\-]+)\]")


class LLMEnhancer:
    def __init__(self):
        self.settings = get_settings()

    @property
    def enabled(self) -> bool:
        return bool(self.settings.ANTHROPIC_API_KEY)

    @staticmethod
    def validate_citations(text: str, allowed_ids: set) -> bool:
        """True only if the text cites at least one ID and every cited ID is allowed."""
        cited = set(_CITE.findall(text))
        return bool(cited) and cited.issubset(allowed_ids)

    def _complete(self, prompt: str) -> Optional[str]:
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.settings.ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.settings.LLM_MODEL,
                "max_tokens": 600,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=self.settings.LLM_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        blocks = resp.json().get("content", [])
        return "".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip() or None

    def refine_root_cause(
        self, title: str, description: str, stack_trace: Optional[str],
        result: RootCauseResult, similar: List[Dict[str, Any]],
    ) -> RootCauseResult:
        if not self.enabled or not similar:
            return result
        allowed = {d["original_issue_id"] for d in similar}
        context = "\n".join(
            f"[{d['original_issue_id']}] {d['title']} — resolution: {(d.get('resolution') or 'n/a')[:300]}"
            for d in similar[:5]
        )
        prompt = (
            "You are a senior debugging assistant. Explain the most likely root cause of the bug below in "
            "3-4 sentences. You may ONLY rely on the historical defects listed and MUST cite each one you "
            "use as [ID] using exactly the IDs given. Do not invent IDs.\n\n"
            f"BUG: {title}\n{description[:1200]}\n\nSTACK TRACE:\n{(stack_trace or 'n/a')[:1500]}\n\n"
            f"HISTORICAL DEFECTS:\n{context}"
        )
        try:
            text = self._complete(prompt)
        except Exception as e:  # network, auth, parsing — never break the pipeline
            logger.warning(f"LLM refinement skipped: {e}")
            return result
        if text and self.validate_citations(text, allowed):
            result.explanation = text
            result.supporting_evidence.append("Explanation refined by LLM using retrieved, cited defects only.")
        else:
            logger.warning("LLM output rejected by Grounded Citation Rule; keeping heuristic explanation.")
        return result
