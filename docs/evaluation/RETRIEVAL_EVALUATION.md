# Empirical Retrieval Evaluation Framework

**Platform:** BugDiag Intelligent Defect Diagnosis Platform  
**Endpoint:** `GET /api/v1/search/evaluate`  
**Evaluation Target:** Dense Semantic vs BM25 vs Hybrid RRF  

---

## 1. Mathematical Metric Formulations

### Precision@K
Measures the proportion of retrieved defect candidates within the top-$K$ rankings that are relevant to the query:
$$\text{Precision@K} = \frac{|\text{Retrieved}_K \cap \text{Relevant}|}{K}$$

### Recall@K
Measures the coverage of relevant defect precedents surfaced in the top-$K$ candidates:
$$\text{Recall@K} = \frac{|\text{Retrieved}_K \cap \text{Relevant}|}{|\text{Relevant}|}$$

### Mean Reciprocal Rank (MRR)
Evaluates the positional efficiency of the ranking algorithm:
$$\text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$$
where $\text{rank}_i$ is the rank position of the first relevant historical defect for query $i$.

---

## 2. Benchmark Queries

The evaluation test suite tests genuine defect categories against indexed historical repositories:
1. `Null pointer dereference gfxFont canvas measureText crash` -> Ground Truth: `MOZ-1428910`
2. `HTTP/2 stream reset abort NS_ERROR_NET_RESET` -> Ground Truth: `MOZ-1563201`
3. `SortMergeJoin OutOfMemoryError Java heap space shuffle memory` -> Ground Truth: `SPARK-34120`
4. `JapaneseTokenizer ArrayIndexOutOfBoundsException array slice kana` -> Ground Truth: `LUCENE-9821`
5. `KafkaConsumer commitSync deadlock heartbeat thread rebalance` -> Ground Truth: `KAFKA-12499`
6. `AST converter LambdaExpression MethodBinding isVarargs NullPointerException` -> Ground Truth: `ECL-540192`
7. `SWTException Invalid thread access Display asyncExec WorkspaceJob` -> Ground Truth: `ECL-571103`

---

## 3. Comparative Observations

- **BM25 Alone:** Surfaces results rapidly when exact tokens match (e.g. `JapaneseTokenizer`), but experiences degradation when users query using conceptual descriptions (e.g., "memory leak during heavy join").
- **Dense Semantic Alone:** Maps concepts smoothly, but occasionally ranks unrelated issues higher if general vocabulary dominates over specific error tokens.
- **Hybrid RRF:** Delivers the highest overall MRR and Precision@1 by rewarding documents that appear in the top tier of both dense semantic proximity and lexical token precision.
