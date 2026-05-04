"""
Full RAG pipeline for one query.

Steps (per query):
  1. Expand query with synonyms            (~0ms)
  2. BM25 retrieval → top 25              (~150ms)
  3. Vector retrieval → top 25            (~250ms)
  4. Merge unique candidates              (~0ms)
  5. Cross-encoder rerank → top 5        (~200ms)
  6. Whitelist filter                     (~0ms)
  7. LLM rationale (UI mode only)        (~1500ms, skipped in fast mode)
  8. Format to schema                     (~0ms)

Total (fast/inference mode): ~600ms
Total (UI mode with rationale): ~2.1s
"""
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
    """Merge two result lists, deduplicating by standard_code. BM25 results take priority."""
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
    """
    Run the full pipeline for a single query.

    Args:
        query:              Natural language query.
        with_rationale:     If True, call LLM to generate rationale (UI mode).
        item_id:            Passthrough ID from the test set.
        expected_standards: Passthrough from test set for eval output.

    Returns:
        QueryResult with retrieved_standards (canonical strings).
    """
    t0 = time.perf_counter()

    # Step 1: query expansion
    expanded = expand_query(query)

    # Step 2: BM25
    bm25_results = bm25_search(expanded, top_k=BM25_TOP_K)

    # Step 3: Vector
    vector_results = vector_search(expanded, top_k=VECTOR_TOP_K)

    # Step 4: Merge
    candidates = _merge_candidates(bm25_results, vector_results)

    # Step 5: Rerank
    reranked = rerank(query, candidates, top_k=RERANK_TOP_K)

    # Step 6: Whitelist filter
    whitelist = get_whitelist()
    filtered = [r for r in reranked if r["standard_code"] in whitelist]

    # If filtering removed everything, fall back to reranked
    if not filtered:
        filtered = reranked

    # Step 7: LLM rationale (optional)
    rationales: list[str] = []
    if with_rationale and filtered:
        rationales = generate_rationales(query, filtered)

    # Step 8: Format
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


# Module-level state — loaded once, reused across all queries
_initialized = False


def initialize(chunks: list[BISChunk]) -> None:
    """
    Pre-warm ALL models so first real query has no cold-start penalty:
      - BM25 index
      - Cross-encoder (biggest cold-start: ~30-40s on first load)
      - Embedder (NVIDIA or local)
      - ChromaDB connection
    """
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
    _get_reranker()  # loads weights into RAM now, not on first query

    print("[pipeline] Pre-warming embedder…")
    embed_query("warmup query")  # initialises NVIDIA client or local model

    print("[pipeline] Pre-warming ChromaDB connection…")
    _get_collection()  # opens DB connection

    print("[pipeline] All models warm. First query will be fast.")
    _initialized = True
