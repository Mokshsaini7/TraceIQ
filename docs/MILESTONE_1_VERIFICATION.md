# TraceIQ — Milestone 1 Verification Record

**Review date:** 22 November 2026  
**Scope:** M1.1 research/architecture, M1.2 system foundation, M1.3 submission workflow, M1.4 historical defect ingestion and retrieval foundation.

## Current result

**Backend verification: PASS. Frontend production build: PENDING. Full browser-to-backend verification: PENDING.**

The repository contains the documented research and architecture, a React/TypeScript submission and reporting UI, FastAPI APIs, SQLAlchemy persistence, five analysis-agent modules, and the historical-defect ingestion/retrieval pipeline. The current seed corpus contains 10 curated sample records (4 Mozilla, 4 Apache, 2 Eclipse). It is a functional seed corpus, not a large-scale benchmark.

## Changes in this verification build

- Added a local BM25-compatible fallback so the backend can still import and perform lexical retrieval when the optional `rank-bm25` package is unavailable. `rank-bm25` remains the preferred implementation and remains declared as a dependency.
- Added ingestion acceptance tests covering all three bundled seed files, field mapping, row processing, chunk creation, and embedding-record persistence.
- Updated the example similarity threshold to match the application default (`0.78`).
- Clarified the size and provenance limitations of the bundled sample datasets.
- Added `scripts/verify_milestone1.ps1` to run compilation, the backend test suite, and a clean frontend install/build on a developer machine.

## Executed checks in the review environment

| Check | Result | Evidence |
|---|---|---|
| Python source compilation | PASS | `python -m compileall -q bugdiag tests` |
| Backend tests | PASS | `python -m pytest -q` — **22 passed** |
| Seed dataset parsing | PASS | All three files parsed by acceptance tests |
| Seed dataset ingestion | PASS | 10/10 rows processed; 0 row failures in SQLite integration test |
| Chunk persistence | PASS | Chunks created for ingested seed records |
| Embedding-record persistence | PASS | One embedding record persisted per generated chunk using deterministic test embeddings |
| Frontend dependency install/build | NOT VERIFIED | `npm ci --offline` blocked because the local npm cache lacks a required package and external registry access is unavailable |
| Browser-to-API end-to-end | NOT RUN | Requires a running local frontend/backend environment |
| Docker/PostgreSQL deployment | NOT RUN | Requires Docker and a live database service |

## How to complete the remaining local verification

From PowerShell at the repository root:

```powershell
.\scripts\verify_milestone1.ps1
```

Then start the backend and frontend in separate terminals:

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev,ml]"
uvicorn bugdiag.main:app --reload --host 127.0.0.1 --port 8000
```

```powershell
cd frontend
npm ci
npm run dev
```

Open `http://localhost:5173`, submit a bug, upload any attachment before diagnosis, trigger diagnosis, open the report, and inspect agent execution logs. Also confirm that stopping the backend produces an explicit API-unavailable state rather than sample/mock results.

## Acceptance interpretation

The backend foundation and historical ingestion path now have repeatable passing automated tests. This review does **not** claim the frontend build, browser integration, PostgreSQL/pgvector deployment, or production readiness has passed. Do not mark those checks complete until they have been run successfully on the target development machine or CI.
