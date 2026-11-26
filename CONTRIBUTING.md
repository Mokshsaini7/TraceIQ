# Contributing to BugDiag

Thank you for your interest in contributing to **BugDiag (Intelligent Bug Diagnosis Platform)**! This document provides guidelines and workflows for contributing to Milestone 1 and future milestones.

---

## Code of Conduct

We are committed to providing a welcoming, inclusive, and harassment-free environment for all contributors. Please adhere to respectful communication in all issues, pull requests, and discussions.

---

## Architecture & Principles

BugDiag adopts a modular 5-agent pipeline orchestrated for defect understanding and resolution assistance:
1. **Triage Agent** (Classification, priority, language detection, completeness check)
2. **Log Analysis Agent** (Stack trace parsing, exception identification, file/line extraction)
3. **Root Cause Agent** (Synthesizing technical evidence and historical defect retrieval)
4. **Duplicate Detection Agent** (Hybrid BM25 + pgvector semantic matching)
5. **Remediation Agent** (Retrieval of historical resolutions, verifiable fix guidance)

When contributing:
- Maintain separation of concerns between agents, API routes, database repositories, and RAG retrieval components.
- Do not add fake or simulated data in core algorithms; write verifiable, deterministic or model-driven logic.
- Preserve the Appnex-inspired visual identity on the frontend (`#1A2B4C` Primary Navy, `#00C2CB` Accent Cyan, soft surfaces).

---

## Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL with pgvector (or Docker Compose)

### Backend Setup
```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
uvicorn bugdiag.main:app --reload --port 8000
```

### Frontend Setup
```powershell
cd frontend
npm install
npm run dev
```

### Running Tests
- **Backend:** `pytest backend/tests -v`
- **Frontend:** `npm run test` (or `npm run build` for type checking and compilation)

---

## Branching & Pull Requests
- Create a topic branch: `git checkout -b feature/agent-enhancement`
- Ensure all tests pass and linters succeed.
- Submit a clear PR describing rationale, affected components, and testing verification.
