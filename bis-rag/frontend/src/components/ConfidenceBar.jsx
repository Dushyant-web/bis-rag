import React from "react";

function confidenceColor(score) {
  if (score >= 0.75) return "#22c55e";
  if (score >= 0.50) return "#f59e0b";
  return "#ef4444";
}

export default function ConfidenceBar({ score }) {
  const pct = Math.round(score * 100);
  const color = confidenceColor(score);

  return (
    <div className="confidence-row">
      <span className="confidence-label">Confidence</span>
      <div className="confidence-track">
        <div
          className="confidence-fill"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
      <span className="confidence-pct" style={{ color }}>
        {pct}%
      </span>
    </div>
  );
}
