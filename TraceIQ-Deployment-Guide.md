# TraceIQ Deployment Guide

This guide reflects the supplied repository implementation. Deployment has not been executed as part of this audit.

## 1. Architecture

- Frontend: React/Vite static build served by Nginx.
- Backend: FastAPI/Uvicorn.
- Database: PostgreSQL with pgvector extension (Docker image `pgvector/pgvector:pg16`).
- Optional LLM refinement: Anthropic API, enabled only when `ANTHROPIC_API_KEY` is configured.
- Embeddings: SentenceTransformers model when available; deterministic hash-vector fallback otherwise.

The frontend and backend are separate services. Netlify can host the frontend static build, but it does not host this Python API as a normal static site.

## 2. Local setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- npm
- PostgreSQL 16 with pgvector, or SQLite for local development

### Backend

```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Create `backend/.env` from `backend/.env.example`, then configure:

```dotenv
APP_ENV=development
DEBUG=true
DATABASE_URL=sqlite:///./bugdiag_local.db
UPLOAD_DIR=./uploads
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

Start the API:

```bash
uvicorn bugdiag.main:app --reload --host 127.0.0.1 --port 8000
```

Run from the `backend` directory. API documentation: `http://localhost:8000/docs`. Health endpoint: `http://localhost:8000/api/v1/health`.

### Frontend

Create `frontend/.env` from `frontend/.env.example`:

```dotenv
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Then:

```bash
cd frontend
npm ci
npm run build
npm run dev
```

Open `http://localhost:5173`.

Vite environment values are compiled into the static frontend at build time. Set the production API URL before running the production build.

## 3. Docker Compose deployment

At repository root:

```bash
cp .env.example .env
```

Edit `.env` and replace `POSTGRES_PASSWORD` with a long random password. Use a password composed of URL-safe characters for the current SQLAlchemy URL interpolation. Set the frontend's API URL to the externally reachable backend base URL, for example:

```dotenv
APP_ENV=production
DEBUG=false
POSTGRES_USER=traceiq
POSTGRES_PASSWORD=REPLACE_WITH_A_LONG_RANDOM_URL_SAFE_VALUE
POSTGRES_DB=traceiq_db
POSTGRES_PORT=5432
VITE_API_BASE_URL=https://api.example.com/api/v1
CORS_ORIGINS=https://traceiq.example.com
```

Build and start:

```bash
docker compose config
docker compose up --build -d
docker compose ps
docker compose logs -f backend
```

The frontend container serves Nginx on port 3000 by default, and the backend publishes port 8000. Put a TLS reverse proxy/load balancer in front of these services for public deployments. Do not expose PostgreSQL's port publicly unless required and firewalled.

Stop services:

```bash
docker compose down
```

Keep database data in the named `pgdata` volume. `docker compose down -v` deletes that persistent volume and should not be used unless intentionally resetting the database.

## 4. Separate frontend hosting (e.g. Netlify)

- Build command: `npm run build`
- Publish directory: `dist`
- Base/root directory: `frontend`
- Build environment variable: `VITE_API_BASE_URL=https://api.example.com/api/v1`
- Ensure SPA fallback redirects unknown routes to `/index.html`. Netlify equivalent: add a redirect rule `/* /index.html 200`.
- Configure backend `CORS_ORIGINS` to include the exact deployed frontend origin.
- Deploy the FastAPI backend separately to a Python-capable host/container service.
- Configure the backend's persistent PostgreSQL URL, upload storage, and optional Anthropic key on the backend host.

Do not set `VITE_API_BASE_URL` to `http://localhost:8000` in a deployed frontend; visitors' browsers would call their own computers.

## 5. Database and migrations

The repository includes Alembic configuration but the supplied archive contains no migration revision scripts. The application currently initializes tables with SQLAlchemy `Base.metadata.create_all` during startup. This is adequate for initial local bootstrap but is not a replacement for a reviewed migration strategy when evolving a production schema.

Before production schema changes, add and test Alembic revisions against a backup/staging database. Do not assume `create_all` alters existing tables to match model changes.

## 6. Diagnosis workflow

1. Create a submission with `POST /api/v1/submissions`.
2. Upload any attachments with `POST /api/v1/submissions/{submission_id}/attachments`.
3. Trigger the five-agent pipeline with `POST /api/v1/diagnosis/trigger` and JSON:
   `{"submission_id":"<id>","force_reanalysis":false}`.
4. Retrieve the report with `GET /api/v1/diagnosis/{submission_id}`.
5. Retrieve agent execution logs with `GET /api/v1/diagnosis/{submission_id}/logs`.

The current pipeline executes synchronously in the API request. Large submissions or slow external LLM calls may occupy a worker. A durable task queue is a future architecture improvement, not a current feature.

## 7. Security and production constraints

- This repository snapshot has no login, JWT/session issuance, or authorization. Do not expose it as a public multi-user application until these are implemented and tested.
- Restrict access at the network/reverse-proxy layer in the interim.
- Never commit `.env` or real credentials.
- Keep `DEBUG=false` in production.
- Set exact CORS origins; avoid wildcard origins when credentials or sensitive browser sessions are introduced.
- Restrict database network access and use strong unique credentials.
- Persist and back up PostgreSQL data and uploaded files.
- Configure the optional LLM provider deliberately; diagnosis context may leave the application when this integration is enabled.
- Hash-vector fallback is not a semantic embedding model. Health status should be checked after deployment.
- Configure log retention and avoid logging source-code contents or secrets.

## 8. Post-deployment smoke test

```bash
curl -fsS https://api.example.com/
curl -fsS https://api.example.com/api/v1/health
```

Then use `/docs` or an API client to create a bug, trigger analysis, retrieve its report, and confirm five agent execution records. Verify browser navigation refreshes correctly on nested frontend routes.

## 9. Rollback

- Keep the previous backend and frontend image/build available.
- Back up PostgreSQL before schema changes.
- Roll back application images independently from database changes.
- Do not delete the `pgdata` volume during application rollback.


## 5. Milestone 2 intake-context migration

The automatic intake orchestration persists a versioned `bug_analysis_contexts` record. Fresh local SQLite installations create the SQLAlchemy metadata at startup. For Alembic-managed deployments, inspect and apply the included revision before rolling out the matching API/frontend release:

```bash
cd backend
alembic upgrade head
```

Deploy the backend and frontend from the same release. New submissions invoke Triage and Log Analysis automatically; the complete five-agent diagnosis remains an explicit trigger. Retrieve the durable handoff with `GET /api/v1/submissions/{submission_id}/context`. See `TraceIQ-Milestone-2.5-Multi-Agent-Orchestration.md` and `TraceIQ-Milestone-2.6-Final-Evaluation-Release-Notes.md`.
