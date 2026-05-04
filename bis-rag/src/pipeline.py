import time
from src.schema import BISChunk, RetrievedStandard, QueryResult
from src.query_expander import expand_query
from src.bm25_store import bm25_search
from src.vector_store import vector_search
from src.reranker import rerank
from src.whitelist import get_whitelist, filter_codes
from src.llm import generate_rationales
from src.config import BM25_TOP_K, VECTOR_TOP_K, RERANK_TOP_K

def _merge_candidates(bm25_results: list[dict], vector_results: list[dict]) -> list[dict]:
    seen: set[str] = set()
    merged: list[dict] = []
    for r in bm25_results + vector_results:
        code = r["standard_code"]
        if code not in seen:
            seen.add(code)
            merged.append(r)
    return merged

def run_query(
    query: str,
    with_rationale: bool = False,
    item_id: str = "",
    expected_standards: list[str] | None = None,
) -> QueryResult:
    t0 = time.perf_counter()

    expanded = expand_query(query)

    bm25_results = bm25_search(expanded, top_k=BM25_TOP_K)

    vector_results = vector_search(expanded, top_k=VECTOR_TOP_K)

    candidates = _merge_candidates(bm25_results, vector_results)

    reranked = rerank(query, candidates, top_k=RERANK_TOP_K)

    whitelist = get_whitelist()
    filtered = [r for r in reranked if r["standard_code"] in whitelist]

    if not filtered:
        filtered = reranked

    rationales: list[str] = []
    if with_rationale and filtered:
        rationales = generate_rationales(query, filtered)

    details: list[RetrievedStandard] = []
    for i, r in enumerate(filtered):
        details.append(
            RetrievedStandard(
                standard_code=r["standard_code"],
                title=r["title"],
                confidence=r.get("rerank_score", 0.0),
                rationale=rationales[i] if i < len(rationales) else "",
                section_name=r.get("section_name", ""),
            )
        )

    latency = time.perf_counter() - t0

    return QueryResult(
        id=item_id,
        query=query,
        expected_standards=expected_standards or [],
        retrieved_standards=[d.standard_code for d in details],
        latency_seconds=round(latency, 4),
        details=details,
    )

_initialized = False

def initialize(chunks: list[BISChunk]) -> None:
    global _initialized
    if _initialized:
        return

    from src.bm25_store import build_bm25_index
    from src.reranker import _get_model as _get_reranker
    from src.embedder import embed_query
    from src.vector_store import _get_collection

    print("[pipeline] Building BM25 index…")
    build_bm25_index(chunks)

    print("[pipeline] Pre-loading cross-encoder model (slow first time)…")
    _get_reranker()

    print("[pipeline] Pre-warming embedder…")
    embed_query("warmup query")

    print("[pipeline] Pre-warming ChromaDB connection…")
    _get_collection()

    print("[pipeline] All models warm. First query will be fast.")
    _initialized = True
