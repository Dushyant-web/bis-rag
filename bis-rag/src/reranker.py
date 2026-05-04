"""
Cross-encoder reranking using cross-encoder/ms-marco-MiniLM-L-6-v2.

Model runs on CPU (~200ms for 30 candidates). Scores are logits;
we sigmoid-normalise to [0,1] for confidence display.
"""
import math
from sentence_transformers import CrossEncoder

from src.config import RERANK_TOP_K

_model: CrossEncoder | None = None
_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def _get_model() -> CrossEncoder:
    global _model
    if _model is None:
        _model = CrossEncoder(_MODEL_NAME, max_length=512)
    return _model


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def rerank(query: str, candidates: list[dict], top_k: int = RERANK_TOP_K) -> list[dict]:
    """
    Rerank candidates using cross-encoder.

    Each candidate dict must have: standard_code, title, full_text, section_name.
    Returns top_k dicts with added 'rerank_score' (0-1, higher = better).
    """
    if not candidates:
        return []

    model = _get_model()

    # Pairs: (query, title + first ~300 chars of body)
    pairs = [
        (query, f"{c['standard_code']} {c['title']}\n{c['full_text'][:300]}")
        for c in candidates
    ]

    scores = model.predict(pairs)

    ranked = sorted(
        zip(candidates, scores),
        key=lambda x: x[1],
        reverse=True,
    )[:top_k]

    result = []
    for candidate, score in ranked:
        entry = dict(candidate)
        entry["rerank_score"] = _sigmoid(float(score))
        result.append(entry)

    return result
