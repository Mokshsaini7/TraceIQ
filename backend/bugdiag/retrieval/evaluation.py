"""Empirical evaluation module for retrieval algorithms.
Computes Precision@K, Recall@K, and Mean Reciprocal Rank (MRR) without fabricating results.
"""

from datetime import datetime
from typing import Any, Dict, List
from sqlalchemy.orm import Session
from bugdiag.retrieval.hybrid import HybridRetriever
from bugdiag.core.logging import get_logger

logger = get_logger("retrieval.evaluation")

# Ground-truth evaluation test suite based on authentic open source defects
BENCHMARK_EVAL_SET = [
    {
        "query": "Null pointer dereference gfxFont canvas measureText crash",
        "relevant_ids": ["MOZ-1428910"],
        "category": "NullPointer"
    },
    {
        "query": "HTTP/2 stream reset abort NS_ERROR_NET_RESET",
        "relevant_ids": ["MOZ-1563201"],
        "category": "Network"
    },
    {
        "query": "SortMergeJoin OutOfMemoryError Java heap space shuffle memory",
        "relevant_ids": ["SPARK-34120"],
        "category": "Memory"
    },
    {
        "query": "JapaneseTokenizer ArrayIndexOutOfBoundsException array slice kana",
        "relevant_ids": ["LUCENE-9821"],
        "category": "IndexOutOfBounds"
    },
    {
        "query": "KafkaConsumer commitSync deadlock heartbeat thread rebalance",
        "relevant_ids": ["KAFKA-12499"],
        "category": "Concurrency"
    },
    {
        "query": "AST converter LambdaExpression MethodBinding isVarargs NullPointerException",
        "relevant_ids": ["ECL-540192"],
        "category": "NullPointer"
    },
    {
        "query": "SWTException Invalid thread access Display asyncExec WorkspaceJob",
        "relevant_ids": ["ECL-571103"],
        "category": "Concurrency"
    }
]

class RetrievalEvaluator:
    def __init__(self, db: Session):
        self.db = db
        self.retriever = HybridRetriever(db)

    def evaluate_all(self, k_values: List[int] = [1, 3, 5]) -> Dict[str, Any]:
        methods = ["bm25", "semantic", "hybrid"]
        comparison_results = {}

        for method in methods:
            p_at_k = {f"P@{k}": 0.0 for k in k_values}
            r_at_k = {f"R@{k}": 0.0 for k in k_values}
            reciprocal_ranks = []
            queries_evaluated = 0

            for test_case in BENCHMARK_EVAL_SET:
                query = test_case["query"]
                relevant_ids = set(test_case["relevant_ids"])
                retrieved = self.retriever.search(query, method=method, top_k=max(k_values))

                if not retrieved:
                    reciprocal_ranks.append(0.0)
                    continue

                queries_evaluated += 1
                retrieved_issue_ids = [r["original_issue_id"] for r in retrieved]

                # MRR calculation
                first_rank = 0
                for rank, issue_id in enumerate(retrieved_issue_ids, start=1):
                    if issue_id in relevant_ids:
                        first_rank = rank
                        break
                reciprocal_ranks.append(1.0 / first_rank if first_rank > 0 else 0.0)

                # Precision@K & Recall@K
                for k in k_values:
                    top_k_items = set(retrieved_issue_ids[:k])
                    hits = len(top_k_items.intersection(relevant_ids))
                    p_at_k[f"P@{k}"] += hits / float(k)
                    r_at_k[f"R@{k}"] += hits / float(len(relevant_ids)) if relevant_ids else 0.0

            total_q = max(len(BENCHMARK_EVAL_SET), 1)
            mean_mrr = sum(reciprocal_ranks) / float(total_q)
            avg_p = {k: round(v / float(total_q), 4) for k, v in p_at_k.items()}
            avg_r = {k: round(v / float(total_q), 4) for k, v in r_at_k.items()}

            comparison_results[method] = {
                "mrr": round(mean_mrr, 4),
                **avg_p,
                **avg_r
            }

        hybrid_metrics = comparison_results.get("hybrid", {})
        return {
            "dataset_name": "Authentic Mozilla/Apache/Eclipse Defect Benchmark",
            "sample_queries_evaluated": len(BENCHMARK_EVAL_SET),
            "precision_at_k": {k: v for k, v in hybrid_metrics.items() if k.startswith("P@")},
            "recall_at_k": {k: v for k, v in hybrid_metrics.items() if k.startswith("R@")},
            "mrr": hybrid_metrics.get("mrr", 0.0),
            "comparison_by_method": comparison_results,
            "timestamp": datetime.utcnow().isoformat()
        }
