# TraceIQ Milestone 2.3 — End-to-End Bug Triage Upgrade

## Scope
This upgrade builds on the existing Milestone 2.1 deterministic TriageAgent and keeps the five-agent diagnosis architecture. It aligns submission, backend validation, triage output, report filtering, and acceptance tests.

## Severity rubric
| Level | Assessment criteria | Typical examples |
|---|---|---|
| Critical | Production-wide outage; all/most users unable to use a core service; irreversible/widespread data loss or corruption; severe actively exploitable security exposure | Production service down, active RCE/authentication bypass, widespread data corruption |
| High | Major workflow blocked; serious crash/deadlock; significant security/data risk without established system-wide impact | Login/payment workflow fails, queue stops, worker OOM |
| Medium | Functional defect with limited scope, workaround, intermittent effect, or impact not established | Single endpoint incorrect, intermittent timeout, isolated null dereference |
| Low | Cosmetic/presentation-only issue without core workflow impact | Alignment, spacing, font or visual defect |

## Priority rubric
Priority expresses response order and urgency, not technical severity alone.

| Priority | Response target | Criteria |
|---|---|---|
| P1 | Immediate | Critical severity OR explicit active production incident, active exploitation, customer-facing outage, SLA breach, release blocker/today, regulatory deadline, or in-progress data breach |
| P2 | Urgent | High severity with a major workflow or serious technical failure; address in the urgent engineering queue |
| P3 | Normal | Medium severity without an explicit urgent deadline; schedule in normal development |
| P4 | Later | Low/cosmetic impact; schedule when capacity permits |

The agent does not blindly trust reporter-selected severity or priority. Those values are retained as context, while the assessment is independently derived from impact, scope, urgency and technical evidence. An urgent medium issue may be P1; severity and priority are deliberately independent.

## Component identification
The agent prefers stack-frame file paths and symbols, then uses explicit domain/module indicators. It returns `Unknown` when evidence is insufficient rather than inventing a module.

## Confidence and explanation
`confidence_score` is a deterministic evidence-coverage score in `[0,1]`, not a calibrated probability. The report includes separate severity, priority and component explanations, evidence, and missing-information prompts. `completeness_score` describes report completeness separately from classification confidence.

## Structured output
`TriageResult` (Pydantic; strict extra fields forbidden):
- `category: str`
- `severity: critical | high | medium | low`
- `priority: p1 | p2 | p3 | p4`
- `affected_component: str`
- `programming_language: str`, `framework: str | null`
- `confidence_score: number [0,1]`
- `reasoning: { severity_reason, priority_reason, component_reason, evidence[] }`
- `missing_information: string[]`
- `completeness_score: number [0,1]`

The validated object is persisted in `DiagnosisReport.triage_result` and returned by the existing diagnosis API.

## Frontend/backend changes
- Bug submission captures a meaningful observed-behaviour/impact description separately from source and log evidence.
- Submission form exposes reporter severity and requested priority as advisory context.
- Backend request schema restricts reporter labels to the supported enum values.
- Bug report list exposes all four severity levels and a P1–P4 priority filter/badge.
- The existing report detail view exposes severity, priority, component, confidence, evidence, reasoning and missing information.

## Verification
Run from `backend/`:
```bash
python -m pytest -q
python -m compileall -q bugdiag tests
```
Historical Mozilla, Eclipse and Apache samples are smoke-tested for valid output and component identification. These checks are not labelled accuracy metrics. Synthetic cases assert known impact/urgency expectations; real deployment should add expert-labelled validation and organization-specific SLA policy.

## Operational caveats
- Rules are transparent heuristics; novel phrasing and domain-specific architecture can reduce accuracy.
- Confidence is evidence coverage, not probability.
- Priority rules should be tuned to the organization's incident policy, SLA and release calendar.
