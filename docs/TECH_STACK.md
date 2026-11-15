# Technology Stack Specification

**Platform:** BugDiag — Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance  
**Milestone:** Milestone 1 — Foundation & Bug Understanding  

---

## Frontend

| Technology | Version | Purpose |
|---|---|---|
| **React** | 18.3.1 | Core component architecture |
| **TypeScript** | 5.7.3 | Strict end-to-end type safety |
| **Vite** | 6.1.0 | Fast HMR dev server and optimized production build |
| **Tailwind CSS** | 3.4.17 | Styling system using Appnex palette (`#1A2B4C` Navy, `#00C2CB` Cyan) |
| **React Router** | 6.28.2 | Single-page application client routing |
| **Axios** | 1.7.9 | HTTP client with automatic response interceptors |
| **Lucide React** | 0.475.0 | Premium modern icons |
| **Recharts** | 2.15.1 | Defect distribution charts & analytics |

---

## Backend

| Technology | Version | Purpose |
|---|---|---|
| **Python** | 3.11+ / 3.13 | High-performance backend runtime |
| **FastAPI** | 0.109+ | High-throughput asynchronous REST API framework |
| **Uvicorn** | 0.27+ | ASGI production web server |
| **SQLAlchemy 2** | 2.0+ | Modern declarative ORM and relational query builder |
| **Alembic** | 1.13+ | Database schema migrations |
| **PostgreSQL** | 16 | ACID-compliant relational persistence |
| **pgvector** | 0.5.1 | Vector extension for dense vector storage & indexing |
| **Pydantic v2** | 2.6+ | Data validation and settings management |
| **Sentence Transformers** | 6.3.0 | Local embedding generation (`all-MiniLM-L6-v2`) |
| **PyTorch** | 2.15.0 | Underlying deep learning inference engine |
| **rank-bm25** | 0.2.2 | BM25Okapi lexical retrieval |
| **Pandas & NumPy** | 2.3+ / 2.4+ | Dataset ingestion, vector math, and array manipulation |
| **PyPDF & Python-Multipart** | 7.0+ / 0.0.32 | Document and file upload parsing |
| **Pytest** | 9.1.1 | Automated unit and integration test suite |

---

## Infrastructure & DevOps

| Component | Tool | Purpose |
|---|---|---|
| **Containerization** | Docker & Docker Compose | Multi-container setup (PostgreSQL/pgvector, Backend, Frontend) |
| **Continuous Integration** | GitHub Actions (`.github/workflows/ci.yml`) | Automated linting, pytest execution, and frontend build verification |
| **Windows Support** | PowerShell & CMD scripts | Local setup and concurrent execution without third-party tools |
