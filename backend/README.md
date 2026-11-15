# TraceIQ Backend

FastAPI service for bug submissions, attachments, five-agent diagnosis, and historical defect retrieval.

## Run locally (Windows PowerShell)

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev,ml]"
uvicorn bugdiag.main:app --reload --host 127.0.0.1 --port 8000
```

The default local database is SQLite. Set `DATABASE_URL` to a PostgreSQL connection string to use PostgreSQL/pgvector. The first SentenceTransformer model load may download model files. If the real model cannot load, `/api/v1/health` reports degraded embedding mode and hybrid retrieval falls back to BM25. The deterministic hash fallback is not treated as semantic retrieval.

## Read-only smoke test

From the repository root, with both services running: `py scripts/traceiq_smoke_test.py`.

## Tests

```powershell
pytest -q
```

## API flow

1. `POST /api/v1/submissions` creates a submission only.
2. Upload each file with `POST /api/v1/submissions/{id}/attachments`.
3. `POST /api/v1/diagnosis/trigger` starts the pipeline after all files are uploaded.
4. Read `GET /api/v1/diagnosis/{id}` and `GET /api/v1/diagnosis/{id}/logs`.

This order is important: attachments must be saved before diagnosis begins.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/health` | Database and embedding status |
| POST / GET | `/api/v1/submissions` | Create / list bug reports |
| GET / DELETE | `/api/v1/submissions/{id}` | Read / delete a submission |
| POST | `/api/v1/submissions/{id}/attachments` | Upload an attachment |
| POST | `/api/v1/diagnosis/trigger` | Run or re-run the pipeline |
| GET | `/api/v1/diagnosis/{id}` | Read diagnosis report |
| GET | `/api/v1/diagnosis/{id}/logs` | Read agent execution records |
| POST | `/api/v1/search/historical` | Search the loaded historical defects |
| GET | `/api/v1/search/evaluate` | Evaluate retrieval (requires a suitable labelled evaluation set) |
| GET | `/api/v1/knowledge-base/stats` | Read knowledge-base counts |

## Optional LLM refinement

Set `ANTHROPIC_API_KEY` to enable optional root-cause explanation refinement. The model output is accepted only when it cites IDs from the retrieved historical records. If no key is set, the deterministic evidence-first analysis is used.


## Authentication status

The supplied application snapshot does not implement user registration, login, JWT/session issuance, or protected API routes. The frontend must therefore not be represented as an authenticated multi-user product. `SECRET_KEY` is reserved for a future authentication implementation and has no default credential. Deploy this version behind an appropriately restricted network or reverse proxy until authentication and authorization are implemented and tested.

## Diagnosis lifecycle

Submission creation persists a report in `pending` state. The client may upload attachments, then calls `POST /api/v1/diagnosis/trigger` with the submission ID. The pipeline runs synchronously in the API process in this version and persists the report plus one execution record per agent. `GET /api/v1/diagnosis/{submission_id}` returns the persisted report; the logs endpoint returns its execution history. This is not a background queue or asynchronous job architecture.
