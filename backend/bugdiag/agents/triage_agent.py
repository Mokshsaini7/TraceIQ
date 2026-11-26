"""Evidence-based deterministic first-level bug triage.

The agent produces a transparent assessment; its confidence score measures evidence
coverage/consistency and is not a calibrated probability.
"""
from __future__ import annotations

import re
from typing import List, Tuple, Optional
from bugdiag.schemas.agent import TriageResult
from bugdiag.core.logging import get_logger

logger = get_logger("agents.triage")

LANGUAGE_INDICATORS = {
    "python": [r"\.py\b", r"\bdef\s+", r"\bimport\s+sys\b", r"\bTraceback\b", r"\bFastAPI\b", r"\bDjango\b", r"\bFlask\b"],
    "java": [r"\.java\b", r"\bpublic\s+class\b", r"NullPointerException", r"ArrayIndexOutOfBoundsException", r"\bSpring\b", r"\borg\.apache\b"],
    "javascript": [r"\.js\b", r"\bconst\s+", r"\blet\s+", r"Cannot read propert", r"\bReact\b", r"\bNode\.js\b"],
    "typescript": [r"\.ts\b", r"\.tsx\b", r"\binterface\s+\w+", r"\btype\s+\w+\s*=", r"\bAngular\b", r"\bNext\.js\b"],
    "c++": [r"\.cpp\b", r"\.h\b", r"\.hpp\b", r"\bstd::", r"\bnullptr\b", r"Segmentation fault", r"access violation"],
    "rust": [r"\.rs\b", r"\bfn\s+main\b", r"\bunwrap\(\)", r"\bpanic!\b", r"\bCargo\b"],
    "go": [r"\.go\b", r"\bfunc\s+", r"\bpackage\s+main\b", r"nil pointer dereference"],
}

CATEGORY_KEYWORDS = {
    "NullPointer": [r"null\s*pointer", r"nullpointer", r"\bnpe\b", r"null dereference", r"\bnull\b.{0,30}dereference", r"cannot read propert", r"nonetype", r"nil pointer"],
    "Memory": [r"out\s*of\s*memory", r"outofmemory", r"\boom\b", r"heap space", r"memory leak", r"buffer overflow", r"segmentation fault"],
    "Concurrency": [r"deadlock", r"race condition", r"thread access", r"concurrentmodification", r"\bmutex\b"],
    "Network": [r"connection refused", r"timeout", r"http 5\d{2}", r"socket error", r"rst_stream", r"net_reset", r"\bcors\b"],
    "IndexOutOfBounds": [r"indexoutofbounds", r"index out of bounds", r"array index out of range", r"slice bounds", r"subscript out of range"],
    "Configuration": [r"module not found", r"classnotfound", r"environment variable", r"nosuchfile", r"config error"],
    "LogicError": [r"assertion failed", r"unexpected result", r"incorrect value", r"calculation error", r"infinite loop"],
    "Security": [r"sql injection", r"cross.site scripting", r"\bxss\b", r"unauthorized access", r"privilege escalation", r"remote code execution", r"authentication bypass", r"credential exposure"],
    "Database": [r"database connection", r"connection pool", r"deadlock detected", r"sqlstate", r"integrity constraint", r"query failed"],
    "UI": [r"alignment", r"misaligned", r"padding", r"font size", r"visual glitch", r"button position", r"layout issue"],
}

FRAME_PATTERNS = [
    re.compile(r'(?P<file>(?:[\w./\\-]+)\.(?:py|java|js|jsx|ts|tsx|cpp|go|rs))(?::(?P<line>\d+))?'),
    re.compile(r'at\s+(?P<func>[\w.$<>]+)\((?P<file>[^():]+\.(?:java|kt)):(?P<line>\d+)\)'),
]
COMPONENT_RULES = [
    (r'\b(auth|authentication|login|oauth|jwt|session)\b', "UserAuthentication"),
    (r'\b(payment|checkout|billing|invoice)\b', "PaymentService"),
    (r'\b(database|db|sql|query|connection pool|repository|migration)\b', "DatabaseConnection"),
    (r'\b(api gateway|gateway|middleware|route handler)\b', "API Gateway"),
    (r'\b(frontend routing|router|routing|navigation)\b', "Frontend Routing"),
    (r'\b(file upload|upload|multipart|attachment)\b', "File Upload Module"),
    (r'\b(memory|heap|allocation|outofmemory)\b', "Memory Management"),
    (r'\b(userprofile|user profile|profile service)\b', "UserProfileService"),
    (r'\b(notification|email service|mailer)\b', "NotificationService"),
]

