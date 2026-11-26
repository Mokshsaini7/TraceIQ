# BugDiag REST API Documentation

**API Version:** `v1`  
**Base URL:** `/api/v1`  
**Interactive Swagger Docs:** `http://localhost:8000/docs`  
**ReDoc Reference:** `http://localhost:8000/redoc`  

---

## 1. Health & System

### `GET /api/v1/health`
Returns health status, database dialect, and embedding configuration.
- **Response 200 OK:**
```json
{
  "status": "healthy",
  "app_name": "BugDiag",
  "environment": "development",
  "database": {
    "status": "healthy",
    "dialect": "postgresql"
  },
  "embeddings": {
    "model_name": "all-MiniLM-L6-v2",
    "dimension": 384
  },
  "version": "0.1.0"
}
```

### `GET /api/v1/system/architecture`
Returns metadata on the 5 agents, the pipeline workflow, and the active technology stack.

---

## 2. Bug Submissions

### `POST /api/v1/submissions`
Creates a defect report only. Upload attachments, then call the diagnosis trigger endpoint.
- **Request Body (`application/json`):**
```json
{
  "title": "NullPointerException in UserProfileService on token refresh",
  "description": "When refreshing expired OAuth2 sessions under high load, user profile lookups crash.",
  "stack_trace": "java.lang.NullPointerException at com.app.UserProfileService.get(UserProfileService.java:42)",
  "error_logs": "ERROR [http-nio-8080-exec-4] Session timeout encountered",
  "programming_language": "Java",
  "framework": "Spring Boot",
  "severity": "high",
  "priority": "p1",
  "reproduction_steps": "1. Expire session token\n2. Trigger concurrent refresh requests"
}
```
- **Response 201 Created:** Returns `BugSubmissionResponse` with UUID `id` and `status: "pending"`.

### `GET /api/v1/submissions`
Lists tracked bug submissions with pagination, sorting, and filtering.
- **Query Parameters:**
  - `page` (int, default: 1)
  - `page_size` (int, default: 10)
  - `status` (string, optional)
  - `severity` (string, optional)
  - `priority` (string, optional)
  - `language` (string, optional)
  - `search` (string, optional)
  - `sort_by` (string, default: "created_at")
  - `sort_order` (string: "desc" | "asc")

### `GET /api/v1/submissions/{id}`
Returns full details of an individual bug submission including attachments and timestamps.

### `POST /api/v1/submissions/{id}/attachments`
Upload all diagnostic files before starting diagnosis.
Safely persists an uploaded log or source file for static analysis.
- **Content-Type:** `multipart/form-data`
- **Supported Formats:** `.txt, .log, .json, .csv, .md, .py, .java, .js, .ts, .tsx, .jsx, .xml, .yaml, .yml`
- **Max File Size:** 10 MB

---

## 3. Diagnosis & Agent Outputs

### `GET /api/v1/diagnosis/{submission_id}`
Returns the comprehensive multi-agent diagnosis report.
- **Response 200 OK:**
```json
{
  "id": "diag-uuid",
  "submission_id": "sub-uuid",
  "triage_result": {
    "category": "NullPointer",
    "severity": "high",
    "priority": "p1",
    "programming_language": "Java",
    "framework": "Spring Boot",
    "missing_information": [],
    "completeness_score": 0.95
  },
  "log_analysis_result": {
    "has_stack_trace": true,
    "exception_type": "java.lang.NullPointerException",
    "error_message": null,
    "stack_frames": [
      {
        "file": "UserProfileService.java",
        "line": 42,
        "function": "get"
      }
    ],
    "suspect_files": ["UserProfileService.java"],
    "technical_evidence": [
      "Identified Exception: java.lang.NullPointerException",
      "Origin Frame: UserProfileService.java:42 in `get()`"
    ]
  },
  "root_cause_result": {
    "identified_root_cause": "Null or undefined object dereference during invocation in Java runtime.",
    "explanation": "Code execution attempted to access member properties on an object reference that was not instantiated.",
    "confidence": 0.88,
    "supporting_evidence": [
      "Categorized as NullPointer exception in Java.",
      "Primary suspect source: UserProfileService.java"
    ],
    "historical_matches": []
  },
  "duplicate_detection_result": {
    "is_duplicate": false,
    "highest_similarity": 0.62,
    "potential_duplicates": []
  },
  "remediation_result": {
    "verified_fixes": [],
    "suggested_fixes": [
      {
        "title": "Defensive Null Assertion / Optional Chaining Guard",
        "description": "Introduce non-null boundary validation prior to accessing member attributes.",
        "diff_snippet": "--- a/UserProfileService.java\n+++ b/UserProfileService.java\n...",
        "is_verified_from_history": false
      }
    ],
    "rationale": "Remediation synthesized for category 'NullPointer' in Java."
  },
  "overall_confidence": 0.82,
  "status": "completed"
}
```

### `POST /api/v1/diagnosis/trigger`
Re-runs the 5-Agent pipeline with updated knowledge base indices.
- **Request:** `{ "submission_id": "sub-uuid", "force_reanalysis": true }`

### `GET /api/v1/diagnosis/{submission_id}/logs`
Returns telemetry execution logs for each agent (duration in ms, input/output payloads).

---

## 4. Knowledge Base & Ingestion

### `GET /api/v1/knowledge-base/stats`
Returns total datasets, historical defects, chunks, embeddings, and source distributions.

### `GET /api/v1/knowledge-base/datasets`
Lists all registered defect repositories and processing statuses.

### `POST /api/v1/knowledge-base/datasets`
Uploads and indexes a new CSV or JSON defect dataset.

### `POST /api/v1/knowledge-base/import-default`
One-click ingestion of the authentic Mozilla, Apache, and Eclipse defect datasets.

### `GET /api/v1/knowledge-base/jobs`
Lists all batch ingestion job audit logs.

---

## 5. Semantic Search & Evaluation

### `POST /api/v1/search/historical`
Performs hybrid or single-mode defect search.
- **Request Body:**
```json
{
  "query": "Null pointer dereference gfxFont canvas measureText crash",
  "method": "hybrid",
  "top_k": 5,
  "source_filter": "Mozilla"
}
```
- **Response 200 OK:**
```json
{
  "query": "Null pointer dereference gfxFont canvas measureText crash",
  "method": "hybrid",
  "total_results": 1,
  "execution_time_ms": 14.2,
  "results": [
    {
      "defect_id": "defect-uuid",
      "original_issue_id": "MOZ-1428910",
      "source_repo": "Firefox",
      "title": "Crash in gfxFont::GetGlyph with null font entry dereference",
      "description": "Firefox crashes when measuring text in OffscreenCanvas...",
      "stack_trace": "0  xul.dll!gfxFont::GetGlyph(unsigned int) [gfxFont.cpp:412]",
      "resolution": "FIXED",
      "similarity_score": 0.94,
      "retrieval_method": "hybrid_rrf"
    }
  ]
}
```

### `GET /api/v1/search/evaluate`
Executes empirical Precision@K, Recall@K, and MRR evaluation comparing BM25, Dense Semantic, and Hybrid RRF.
