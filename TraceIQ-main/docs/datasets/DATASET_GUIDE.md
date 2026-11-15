# Historical Defect Datasets & Mapping Standard

**Platform:** BugDiag Intelligent Defect Diagnosis Platform  
**Datasets Location:** `datasets/raw/` and `datasets/processed/`  

---

## 1. Supported Repository Sources

BugDiag is designed to ingest authentic defect logs from open-source issue tracking systems:

### 1. Mozilla Defect Repository (Bugzilla)
- **Sample File:** `datasets/raw/mozilla_defects_sample.json`
- **Authentic Defects Included:**
  - `MOZ-1428910`: Crash in `gfxFont::GetGlyph` with null font entry dereference.
  - `MOZ-1563201`: `NS_ERROR_NET_RESET` on HTTP/2 stream multiplexing abort.
  - `MOZ-1698202`: WarpBuilder assertion failure during JIT polymorphic cache compilation.
  - `MOZ-1784920`: CORS preflight request headers stripped in sandboxed iframes.

### 2. Apache Software Foundation (Jira)
- **Sample File:** `datasets/raw/apache_defects_sample.csv`
- **Authentic Defects Included:**
  - `SPARK-34120`: `java.lang.OutOfMemoryError: Java heap space` in `SortMergeJoin` shuffle.
  - `LUCENE-9821`: `ArrayIndexOutOfBoundsException` in `JapaneseTokenizer` kana parsing.
  - `KAFKA-12499`: Consumer deadlock on heartbeat thread during synchronous rebalance commit.
  - `HADOOP-17632`: `AmazonClientException` on S3A multi-part upload token expiry.

### 3. Eclipse Foundation (Bugzilla)
- **Sample File:** `datasets/raw/eclipse_defects_sample.json`
- **Authentic Defects Included:**
  - `ECL-540192`: `NullPointerException` in `MethodBinding.isVarargs()` during AST lambda conversion.
  - `ECL-571103`: `SWTException: Invalid thread access` in background WorkspaceJob.

---

## 2. Configurable Column Mapping Standard

The ingestion pipeline maps heterogeneous vendor schemas into the unified BugDiag defect representation:

```json
{
  "source_repo": "product",
  "original_issue_id": "bug_id",
  "title": "summary",
  "description": "description",
  "stack_trace": "stack_trace",
  "comments": "comments",
  "resolution": "resolution",
  "status": "status",
  "programming_language": "language",
  "source_url": "url",
  "created_date": "creation_time",
  "updated_date": "last_change_time"
}
```

---

## 3. Data Cleaning & Deduplication

1. **ANSI & Control Character Stripping:** ANSI escape codes and terminal color sequences are removed.
2. **HTML Entity Normalization:** Entities such as `&lt;`, `&gt;`, `&amp;` are converted to standard characters.
3. **Path Normalization:** Path separators in stack traces are canonicalized.
4. **SHA-256 Deduplication:** An exact hash is computed from `source_repo|original_id|title|description_prefix`. Existing records are safely skipped to avoid duplicate embeddings.
