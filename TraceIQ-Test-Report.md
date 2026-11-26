# TraceIQ Test and Verification Report

**Date:** 25 November 2026  
**Release:** Final Milestone 2 demo package (M2.1–M2.6)

## Results

| Validation | Result | Evidence |
|---|---|---|
| Python syntax compilation | PASS | `python -m compileall -q backend/bugdiag backend/tests backend/scripts` |
| Backend automated suite | PASS | **64 passed** (`cd backend && pytest -q`) |
| Triage historical severity / priority / component | PASS | 10/10 each against documented manual annotations |
| Log Analysis historical exception / failure point / code path | PASS | 10/10 each against documented manual annotations |
| Synthetic log formats | PASS | 8/8 for exception type, failure point, code path, and format |
| Input-shape resilience | PASS | Description-only, missing logs, logs without description, messy logs |
| Current benchmark mismatches | PASS | 0 remaining mismatches in the checked-in labelled set |
| Frontend clean install/build | NOT VERIFIED | `npm ci --offline` could not find a locked package in local npm cache (`ENOTCACHED`) |
| Browser-to-backend end-to-end | NOT RUN | Requires running local services and browser interaction |
| Docker/PostgreSQL deployment | NOT RUN | Requires Docker and PostgreSQL service |

## Repeatable commands

```bash
python -m compileall -q backend/bugdiag backend/tests backend/scripts
cd backend && pytest -q
cd ..
python backend/scripts/run_agent_benchmark.py
cd frontend && npm ci && npm run build
```

## Evaluation details

The benchmark reads the 10 bundled Milestone 1 seed defects (Mozilla, Apache, Eclipse) and eight additional synthetic log-format fixtures. Gold annotations are maintained in `datasets/benchmarks/milestone2_gold_labels.json`. The raw historical source files do not provide normalized severity/priority labels for every record; those fields are manually annotated for this evaluation. The 100% values in the report are agreement on this small regression set only, not a statistically meaningful production accuracy guarantee.

Detailed results: `reports/MILESTONE_2_AGENT_EVALUATION.md` and `reports/milestone2_agent_benchmark.json`.

## Full-stack verification still required

On a developer machine with npm registry access, install frontend dependencies and run the production build. Then follow `DEMO_GUIDE.md` to exercise submission, automatic intake orchestration, context retrieval, full diagnosis, and UI rendering. Production database, Docker, authentication/authorization, background job durability, monitoring, and operational hardening are separate deployment checks.
