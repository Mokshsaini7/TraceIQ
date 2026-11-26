# Milestone 2.2 — Log Analysis Agent

**Status:** Backend implemented and automated tests passing; frontend production build and browser E2E remain unverified.

## Purpose

The existing `LogAnalysisAgent` runs as Agent 2 in TraceIQ's existing sequential five-agent diagnosis workflow. M2.2 upgrades that implementation; it does not add an agent, pipeline, endpoint, database table, or external service.

## Responsibilities

- Detect common exception/error identifiers and extract the accompanying message when present.
- Parse stack frames and normalize file, line, function/method, and class where the format exposes them.
- Identify a likely failure point using format-aware frame ordering.
- Preserve the ordered parsed frames as the probable code path.
- Return a bounded evidence-coverage confidence score and explicit technical evidence.
- Return null/empty values when the input does not support a reliable extraction.

## Supported formats

The parser currently handles common signatures for:

- Python tracebacks (`File ..., line ..., in ...`)
- JVM stack traces (Java/Kotlin-style `at ... (File.java:line)`), including single-line bug-tracker traces
- Node/V8 and Firefox JavaScript frames
- C/C++ GDB frames (`#0 ... at file:line`)
- Go panic frames (`file.go:line +0x...`)
- .NET frames (`at Namespace.Type.Method() in file.cs:line N`)
- Ruby frames (`from file.rb:line:in 'method'`)
- Rust source frames (`at file.rs:line:column`)

These are regex-based format recognizers, not full language-runtime parsers. Unrecognized or heavily customized log formats may yield partial results.

## Failure-point and code-path rules

- Python traceback frames are displayed from outer caller to innermost frame; the final parsed Python frame is selected as the likely failure point.
- JVM, JavaScript, Go, native, .NET, and Ruby traces conventionally place the top frame first; the first parsed frame is selected.
- The complete parsed sequence is returned as `code_path` and retained in `stack_frames` for compatibility.
- The selected frame is a likely failure location inferred from the trace, not proof of the defective source statement.
- Class and method are nullable because many formats do not provide both.

## Structured output

`LogAnalysisResult` preserves the Milestone 1 fields and adds:

- `failure_point`: nullable object containing `file`, `class_name`, `method`, and `line`
- `code_path`: ordered list of normalized `StackFrameInfo`
- `confidence_score`: float constrained to 0.0–1.0

The score is a deterministic evidence-coverage heuristic. It rewards detected exception type/message and parsed frames, and is not a calibrated probability or accuracy estimate.

## Integration

The orchestrator still runs Triage first, then Log Analysis, then Root Cause, Duplicate Detection, and Remediation. The structured log result is persisted through the existing diagnosis report JSON and LogAnalysisAgent execution log. Root Cause and Remediation continue consuming the existing `stack_frames`, `exception_type`, and `error_message` fields. The diagnosis API exposes the expanded Pydantic schema. The existing Stack Forensics screen was extended without changing the overall theme or navigation.

## Tests and verification

The dedicated `backend/tests/test_log_analysis_agent.py` suite covers Python, Java, JavaScript/Node, Go, C/C++, .NET, Ruby, empty input, and incomplete logs. The complete backend suite also exercises the existing submission-to-diagnosis API workflow and regression coverage.

Latest verification in this build environment:

- `python -m pytest -q`: **49 passed**
- `python -m compileall -q bugdiag tests`: **passed**
- `npm ci --ignore-scripts --no-audit --no-fund`: **timed out**; frontend production build is therefore **unverified**
- Browser E2E/live deployment: **not run**

## Known limitations

- Regex parsing cannot reliably understand every vendor-specific, obfuscated, async, or multi-cause trace.
- Exception extraction may return only the first recognizable exception and message; chained causes are not yet represented as a separate causal chain.
- Source code is not loaded or inspected, so the parser cannot prove the exact faulty statement or map optimized binaries to source.
- Confidence is a transparent heuristic and must not be interpreted as statistical probability.
- Frontend TypeScript/build and live browser workflow need local or CI verification after dependency installation.
