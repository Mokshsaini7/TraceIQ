"""Evidence-first parser for common application log and stack-trace formats."""
from __future__ import annotations

import re
from typing import Optional

from bugdiag.core.logging import get_logger
from bugdiag.schemas.agent import FailurePoint, LogAnalysisResult, StackFrameInfo

logger = get_logger("agents.log_analysis")

# Python: File "...", line N, in method
PYTHON_FRAME_RE = re.compile(
    r'File\s+["\'](?P<file>[^"\']+)["\'],\s*line\s+(?P<line>\d+)(?:,\s*in\s+(?P<func>[^\s]+))?(?:\n\s*(?P<code>[^\n]+))?'
)
# Java/Kotlin/Scala: at package.Class.method(File.java:123)
JAVA_FRAME_RE = re.compile(
    r'^\s*at\s+(?P<func>[\w.$<>/]+)\((?P<location>[^()]+)\)\s*$', re.MULTILINE
)
# Node/V8 and browser: at fn (file:line:column), at file:line:column
JS_FRAME_RE = re.compile(
    r'^\s*at\s+(?:(?P<func>.*?)\s+\()?\s*(?P<file>(?:file://)?[^\s()]+?):(?P<line>\d+):(?P<col>\d+)\)?\s*$', re.MULTILINE
)
# Firefox: fn@http://host/file.js:line:column
FIREFOX_FRAME_RE = re.compile(
    r'^(?P<func>[^@\n]*)@(?P<file>\S+?):(?P<line>\d+):(?P<col>\d+)\s*$', re.MULTILINE
)
# C/C++ gdb: #0 function (...) at file:line
CPP_FRAME_RE = re.compile(
    r'^\s*#(?P<idx>\d+)\s+(?:(?:0x[\da-fA-F]+\s+in\s+))?(?P<func>.*?)\s+at\s+(?P<file>[^:\n]+):(?P<line>\d+)\s*$', re.MULTILINE
)
# Go: file.go:line +0x... followed by function name (handled as location frame)
GO_FRAME_RE = re.compile(r'^\s*(?P<file>[^\s:]+\.go):(?P<line>\d+)\s+\+0x[\da-fA-F]+\s*$', re.MULTILINE)
# Rust: at file.rs:line:column
RUST_FRAME_RE = re.compile(r'^\s*(?P<func>[^\n]+)\n\s*at\s+(?P<file>[^:\n]+\.rs):(?P<line>\d+):\d+\s*$', re.MULTILINE)
DOTNET_FRAME_RE = re.compile(r'^\s*at\s+(?P<func>[\w.+`<>]+)(?:\(.*?\))?\s+in\s+(?P<file>.+?):line\s+(?P<line>\d+)\s*$', re.MULTILINE)
# PHP: #0 /path/file.php(42): Class->method() and {main}
PHP_FRAME_RE = re.compile(r'^\s*#(?P<idx>\d+)\s+(?P<file>[^()\s]+)\((?P<line>\d+)\):\s*(?P<func>[^\n]+)', re.MULTILINE)
# Common structured JSON logger payloads.
JSON_ERROR_KEYS = ("exception", "exception_type", "error_type", "type")
JSON_MESSAGE_KEYS = ("message", "error", "error_message", "msg")

RUBY_FRAME_RE = re.compile(r"^\s*from\s+(?P<file>.+?):(?P<line>\d+):in [`\'](?P<func>[^`\']+)[`\']\s*$", re.MULTILINE)
# Mozilla/Breakpad and SpiderMonkey native frames: module!symbol [source.cpp:123]
MOZILLA_FRAME_RE = re.compile(
    r'^\s*(?:#?\d+\s*:?[ \t]*)?(?:[^!\s]+!)?(?P<func>[\w:~.$<>]+)\([^\n]*?\)\s*\[(?P<file>[^\]:]+\.(?:cpp|cc|c|h)):(?P<line>\d+)\]\s*$',
    re.MULTILINE
)
MOZILLA_LOCATION_RE = re.compile(
    r'^\s*(?P<func>[\w:~.$<>]+)\([^\n]*?\)\s+(?:failed with [^ ]+\s+)?at\s+(?P<file>[^:\s]+\.(?:cpp|cc|c|h)):(?P<line>\d+)\s*$',
    re.MULTILINE
)
MOZILLA_BARE_LOCATION_RE = re.compile(
    r'^\s*(?:at\s+)?(?P<file>(?:[\w./-]+/)?[\w.-]+\.(?:cpp|cc|c|h)):(?P<line>\d+)\s*$',
    re.MULTILINE
)