class TriageAgent:
    """Transparent deterministic triage engine."""

    def analyze(
        self, title: str, description: str, stack_trace: str | None = None,
        error_logs: str | None = None, language_hint: str | None = None,
        framework_hint: str | None = None, user_severity: str = "medium",
        user_priority: str = "p2", reproduction_steps: str | None = None,
        environment_info: str | None = None, expected_behavior: str | None = None,
        actual_behavior: str | None = None,
    ) -> TriageResult:
        sections = {
            "title": title or "", "description": description or "",
            "stack_trace": stack_trace or "", "error_logs": error_logs or "",
            "reproduction_steps": reproduction_steps or "",
            "environment": environment_info or "",
            "expected": expected_behavior or "", "actual": actual_behavior or "",
        }
        full_text = "\n".join(sections.values())
        category = self._classify_category(full_text)
        language = self._detect_language(full_text, language_hint)
        framework = self._detect_framework(full_text, framework_hint)
        component, component_evidence = self._identify_component(full_text)
        missing, completeness = self._evaluate_completeness(
            description or "", stack_trace, reproduction_steps,
            expected_behavior, actual_behavior, environment_info
        )
        severity, priority, severity_reason, priority_reason = self._assess_severity_priority(
            category, full_text, user_severity, user_priority
        )
        evidence = []
        if stack_trace and stack_trace.strip():
            evidence.append("Stack trace supplied")
        if error_logs and error_logs.strip():
            evidence.append("Error logs supplied")
        if reproduction_steps and reproduction_steps.strip():
            evidence.append("Reproduction steps supplied")
        if component_evidence:
            evidence.extend(component_evidence)
        if category != "GeneralDefect":
            evidence.append(f"Technical indicators match category {category}")
        if language != "General":
            evidence.append(f"Language indicators support {language}")
        if not evidence:
            evidence.append("Only the submitted title/description are available")

        confidence = self._confidence_score(
            title, description, stack_trace, error_logs, reproduction_steps,
            component, category, language
        )
        component_reason = (
            f"Identified {component} from: {'; '.join(component_evidence)}."
            if component != "Unknown" else
            "No reliable module, class, function, endpoint, or file-path evidence identifies a component."
        )
        missing_information = list(missing)
        if component == "Unknown":
            missing_information.append("Source file, module, class, function, or endpoint identifying the affected component")
        if not stack_trace and not error_logs:
            missing_information.append("Technical error output or stack trace")

        return TriageResult(
            category=category, severity=severity, priority=priority,
            affected_component=component,
            programming_language=language, framework=framework,
            confidence_score=confidence,
            reasoning={
                "severity_reason": severity_reason,
                "priority_reason": priority_reason,
                "component_reason": component_reason,
                "evidence": list(dict.fromkeys(evidence)),
            },
            missing_information=list(dict.fromkeys(missing_information)),
            completeness_score=round(completeness, 2),
        )

    def _detect_language(self, text: str, hint: str | None) -> str:
        if hint and hint.strip() and hint.lower().strip() not in {"unknown", "general"}:
            return hint.strip()
        scores = {lang: sum(len(re.findall(p, text, re.I)) for p in patterns)
                  for lang, patterns in LANGUAGE_INDICATORS.items()}
        lang, score = max(scores.items(), key=lambda x: x[1])
        return lang.upper() if lang == "c++" and score else lang.capitalize() if score else "General"

    def _detect_framework(self, text: str, hint: str | None) -> str | None:
        if hint and hint.strip() and hint.lower().strip() not in {"unknown", "none"}:
            return hint.strip()
        signatures = [
            ("FastAPI", r"\bfastapi\b"), ("Django", r"\bdjango\b"),
            ("Flask", r"\bflask\b"), ("Spring Boot", r"\bspring[- ]boot|springframework\b"),
            ("React", r"\breact|jsx|tsx\b"), ("Express", r"\bexpress(?:\.js)?\b"),
            ("Apache Spark", r"\bspark\b"), ("Apache Kafka", r"\bkafka\b"), ("Lucene", r"\blucene\b"),
        ]
        return next((name for name, pat in signatures if re.search(pat, text, re.I)), None)

    def _classify_category(self, text: str) -> str:
        scores = {cat: sum(len(re.findall(p, text, re.I)) for p in patterns)
                  for cat, patterns in CATEGORY_KEYWORDS.items()}
        category, score = max(scores.items(), key=lambda x: x[1])
        return category if score else "GeneralDefect"

    def _identify_component(self, text: str) -> Tuple[str, List[str]]:
        evidence = []
        # Stack frame paths and symbols are stronger than generic keyword matches.
        for pattern in FRAME_PATTERNS:
            for match in pattern.finditer(text):
                path = match.groupdict().get("file")
                func = match.groupdict().get("func")
                if path:
                    parts = re.split(r"[/\\]", path)
                    stem = re.sub(r"\.(py|java|js|jsx|ts|tsx|cpp|go|rs)$", "", parts[-1], flags=re.I)
                    if stem and stem.lower() not in {"main", "app", "index", "test"}:
                        return stem, [f"Stack trace references {path}"]
                if func:
                    return func.split(".")[-1], [f"Stack trace references function {func}"]
        lower = text.lower()
        for pattern, name in COMPONENT_RULES:
            if re.search(pattern, lower):
                evidence.append(f"Description/logs mention {name}")
                return name, evidence
        return "Unknown", []

    def _evaluate_completeness(self, description, stack_trace, reproduction_steps,
                               expected_behavior=None, actual_behavior=None, environment_info=None):
        missing, score = [], 1.0
        checks = [
            (len((description or "").strip()) >= 50, "Detailed description", .20),
            (bool(stack_trace and stack_trace.strip()) or bool(environment_info and environment_info.strip()),
             "Stack trace, error log, or environment diagnostics", .25),
            (bool(reproduction_steps and reproduction_steps.strip()), "Step-by-step reproduction instructions", .20),
            (bool(expected_behavior and expected_behavior.strip()), "Expected behavior", .10),
            (bool(actual_behavior and actual_behavior.strip()), "Actual behavior", .10),
            (bool(environment_info and environment_info.strip()), "Environment and runtime details", .05),
        ]
        for present, label, penalty in checks:
            if not present:
                missing.append(label)
                score -= penalty
        return missing, max(.0, score)

    def _assess_severity_priority(self, category, text, user_sev, user_pri):
        t = text.lower()
        critical_patterns = [
            r"\bproduction\b.{0,50}\b(outage|unavailable|down)\b",
            r"\b(system[- ]wide|all users|entire service|widespread)\b.{0,60}\b(fail|down|unavailable|outage|corrupt)\b",
            r"\b(permanent|irreversible|widespread)\b.{0,40}\b(data loss|data corruption)\b",
            r"\b(remote code execution|actively exploited|authentication bypass|exploitable sql injection)\b",
            r"\bcritical service outage\b", r"\bproduction\b.{0,80}\b(outage|unavailable|down)\b",
            r"\b(all|every) customers?\b.{0,50}\b(cannot|unable|blocked)\b.{0,40}\b(access|use|log in|pay)\b",
        ]
        high_patterns = [
            r"\b(authentication|login|payment|checkout)\b.{0,70}\b(fail|broken|unavailable|cannot|unable)\b",
            r"\b(crash|outofmemory(?:error)?|out of memory|deadlock)\b",
            r"\b(data corruption|security vulnerability|privilege escalation|exploitable sql injection)\b",
            r"\bmajor functionality\b",
            r"\b(core|primary|critical) workflow\b.{0,60}\b(blocked|broken|unavailable|fails)\b",
            r"\bservice[- ]wide\b.{0,50}\b(degradation|failure|unavailable)\b",
        ]
        low_patterns = [r"\b(cosmetic|alignment|misaligned|font|padding|minor ui|visual only)\b"]
        if any(re.search(p, t) for p in critical_patterns):
            severity, s_reason = "critical", "Evidence indicates a production-wide outage, irreversible/widespread data impact, or a severe exploitable security condition."
        elif any(re.search(p, t) for p in high_patterns):
            severity, s_reason = "high", "Evidence indicates a major workflow failure, serious crash, concurrency failure, or significant security/data risk; system-wide impact is not established."
        elif category == "UI" or any(re.search(p, t) for p in low_patterns):
            severity, s_reason = "low", "The reported impact is cosmetic or limited to presentation, with no evidence of core functionality failure."
        elif category in {"Network", "Database", "NullPointer", "IndexOutOfBounds", "Memory", "Concurrency", "Security"}:
            severity, s_reason = "medium", "A functional or technical defect is indicated, but the available evidence does not establish broad outage or major workflow impact."
        else:
            severity, s_reason = "medium", "The report indicates a defect, but impact and scope are not sufficiently established for a higher or lower classification."

        urgent = bool(re.search(
            r"\b(release blocker|release today|production incident|actively exploited|urgent|immediate|"
            r"customer[- ]facing outage|sla breach|regulatory deadline|data breach in progress)\b", t
        ))
        if severity == "critical" or urgent:
            priority, p_reason = "p1", "Immediate priority is justified by critical impact or explicit production/release urgency."
        elif severity == "high":
            priority, p_reason = "p2", "High priority is appropriate for a major workflow or serious technical failure."
        elif severity == "medium":
            priority, p_reason = "p3", "Normal priority is appropriate because the impact is limited or its urgency is not established."
        else:
            priority, p_reason = "p4", "Low priority is appropriate for a cosmetic or low-impact issue."
        # User-entered labels are deliberately not used as classification evidence.
        return severity, priority, s_reason, p_reason

    def _confidence_score(self, title, description, stack_trace, error_logs,
                          reproduction_steps, component, category, language):
        score = .20
        if title and len(title.strip()) >= 8: score += .08
        if description and len(description.strip()) >= 50: score += .14
        if stack_trace and stack_trace.strip(): score += .22
        elif error_logs and error_logs.strip(): score += .14
        if reproduction_steps and reproduction_steps.strip(): score += .12
        if component != "Unknown": score += .12
        if category != "GeneralDefect": score += .08
        if language != "General": score += .04
        return round(min(1.0, max(0.0, score)), 2)
