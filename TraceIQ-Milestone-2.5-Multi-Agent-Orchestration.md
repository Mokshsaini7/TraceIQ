# TraceIQ Milestone 2.5 — Multi-Agent Intake Orchestration

## Overview

New bug submissions now invoke the Triage Agent and Log Analysis Agent automatically in the backend. Their outputs are persisted as a versioned, machine-readable handoff contract for the downstream diagnosis pipeline and future Milestone 3 agents.

## Submission lifecycle

1. `POST /api/v1/submissions` validates and stores the submitted bug.
2. The intake orchestrator invokes `TriageAgent` with title, description, stack trace, logs, language/framework hints, reporter labels, reproduction steps, environment and expected/actual behavior.
3. The same orchestrator invokes `LogAnalysisAgent` with stack trace and error logs.
4. Each agent is isolated by its own exception boundary. A failure in one does not prevent the other from running or the bug report from being retained.
5. Outputs and statuses are stored in `bug_analysis_contexts` with schema version `1.0`.
6. The API response includes `analysis_context`; downstream services can fetch the durable contract from `GET /api/v1/submissions/{submission_id}/context`.
7. The full diagnosis pipeline reuses valid persisted triage/log outputs. If an output is missing or fails schema validation, it recalculates that agent. If attachments are added later, log analysis is rerun so attachment contents are included.

## Handoff contract (schema version 1.0)

```json
{
  "schema_version": "1.0",
  "submission_id": "<uuid>",
  "bug": {
    "title": "...",
    "description": "...",
    "stack_trace": "...",
    "error_logs": "...",
    "programming_language": "...",
    "framework": "..."
  },
  "triage": { "severity": "high", "priority": "p2", "affected_component": "..." },
  "log_analysis": { "exception_type": "...", "error_message": "...", "failure_point": {}, "code_path": [] },
  "agent_status": { "triage": "completed", "log_analysis": "completed" },
  "downstream_ready": true
}
```

The persisted record also exposes `orchestration_status` (`completed`, `partial`, or `failed`), per-agent statuses (`completed`, `incomplete`, `failed`, `pending`), raw agent outputs and an `errors` array. A missing stack trace/log is not a submission validation error: Log Analysis returns a valid low-confidence/incomplete result and records the evidence gap.

## Failure handling

- Invalid title/description or invalid severity/priority: rejected by Pydantic request validation (HTTP 422).
- Missing logs/stack trace: accepted; log analysis returns an explicit empty/incomplete result.
- Triage agent exception: captured; log analysis still runs; orchestration is partial if the other result is available.
- Log agent exception: captured; triage result is retained.
- Both agents fail: submission is retained and context status is failed.
- Persisted output fails schema validation downstream: the affected agent is recalculated.
- Context persistence failure: submission remains stored; an error is logged and the response may have a null context. The context endpoint returns 404 until a context is available.

## Frontend changes

- Dedicated optional stack-trace field, separate from free-form error logs and source code.
- Stack trace/log fields are optional; users can submit a description-only report for triage.
- Progress copy reflects automatic intake orchestration and subsequent full diagnosis.
- Submission response types include the structured `analysis_context` object.

## Verification

- Automated backend suite: 60 tests passed.
- New integration coverage submits multiple bug types, verifies automatic agent execution and durable context retrieval, checks missing-log behavior, and simulates a Triage Agent failure to verify isolation.
- Python compilation is checked as part of release validation.
- Frontend production build remains unverified in this environment because `frontend/node_modules` is not installed. Run `npm ci && npm run build` from `frontend/` before deployment.

## Deployment notes

`bug_analysis_contexts` is a new table. `Base.metadata.create_all()` creates it for fresh/local installations. Production deployments using Alembic should generate and apply a migration before rollout. Keep the API and frontend deployed from the same release so the new response field and context endpoint are available together.
