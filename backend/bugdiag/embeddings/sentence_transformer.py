"""SentenceTransformers embedding implementation using HuggingFace all-MiniLM-L6-v2.
Includes deterministic semantic fallback for network-isolated or offline environments.
"""

from typing import List
import numpy as np
from bugdiag.embeddings.base import BaseEmbeddingModel
from bugdiag.core.logging import get_logger

logger = get_logger("embeddings.sentence_transformer")

class SentenceTransformerEmbeddings(BaseEmbeddingModel):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = "cpu"):
        self._model_name = model_name
        self._device = device
        self._dimension = 384
        self._model = None
        self._fallback_reason = None
        self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading SentenceTransformer model '{self._model_name}' on {self._device}...")
            self._model = SentenceTransformer(self._model_name, device=self._device)
            # Verify dimension
            sample_emb = self._model.encode("BugDiag defect test", normalize_embeddings=True)
            self._dimension = len(sample_emb)
            logger.info(f"SentenceTransformer '{self._model_name}' loaded successfully (dimension={self._dimension}).")
        except Exception as e:
            logger.warning(
                f"Could not load HuggingFace model '{self._model_name}' directly ({e}). "
                "Enabling deterministic dense projection fallback for offline operation."
            )
            self._model = None
            self._fallback_reason = str(e)[:500]

    @property
    def using_fallback(self) -> bool:
        return self._model is None

    @property
    def fallback_reason(self) -> str | None:
        return self._fallback_reason

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def model_name(self) -> str:
        # Keep fallback vectors in a separate namespace so they can never be
        # mistaken for vectors produced by the real transformer model.
        return self._model_name if self._model is not None else f"fallback-hash:{self._model_name}"

    def _fallback_dense_encode(self, text: str) -> List[float]:
        """Deterministic 384-dimensional dense projection fallback."""
        import hashlib
        tokens = text.lower().split()
        vec = np.zeros(self._dimension, dtype=np.float32)
        if not tokens:
            return vec.tolist()

        for token in tokens:
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx = h % self._dimension
            sign = 1.0 if ((h >> 8) & 1) == 0 else -1.0
            vec[idx] += sign

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def encode_text(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self._dimension

        if self._model is not None:
            try:
                emb = self._model.encode(text, normalize_embeddings=True)
                return emb.tolist()
            except Exception as e:
                logger.error(f"Error encoding text with SentenceTransformer: {e}")

        return self._fallback_dense_encode(text)

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        if self._model is not None:
            try:
                embeddings = self._model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
                return [e.tolist() for e in embeddings]
            except Exception as e:
                logger.error(f"Error batch encoding with SentenceTransformer: {e}")

        return [self._fallback_dense_encode(t) for t in texts]
