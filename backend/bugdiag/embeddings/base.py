"""Abstract base interface for text embedding providers in BugDiag.
"""

from abc import ABC, abstractmethod
from typing import List

class BaseEmbeddingModel(ABC):
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Returns the vector dimensionality of this embedding model."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Returns the canonical model identifier."""
        pass

    @abstractmethod
    def encode_text(self, text: str) -> List[float]:
        """Encodes a single text into a normalized embedding vector."""
        pass

    @abstractmethod
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """Encodes a batch of texts into normalized embedding vectors."""
        pass
