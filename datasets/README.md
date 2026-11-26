# Historical Defect Knowledge Base Datasets

This directory contains historical defect datasets curated from public open-source software repositories for **Milestone 1 — Foundation & Bug Understanding**.

## Data Sources

1. **Mozilla Defect Repository (Bugzilla / BugHub)**
   - System: Firefox, Core, Gecko, SpiderMonkey
   - Languages: C++, JavaScript, Rust, Python
   - Format: JSON & CSV
   - Authentic Issues: Memory leaks, DOM rendering race conditions, null pointer dereferences, SSL handshake failures.

2. **Apache Software Foundation (Jira)**
   - Projects: Apache Spark, Lucene, Commons, Kafka, Hadoop
   - Languages: Java, Scala, Python
   - Format: CSV & JSON
   - Authentic Issues: OutOfMemoryError in shuffle operations, IndexOutOfBounds in tokenizers, NPE in deserialization, deadlock in concurrent worker queues.

3. **Eclipse Foundation (Bugzilla)**
   - Projects: Eclipse Platform, JDT, PDE, Equinox
   - Languages: Java
   - Format: JSON & CSV
   - Authentic Issues: ClassCastException in AST parsers, plugin lifecycle deadlock, workspace lock timeout, SWT thread access violations.

## Current seed-data scope and provenance

The checked-in seed files currently contain **10 curated sample records**: 4 Mozilla, 4 Apache, and 2 Eclipse. They are suitable for verifying parsing, normalization, chunking, embedding storage, and basic retrieval workflows; they are **not** a large-scale benchmark and do not establish production retrieval accuracy. The issue URLs in the records are provided for traceability, but this repository snapshot has not independently re-validated each source record or its current public availability. Do not describe these ten samples as a comprehensive or fully verified historical archive.

A repeatable ingestion test is included at `backend/tests/test_milestone1_foundation.py`. It checks that every seeded record can be parsed, ingested, chunked, and assigned an embedding record without row failures.

## Directory Layout

```
datasets/
├── raw/
│   ├── mozilla_defects_sample.json
│   ├── apache_defects_sample.csv
│   └── eclipse_defects_sample.json
├── processed/
│   └── normalized_defects_benchmark.json
└── README.md
```

## Schema & Column Mapping Standard

The BugDiag ingestion pipeline supports configurable column mappings to map disparate vendor schemas into the unified BugDiag defect representation:

| Unified Target Field | Mozilla Bugzilla Key | Apache Jira Key | Eclipse Key | Type |
|---|---|---|---|---|
| `source_repo` | `product` / `component` | `project_key` | `product` | string |
| `original_issue_id` | `bug_id` / `id` | `issue_key` | `id` | string |
| `title` | `summary` | `summary` | `summary` | string |
| `description` | `description` | `description` | `description` | string |
| `stack_trace` | `crash_signature` / `stack` | `environment_log` / `stack_trace`| `stack_trace` | string |
| `comments` | `comments` | `comment_log` | `comments` | list/string |
| `resolution` | `resolution` | `resolution` | `resolution` | string |
| `status` | `status` | `status` | `status` | string |
| `programming_language`| `language` | `language` | `language` | string |
| `created_date` | `creation_time` | `created` | `creation_ts` | ISO timestamp |
| `updated_date` | `last_change_time` | `updated` | `delta_ts` | ISO timestamp |
| `source_url` | `url` | `link` | `url` | URL string |

## Ingestion Pipeline Stages

1. **Dataset Import**: Parsed via streaming JSON / Pandas CSV readers with dynamic field mapper.
2. **Data Cleaning**: Strips ANSI control characters, HTML entities, and formatting artifacts.
3. **Normalization**: Canonicalizes severity/priority scales (e.g., P1-P5 to High/Medium/Low).
4. **Deduplication**: Content hashing (SHA-256 of normalized text) and semantic threshold comparison.
5. **Configurable Chunking**: Overlapping sliding window (chunk size: 512 tokens, overlap: 64 tokens) preserving stack trace blocks.
6. **Dense Embedding**: Generated using `sentence-transformers` (`all-MiniLM-L6-v2`, 384 dimensions).
7. **Vector Indexing**: Stored in PostgreSQL with pgvector `HNSW` or `IVFFlat` index using cosine similarity.
8. **Sparse Indexing**: Inverted index built via `rank-bm25` for exact token and exception matching.
