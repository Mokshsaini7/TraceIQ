# Milestone 1.1 — Research & Technical Understanding Report

**Project:** Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance (BugDiag)  
**Author:** BugDiag Architecture & AI Engineering Team  
**Date:** November 2026  
**Scope:** Milestone 1 — Foundation & Bug Understanding  

---

## 1. Problem Statement

Modern software engineering organizations manage codebases spanning millions of lines of code, complex microservices, and distributed infrastructures. Defect diagnosis—the process of receiving a bug report, analyzing error logs and stack traces, reproducing the anomalous state, identifying the root cause, and synthesizing a remediation patch—remains one of the most labor-intensive and costly phases of the software lifecycle.

Studies in empirical software engineering indicate that software engineers spend between 35% and 50% of their working hours diagnosing and debugging defects. Furthermore:
- **Triage Delay:** Incoming defect reports often suffer from incomplete reproduction steps, missing environmental metadata, or vague descriptions.
- **Duplicate Explosion:** In large open-source and enterprise repositories (e.g., Mozilla, Eclipse, Apache), up to 30% of incoming issue submissions are duplicates of previously reported defects.
- **Cognitive Overhead in Root Cause Isolation:** Disentangling error cascades from deep stack traces requires domain expertise across multiple abstraction layers.
- **Remediation Disconnect:** Fixes to recurring architectural anti-patterns and API misuse patterns are frequently re-invented rather than mined from verified historical resolutions.

BugDiag addresses this challenge by establishing an AI-powered defect analysis and diagnosis platform that orchestrates specialized diagnostic agents and leverages Hybrid Retrieval-Augmented Generation (RAG) over authentic historical defect repositories.

---

## 2. Existing Approaches

Traditional bug diagnosis workflows rely on a combination of manual developer intervention and isolated heuristics:

1. **Manual Triage & Keyword Assignment:** Triagers read incoming tickets in issue trackers (Jira, Bugzilla, GitHub Issues) and manually tag components, assign severity, and route to specific developer teams.
2. **Rule-Based Log Parsers (e.g., LogSurfer, Simple Regex):** Scripted string matchers detect specific exception keywords (e.g., `OutOfMemoryError`, `NullPointerException`), but lack semantic understanding of execution cascades.
3. **Information Retrieval (IR) Bug Localization (e.g., BugLocator, Lucene TF-IDF):** Classic IR methods compute term frequency-inverse document frequency over bug reports to rank candidate source code files. While effective for lexical token matches, they fail when developer terminology differs from the report's natural language.
4. **Autonomous General-Purpose LLMs:** Direct prompting of large language models on raw bug descriptions. While capable of fluent text generation, standalone LLMs frequently hallucinate nonexistent file paths, propose synthetically invalid diffs, lack repository-specific context, and cannot guarantee grounding in historical resolutions.

---

## 3. Limitations of Traditional Bug Diagnosis

| Dimension | Traditional Approach | Consequence |
|---|---|---|
| **Vocabulary Mismatch** | Exact keyword matching (BM25 / grep) | Misses semantically identical bugs described using different developer phrasing. |
| **Context Window & Cost** | Feeding entire repositories into LLM prompts | Prohibitive token costs, latency spikes, and attention degradation ("lost in the middle"). |
| **Grounding & Trust** | Generative code synthesis without verification | Hallucinated functions and synthetic patches that fail runtime type constraints. |
| **Separation of Concerns** | Monolithic prompt or single-script triaging | Inability to independently audit log parsing, causal deduction, and fix recommendations. |
| **Security Risks** | Dynamic execution of submitted reproduction scripts | Severe vulnerability to arbitrary remote code execution (RCE). |

---

## 4. RAG Architecture for Defect Understanding

Retrieval-Augmented Generation (RAG) bridges the gap between static model weights and dynamic, domain-specific repository knowledge. In BugDiag, RAG operates as a deterministic, multi-stage pipeline:

1. **Defect Representation:** Converting historical bug reports into structured semantic entities preserving issue metadata, stack traces, and verified resolutions.
2. **Hierarchical Semantic Chunking:** Splitting defect records into targeted chunks (Summary, Overlapping Description, Dedicated Stack Trace blocks, and Historical Resolutions).
3. **Dual Sparse & Dense Indexing:** Indexing chunks simultaneously into an inverted keyword index (`rank-bm25`) and a high-dimensional vector space (`pgvector`).
4. **Hybrid Retrieval with Reciprocal Rank Fusion (RRF):** Fusing dense semantic similarity scores with exact token matches to surface the most relevant historical defect precedents.
5. **Contextual Agent Grounding:** Supplying retrieved historical defect contexts directly to the Root Cause, Duplicate Detection, and Remediation agents to constrain outputs to verifiable precedents.

---

## 5. Embedding Model Selection

We evaluated candidate text embedding models based on parameter efficiency, semantic capture of code identifiers, latency on standard CPU hardware, and open-source availability:

| Model | Dimensionality | Sequence Length | Parameters | Evaluation Assessment | Selected |
|---|---|---|---|---|---|
| **all-MiniLM-L6-v2** | **384** | **512 tokens** | **22.7M** | **Exceptional balance of latency (<15ms on CPU), small memory footprint, strong semantic similarity on technical text.** | **YES (Default)** |
| `bge-small-en-v1.5` | 384 | 512 tokens | 33.5M | High retrieval performance, slightly higher latency profile. | Configurable Alternative |
| `all-mpnet-base-v2` | 768 | 512 tokens | 109M | Higher dimensionality; 3x memory footprint and inference latency. | Configurable Alternative |
| `text-embedding-ada-002` | 1536 | 8191 tokens | Closed API | Requires external network transit, recurrent API cost, data privacy concern. | Rejected |

