"""
Embedding abstraction with NVIDIA NIM primary and local sentence-transformers fallback.

NVIDIA NIM model: nvidia/nv-embedqa-e5-v5 (1024-dim)
Local fallback:   BAAI/bge-small-en-v1.5 (384-dim)

The same class is used for both query and document embedding.
ChromaDB requires consistent dimensions within a collection — so we
pick a backend once at startup and stick with it.
"""
import os
import numpy as np
from typing import Union
from openai import OpenAI

from src.config import (
    NVIDIA_API_KEY,
    NVIDIA_BASE_URL,
    NVIDIA_EMBED_MODEL,
    LOCAL_EMBED_MODEL,
    EMBED_BACKEND,
)

_local_model = None  # lazy-loaded sentence-transformers model


def _get_local_model():
    global _local_model
    if _local_model is None:
        from sentence_transformers import SentenceTransformer
        _local_model = SentenceTransformer(LOCAL_EMBED_MODEL)
    return _local_model


def _embed_nvidia(texts: list[str]) -> list[list[float]]:
    client = OpenAI(api_key=NVIDIA_API_KEY, base_url=NVIDIA_BASE_URL)
    # NVIDIA NIM allows batch up to 96 texts
    all_embeddings: list[list[float]] = []
    batch_size = 64
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(
            input=batch,
            model=NVIDIA_EMBED_MODEL,
            encoding_format="float",
            extra_body={"input_type": "query", "truncate": "END"},
        )
        all_embeddings.extend([item.embedding for item in response.data])
    return all_embeddings


def _embed_local(texts: list[str]) -> list[list[float]]:
    model = _get_local_model()
    vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return vecs.tolist()


def embed_texts(texts: list[str], backend: str = EMBED_BACKEND) -> list[list[float]]:
    """Embed a list of strings. Returns list of float vectors."""
    if not texts:
        return []
    if backend == "nvidia" and NVIDIA_API_KEY:
        try:
            return _embed_nvidia(texts)
        except Exception as e:
            print(f"[embedder] NVIDIA API failed ({e}), falling back to local.")
    return _embed_local(texts)


def embed_query(query: str, backend: str = EMBED_BACKEND) -> list[float]:
    """Single-query embedding (query-optimised input_type for NVIDIA)."""
    if backend == "nvidia" and NVIDIA_API_KEY:
        try:
            client = OpenAI(api_key=NVIDIA_API_KEY, base_url=NVIDIA_BASE_URL)
            response = client.embeddings.create(
                input=[query],
                model=NVIDIA_EMBED_MODEL,
                encoding_format="float",
                extra_body={"input_type": "query", "truncate": "END"},
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"[embedder] NVIDIA API failed ({e}), falling back to local.")
    model = _get_local_model()
    vec = model.encode([query], normalize_embeddings=True, show_progress_bar=False)
    return vec[0].tolist()
