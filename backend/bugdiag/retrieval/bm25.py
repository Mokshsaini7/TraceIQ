"""BM25 Lexical retrieval engine using rank-bm25.
Specialized for exact token matching, exception names, and file/line signatures.
"""

import re
from typing import Any, Dict, List, Tuple
from rank_bm25 import BM25Okapi
from bugdiag.core.logging import get_logger

logger = get_logger("retrieval.bm25")

TOKENIZE_PATTERN = re.compile(r"\w+|[^\w\s]")

def tokenize_code_and_text(text: str) -> List[str]:
    """Tokenizes text preserving exception names, symbols, and code identifiers."""
    if not text:
        return []
    # Tokenize words, camelCase splits, snake_case tokens
    tokens = TOKENIZE_PATTERN.findall(text.lower())
    sub_tokens = []
    for t in tokens:
        sub_tokens.append(t)
        if "_" in t:
            sub_tokens.extend([part for part in t.split("_") if part])
    return sub_tokens

class BM25Retriever:
    def __init__(self, corpus_chunks: List[Dict[str, Any]], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_chunks = corpus_chunks
        self.tokenized_corpus = [
            tokenize_code_and_text(chunk.get("content", "")) for chunk in corpus_chunks
        ]
        if self.tokenized_corpus:
            self.bm25 = BM25Okapi(self.tokenized_corpus, k1=self.k1, b=self.b)
        else:
            self.bm25 = None

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        if not self.bm25 or not self.corpus_chunks or not query.strip():
            return []

        tokenized_query = tokenize_code_and_text(query)
        if not tokenized_query:
            return []

        scores = self.bm25.get_scores(tokenized_query)
        # Pair with chunks
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)

        results = []
        for idx in ranked_indices[:top_k]:
            score = float(scores[idx])
            if score > 0.0:
                results.append((self.corpus_chunks[idx], score))
        return results
