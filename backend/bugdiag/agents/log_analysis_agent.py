"""Log Analysis Agent: Parses stack traces, extracts error messages,
identifies filenames and line numbers, detects exception types, and gathers technical evidence.
"""

import re
from typing import List, Optional
from bugdiag.schemas.agent import LogAnalysisResult, StackFrameInfo
from bugdiag.core.logging import get_logger

logger = get_logger("agents.log_analysis")

# Multi-language stack frame regex patterns
PYTHON_FRAME_RE = re.compile(r'File\s+"(?P<file>[^"]+)",\s+line\s+(?P<line>\d+)(?:,\s+in\s+(?P<func>\w+))?(?:\n\s*(?P<code>.+))?')
JAVA_FRAME_RE = re.compile(r'at\s+(?P<func>[\w\.$]+)\((?P<file>[\w\.-]+\.java):(?P<line>\d+)\)')
JS_FRAME_RE = re.compile(r'at\s+(?:(?P<func>[^\s\(]+)\s+\()?\(?(?P<file>[^\s:\)]+):(?P<line>\d+):(?P<col>\d+)\)?')
CPP_FRAME_RE = re.compile(r'(?:#\d+|\d+)\s+(?:0x[0-9a-fA-F]+\s+in\s+)?(?P<func>[^\(]+)\(.*\)\s+(?:at|\[)(?P<file>[^:\]]+):(?P<line>\d+)(?:\])?')

# Common exception header patterns
EXCEPTION_PATTERNS = [
    re.compile(r'^(?P<type>[A-Za-z0-9_\.]*(?:Exception|Error|Fault|Failure|Crash|Panic))(?::\s*(?P<msg>.+))?', re.MULTILINE),
    re.compile(r'^(?P<type>Assertion failure):\s*(?P<msg>.+)', re.MULTILINE),
    re.compile(r'^(?P<type>panic):\s*(?P<msg>.+)', re.MULTILINE)
]

class LogAnalysisAgent:
    """Specialized stack trace and runtime log analysis agent."""

    def analyze(self, stack_trace: Optional[str], error_logs: Optional[str]) -> LogAnalysisResult:
        raw_log = f"{stack_trace or ''}\n{error_logs or ''}".strip()
        if not raw_log:
            return LogAnalysisResult(
                has_stack_trace=False,
                exception_type=None,
                error_message=None,
                stack_frames=[],
                suspect_files=[],
                technical_evidence=["No stack trace or error log provided in bug submission."]
            )

        # 1. Detect Exception Type and Message
        exc_type, exc_msg = self._extract_exception(raw_log)

        # 2. Parse Stack Frames
        frames = self._extract_frames(raw_log)

        # 3. Identify Suspect Files
        suspect_files = []
        for f in frames:
            if f.file and f.file not in suspect_files:
                suspect_files.append(f.file)

        # 4. Formulate Technical Evidence
        evidence = []
        if exc_type:
            evidence.append(f"Identified Exception: {exc_type}" + (f" with message: '{exc_msg}'" if exc_msg else ""))
        if frames:
            deepest = frames[0]
            evidence.append(f"Origin Frame: {deepest.file}" + (f":{deepest.line}" if deepest.line else "") + (f" in `{deepest.function}()`" if deepest.function else ""))
            evidence.append(f"Extracted {len(frames)} stack execution frames across {len(suspect_files)} source files.")
        if not frames and raw_log:
            evidence.append("Log contents contained diagnostic output without standard stack frame signatures.")

        logger.info(f"Log analysis complete: Exc={exc_type}, Frames={len(frames)}, SuspectFiles={len(suspect_files)}")
        return LogAnalysisResult(
            has_stack_trace=bool(frames),
            exception_type=exc_type,
            error_message=exc_msg,
            stack_frames=frames,
            suspect_files=suspect_files,
            technical_evidence=evidence
        )

    def _extract_exception(self, text: str) -> tuple[Optional[str], Optional[str]]:
        for pat in EXCEPTION_PATTERNS:
            match = pat.search(text)
            if match:
                e_type = match.group("type").strip()
                e_msg = match.group("msg").strip() if "msg" in match.groupdict() and match.group("msg") else None
                return e_type, e_msg
        return None, None

    def _extract_frames(self, text: str) -> List[StackFrameInfo]:
        frames: List[StackFrameInfo] = []

        # Try Python
        for m in PYTHON_FRAME_RE.finditer(text):
            frames.append(StackFrameInfo(
                file=m.group("file"),
                line=int(m.group("line")),
                function=m.group("func"),
                code_context=m.group("code").strip() if m.group("code") else None
            ))

        # Try Java
        if not frames:
            for m in JAVA_FRAME_RE.finditer(text):
                frames.append(StackFrameInfo(
                    file=m.group("file"),
                    line=int(m.group("line")),
                    function=m.group("func")
                ))

        # Try JS/TS
        if not frames:
            for m in JS_FRAME_RE.finditer(text):
                frames.append(StackFrameInfo(
                    file=m.group("file"),
                    line=int(m.group("line")),
                    function=m.group("func")
                ))

        # Try C/C++
        if not frames:
            for m in CPP_FRAME_RE.finditer(text):
                frames.append(StackFrameInfo(
                    file=m.group("file").strip(),
                    line=int(m.group("line")),
                    function=m.group("func").strip()
                ))

        return frames
