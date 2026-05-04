import React, { useState } from "react";
import QueryInput from "./components/QueryInput.jsx";
import ResultsView from "./components/ResultsView.jsx";
import EvaluationView from "./components/EvaluationView.jsx";
import { queryStandards } from "./utils/api.js";

// Screens: "search" | "results" | "evaluation"
export default function App() {
  const [screen, setScreen] = useState("search");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [queryText, setQueryText] = useState("");
  const [results, setResults] = useState(null);

  async function handleSearch(query) {
    setError(null);
    setLoading(true);
    setQueryText(query);
    try {
      const data = await queryStandards(query);
      setResults(data);
      setScreen("results");
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  function handleBack() {
    setScreen("search");
    setResults(null);
    setError(null);
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-logo">
          BIS <span>Compliance</span> Engine
        </div>
        <nav className="nav">
          <button
            className={`nav-btn${screen !== "evaluation" ? " active" : ""}`}
            onClick={handleBack}
          >
            Search
          </button>
          <button
            className={`nav-btn${screen === "evaluation" ? " active" : ""}`}
            onClick={() => setScreen("evaluation")}
          >
            Evaluation
          </button>
        </nav>
      </header>

      <main className="main">
        {screen === "search" && (
          <>
            <QueryInput onSearch={handleSearch} loading={loading} />
            {loading && (
              <>
                <div className="loading-ring" />
                <p className="loading-text">
                  Running hybrid retrieval + reranking…
                </p>
              </>
            )}
            {error && <div className="error-box">{error}</div>}
          </>
        )}

        {screen === "results" && results && (
          <ResultsView
            query={queryText}
            results={results.results}
            latency={results.latency_seconds}
            onBack={handleBack}
          />
        )}

        {screen === "evaluation" && <EvaluationView />}
      </main>
    </div>
  );
}