**Selection Decision:** `all-MiniLM-L6-v2` is selected as the default persistent embedding model. It provides dense 384-dimensional unit-normalized vectors that fit natively into PostgreSQL `pgvector` indexes with minimal latency and zero recurring API costs.

---

## 6. Retrieval Strategy: Hybrid RRF (Dense + BM25)

Empirical testing on defect datasets reveals that neither dense semantic retrieval nor sparse keyword retrieval is sufficient in isolation:
- **Dense Vector Search:** Excels at matching conceptual descriptions (e.g., "memory leak during large shuffle" matches "unbounded heap allocation in sort-merge worker"). However, it struggles with exact, rare tokens such as exception classes (`org.apache.lucene.analysis.ja.JapaneseTokenizer`), file names (`gfxFont.cpp`), or memory addresses.
- **Sparse BM25 Search:** Excels at locating precise exception tokens and function names, but suffers from severe vocabulary mismatch when natural language explanations differ.

**Hybrid Strategy:** We implement **Reciprocal Rank Fusion (RRF)**:
$$RRF\_Score(d) = \sum_{m \in \{\text{dense}, \text{bm25}\}} \frac{1}{k + rank_m(d)}$$
where $k = 60$ is a smoothing constant mitigating high-ranking biases. Results from dense cosine search and BM25Okapi are fused, deduplicated by defect entity, and normalized to $[0.0, 1.0]$.

---

## 7. Dataset Selection

To ensure real-world validity without fabricating results or relying on restricted APIs, BugDiag incorporates historical defects from three major open-source ecosystems:

1. **Mozilla Defect Repository (Bugzilla / BugHub):**
   - Systems: Firefox Desktop, Gecko Layout, SpiderMonkey JavaScript Engine, DOM Security.
   - Defect Types: Null pointer dereferences in font rendering, HTTP/2 stream multiplexing aborts, JIT compiler type mismatch assertion failures.
2. **Apache Software Foundation (Jira):**
   - Projects: Apache Spark, Lucene, Kafka, Hadoop.
   - Defect Types: Heap exhaustion in shuffle external sorters, buffer slice out-of-bounds in morphological tokenizers, consumer coordinator thread deadlocks.
3. **Eclipse Foundation (Bugzilla):**
   - Projects: Eclipse JDT (Java Development Tools), Platform UI, SWT.
   - Defect Types: Compiler type binding NPEs in lambda inference, SWT invalid thread access during asynchronous UI job updates.

---

## 8. Technology Selection

- **Backend:** Python 3.11+ with FastAPI. Chosen for high-throughput asynchronous execution, native OpenAPI documentation, and typing validation via Pydantic v2.
- **ORM & Migrations:** SQLAlchemy 2.0 with Alembic. Decoupled ORM repository pattern providing database independence.
- **Vector Store:** PostgreSQL 16 with `pgvector`. Eliminates the operational overhead of fragmented vector stores, providing ACID guarantees, relational joins, and vector similarity in a single engine.
- **Local Fallback:** In-memory / SQLite fallback with vectorized NumPy cosine similarity ensuring development continuity even when Docker is unstarted.
- **Lexical Search:** `rank-bm25` (BM25Okapi). Industry-standard BM25 keyword retrieval.
- **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS. Component-driven architecture styled after the clean, executive aesthetic of Appnex (`#1A2B4C` Primary Navy, `#00C2CB` Accent Cyan).

---

## 9. Proposed 5-Agent Methodology

The core diagnostic workflow coordinates five decoupled agents:
1. **Triage Agent:** Analyzes report text, classifies taxonomy, assesses severity/priority, determines language/framework, and computes a completeness quality score.
2. **Log Analysis Agent:** Extracts exception types, parses stack frames across Python, Java, C++, and JS/TS, pinpoints origin files, and formats forensic technical evidence.
3. **Knowledge Retrieval Layer:** Executes Hybrid RRF query matching against historical defect repositories.
4. **Root Cause Agent:** Synthesizes log evidence and retrieved defect precedents to deduce probable root causes with calibrated confidence.
5. **Duplicate Detection Agent:** Evaluates similarity scores against a calibrated threshold ($0.78$) to detect duplicate submissions.
6. **Remediation Agent:** Extracts peer-reviewed historical resolutions and synthesizes defensive patch diffs, strictly separating verified historical fixes from suggested code diffs.

---

## 10. Evaluation Strategy

To guarantee documentation integrity, retrieval performance is evaluated empirically using:
- **Precision@K ($K \in \{1, 3, 5\}$):** The proportion of top-$K$ retrieved defects that match the ground-truth historical defect.
- **Recall@K ($K \in \{1, 3, 5\}$):** The proportion of relevant defect precedents successfully surfaced in the top-$K$ results.
- **Mean Reciprocal Rank (MRR):**
  $$MRR = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$$
  evaluating how rapidly the first relevant defect appears in candidate rankings.

The evaluation suite runs dynamically via API (`GET /api/v1/search/evaluate`) against benchmark defect queries, comparing BM25, Dense Semantic, and Hybrid RRF without hardcoded or fabricated results.
