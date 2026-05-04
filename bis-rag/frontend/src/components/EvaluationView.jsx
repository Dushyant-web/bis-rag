import React, { useEffect, useState } from "react";
import { fetchEvaluation } from "../utils/api.js";

function MetricCard({ label, value, target, passed, unit, decimals = 2 }) {
  return (
    <div className={`metric-card ${passed ? "pass" : "fail"}`}>
      <div className="metric-label">{label}</div>
      <div className="metric-value">
        {typeof value === "number" ? value.toFixed(decimals) : value}
        {unit && <span style={{ fontSize: 18 }}>{unit}</span>}
      </div>
      <div className="metric-target">target: {target}</div>
    </div>
  );
}

export default function EvaluationView() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchEvaluation()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <>
        <div className="loading-ring" />
        <p className="loading-text">Loading evaluation results…</p>
      </>
    );
  }

  if (error) {
    return (
      <div className="error-box">
        <strong>Could not load evaluation data.</strong>
        <br />
        Run <code>python scripts/run_eval.py</code> first.
        <br />
        <small>{error}</small>
      </div>
    );
  }

  const m = data.metrics;
  const results = data.results || [];

  function isHit(item) {
    const expected = (item.expected_standards || []).map((s) =>
      s.replace(/\s/g, "").toLowerCase()
    );
    const retrieved = (item.retrieved_standards || [])
      .slice(0, 3)
      .map((s) => s.replace(/\s/g, "").toLowerCase());
    return expected.some((e) => retrieved.includes(e));
  }

  return (
    <div>
      <h2 style={{ marginBottom: 20, fontWeight: 700, fontSize: 22 }}>
        Live Evaluation — Public Test Set
      </h2>

      <div className="eval-grid">
        <MetricCard
          label="Hit Rate @3"
          value={m.hit_rate_at_3}
          target="> 80%"
          unit="%"
          passed={m.hit_rate_at_3 >= 80}
          decimals={2}
        />
        <MetricCard
          label="MRR @5"
          value={m.mrr_at_5}
          target="> 0.70"
          passed={m.mrr_at_5 >= 0.70}
          decimals={4}
        />
        <MetricCard
          label="Avg Latency"
          value={m.avg_latency_seconds}
          target="< 5.0s"
          unit="s"
          passed={m.avg_latency_seconds < 5.0}
          decimals={2}
        />
      </div>

      <h3 style={{ marginBottom: 12, fontWeight: 600, fontSize: 16 }}>
        Per-Query Results ({results.length} queries)
      </h3>

      <table className="eval-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Query</th>
            <th>Expected</th>
            <th>Top Result</th>
            <th>Status</th>
            <th>Latency</th>
          </tr>
        </thead>
        <tbody>
          {results.map((item, i) => {
            const hit = isHit(item);
            return (
              <tr key={item.id}>
                <td>{i + 1}</td>
                <td style={{ maxWidth: 220 }}>{item.query}</td>
                <td style={{ color: "var(--text-muted)", fontSize: 12 }}>
                  {(item.expected_standards || []).join(", ")}
                </td>
                <td style={{ fontSize: 12, color: "var(--accent)" }}>
                  {item.retrieved_standards?.[0] || "—"}
                </td>
                <td className={hit ? "hit" : "miss"}>
                  {hit ? "HIT" : "MISS"}
                </td>
                <td style={{ color: "var(--text-muted)", fontSize: 12 }}>
                  {item.latency_seconds?.toFixed(2)}s
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
