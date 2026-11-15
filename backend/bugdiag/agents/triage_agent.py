"""Triage Agent: Classifies bug categories, validates report completeness,
extracts programming languages and frameworks, and evaluates severity and priority.
"""

import re
from typing import List, Tuple
from bugdiag.schemas.agent import TriageResult
from bugdiag.core.logging import get_logger

logger = get_logger("agents.triage")

LANGUAGE_INDICATORS = {
    "python": [r"\.py\b", r"\bdef\s+", r"\bimport\s+sys\b", r"\bTraceback\s+\(most recent call last\)", r"\bFastAPI\b", r"\bDjango\b", r"\bFlask\b"],
    "java": [r"\.java\b", r"\bpublic\s+class\b", r"NullPointerException", r"ArrayIndexOutOfBoundsException", r"\bSpring\b", r"\borg\.apache\b"],
    "javascript": [r"\.js\b", r"\bconst\s+", r"\blet\s+", r"Cannot read propert", r"\bReact\b", r"\bNode\.js\b"],
    "typescript": [r"\.ts\b", r"\.tsx\b", r"\binterface\s+\w+", r"\btype\s+\w+\s*=", r"\bAngular\b", r"\bNext\.js\b"],
    "c++": [r"\.cpp\b", r"\.h\b", r"\.hpp\b", r"\bstd::", r"\bnullptr\b", r"Segmentation fault", r"access violation", r"\bxul\.dll\b"],
    "rust": [r"\.rs\b", r"\bfn\s+main\b", r"\bunwrap\(\)", r"\bpanic!\b", r"\bCargo\b"],
    "go": [r"\.go\b", r"\bfunc\s+", r"\bpackage\s+main\b", r"nil pointer dereference"]
}

CATEGORY_KEYWORDS = {
    "NullPointer": [r"null\s*pointer", r"nullpointer", r"\bnpe\b", r"null dereference", r"cannot read propert", r"nonetype", r"nil pointer"],
    "Memory": [r"out\s*of\s*memory", r"outofmemory", r"\boom\b", r"heap space", r"memory leak", r"buffer overflow", r"segmentation fault"],
    "Concurrency": [r"deadlock", r"race condition", r"thread access", r"synchronized", r"concurrentmodification", r"mutex"],
    "Network": [r"connection refused", r"timeout", r"http 5\d{2}", r"socket error", r"rst_stream", r"net_reset", r"cors"],
    "IndexOutOfBounds": [r"indexoutofbounds", r"index out of bounds", r"array index out of range", r"slice bounds", r"subscript out of range"],
    "Configuration": [r"module not found", r"classnotfound", r"environment variable", r"nosuchfile", r"config error"],
    "LogicError": [r"assertion failed", r"unexpected result", r"incorrect value", r"calculation error", r"infinite loop"]
}

class TriageAgent:
    """Deterministic, transparent triage engine for bug analysis."""

    def analyze(
        self,
        title: str,
        description: str,
        stack_trace: str | None = None,
        error_logs: str | None = None,
        language_hint: str | None = None,
        framework_hint: str | None = None,
        user_severity: str = "medium",
        user_priority: str = "p2",
        reproduction_steps: str | None = None
    ) -> TriageResult:
        full_text = f"{title} {description} {stack_trace or ''} {error_logs or ''}"

        # 1. Determine Language
        detected_language = self._detect_language(full_text, language_hint)

        # 2. Detect Framework
        detected_framework = self._detect_framework(full_text, framework_hint)

        # 3. Classify Bug Category
        category = self._classify_category(full_text)

        # 4. Check Missing Information & Calculate Completeness
        missing_info, completeness_score = self._evaluate_completeness(
            description, stack_trace, reproduction_steps
        )

        # 5. Assess Severity and Priority
        severity, priority = self._assess_severity_priority(
            category, full_text, user_severity, user_priority
        )

        logger.info(f"Triage complete: Category={category}, Lang={detected_language}, Severity={severity}, Score={completeness_score}")
        return TriageResult(
            category=category,
            severity=severity,
            priority=priority,
            programming_language=detected_language,
            framework=detected_framework,
            missing_information=missing_info,
            completeness_score=round(completeness_score, 2)
        )

    def _detect_language(self, text: str, hint: str | None) -> str:
        if hint and hint.strip() and hint.lower() != "unknown":
            return hint.strip()

        scores = {}
        for lang, patterns in LANGUAGE_INDICATORS.items():
            score = sum(len(re.findall(p, text, re.IGNORECASE)) for p in patterns)
            scores[lang] = score

        best_lang, best_score = max(scores.items(), key=lambda x: x[1])
        return best_lang.capitalize() if best_score > 0 else "General"

    def _detect_framework(self, text: str, hint: str | None) -> str | None:
        if hint and hint.strip():
            return hint.strip()

        framework_signatures = [
            ("FastAPI", r"\bfastapi\b"),
            ("Django", r"\bdjango\b"),
            ("Flask", r"\bflask\b"),
            ("Spring Boot", r"\bspring-boot|springframework\b"),
            ("React", r"\breact|jsx|tsx\b"),
            ("Express", r"\bexpress\.js|express\b"),
            ("Apache Spark", r"\bspark\b"),
            ("Apache Kafka", r"\bkafka\b"),
            ("Lucene", r"\blucene\b")
        ]
        for name, pat in framework_signatures:
            if re.search(pat, text, re.IGNORECASE):
                return name
        return None

    def _classify_category(self, text: str) -> str:
        category_scores = {}
        for cat, keywords in CATEGORY_KEYWORDS.items():
            count = sum(len(re.findall(kw, text, re.IGNORECASE)) for kw in keywords)
            category_scores[cat] = count

        best_cat, score = max(category_scores.items(), key=lambda x: x[1])
        return best_cat if score > 0 else "GeneralDefect"

    def _evaluate_completeness(
        self,
        description: str,
        stack_trace: str | None,
        reproduction_steps: str | None
    ) -> Tuple[List[str], float]:
        missing = []
        score = 1.0

        if len(description.strip()) < 50:
            missing.append("Detailed description (current description is under 50 characters)")
            score -= 0.25

        if not stack_trace or len(stack_trace.strip()) < 10:
            missing.append("Stack trace or crash diagnostic log")
            score -= 0.35

        if not reproduction_steps or len(reproduction_steps.strip()) < 15:
            missing.append("Step-by-step reproduction instructions")
            score -= 0.20

        return missing, max(0.2, score)

    def _assess_severity_priority(
        self,
        category: str,
        text: str,
        user_sev: str,
        user_pri: str
    ) -> Tuple[str, str]:
        critical_markers = [r"\bcrash\b", r"\bdeadlock\b", r"\bdata loss\b", r"\bsecurity\b", r"segmentation fault", r"\boom\b"]
        has_critical = any(re.search(m, text, re.IGNORECASE) for m in critical_markers)

        if has_critical:
            return "critical", "p1"
        elif category in ["NullPointer", "IndexOutOfBounds"]:
            return "high", "p2"
        return user_sev.lower(), user_pri.lower()
