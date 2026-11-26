# TraceIQ — Intelligent Bug Diagnosis Platform

**Final Milestone 2 demo package:** see [`DEMO_GUIDE.md`](DEMO_GUIDE.md), [`TraceIQ-Milestone-2.6-Final-Evaluation-Release-Notes.md`](TraceIQ-Milestone-2.6-Final-Evaluation-Release-Notes.md), and [`reports/MILESTONE_2_AGENT_EVALUATION.md`](reports/MILESTONE_2_AGENT_EVALUATION.md).

TraceIQ is a project that accepts bug reports, stack traces, logs, and diagnostic attachments. Its Python backend runs a five-agent analysis pipeline and searches the historical defect records that have been imported into its knowledge base.

The project is a development build. Diagnosis results are hypotheses and investigation guidance, not guaranteed root causes or automatically tested code fixes. The bundled historical seed corpus contains 10 curated sample defects; it validates the ingestion path, not large-scale retrieval accuracy.

## What is implemented

- React 18, TypeScript, and Vite frontend.
- FastAPI, SQLAlchemy, and Pydantic backend.
- SQLite for local development; PostgreSQL with pgvector is supported.
- Five sequential Python diagnosis agents: Triage, Log Analysis, Root Cause, Duplicate Detection, and Remediation.
- Automatic intake orchestration: each new bug submission invokes Triage and Log Analysis independently and persists a versioned combined context for the diagnosis pipeline and Milestone 3 consumers.
- Reproducible Milestone 2 evaluation harness using the 10 checked-in Mozilla, Apache, and Eclipse seed defects plus eight labelled stack-trace/log-format fixtures.
- BM25 keyword retrieval (using `rank-bm25` when installed, with a local BM25-compatible fallback) and optional SentenceTransformer vector retrieval.
- Optional Anthropic refinement when `ANTHROPIC_API_KEY` is configured.
- File uploads are analyzed as text. Uploaded code is not executed.

**Technology accuracy note:** The current source uses a sequential Python orchestrator, not LangGraph. It uses PostgreSQL/pgvector, not Qdrant. The repository includes sample defect datasets; the actual number of records available to search is shown by the knowledge-base statistics endpoint.

## Run locally on Windows

### 1. Start the backend

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev,ml]"
uvicorn bugdiag.main:app --reload --host 127.0.0.1 --port 8000
```

The optional `ml` dependencies install SentenceTransformers and PyTorch. The first real model load may download model files. If the model is unavailable, health reports degraded embedding mode and hybrid retrieval uses BM25 rather than pretending hash vectors are semantic embeddings.

### 2. Start the frontend

In a second PowerShell window:

```powershell
cd frontend
npm ci
npm run dev
```

Open `http://localhost:5173`. API documentation is at `http://127.0.0.1:8000/docs`.

Set `frontend/.env` or your deployment environment variable `VITE_API_BASE_URL` if the backend is not at `http://localhost:8000/api/v1`. Add the frontend origin to backend `CORS_ORIGINS`.

## Run tests and Milestone 2 evaluation

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest -q
cd ..
python backend/scripts/run_agent_benchmark.py
```

The benchmark writes machine-readable results to `reports/milestone2_agent_benchmark.json` and a mentor/demo-friendly summary to `reports/MILESTONE_2_AGENT_EVALUATION.md`. It uses manual gold labels documented in `datasets/benchmarks/milestone2_gold_labels.json`; see the report for sample-size and confidence limitations.

Build the frontend:

```powershell
cd frontend
npm ci
npm run build
```

## Submission and diagnosis flow

1. Create a bug submission. The intake orchestrator automatically invokes Triage and Log Analysis with the appropriate description, stack trace, and error-log evidence.
2. Both agent results, per-agent status, evidence gaps, and errors are saved in the versioned `analysis_context` handoff. A missing log does not block submission; one agent failure does not suppress the other result.
3. Upload any diagnostic attachments. Attachment contents are safely extracted as text during full diagnosis.
4. Trigger the full diagnosis pipeline. It reuses valid intake results and passes the Triage and Log Analysis outputs to Root Cause, Duplicate Detection, and Remediation agents.
5. The frontend displays the diagnosis report and the backend retains execution telemetry.

API errors are not replaced with local mock reports. A failed request should be shown as an error instead of appearing successful.

## Main API endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/health` | Database and embedding health |
| POST / GET | `/api/v1/submissions` | Create or list submissions; POST automatically runs intake Triage and Log Analysis |
| GET | `/api/v1/submissions/{submission_id}/context` | Fetch versioned combined Triage + Log Analysis context for downstream agents |
| POST | `/api/v1/submissions/{id}/attachments` | Upload diagnostic attachments |
| POST | `/api/v1/diagnosis/trigger` | Run or re-run the diagnosis pipeline |
| GET | `/api/v1/diagnosis/{id}` | Get the saved diagnosis report |
| GET | `/api/v1/diagnosis/{id}/logs` | Get agent execution logs |
| POST | `/api/v1/search/historical` | Search historical defects |
| GET | `/api/v1/knowledge-base/stats` | Knowledge-base record counts |

