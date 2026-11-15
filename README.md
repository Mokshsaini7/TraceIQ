# TraceIQ — Intelligent Bug Diagnosis Platform

TraceIQ is a project that accepts bug reports, stack traces, logs, and diagnostic attachments. Its Python backend runs a five-agent analysis pipeline and searches the historical defect records that have been imported into its knowledge base.

The project is a development build. Diagnosis results are hypotheses and investigation guidance, not guaranteed root causes or automatically tested code fixes.

## What is implemented

- React 18, TypeScript, and Vite frontend.
- FastAPI, SQLAlchemy, and Pydantic backend.
- SQLite for local development; PostgreSQL with pgvector is supported.
- Five sequential Python agents: Triage, Log Analysis, Root Cause, Duplicate Detection, and Remediation.
- BM25 keyword retrieval and optional SentenceTransformer vector retrieval.
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

## Run tests

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest -q
```

Build the frontend:

```powershell
cd frontend
npm ci
npm run build
```

## Submission and diagnosis flow

1. Create a bug submission.
2. Upload all attachments.
3. Trigger diagnosis.
4. The backend saves the five-agent report and execution logs.
5. The frontend displays the report returned by the backend.

API errors are not replaced with local mock reports. A failed request should be shown as an error instead of appearing successful.

## Main API endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/health` | Database and embedding health |
| POST / GET | `/api/v1/submissions` | Create or list submissions |
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

## Reliability report

Read [`docs/TRACEIQ_BACKEND_RELIABILITY_REPORT.md`](docs/TRACEIQ_BACKEND_RELIABILITY_REPORT.md) for the changes made, tests that passed, checks that could not be run in this environment, and the remaining work before production deployment.

## License

MIT — see [LICENSE](LICENSE).


## Current implementation boundaries

- Diagnosis is explicitly started with `POST /api/v1/diagnosis/trigger` after submission and any attachment uploads.
- The current orchestrator executes synchronously in the API process; it is not a durable background worker/queue.
- The supplied snapshot does not implement login, user accounts, JWT issuance, or API authorization. Do not expose it publicly as a multi-user authenticated service until those controls are implemented.
- If the optional SentenceTransformers model cannot load, the deterministic hash-vector fallback is used. That fallback is not semantic model inference; hybrid retrieval can still use lexical BM25 results.
