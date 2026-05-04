import React from "react";
import StandardCard from "./StandardCard.jsx";

export default function ResultsView({ query, results, latency, onBack }) {
  return (
    <div>
      <div className="results-header">
        <button className="back-btn" onClick={onBack}>
          ← Back
        </button>
        <div className="results-meta">
          {results.length} standard{results.length !== 1 ? "s" : ""} &nbsp;·&nbsp;{" "}
          {(latency * 1000).toFixed(0)} ms
        </div>
      </div>

      <div className="results-query">"{query}"</div>

      {results.length === 0 ? (
        <p style={{ color: "var(--text-muted)", textAlign: "center", padding: "40px 0" }}>
          No applicable standards found. Try rephrasing your query.
        </p>
      ) : (
        <div className="results-list">
          {results.map((std, i) => (
            <StandardCard key={std.standard_code} standard={std} rank={i + 1} />
          ))}
        </div>
      )}
    </div>
  );
}
