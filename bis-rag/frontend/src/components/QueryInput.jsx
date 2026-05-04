import React, { useState } from "react";

const EXAMPLES = [
  {
    label: "Cement",
    text: "33 grade ordinary Portland cement for general construction",
  },
  {
    label: "Aggregates",
    text: "Coarse and fine aggregates from natural sources for concrete",
  },
  {
    label: "Blocks",
    text: "Lightweight concrete masonry hollow blocks for partition walls",
  },
];

export default function QueryInput({ onSearch, loading }) {
  const [query, setQuery] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (query.trim()) onSearch(query.trim());
  }

  return (
    <div>
      <div className="hero">
        <h1>
          Find your <span>BIS Standard</span>
          <br />
          in seconds
        </h1>
        <p>
          Describe your product or material. Our AI identifies the applicable
          Indian Standards instantly — no consultants needed.
        </p>
      </div>

      <form className="search-box" onSubmit={handleSubmit}>
        <input
          className="search-input"
          type="text"
          placeholder="e.g. 33 grade Portland cement for construction..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={loading}
          autoFocus
        />
        <button
          type="submit"
          className="search-btn"
          disabled={loading || !query.trim()}
        >
          {loading ? "Searching…" : "Find Standards"}
        </button>
      </form>
      <p className="hint">
        Covers Cement, Steel, Concrete &amp; Aggregates — SP 21 (2005)
      </p>

      <div className="examples">
        {EXAMPLES.map((ex) => (
          <div
            key={ex.label}
            className="example-card"
            onClick={() => !loading && onSearch(ex.text)}
          >
            <div className="example-label">{ex.label}</div>
            <div className="example-text">{ex.text}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
