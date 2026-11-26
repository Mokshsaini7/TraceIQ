# Milestone 2.4 — Stack Trace & Log Forensics Agent

## Goal

Upgrade TraceIQ's existing `LogAnalysisAgent` into a deterministic, evidence-first forensic parser that can normalize application exceptions, error messages, source locations, and call paths across common runtime and logging formats. The agent remains part of the existing diagnosis pipeline; it does not execute submitted code or require an external LLM.

## Supported input families

- Python traceback (`File ..., line ..., in ...`)
- JVM stack traces (Java/Kotlin/Scala `at package.Class.method(File.java:line)`)
- Node.js/V8 and browser JavaScript frames
- Firefox `function@url:line:column` frames
- .NET frames (`in file.cs:line N`)
- Go panic locations (`file.go:line +0x...`)
- Rust source locations (`at file.rs:line:column`)
- C/C++ GDB frames (`#0 ... at file.cpp:line`)
- Ruby backtraces (`from file.rb:line:in ...`)
- PHP traces (`#0 file.php(line): Class->method()`)
- JSON structured logger records containing `exception`, `exception_type`, `error_type`, `type`, `message`, `error`, `error_message`, or `msg`
- Timestamp/level-prefixed log lines containing recognizable exception signatures

Parser support is best-effort: unknown/custom formats are retained as evidence, but no source location is fabricated.

## Structured output contract

`LogAnalysisResult` is the canonical Pydantic response and is persisted under `diagnosis_report.log_analysis_result` and in `LogAnalysisAgent` execution telemetry.

| Field | Type | Meaning |
|---|---|---|
| `has_stack_trace` | boolean | True only when at least one frame was parsed |
| `detected_format` | string | Parser family (`python`, `java`, `javascript`, `dotnet`, `go`, `rust`, `cpp`, `ruby`, `php`, `unknown`) |
| `frame_count` | integer | Number of normalized frames |
| `analysis_summary` | string/null | Human-readable evidence summary |
| `exception_type` | string/null | Detected exception/error type |
| `error_message` | string/null | Extracted exception/log message |
| `stack_frames` | array | Ordered normalized call frames |
| `suspect_files` | string array | Unique source files in observed frames |
| `technical_evidence` | string array | Explainable evidence used by downstream agents |
| `failure_point` | object/null | Most likely failing frame (`file`, `class_name`, `method`, `line`) |
| `code_path` | array | Ordered stack frames representing the observed path |
| `confidence_score` | number 0–1 | Evidence-coverage score; **not** a calibrated probability |

Each frame contains `file`, optional `line`, `function`, `class_name`, and `code_context`.

## Failure-point and code-path policy

- Python tracebacks are ordered caller-to-callee, so the innermost (last) parsed frame is selected.
- JVM, V8, .NET, Go, C/C++, Ruby, Rust, and PHP traces conventionally put the top/throwing frame first, so the first parsed frame is selected.
- The full normalized ordered frame sequence is preserved as `code_path`; it is not silently reordered.
- Missing class, method, file, or line values remain null/unknown.

## Confidence policy

The score is transparent evidence coverage, not statistical confidence. It increases when an exception type, message, frames, source line, multiple frames, and a recognized format are available. It must not be presented as a probability that the diagnosis is correct.

## Frontend

The submission forensics panel now surfaces detected parser format, parsed frame count, a concise analysis summary, exception type, extracted message, likely failure point, ordered frames, suspect files, and the evidence-coverage score.

## Validation

Automated tests cover Python, Java, Node.js, Go, C/C++, .NET, Ruby, PHP, timestamp-prefixed logs, JSON structured logs, empty inputs, and output-contract bounds. Run:

```bash
cd backend
PYTHONPATH=. pytest -q
```

The frontend has no bundled `node_modules` in the source archive. Install dependencies with `cd frontend && npm ci`, then validate with `npm run build`.

## Production hardening notes

- Treat uploaded logs as untrusted data; never execute stack-trace snippets.
- Apply request-size limits and redact secrets/tokens before persistence in production.
- Add parser fixtures from your actual runtime versions before enabling strict SLAs.
- Keep parser confidence distinct from root-cause confidence and overall diagnosis confidence.
- For proprietary/custom formats, add a parser with fixture-based regression tests rather than broad permissive regexes.
