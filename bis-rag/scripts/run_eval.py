import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import PUBLIC_TEST_SET, PUBLIC_RESULTS
from src.chunker import get_chunks
from src.pipeline import initialize, run_query
from eval_script import normalize_std

def compute_metrics(results):
    hits_at_3 = 0
    mrr_sum = 0.0
    total_latency = 0.0
    for item in results:
        expected = set(normalize_std(s) for s in item.get("expected_standards", []))
        retrieved = [normalize_std(s) for s in item.get("retrieved_standards", [])]
        total_latency += item.get("latency_seconds", 0.0)
        if any(s in expected for s in retrieved[:3]):
            hits_at_3 += 1
        for rank, s in enumerate(retrieved[:5], 1):
            if s in expected:
                mrr_sum += 1.0 / rank
                break
    n = len(results)
    return {
        "hit_rate_at_3": (hits_at_3 / n) * 100 if n else 0,
        "mrr_at_5": mrr_sum / n if n else 0,
        "avg_latency_seconds": total_latency / n if n else 0,
    }

def main():
    if not PUBLIC_TEST_SET.exists():
        print(f"ERROR: Test set not found at {PUBLIC_TEST_SET}")
        print("Place the organizer-provided public_test_set.json in data/")
        sys.exit(1)

    with open(PUBLIC_TEST_SET, encoding="utf-8") as f:
        test_set = json.load(f)

    print(f"[eval] Loaded {len(test_set)} test queries.")
    print("[eval] Loading index…")

    chunks = get_chunks()
    initialize(chunks)

    print("[eval] Index ready. Running queries…\n")

    results = []
    for item in test_set:
        result = run_query(
            query=item["query"],
            with_rationale=False,
            item_id=str(item.get("id", "")),
            expected_standards=item.get("expected_standards", []),
        )
        results.append({
            "id": result.id,
            "query": result.query,
            "expected_standards": result.expected_standards,
            "retrieved_standards": result.retrieved_standards,
            "latency_seconds": result.latency_seconds,
        })

        expected = item.get("expected_standards", [])
        hit = any(
            e.replace(" ", "").lower() in [r.replace(" ", "").lower() for r in result.retrieved_standards[:3]]
            for e in expected
        )
        status = "HIT " if hit else "MISS"
        print(
            f"  [{status}] {item['query'][:60]:<60}  "
            f"→ {result.retrieved_standards[0] if result.retrieved_standards else 'NONE':<30}  "
            f"({result.latency_seconds:.2f}s)"
        )

    PUBLIC_RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with open(PUBLIC_RESULTS, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    metrics = compute_metrics(results)

    print("\n" + "=" * 50)
    print("  EVALUATION RESULTS")
    print("=" * 50)
    print(f"  Hit Rate @3:         {metrics['hit_rate_at_3']:.2f}%  (target: >80%)")
    print(f"  MRR @5:              {metrics['mrr_at_5']:.4f}   (target: >0.70)")
    print(f"  Avg Latency:         {metrics['avg_latency_seconds']:.2f}s     (target: <5.0s)")
    print("=" * 50)
    print(f"\nResults saved to {PUBLIC_RESULTS}")
    print("Run `python eval_script.py --results data/public_results.json` to verify.")

if __name__ == "__main__":
    main()
