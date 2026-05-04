import chromadb
from chromadb.config import Settings

from src.config import CHROMA_DIR, CHROMA_COLLECTION, VECTOR_TOP_K
from src.schema import BISChunk
from src.embedder import embed_texts, embed_query, EMBED_BACKEND

_client: chromadb.PersistentClient | None = None
_collection = None

def _get_collection():
    global _client, _collection
    if _collection is not None:
        return _collection
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    _client = chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=Settings(anonymized_telemetry=False),
    )
    _collection = _client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )
    return _collection

def index_chunks(chunks: list[BISChunk], batch_size: int = 64) -> None:
    col = _get_collection()

    texts = [
        f"{c.standard_code} {c.title}\n{c.full_text[:1500]}"
        for c in chunks
    ]

    print(f"[vector_store] Embedding {len(chunks)} chunks in batches of {batch_size}…")
    embeddings = embed_texts(texts)

    print("[vector_store] Upserting into ChromaDB…")
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i : i + batch_size]
        batch_embeddings = embeddings[i : i + batch_size]
        col.upsert(
            ids=[c.chunk_id for c in batch_chunks],
            embeddings=batch_embeddings,
            documents=[c.full_text[:2000] for c in batch_chunks],
            metadatas=[
                {
                    "standard_code": c.standard_code,
                    "title": c.title,
                    "section_name": c.section_name,
                }
                for c in batch_chunks
            ],
        )
    print(f"[vector_store] Indexed {len(chunks)} documents.")

def vector_search(query: str, top_k: int = VECTOR_TOP_K) -> list[dict]:
    col = _get_collection()
    q_vec = embed_query(query)
    results = col.query(
        query_embeddings=[q_vec],
        n_results=min(top_k, col.count()),
        include=["documents", "metadatas", "distances"],
    )
    output = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        output.append(
            {
                "standard_code": meta["standard_code"],
                "title": meta["title"],
                "section_name": meta["section_name"],
                "full_text": doc,
                "score": float(1.0 - dist),
            }
        )
    return output

def collection_count() -> int:
    return _get_collection().count()
