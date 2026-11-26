# BugDiag RAG Methodology & Hybrid Retrieval Specification

**Platform:** Intelligent Bug Diagnosis Platform (BugDiag)  
**Scope:** Ingestion, Semantic Chunking, Embedding Generation, and Hybrid Ranking  

---

## 1. Defect Chunking Strategy

Software defects require a multi-aspect chunking strategy rather than naive character splitting:
- **Summary Chunk:** Preserves the bug title and initial 512 characters.
- **Description Segments:** If a description exceeds 512 characters, a sliding window of 512 characters with 64-character overlap captures detailed reproduction steps without cutting sentences abruptly.
- **Dedicated Stack Trace Chunk:** Preserves the entire call stack as an atomic chunk so that file names, line numbers, and exception messages are indexed in context.
- **Historical Resolution Chunk:** Isolates the verified fix notes, commits, or patch descriptions for direct retrieval by the Remediation Agent.

---

## 2. Local Dense Embedding Generation

- **Model:** `all-MiniLM-L6-v2` (SentenceTransformers)
- **Dimensionality:** 384 dimensions
- **Vector Normalization:** Embeddings are L2 normalized to unit length ($\|v\|_2 = 1.0$), transforming cosine similarity into a dot product:
  $$\text{CosineSimilarity}(u, v) = u \cdot v$$
- **Storage:** Stored in PostgreSQL with `pgvector` indexing.

---

## 3. Sparse Keyword Retrieval (BM25Okapi)

Implemented using `rank-bm25`:
- Tokenizes code identifiers, camelCase, snake_case, and exception names.
- Scoring formula:
  $$\text{BM25}(D, Q) = \sum_{q \in Q} \text{IDF}(q) \cdot \frac{f(q, D) \cdot (k_1 + 1)}{f(q, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}$$
  where $k_1 = 1.5$ and $b = 0.75$.

---

## 4. Reciprocal Rank Fusion (RRF)

To unite semantic vector matches and exact code tokens:
$$RRF(d) = \sum_{m \in \{\text{dense}, \text{bm25}\}} \frac{1}{k + rank_m(d)}$$
where $k = 60$. RRF eliminates score calibration discrepancies between unbounded BM25 scores and $[-1, 1]$ cosine similarities, providing stable, top-ranked historical precedents.
