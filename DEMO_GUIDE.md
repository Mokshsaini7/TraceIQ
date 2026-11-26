# TraceIQ — Mentor Demo Guide

This guide demonstrates the complete Milestone 2 flow in the same application: bug submission → automatic Triage + Log Analysis → persisted combined context → downstream diagnosis agents → evaluation evidence.

## 1. Start the application

Backend (Python 3.11+):

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
uvicorn bugdiag.main:app --reload
```

Frontend (Node version supported by Vite 6):

```bash
cd frontend
npm ci
npm run dev
```

Open the frontend URL printed by Vite (normally `http://localhost:5173`) and the API docs at `http://localhost:8000/docs`.

## 2. Demonstrate automatic two-agent intake

Submit this sample through the Bug Submission page or `POST /api/v1/submissions`:

```json
{
  "title": "Profile update crashes when preferences are missing",
  "description": "Production users receive an error when saving a profile if optional preferences are absent. The profile update endpoint returns a server error and the user cannot complete the save operation.",
  "programming_language": "Python",
  "framework": "FastAPI",
  "stack_trace": "Traceback (most recent call last):\n  File \"/srv/api.py\", line 10, in update_profile\n    service.save(profile)\n  File \"/srv/services/profile.py\", line 42, in save\n    raise AttributeError('preferences is None')\nAttributeError: preferences is None",
  "error_logs": "2026-11-25T10:00:00Z ERROR profile update failed for request 1234",
  "reproduction_steps": "1. Create a user without optional preferences. 2. Open profile settings. 3. Change display name. 4. Save.",
  "expected_behavior": "Profile saves successfully when optional preferences are absent.",
  "actual_behavior": "The API returns an error and the profile is not saved."
}
```

The submission response includes `analysis_context`. Show that it contains:

- `triage_output`: severity, priority, component, confidence, reasoning, and evidence.
- `log_analysis_output`: exception, error message, failure point, stack frames, code path, format, and confidence.
- `triage_status`, `log_analysis_status`, `orchestration_status`, and any `errors`.

Fetch the durable downstream handoff using:

```http
GET /api/v1/submissions/{submission_id}/context
```

## 3. Demonstrate graceful evidence gaps

Submit a description-only bug (no stack trace or logs). Submission should still succeed; triage should run and log analysis should return an explicit low-confidence/incomplete result. Also try logs without a useful description to demonstrate that the forensic parser does not depend on narrative text.

## 4. Demonstrate the full diagnosis pipeline

From the submission details, trigger the full diagnosis. The diagnosis orchestrator reuses valid persisted intake outputs and passes them to Root Cause, Duplicate Detection, and Remediation. Show the final report and per-agent execution logs.

## 5. Demonstrate Milestone 2 evaluation

From the repository root:

```bash
python backend/scripts/run_agent_benchmark.py
cd backend && pytest -q
```

Open `reports/MILESTONE_2_AGENT_EVALUATION.md` for readable field-level accuracy and `reports/milestone2_agent_benchmark.json` for machine-readable results. The checked-in evaluation covers 10 curated historical defects plus eight synthetic parser fixtures. Explain the documented limitation: this is a small manually labelled regression set, not a statistically representative production benchmark.

## Demo narrative

“TraceIQ does not stop at accepting a bug report. On submission it independently triages impact and priority, parses stack traces and logs into a structured failure location and code path, persists both analyses as a versioned context, and makes that context reusable by the deeper diagnosis agents. We validate the agents against seeded historical defects and cross-language synthetic traces, record field-level accuracy, and keep the evaluation reproducible.”
