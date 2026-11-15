# TraceIQ Backend Reliability Report

**Prepared:** 14 November 2026  
**Project:** TraceIQ — Intelligent Bug Diagnosis Platform  
**Review basis:** `TraceIQ-updated-v2(1).zip` uploaded for this review

## 1. Short summary

TraceIQ has a real FastAPI backend, a React frontend, a database layer, five Python diagnosis agents, and a historical-defect search pipeline. The project has a useful foundation, but the original code could show demo information when the backend was unavailable. Some report wording also made weak evidence sound certain.

I made a reliability-focused update. The main rule is simple: **if TraceIQ cannot prove that something happened, it must not say that it happened.**

This is an improved development build, not a claim that the product is perfect or production-certified. Real accuracy still needs to be measured against labelled bug reports and tested on the machine where the project will run.

## 2. Important problems found and changes made

| Area | Problem in the uploaded project | Change in this build |
|---|---|---|
| Frontend API client | API errors could return sample submissions, reports, search results, and a fake healthy status. | Removed silent mock-data fallbacks from the live API client. API errors now reach the UI. |
| Submission flow | The backend started diagnosis when a submission was created, before attachments were uploaded. | Submission creation now only saves the report. The frontend uploads attachments first, then explicitly starts diagnosis. |
| Root-cause wording | A low historical match could be described as a strong match and increase confidence. | Historical matches below 78% are described as weak leads. Root causes are written as hypotheses. |
| Confidence | Confidence values looked like calibrated probabilities even though they came from fixed rules. | The score is conservative evidence coverage, capped at 80%, and is not described as a probability. |
| Embedding fallback | A deterministic hash fallback could be mistaken for real semantic embeddings. | Dense search is disabled when the real SentenceTransformer model is unavailable. Health reports degraded embedding mode. Fallback vectors use a separate model name so they are not mixed with real model vectors. |
| Retrieval filters | If a requested language/source filter returned no records, the old code searched the unfiltered corpus instead. | Filters are now respected. No matching records means no results. |
| Remediation | Generic code diffs could be invalid for the detected programming language. Dataset resolution text could be called a verified fix. | Removed invented code diffs. Historical resolution text is shown as an unverified note. Suggestions are investigation guidance and must be reviewed and tested. |
| Health check | The health response could look healthy while using fallback services. | Health now distinguishes healthy and degraded database/embedding states and reports configured vs active database type. |
| UI metrics | Missing values could display made-up 92%/94% values; completeness fractions could be shown as tiny percentages. | Removed fabricated metric defaults and display completeness as a percentage of the 0–1 score. |
| Architecture labels | UI and API descriptions claimed LangGraph, Qdrant, 200k+ records, and model details that did not match the source code. | Updated key architecture descriptions to reflect the actual sequential Python agents, PostgreSQL/pgvector, BM25, and currently loaded records. |
| Docker database | The compose file used plain PostgreSQL while the setup script requests the pgvector extension. | Switched the database image to the pgvector-enabled PostgreSQL 16 image. |

## 3. Current real architecture

1. React 18 + TypeScript + Vite frontend.
2. FastAPI backend with SQLAlchemy and Pydantic.
3. SQLite for local development by default; PostgreSQL with pgvector is supported.
4. Five sequential Python agents: Triage, Log Analysis, Root Cause, Duplicate Detection, and Remediation.
5. BM25 keyword retrieval and optional SentenceTransformer vector retrieval, combined through reciprocal-rank fusion when compatible vectors are available.
6. Optional Anthropic explanation refinement. It is disabled unless `ANTHROPIC_API_KEY` is configured.

The code in this build does **not** implement LangGraph or Qdrant. The user interface and project documentation should not claim those technologies are active.

## 4. How to understand the scores

- **Completeness:** A 0–1 score describing how much useful information the submitted report contains. The UI converts it to a percentage. It is not the chance that the diagnosis is correct.
- **Root-cause evidence score:** A conservative score based on whether the report contains an exception, parsed stack frames, an error message, enough description, and a strong historical reference. It is not a statistically calibrated probability.
- **Historical relevance:** A ranking signal from the current retrieval pipeline. It is not a probability that two bugs are identical. A match below 78% is not called a strong historical match by the root-cause agent.
- **Verified fixes:** This build does not claim historical text as an independently tested patch. Historical notes and suggested investigation steps are shown as unverified.

