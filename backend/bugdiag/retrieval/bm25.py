"""BM25 Lexical retrieval engine using rank-bm25.
Specialized for exact token matching, exception names, and file/line signatures.
"""

import re
from typing import Any, Dict, List, Tuple
try:
    from rank_bm25 import BM25Okapi as _RankBM25Okapi
except ImportError:  # Keep lexical retrieval available in minimal/offline installs.
    _RankBM25Okapi = None
from bugdiag.core.logging import get_logger

logger = get_logger("retrieval.bm25")


class _LocalBM25Okapi:
    """Small Okapi BM25 implementation used only when rank-bm25 is unavailable.

    The project still declares rank-bm25 as its preferred implementation. This
    fallback keeps local development and tests usable in offline environments.
    """

    def __init__(self, corpus, k1=1.5, b=0.75):
        import math
        from collections import Counter

        self.k1 = float(k1)
        self.b = float(b)
        self.corpus = corpus
        self.doc_len = [len(doc) for doc in corpus]
        self.avgdl = (sum(self.doc_len) / len(self.doc_len)) if self.doc_len else 0.0
        self.doc_freqs = [Counter(doc) for doc in corpus]
        self.idf = {}
        n_docs = len(corpus)
        all_terms = set(term for doc in corpus for term in doc)
        for term in all_terms:
            df = sum(1 for freqs in self.doc_freqs if term in freqs)
            # Robertson/Sparck Jones IDF with a positive offset.
            self.idf[term] = math.log(1.0 + (n_docs - df + 0.5) / (df + 0.5))

    def get_scores(self, query_tokens):
        import numpy as np

        scores = np.zeros(len(self.corpus), dtype=float)
        if not self.corpus or not self.avgdl:
            return scores
        for term in query_tokens:
            idf = self.idf.get(term, 0.0)
            if not idf:
                continue
            for idx, frequencies in enumerate(self.doc_freqs):
                tf = frequencies.get(term, 0)
                if not tf:
                    continue
                length_norm = self.k1 * (1.0 - self.b + self.b * self.doc_len[idx] / self.avgdl)
                scores[idx] += idf * (tf * (self.k1 + 1.0)) / (tf + length_norm)
        return scores


BM25Okapi = _RankBM25Okapi or _LocalBM25Okapi
if _RankBM25Okapi is None:
    logger.warning("rank-bm25 is not installed; using the built-in BM25-compatible fallback.")

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
