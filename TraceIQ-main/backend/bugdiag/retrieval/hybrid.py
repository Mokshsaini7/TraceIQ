"""Hybrid Search engine using Reciprocal Rank Fusion (RRF).
Fuses dense semantic similarity with BM25 lexical precision.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from bugdiag.core.config import get_settings
from bugdiag.core.logging import get_logger
from bugdiag.repositories.knowledge_repo import KnowledgeRepository
from bugdiag.retrieval.bm25 import BM25Retriever
from bugdiag.retrieval.vector_search import VectorSearchRetriever

logger = get_logger("retrieval.hybrid")

class HybridRetriever:
    def __init__(self, db: Session):
        self.db = db
        self.repo = KnowledgeRepository(db)
        self.settings = get_settings()
        self.vector_retriever = VectorSearchRetriever(db)

    def _build_corpus_chunks(self) -> List[Dict[str, Any]]:
        raw_records = self.repo.get_all_chunks_with_embeddings()
        corpus = []
        active_model_name = self.vector_retriever.embedding_model.model_name
        for chunk, defect, vector, stored_model_name in raw_records:
            # Never compare vectors produced by different models or the offline hash fallback.
            compatible_vector = vector if stored_model_name == active_model_name else None
            corpus.append({
                "chunk_id": chunk.id,
                "defect_id": defect.id,
                "original_issue_id": defect.original_issue_id,
                "source_repo": defect.source_repo,
                "title": defect.title,
                "description": defect.description,
                "stack_trace": defect.stack_trace,
                "resolution": defect.resolution,
                "status": defect.status,
                "programming_language": defect.programming_language,
                "source_url": defect.source_url,
                "chunk_content": chunk.content,
                "content": chunk.content,
                "chunk_type": chunk.chunk_type,
                "vector": compatible_vector,
                "embedding_model": stored_model_name
            })
        return corpus

    def search(
        self,
        query: str,
        method: str = "hybrid",
        top_k: int = 5,
        source_filter: Optional[str] = None,
        language_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        corpus = self._build_corpus_chunks()
        if not corpus:
            return []

        # Apply metadata filters if provided
        filtered_corpus = corpus
        if source_filter:
            filtered_corpus = [c for c in filtered_corpus if source_filter.lower() in c["source_repo"].lower()]
        if language_filter:
            filtered_corpus = [c for c in filtered_corpus if c.get("programming_language") and language_filter.lower() in c["programming_language"].lower()]

        # Respect requested filters. Returning unrelated records when a filter has no
        # matches is misleading and can produce false duplicate recommendations.
        if not filtered_corpus:
            return []

        method_lower = method.lower()
        if method_lower == "semantic":
            dense_results = self.vector_retriever.search(query, filtered_corpus, top_k=top_k * 2)
            ranked_defects = self._aggregate_by_defect(dense_results, "semantic", top_k)
            return ranked_defects
        elif method_lower == "bm25":
            bm25_retriever = BM25Retriever(filtered_corpus, k1=self.settings.BM25_K1, b=self.settings.BM25_B)
            bm25_results = bm25_retriever.search(query, top_k=top_k * 2)
            ranked_defects = self._aggregate_by_defect(bm25_results, "bm25", top_k)
            return ranked_defects
        else:
            # Hybrid RRF. If the real embedding model is unavailable, dense_results is
            # empty and the search safely degrades to BM25-only results.
            dense_results = self.vector_retriever.search(query, filtered_corpus, top_k=top_k * 3)
            bm25_retriever = BM25Retriever(filtered_corpus, k1=self.settings.BM25_K1, b=self.settings.BM25_B)
            bm25_results = bm25_retriever.search(query, top_k=top_k * 3)

            cos_by_cid = {c["chunk_id"]: sc for c, sc in dense_results}
            bm_by_cid = {c["chunk_id"]: sc for c, sc in bm25_results}
            rrf_scores: Dict[str, float] = {}
            chunk_map: Dict[str, Dict[str, Any]] = {}
            k = self.settings.RRF_K

            # Rank dense results
            for rank, (chunk, score) in enumerate(dense_results, start=1):
                cid = chunk["chunk_id"]
                rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k + rank))
                chunk_map[cid] = chunk

            # Rank BM25 results
            for rank, (chunk, score) in enumerate(bm25_results, start=1):
                cid = chunk["chunk_id"]
                rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k + rank))
                chunk_map[cid] = chunk

            sorted_chunk_ids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)
            fused_pairs = []
            for cid in sorted_chunk_ids:
                ch = dict(chunk_map[cid])
                # Absolute (not rank-relative) similarity so the top hit is not always 1.0
                # This is a heuristic relevance indicator, not a calibrated probability.
                if cid in cos_by_cid:
                    ch["_sim"] = 0.7 * max(0.0, min(1.0, cos_by_cid[cid])) + 0.3 * self._saturate(bm_by_cid.get(cid, 0.0))
                else:
                    ch["_sim"] = self._saturate(bm_by_cid.get(cid, 0.0))
                fused_pairs.append((ch, rrf_scores[cid]))

            return self._aggregate_by_defect(fused_pairs, "hybrid_rrf", top_k)

    @staticmethod
    def _saturate(score: float, k: float = 8.0) -> float:
        """Map an unbounded BM25 score into [0, 1) with diminishing returns."""
        return score / (score + k) if score > 0 else 0.0

    def _aggregate_by_defect(
        self,
        scored_chunks: List[tuple],
        retrieval_method: str,
        top_k: int
    ) -> List[Dict[str, Any]]:
        seen_defects = set()
        aggregated = []

        max_raw_score = scored_chunks[0][1] if scored_chunks else 1.0
        if max_raw_score <= 0:
            max_raw_score = 1.0

        for chunk, raw_score in scored_chunks:
            defect_id = chunk["defect_id"]
            if defect_id in seen_defects:
                continue
            seen_defects.add(defect_id)

            # Normalize score between 0.0 and 1.0
            if retrieval_method == "semantic":
                norm_score = max(0.0, min(1.0, raw_score))
            elif retrieval_method == "hybrid_rrf":
                norm_score = max(0.0, min(1.0, chunk.get("_sim", 0.0)))
            else:
                norm_score = self._saturate(raw_score)

            aggregated.append({
                "defect_id": defect_id,
                "original_issue_id": chunk["original_issue_id"],
                "source_repo": chunk["source_repo"],
                "title": chunk["title"],
                "description": chunk["description"],
                "stack_trace": chunk.get("stack_trace"),
                "resolution": chunk.get("resolution"),
                "status": chunk.get("status"),
                "programming_language": chunk.get("programming_language"),
                "similarity_score": round(norm_score, 4),
                "source_url": chunk.get("source_url"),
                "retrieval_method": retrieval_method,
                "matched_chunk": chunk.get("chunk_content")
            })

            if len(aggregated) >= top_k:
                break

        return aggregated
