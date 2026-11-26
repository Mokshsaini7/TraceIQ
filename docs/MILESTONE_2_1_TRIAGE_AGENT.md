# TraceIQ Milestone 2.1 — Intelligent First-Level Triage Agent

## Status
**Implemented and backend-verified in this candidate.** This is a deterministic, evidence-based first-level assessment, not a calibrated ML probability model.

## Responsibilities
The existing `TriageAgent` runs first in the existing sequential five-agent pipeline. It evaluates title, description, stack trace, error logs (including safely extracted text attachments), language/framework hints, reproduction steps, environment details, and expected/actual behaviour. The orchestrator persists the same validated result in `DiagnosisReport.triage_result` and the `TriageAgent` execution log.

## Classification methodology
Severity and priority are independently derived from observed impact and urgency. User-entered severity/priority are retained as submission context but are not trusted as agent conclusions.

| Severity | Meaning |
|---|---|
| Critical | Evidence of broad production outage, widespread/irreversible data impact, or severe exploitable security condition |
| High | Major workflow failure, serious crash, deadlock, or significant security/data risk without established system-wide impact |
| Medium | Functional/technical defect with limited or unproven scope |
| Low | Cosmetic or low-impact presentation defect |

| Priority | Meaning |
|---|---|
| P1 | Immediate; critical impact or explicit production/release urgency |
| P2 | Urgent; major workflow or serious technical failure |
| P3 | Normal development cycle |
| P4 | Later release; cosmetic/low-impact issue |

The rule set intentionally does not equate every exception, crash, timeout, deadlock, or OOM with Critical. Context and scope markers are required for Critical classification.

## Affected component identification
The agent first inspects source file paths and stack-frame symbols, then applies a small transparent set of module/domain indicators (authentication, payments, database, API gateway, routing, uploads, memory, profiles, notifications). If the evidence cannot identify a module, it returns `Unknown`. A stack-frame filename may identify a class/module name rather than a complete architectural subsystem.

## Confidence and completeness
`confidence_score` is a deterministic evidence-coverage score from 0.0 to 1.0, not a statistical probability. It starts at 0.20 and adds bounded evidence contributions: meaningful title (+0.08), detailed description (+0.14), stack trace (+0.22) or logs (+0.14), reproduction steps (+0.12), identified component (+0.12), recognized category (+0.08), and language (+0.04). The result is capped at 1.0.

`completeness_score` measures the presence of a detailed description, diagnostics, reproduction steps, expected behaviour, actual behaviour, and environment details. Missing evidence is listed explicitly. Unknown component and absent diagnostics are also called out in `missing_information`.

## Structured response
`TriageResult` validates:
- category and language/framework metadata
- severity: `critical | high | medium | low`
- priority: `p1 | p2 | p3 | p4`
- `affected_component`
- `confidence_score` and `completeness_score` in `[0, 1]`
- nested reasoning: severity reason, priority reason, component reason, and evidence
- missing-information list

The response remains inside the existing `triage_result` JSON column and diagnosis API response. No new table, endpoint, or agent was introduced.

## Architecture and execution flow
Bug submission → attachment text extraction → **TriageAgent** → LogAnalysisAgent → hybrid historical retrieval → RootCauseAgent → DuplicateDetectionAgent → RemediationAgent → diagnosis report persistence and API response.

The frontend retains its existing visual design. The diagnosis view now displays the assessed severity, priority, affected component, confidence, reasoning, evidence, and missing information.

## Testing methodology
`backend/tests/test_triage_agent.py` includes 14 synthetic scenarios (production outage, authentication, API error, cosmetic UI, database failure, OOM, null pointer, timeout, SQL injection, deadlock, incomplete/ambiguous reports, conflicting user labels, and unknown component), schema validation checks, and smoke evaluation against the bundled Mozilla, Eclipse, and Apache samples.

Historical smoke tests check that the existing sample records can be processed and that evidence-based fields are returned. They are not a labelled accuracy benchmark. Synthetic expected outcomes are explicit rule-based acceptance cases; passing them does not establish real-world predictive accuracy.

## Verification results
- `python -m pytest -q`: **41 tests passed** (including 21 triage-focused cases and the existing Milestone 1 regression suite).
- `python -m compileall -q bugdiag tests`: **passed**.
- Frontend production build: **unverified**. The environment had no installed `node_modules`; `npm ci` did not complete within the execution window, so no build result is claimed.
- Browser-to-backend end-to-end verification: **unverified**; requires running the application and its configured database/services.

## Known limitations
- Deterministic keyword/rule matching can miss novel phrasing and domain-specific architecture.
- Component identification is heuristic; filenames/classes are not always true subsystem boundaries.
- Confidence is an evidence score, not calibrated probability.
- Priority depends on explicit urgency wording and deterministic impact rules; organization-specific SLAs and release calendars are not integrated.
- Historical dataset smoke tests do not measure severity/priority accuracy against expert labels.
- Attachment extraction is limited to formats supported by the existing safe file parser.
