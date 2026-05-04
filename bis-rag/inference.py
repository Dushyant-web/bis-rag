"""
inference.py — Judge entry point.

Usage:
    python inference.py --input hidden_private_dataset.json --output team_results.json

Reads a JSON list from --input. Each item has:
    id, query, expected_standards (and possibly other fields)

Writes a JSON list to --output. Each item has EXACTLY:
    id                   — from input
    query                — from input
    expected_standards   — PASSTHROUGH from input (required by eval_script.py)
    retrieved_standards  — list[str], canonical IS codes, top-5
    latency_seconds      — float

CRITICAL: Never crashes — all errors are caught and produce empty results.
"""
import argparse
import json
import sys
import time
from pathlib import Path

# Ensure repo root is on sys.path when run from any directory
sys.path.insert(0, str(Path(__file__).parent))

from src.chunker import get_chunks
from src.pipeline import initialize, run_query


def load_index():
    """Load chunks and build in-memory BM25 index. Called once."""
    chunks = get_chunks()
    initialize(chunks)
    return chunks


def process_item(item: dict) -> dict:
    """
    Run the RAG pipeline for one test item.
    Returns the output dict with all required fields.
    """
    item_id = str(item.get("id", ""))
    query = str(item.get("query", ""))
    expected = item.get("expected_standards", [])

    t0 = time.perf_counter()
    try:
        result = run_query(
            query=query,
            with_rationale=False,   # skip LLM to stay under latency budget
            item_id=item_id,
            expected_standards=expected,
        )
        return {
            "id": item_id,
            "query": query,
            "expected_standards": expected,
            "retrieved_standards": result.retrieved_standards,
            "latency_seconds": result.latency_seconds,
        }
    except Exception as exc:
        latency = time.perf_counter() - t0
        print(f"[inference] ERROR on item {item_id!r}: {exc}", file=sys.stderr)
        return {
            "id": item_id,
            "query": query,
            "expected_standards": expected,
            "retrieved_standards": [],
            "latency_seconds": round(latency, 4),
        }


def main():
    parser = argparse.ArgumentParser(description="BIS RAG inference")
    parser.add_argument("--input", required=True, help="Path to input JSON file")
    parser.add_argument("--output", required=True, help="Path to output JSON file")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"[inference] Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(input_path, encoding="utf-8") as f:
        dataset = json.load(f)

    print(f"[inference] Loaded {len(dataset)} items from {input_path}")
    print("[inference] Building index…")

    try:
        load_index()
    except Exception as exc:
        print(f"[inference] FATAL: Could not load index: {exc}", file=sys.stderr)
        sys.exit(1)

    print("[inference] Index ready. Running queries…")

    results = []
    for i, item in enumerate(dataset):
        out = process_item(item)
        results.append(out)
        # Progress every 10 items
        if (i + 1) % 10 == 0 or (i + 1) == len(dataset):
            avg_lat = sum(r["latency_seconds"] for r in results) / len(results)
            print(
                f"[inference] {i+1}/{len(dataset)} done | "
                f"avg latency: {avg_lat:.2f}s"
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"[inference] Wrote {len(results)} results to {output_path}")


if __name__ == "__main__":
    main()
