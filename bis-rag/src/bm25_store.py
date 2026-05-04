"""
BM25 retrieval over BIS chunks using rank_bm25.

Corpus is built at index time and stored in memory (tiny — ~570 docs).
Each document = standard_code + title + full_text (tokenised).
"""
import re
from rank_bm25 import BM25Okapi

from src.config import BM25_TOP_K
from src.schema import BISChunk

_bm25: BM25Okapi | None = None
_index_chunks: list[BISChunk] | None = None


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


def build_bm25_index(chunks: list[BISChunk]) -> None:
    """Build BM25 index from chunks (call once at startup)."""
    global _bm25, _index_chunks
    corpus = [
        _tokenize(f"{c.standard_code} {c.title} {c.full_text}")
        for c in chunks
    ]
    _bm25 = BM25Okapi(corpus)
    _index_chunks = chunks


def bm25_search(query: str, top_k: int = BM25_TOP_K) -> list[dict]:
    """
    Return top_k results as list of dicts:
        {standard_code, title, section_name, full_text, score}
    Score is BM25 score (not normalised, larger = better).
    """
    if _bm25 is None or _index_chunks is None:
        raise RuntimeError("BM25 index not built. Call build_bm25_index() first.")
    tokens = _tokenize(query)
    scores = _bm25.get_scores(tokens)
    # Get top_k indices by descending score
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    results = []
    for idx in top_indices:
        chunk = _index_chunks[idx]
        results.append(
            {
                "standard_code": chunk.standard_code,
                "title": chunk.title,
                "section_name": chunk.section_name,
                "full_text": chunk.full_text,
                "score": float(scores[idx]),
            }
        )
    return results