## Read-only smoke test

With the backend and frontend running, execute:

```powershell
py scripts/traceiq_smoke_test.py
```

The script checks the frontend, backend, health, OpenAPI, submissions, knowledge-base stats, and architecture endpoints. It does not create or delete data.

## Milestone 1 verification

Run the repeatable verification script from the repository root in PowerShell:

```powershell
.\scripts\verify_milestone1.ps1
```

It runs Python compilation, the complete backend pytest suite, and the frontend production build. The final Milestone 2 release currently passes 64 backend tests; the frontend production build still needs to be run on a machine with npm registry access. The M1 document records the original baseline verification. See [`TraceIQ-Test-Report.md`](TraceIQ-Test-Report.md) for final release evidence.

## Milestone 2 evaluation and improvements

The final Milestone 2 evaluation is documented in [`reports/MILESTONE_2_AGENT_EVALUATION.md`](reports/MILESTONE_2_AGENT_EVALUATION.md). Run it with `python backend/scripts/run_agent_benchmark.py`. The benchmark covers all 10 seeded historical defects, eight synthetic log-format fixtures, and description-only/log-only/missing/messy input shapes. The checked-in report is a small-sample engineering regression result, not a production accuracy claim.

## Reliability report

Read [`docs/TRACEIQ_BACKEND_RELIABILITY_REPORT.md`](docs/TRACEIQ_BACKEND_RELIABILITY_REPORT.md) for the changes made, tests that passed, checks that could not be run in this environment, and the remaining work before production deployment.

## License

MIT — see [LICENSE](LICENSE).


## Current implementation boundaries

- Triage and Log Analysis run automatically during submission intake. The complete five-agent diagnosis pipeline is explicitly started with `POST /api/v1/diagnosis/trigger` after submission and any attachment uploads.
- The current orchestrator executes synchronously in the API process; it is not a durable background worker/queue.
- The supplied snapshot does not implement login, user accounts, JWT issuance, or API authorization. Do not expose it publicly as a multi-user authenticated service until those controls are implemented.
- If the optional SentenceTransformers model cannot load, the deterministic hash-vector fallback is used. That fallback is not semantic model inference; hybrid retrieval can still use lexical BM25 results.


## First-level triage (Milestone 2.3)
See [the triage rubric and end-to-end upgrade guide](docs/MILESTONE_2_3_TRIAGE_UPGRADE.md) for severity/priority criteria, output schema, UI changes, and verification steps.

## Stack Trace & Log Forensics (Milestone 2.4)

TraceIQ's Log Analysis Agent normalizes exception types, error messages, failure locations, and ordered code paths from Python, JVM, JavaScript, .NET, Go, Rust, C/C++, Ruby, and PHP stack traces, plus common JSON structured logger records. Its structured response includes detected format, frame count, failure point, suspect files, technical evidence, and a bounded evidence-coverage score. See [the forensic agent specification](docs/MILESTONE_2_4_STACK_TRACE_FORENSICS_AGENT.md) for the output contract, parser behavior, and validation instructions.


## Milestone 2.5 — Multi-Agent Intake Orchestration

New bug submissions automatically execute the Triage and Log Analysis agents. Their versioned outputs are persisted in `bug_analysis_contexts`, returned in `analysis_context`, and exposed to downstream agents at `GET /api/v1/submissions/{submission_id}/context`. See [Milestone 2.5 documentation](TraceIQ-Milestone-2.5-Multi-Agent-Orchestration.md).


## Final Milestone 2.6 evaluation

The final benchmark and regression improvements are described in [Milestone 2.6 release notes](TraceIQ-Milestone-2.6-Final-Evaluation-Release-Notes.md). Run `python backend/scripts/run_agent_benchmark.py` to regenerate the field-level metrics. The [mentor demo guide](DEMO_GUIDE.md) contains a sample submission and suggested walkthrough.