EXCEPTION_PATTERNS = [
    re.compile(r'(?m)^\s*(?P<type>[\w.$:+]+(?:Exception|Error|Fault|Failure|Panic|Abort|Signal))(?::\s*(?P<msg>[^\n]+))?\s*$'),
    re.compile(r'(?m)^\s*(?P<type>panic)(?:\s*:\s*(?P<msg>[^\n]+))?\s*$'),
    re.compile(r'(?m)^\s*(?:Caused by:\s*)?(?P<type>[\w.$]+Exception)(?::\s*(?P<msg>[^\n]+))?'),
    re.compile(r'(?mi)^.*?\b(FATAL EXCEPTION|Unhandled exception|Uncaught (?:Exception|Error)|PHP Fatal error|Fatal error)\b(?::\s*(?P<msg>[^\n]+))?'),
]


def _clean_path(path: str) -> str:
    return path.strip().rstrip(",")


class LogAnalysisAgent:
    """Parse stack frames and identify the most defensible failure location."""

    def analyze(self, stack_trace: Optional[str], error_logs: Optional[str]) -> LogAnalysisResult:
        trace = (stack_trace or "").strip()
        logs = (error_logs or "").strip()
        raw = "\n".join(part for part in (trace, logs) if part).strip()
        if not raw:
            return LogAnalysisResult(
                has_stack_trace=False,
                detected_format="unknown", frame_count=0, analysis_summary="No diagnostic log content was supplied.",
                exception_type=None,
                error_message=None,
                stack_frames=[],
                suspect_files=[],
                technical_evidence=["No stack trace or error log provided in bug submission."],
                failure_point=None,
                code_path=[],
                confidence_score=0.0,
            )

        exception_type, error_message = self._extract_exception(raw)
        json_exception, json_message = self._extract_json_error(raw)
        exception_type = exception_type or json_exception
        error_message = error_message or json_message
        frames, frame_format = self._extract_frames(raw)
        suspect_files = list(dict.fromkeys(frame.file for frame in frames if frame.file))

        # Python tracebacks list callers before the innermost raising frame; JVM/V8,
        # Go and native traces conventionally list the top frame first.
        failure_frame = (frames[-1] if frame_format == "python" else frames[0]) if frames else None
        failure_point = None
        if failure_frame:
            failure_point = FailurePoint(
                file=failure_frame.file,
                class_name=failure_frame.class_name,
                method=failure_frame.function,
                line=failure_frame.line,
            )

        evidence: list[str] = []
        if exception_type:
            evidence.append(f"Detected exception/error type: {exception_type}.")
        if error_message:
            evidence.append(f"Extracted error message: {error_message[:300]}")
        if failure_frame:
            loc = failure_frame.file + (f":{failure_frame.line}" if failure_frame.line else "")
            evidence.append(f"Likely failure point: {loc}" + (f" in {failure_frame.function}" if failure_frame.function else ""))
        if frames:
            evidence.append(f"Parsed {len(frames)} stack frame(s) using {frame_format} format.")
        else:
            evidence.append("No supported stack-frame signature was found in the supplied log text.")

        # Transparent evidence coverage score, not a calibrated probability.
        confidence = 0.10
        if exception_type: confidence += 0.25
        if error_message: confidence += 0.10
        if frames: confidence += 0.30
        if failure_frame and failure_frame.line is not None: confidence += 0.10
        if len(frames) >= 2: confidence += 0.10
        if frame_format != "unknown": confidence += 0.05
        confidence = round(min(1.0, confidence), 2)

        logger.info("Log analysis complete: exception=%s frames=%d format=%s confidence=%.2f",
                    exception_type, len(frames), frame_format, confidence)
        return LogAnalysisResult(
            has_stack_trace=bool(frames),
            detected_format=frame_format, frame_count=len(frames),
            analysis_summary=self._summary(exception_type, failure_point, len(frames), frame_format),
            exception_type=exception_type,
            error_message=error_message,
            stack_frames=frames,
            suspect_files=suspect_files,
            technical_evidence=evidence,
            failure_point=failure_point,
            code_path=frames,
            confidence_score=confidence,
        )

    @staticmethod
    def _extract_json_error(text: str) -> tuple[Optional[str], Optional[str]]:
        import json
        for line in text.splitlines():
            candidate = line.strip()
            if not candidate.startswith("{"):
                continue
            try:
                payload = json.loads(candidate)
            except (ValueError, TypeError):
                continue
            if not isinstance(payload, dict):
                continue
            exception = next((payload.get(key) for key in JSON_ERROR_KEYS if isinstance(payload.get(key), (str, dict))), None)
            message = next((payload.get(key) for key in JSON_MESSAGE_KEYS if isinstance(payload.get(key), str)), None)
            if isinstance(exception, dict):
                message = message or exception.get("message")
                exception = exception.get("type") or exception.get("name")
            if exception or message:
                return (str(exception) if exception else None, str(message) if message else None)
        return None, None

    @staticmethod
    def _summary(exception_type, failure_point, frame_count, frame_format) -> str:
        parts = []
        if exception_type:
            parts.append(f"Detected {exception_type}")
        if failure_point:
            location = failure_point.file or "unknown file"
            if failure_point.line is not None:
                location += f":{failure_point.line}"
            parts.append(f"likely failing at {location}")
        if frame_count:
            parts.append(f"traced {frame_count} frame(s) in {frame_format} format")
        return "; ".join(parts) + "." if parts else "Insufficient structured evidence to identify a failure location."

    def _extract_exception(self, text: str) -> tuple[Optional[str], Optional[str]]:
        php_fatal = re.search(r'PHP\s+Fatal\s+error:\s*(?:Uncaught\s+)?(?P<type>[\w\\]+)(?::\s*(?P<msg>[^\n]+))?', text, re.IGNORECASE)
        if php_fatal:
            return php_fatal.group("type"), php_fatal.group("msg")
        # Mozilla/Gecko error identifiers are stable diagnostic types even when
        # the report does not use a language-native Exception class.
        native_error = re.search(r'\b(NS_ERROR_[A-Z0-9_]+)\b(?:\s+at\s+[^\n]+)?', text)
        if native_error:
            return native_error.group(1), None
        assertion = re.search(r'(?im)^\s*Assertion failure:\s*(.+)$', text)
        if assertion:
            return "AssertionFailure", assertion.group(1).strip()
        for pattern in EXCEPTION_PATTERNS:
            match = pattern.search(text)
            if not match:
                continue
            groups = match.groupdict()
            exception_type = groups.get("type") or (match.group(1) if match.lastindex else None)
            message = groups.get("msg")
            if exception_type:
                return exception_type.strip(), message.strip() if message else None
        # Some loggers prefix the exception with timestamp / level / logger name.
        prefixed = re.search(r'\b([\w.$]+(?:Exception|Error|Fault|Failure))(?::\s*([^\n]+))?', text)
        if prefixed:
            return prefixed.group(1), prefixed.group(2).strip() if prefixed.group(2) else None
        return None, None

    def _extract_frames(self, text: str) -> tuple[list[StackFrameInfo], str]:
        frames: list[StackFrameInfo] = []
        assertion_location = re.search(r'(?im)^\s*Assertion failure:.*?\bat\s+(?P<file>[\w./-]+\.(?:cpp|cc|c|h)):(?P<line>\d+)', text)
        if assertion_location:
            frames.append(StackFrameInfo(file=_clean_path(assertion_location.group("file")),
                line=int(assertion_location.group("line"))))
        for pattern in (MOZILLA_FRAME_RE, MOZILLA_LOCATION_RE):
            for match in pattern.finditer(text):
                func = match.group("func")
                frames.append(StackFrameInfo(
                    file=_clean_path(match.group("file")), line=int(match.group("line")),
                    function=func.rsplit("::", 1)[-1],
                    class_name=func.rsplit("::", 1)[0] if "::" in func else None,
                ))
        if frames:
            # The assertion source location is the failure site and precedes
            # subsequent native call frames in this report format.
            return frames, "mozilla_cpp"
        for match in MOZILLA_BARE_LOCATION_RE.finditer(text):
            frames.append(StackFrameInfo(file=_clean_path(match.group("file")), line=int(match.group("line"))))
        if frames:
            return frames, "mozilla_cpp"

        # Some JVM crash reports place the exception and first frame on the
        # same line. Preserve that leading frame before ordinary `at` entries.
        inline_java_frames = []
        inline_java = re.compile(r'(?P<func>[\w.$]+)\((?P<file>[^():]+\.(?:java|kt|scala)):(?P<line>\d+)\)')
        for match in inline_java.finditer(text):
            func = match.group("func")
            inline_java_frames.append(StackFrameInfo(
                file=_clean_path(match.group("file")), line=int(match.group("line")),
                function=func.rsplit(".", 1)[-1],
                class_name=func.rsplit(".", 1)[0] if "." in func else None,
            ))
        for match in PYTHON_FRAME_RE.finditer(text):
            frames.append(StackFrameInfo(file=_clean_path(match.group("file")),
                line=int(match.group("line")), function=match.group("func"),
                code_context=match.group("code").strip() if match.group("code") else None))
        if frames:
            return frames, "python"

        for match in JAVA_FRAME_RE.finditer(text):
            location = match.group("location")
            file_name, line = self._parse_file_line(location)
            func = match.group("func")
            class_name = func.rsplit(".", 1)[0] if "." in func else None
            frames.append(StackFrameInfo(file=file_name or location, line=line,
                function=func.rsplit(".", 1)[-1], class_name=class_name))
        # Some bug trackers collapse the exception and first frame onto one line:
        # "NullPointerException at a.b.Service.run(Service.java:42)".
        if not frames:
            inline_java = re.compile(r'(?P<func>[\w.$]+)\((?P<file>[^():]+\.java):(?P<line>\d+)\)')
            for match in inline_java.finditer(text):
                func = match.group("func")
                frames.append(StackFrameInfo(file=_clean_path(match.group("file")),
                    line=int(match.group("line")), function=func.rsplit(".", 1)[-1],
                    class_name=func.rsplit(".", 1)[0] if "." in func else None))
        if inline_java_frames:
            # Inline JVM traces (common in Jira exports) can contain several
            # `at ... (File.java:line)` entries on one physical line. The
            # dedicated scan preserves their original left-to-right order.
            return inline_java_frames, "java"
        if frames:
            return frames, "java"

        for pattern, fmt in ((JS_FRAME_RE, "javascript"), (FIREFOX_FRAME_RE, "javascript")):
            for match in pattern.finditer(text):
                func = (match.groupdict().get("func") or "").strip() or None
                frames.append(StackFrameInfo(file=_clean_path(match.group("file")),
                    line=int(match.group("line")), function=func))
            if frames:
                return frames, fmt

        for match in CPP_FRAME_RE.finditer(text):
            frames.append(StackFrameInfo(file=_clean_path(match.group("file")),
                line=int(match.group("line")), function=match.group("func").strip() or None))
        if frames:
            return frames, "cpp"

        for match in GO_FRAME_RE.finditer(text):
            frames.append(StackFrameInfo(file=_clean_path(match.group("file")), line=int(match.group("line"))))
        if frames:
            return frames, "go"

        for match in DOTNET_FRAME_RE.finditer(text):
            func = match.group("func")
            frames.append(StackFrameInfo(file=_clean_path(match.group("file")),
                line=int(match.group("line")), function=func.rsplit(".", 1)[-1],
                class_name=func.rsplit(".", 1)[0] if "." in func else None))
        if frames:
            return frames, "dotnet"

        for match in PHP_FRAME_RE.finditer(text):
            frames.append(StackFrameInfo(file=_clean_path(match.group("file")),
                line=int(match.group("line")), function=match.group("func").strip()))
        if frames:
            return frames, "php"

        for match in RUBY_FRAME_RE.finditer(text):
            frames.append(StackFrameInfo(file=_clean_path(match.group("file")),
                line=int(match.group("line")), function=match.group("func")))
        if frames:
            return frames, "ruby"

        for match in RUST_FRAME_RE.finditer(text):
            frames.append(StackFrameInfo(file=_clean_path(match.group("file")),
                line=int(match.group("line")), function=match.group("func").strip() or None))
        return (frames, "rust") if frames else ([], "unknown")

    @staticmethod
    def _parse_file_line(location: str) -> tuple[Optional[str], Optional[int]]:
        match = re.match(r'(.+?):(\d+)(?::\d+)?$', location)
        if match:
            return _clean_path(match.group(1)), int(match.group(2))
        # Native methods / unknown source locations may have only a filename.
        return (_clean_path(location), None) if location and location != "Native Method" else (None, None)
