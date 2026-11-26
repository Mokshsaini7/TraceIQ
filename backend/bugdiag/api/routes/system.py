"""System architecture metadata and settings endpoint.
"""

from fastapi import APIRouter
from bugdiag.core.config import get_settings

router = APIRouter(prefix="/system", tags=["System Architecture"])

@router.get("/architecture")
def get_architecture_overview():
    settings = get_settings()
    return {
        "platform_name": "TraceIQ",
        "milestone": "Milestone 1 — Foundation & Bug Understanding",
        "pipeline_workflow": [
            "Bug Submission",
            "Security Validation & Sanitization",
            "Preprocessing & Parsing",
            "Agent 1: Triage Agent (Classification & Completeness)",
            "Agent 2: Log Analysis Agent (Stack Trace Parsing & Exception Extraction)",
            "Knowledge Retrieval (Hybrid BM25 + pgvector Reciprocal Rank Fusion)",
            "Agent 3: Root Cause Agent (Evidence-Based Hypotheses)",
            "Agent 4: Duplicate Detection Agent (Thresholded Defect Deduplication)",
            "Agent 5: Remediation Agent (Historical Notes & Investigation Guidance)",
            "Structured Diagnosis Report Generation"
        ],
        "agents": [
            {
                "name": "Triage Agent",
                "role": "Bug Classification & Completeness Assessment",
                "responsibilities": [
                    "Classifies defect into technical taxonomies (NullPointer, Memory, Concurrency, etc.)",
                    "Validates report completeness and scores submission quality",
                    "Detects programming language and frameworks",
                    "Assesses adjusted severity and priority"
                ]
            },
            {
                "name": "Log Analysis Agent",
                "role": "Stack Trace Parsing & Forensic Log Extraction",
                "responsibilities": [
                    "Extracts exception classes and error messages",
                    "Parses multi-language stack frames (Python, Java, C++, JS/TS)",
                    "Identifies origin source files and line numbers",
                    "Extracts structured technical evidence snippets"
                ]
            },
            {
                "name": "Root Cause Agent",
                "role": "Hypothesis Synthesis & Evidence Association",
                "responsibilities": [
                    "Correlates runtime exception patterns with source files",
                    "Synthesizes technical evidence from log analysis",
                    "Cross-references retrieved historical defects",
                    "Computes a conservative evidence-coverage score; it is not a probability"
                ]
            },
            {
                "name": "Duplicate Detection Agent",
                "role": "Defect Deduplication & Historical Similarity",
                "responsibilities": [
                    "Uses compatible dense vectors when available and BM25 keyword retrieval",
                    "Ranks historical defect matches",
                    "Flags possible duplicates using a configurable relevance threshold",
                    "Surfaces exact duplicate candidates"
                ]
            },
            {
                "name": "Remediation Agent",
                "role": "Fix Recommendation & Historical Resolution Retrieval",
                "responsibilities": [
                    "Retrieves historical resolution notes from records in the knowledge base",
                    "Provides safe investigation guidance instead of untested code diffs",
                    "Clearly labels historical notes as unverified references",
                    "Provides contextual remediation rationale"
                ]
            }
        ],
        "tech_stack": {
            "backend": "FastAPI, SQLAlchemy 2, Pydantic v2, Alembic",
            "vector_store": "PostgreSQL with pgvector (or SQLite for local development)",
            "embeddings": f"{settings.EMBEDDING_MODEL} (384 dimensions when the model is available; health endpoint reports fallback mode)",
            "keyword_search": "BM25Okapi (rank-bm25)",
            "ranking_strategy": f"Reciprocal Rank Fusion (RRF, k={settings.RRF_K})",
            "frontend": "React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Recharts"
        }
    }
