"""Dense vector similarity search engine supporting both pgvector and vectorized fallback.
"""

from typing import Any, Dict, List, Tuple
import numpy as np
from sqlalchemy import text
from sqlalchemy.orm import Session
from bugdiag.embeddings.factory import get_embedding_model
from bugdiag.core.logging import get_logger

logger = get_logger("retrieval.vector")

class VectorSearchRetriever:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_model = get_embedding_model()

    def search(
        self,
        query: str,
        corpus_chunks: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Tuple[Dict[str, Any], float]]:
        if not corpus_chunks or not query.strip():
            return []
        # Hash-projection fallback vectors are useful for deterministic operation, but they
        # are not semantic embeddings. Never present them as semantic similarity.
        if getattr(self.embedding_model, "using_fallback", False):
            logger.warning("Dense retrieval disabled: real SentenceTransformer model is unavailable.")
            return []

        query_vector = np.array(self.embedding_model.encode_text(query), dtype=np.float32)
        q_norm = np.linalg.norm(query_vector)
        if q_norm > 0:
            query_vector = query_vector / q_norm

        scored_chunks = []
        for chunk in corpus_chunks:
            vec_data = chunk.get("vector")
            if not vec_data:
                continue

            doc_vector = np.array(vec_data, dtype=np.float32)
            d_norm = np.linalg.norm(doc_vector)
            if d_norm > 0:
                doc_vector = doc_vector / d_norm

            sim = float(np.dot(query_vector, doc_vector))
            scored_chunks.append((chunk, sim))

        # Sort descending by similarity
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return scored_chunks[:top_k]
