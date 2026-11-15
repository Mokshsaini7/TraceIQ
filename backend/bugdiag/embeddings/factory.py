"""Factory and cached singleton manager for embedding models.
"""

from functools import lru_cache
from bugdiag.core.config import get_settings
from bugdiag.embeddings.base import BaseEmbeddingModel
from bugdiag.embeddings.sentence_transformer import SentenceTransformerEmbeddings

_cached_instance: BaseEmbeddingModel | None = None

def get_embedding_model() -> BaseEmbeddingModel:
    global _cached_instance
    if _cached_instance is None:
        settings = get_settings()
        _cached_instance = SentenceTransformerEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            device=settings.EMBEDDING_DEVICE
        )
    return _cached_instance
