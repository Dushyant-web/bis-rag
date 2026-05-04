import React from "react";
import ConfidenceBar from "./ConfidenceBar.jsx";

export default function StandardCard({ standard, rank }) {
  const isTop = rank === 1;

  return (
    <div className={`standard-card${isTop ? " rank-1" : ""}`}>
      <div className="card-header">
        <div className={`rank-badge${isTop ? " top" : ""}`}>{rank}</div>
        <div className="card-info">
          <div className="card-code">{standard.standard_code}</div>
          <div className="card-title">{standard.title}</div>
          {standard.section_name && (
            <div className="card-section">{standard.section_name}</div>
          )}
        </div>
      </div>

      {standard.rationale && (
        <div className="card-rationale">{standard.rationale}</div>
      )}

      {standard.confidence > 0 && (
        <ConfidenceBar score={standard.confidence} />
      )}
    </div>
  );
}
