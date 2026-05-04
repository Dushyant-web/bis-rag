import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.config import PUBLIC_TEST_SET, PUBLIC_RESULTS
from src.schema import QueryRequest, QueryResponse, RetrievedStandard
from src.chunker import get_chunks
from src.pipeline import initialize, run_query

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[api] Loading BIS index…")
    chunks = get_chunks()
    initialize(chunks)
    print(f"[api] Ready — {len(chunks)} standards indexed.")
    yield

app = FastAPI(title="BIS RAG API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    result = run_query(req.query, with_rationale=True)
    return QueryResponse(
        query=result.query,
        results=result.details,
        latency_seconds=result.latency_seconds,
    )

@app.get("/evaluate")
async def evaluate_endpoint():
    if not PUBLIC_RESULTS.exists():
        raise HTTPException(
            status_code=404,
            detail="Run scripts/run_eval.py first to generate public_results.json.",
        )
    with open(PUBLIC_RESULTS, encoding="utf-8") as f:
        results = json.load(f)

    from eval_script import normalize_std
    hits_at_3, mrr_sum, total_lat = 0, 0.0, 0.0
    for item in results:
        expected = set(normalize_std(s) for s in item.get("expected_standards", []))
        retrieved = [normalize_std(s) for s in item.get("retrieved_standards", [])]
        total_lat += item.get("latency_seconds", 0.0)
        if any(s in expected for s in retrieved[:3]):
            hits_at_3 += 1
        for rank, s in enumerate(retrieved[:5], 1):
            if s in expected:
                mrr_sum += 1.0 / rank
                break
    n = len(results)
    metrics = {
        "hit_rate_at_3": round((hits_at_3 / n) * 100, 2) if n else 0,
        "mrr_at_5": round(mrr_sum / n, 4) if n else 0,
        "avg_latency_seconds": round(total_lat / n, 2) if n else 0,
    }
    return {"metrics": metrics, "results": results}

@app.get("/health")
async def health():
    return {"status": "ok"}

_dist = Path(__file__).parent.parent / "frontend" / "dist"
if _dist.exists():
    app.mount("/", StaticFiles(directory=str(_dist), html=True), name="frontend")