## 5. Tests run during this review

### Passed

The following source-level checks passed in the review environment:

```text
python -m compileall -q backend/bugdiag backend/tests
```

Focused unit tests passed:

```text
8 passed
```

These cover triage classification, Python and Java stack-trace parsing, exception-only log handling, conservative historical-match wording, completeness score bounds, and the rule that historical resolution text is not marked as a verified patch.

### Not completed in this environment

- The full backend test suite could not be collected because `rank-bm25` is not installed in the review environment. Installing dependencies was blocked because the environment could not reach the Python package index.
- The frontend production build could not be completed because `node_modules` was not present and `npm ci --offline` could not find all packages in the local npm cache. Network access to the npm registry was unavailable.
- Docker services were not started in this review environment.
- No live browser-to-backend test was possible here.

These are verification limits, not proof that those parts of the source code fail. Run the complete commands below on your Windows machine after installing dependencies.

## 6. Windows setup and verification

### Backend

Open PowerShell in the project folder:

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev,ml]"
uvicorn bugdiag.main:app --reload --host 127.0.0.1 --port 8000
```

The first SentenceTransformer model load may download model files. If that is unavailable, the backend will report degraded embedding mode and use BM25 for hybrid search rather than pretending the fallback is semantic search.

### Frontend

Open a second PowerShell window:

```powershell
cd frontend
npm ci
npm run build
npm run dev
```

If the frontend is hosted somewhere other than localhost, set `VITE_API_BASE_URL` to the deployed backend API URL and add the frontend origin to backend `CORS_ORIGINS`.

### Backend tests

Open a third PowerShell window:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest -q
```

### Read-only smoke test

With both services running, use:

```powershell
py scripts/traceiq_smoke_test.py
```

This checks frontend/backend reachability, OpenAPI, submissions, knowledge-base stats, architecture, database health, and embedding mode. It does not change project data.

### Manual end-to-end test

1. Open the frontend and confirm the backend indicator is healthy or degraded (never falsely healthy).
2. Submit a bug report with a real stack trace.
3. Attach a small `.log` or source file.
4. Confirm the attachment upload succeeds before diagnosis starts.
5. Confirm the diagnosis request completes and the report is saved.
6. Open Agent Execution Trace and confirm the five backend agent log records are present.
7. Check that the report shows parsed file/line evidence when the stack trace contains it.
8. Check that weak historical matches are not called strong matches.
9. Stop the backend and refresh the frontend. The app should show an API error/unavailable state, not sample results.

## 7. What is still needed before calling the project production-ready

- Run the full test suite and frontend build on the developer machine or CI.
- Add a labelled evaluation set with known root causes and duplicate pairs. Measure precision, recall, and false-positive rates.
- Add parser tests for more real-world Python, Java, JavaScript/TypeScript, and C/C++ trace formats.
- Add database migrations and test PostgreSQL/pgvector on a clean database.
- Add authentication, authorization, rate limits, request-size limits, and production secret management before public deployment.
- Test file uploads, retention, deletion, and backup/restore policies.
- Add concurrency/idempotency protection for simultaneous diagnosis requests.
- Validate all external dataset licenses, provenance, and resolution quality before making claims about the knowledge base.

## 8. Milestone status

The repository's Milestone 1 checklist marks the implementation complete. This review confirms that the core modules and documentation exist, but the earlier checklist's statement that everything was independently tested and verified is not supported by the tests that could be run in this environment.

**Recommended status: Milestone 1 implementation is present; verification is in progress.** Do not mark the milestone fully verified until the full Windows/CI test and end-to-end checklist above passes.

## 9. Final assessment

This update makes TraceIQ more honest and safer to evaluate: it no longer silently substitutes mock data for live API results, attachments are included before diagnosis, weak evidence is described carefully, and historical resolution notes are not presented as tested patches.

The next goal should be repeatable test results on the actual development machine, followed by an accuracy evaluation using known bugs. Better wording and safer scoring improve trust, but only measured results can show how accurate the diagnosis engine really is.
