# BIS Compliance Engine


## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+ (for frontend only)
- 8 GB RAM minimum (no GPU needed)
- NVIDIA NIM API key — free at [build.nvidia.com](https://build.nvidia.com) (optional — local fallback works without it)

### 1. Clone and install

```bash
git clone <your-repo-url>
cd bis-rag

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:
```
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxx
```

> If you skip this, the system automatically uses local models (`BAAI/bge-small-en-v1.5` for embeddings, template-based rationale). Accuracy is slightly lower but everything still works.

### 3. Add the PDF

Download **SP 21 (2005)** from the BIS website and place it at:
```
data/bis_sp21.pdf
```

The file should be ~7.5 MB, 929 pages.

### 4. Build the index

```bash
python scripts/build_index.py
```

This runs once and takes 2–5 minutes. It:
- Parses the PDF into 557 standard chunks
- Extracts 777 valid IS codes into a whitelist
- Embeds all chunks into ChromaDB
- Caches everything to `data/`

Expected output:
```
[build] Parsed 557 standard chunks
[build] Whitelist: 777 valid IS codes
[build] BM25 index built.
[build] ChromaDB has 557 documents.
==================================================
  BUILD COMPLETE
==================================================
```

### 5. Run evaluation

```bash
python scripts/run_eval.py
```

Then verify with the official eval script:
```bash
python eval_script.py --results data/public_results.json
```

Expected:
```
Hit Rate @3  : 100.00%   (Target: >80%)
MRR @5       : 0.9000    (Target: >0.7)
Avg Latency  : 0.83 sec  (Target: <5 seconds)
```

---

## Running the Backend API

```bash
source .venv/bin/activate
uvicorn src.api:app --reload --port 8000
```

API starts at `http://localhost:8000`

**Endpoints:**

| Method | Path | Description |
|---|---|---|
| `POST` | `/query` | Submit a product query, get top 5 standards |
| `GET` | `/evaluate` | Get live metrics from the public test set |
| `GET` | `/health` | Health check |

**Example query:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "33 grade ordinary Portland cement"}'
```

---

## Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

Opens at `http://localhost:5173`

**Three screens:**

1. **Search** — Type any product description, click "Find Standards". Results appear in ~1 second with confidence scores and rationale.
2. **Results** — Top 5 standards as cards. Each shows IS code, title, section, confidence bar, and a one-line explanation of why it matches.
3. **Evaluation** — Live metrics dashboard (Hit Rate, MRR, Latency) pulled from the public test set results. All 10 queries shown with expected vs retrieved and HIT/MISS status.

> The backend must be running on port 8000 for the frontend to work.

---

## Judge Commands

Exactly what judges run:

```bash
# Step 1 — generate results
python inference.py --input hidden_private_dataset.json --output team_results.json

# Step 2 — evaluate
python eval_script.py --results team_results.json
```

`inference.py` never crashes — every query is wrapped in try/except and returns empty results on failure rather than exiting.

---


**BIS × SS Hackathon 2026 — RAG Track**

> Type a product description → get the top 5 applicable Indian Standards in under 1 second.

**Scores on public test set (10 queries):**

| Metric | Score | Target |
|---|---|---|
| Hit Rate @3 | **100%** | > 80% |
| MRR @5 | **0.9000** | > 0.70 |
| Avg Latency | **0.83s** | < 5.0s |
| Hallucinations | **0** | 0 |

---

## How It Works

The source document is SP 21 (2005) — a 929-page PDF published by BIS containing summaries of 557 Indian Standards for building materials (Cement, Steel, Concrete, Aggregates).

### The Pipeline (per query)

```
User query
    │
    ▼
Query Expansion          — synonym dict adds "portland", "opc", etc. (0ms)
    │
    ├──────────────────────┐
    ▼                      ▼
BM25 retrieval         Vector retrieval
(top 25)               (top 25)
exact code match       semantic similarity
    │                      │
    └──────────┬────────────┘
               ▼
         Merge unique
         (~35 candidates)
               │
               ▼
     Cross-encoder rerank         — scores actual query-doc pairs
     (top 5)
               │
               ▼
       Whitelist filter           — only real IS codes pass
               │
               ▼
         Top 5 results
         + confidence score
         + 1-line rationale (UI mode)
```

**Total latency: ~0.83s average on 10 queries (no GPU, Apple Silicon M-series)**

### Why These Scores?

**1. Standard-boundary chunking** — Instead of splitting the PDF by character count (which bleeds text from one standard into another), we split on the `SUMMARY OF` marker that begins every standard in SP 21. Result: 557 atomic chunks, each = exactly one BIS standard. Zero contamination.

**2. Hybrid BM25 + Vector retrieval** — BM25 catches exact IS code matches (`IS 269` in the query → guaranteed hit). Vector search catches semantic synonyms (`lightweight blocks` → `hollow concrete masonry units`). Neither alone is sufficient.

**3. Cross-encoder reranking** — After merging 35–50 candidates, a cross-encoder (`ms-marco-MiniLM-L-6-v2`) scores each query-document pair directly. This is far more accurate than cosine similarity because it sees the query and document together.

**4. Hallucination whitelist** — At build time we extract all 777 valid IS codes from the PDF into a set. Before returning any result, every code is checked against this set. It is structurally impossible to return a code that doesn't exist in the document.

**5. Query expansion** — A hardcoded synonym dictionary (zero latency, no LLM call) expands queries before retrieval. `cement` → adds `portland`, `opc`, `hydraulic`, `slag`. `block` → adds `masonry unit`, `hollow blocks`. Bridges the vocabulary gap between user language and PDF language.

**6. Model pre-warming** — All models (cross-encoder, embedder, ChromaDB) are loaded into RAM during startup, before the first query. Eliminates the 40s cold-start penalty on the first query.

---

## Tech Stack

| Component | Tool |
|---|---|
| PDF parsing | `pdfplumber` (pure Python) |
| BM25 retrieval | `rank-bm25` |
| Vector store | `ChromaDB` (local, disk-persisted) |
| Embeddings | NVIDIA NIM `nv-embedqa-e5-v5` → fallback: `BAAI/bge-small-en-v1.5` |
| Reranking | `cross-encoder/ms-marco-MiniLM-L-6-v2` (CPU, ~200ms) |
| LLM rationale | NVIDIA NIM `meta/llama-3.1-70b-instruct` → fallback: template |
| Backend API | FastAPI + Uvicorn |
| Frontend | React 18 + Vite (plain CSS, no Tailwind) |

---


## Project Structure

```
bis-rag/
├── inference.py              # Judge entry point (root level, required)
├── eval_script.py            # Organizer evaluation script (verbatim)
├── requirements.txt
├── README.md
├── .env.example
│
├── src/
│   ├── config.py             # All paths, model names, env vars
│   ├── schema.py             # Pydantic models for I/O
│   ├── pdf_parser.py         # pdfplumber + SUMMARY OF splitter
│   ├── chunker.py            # Build + cache BISChunk objects
│   ├── code_normalizer.py    # "IS 269 : 1989" → "IS 269: 1989"
│   ├── whitelist.py          # 777 valid IS codes, hallucination filter
│   ├── synonyms.py           # Domain synonym dictionary
│   ├── query_expander.py     # Zero-latency query expansion
│   ├── embedder.py           # NVIDIA NIM + local fallback
│   ├── vector_store.py       # ChromaDB wrapper
│   ├── bm25_store.py         # BM25 wrapper
│   ├── reranker.py           # Cross-encoder reranker
│   ├── llm.py                # LLM rationale + template fallback
│   ├── pipeline.py           # Full RAG orchestration + warmup
│   └── api.py                # FastAPI backend
│
├── scripts/
│   ├── build_index.py        # One-time: PDF → index
│   └── run_eval.py           # Evaluate on public test set
│
├── data/
│   └── public_test_set.json  # 10 public queries
│
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── App.jsx
        ├── index.css
        ├── utils/api.js
        └── components/
            ├── QueryInput.jsx
            ├── ResultsView.jsx
            ├── StandardCard.jsx
            ├── EvaluationView.jsx
            └── ConfidenceBar.jsx
```

---

## Disclosure

- NVIDIA NIM free tier used for embeddings and LLM inference
- Local fallback: `BAAI/bge-small-en-v1.5` (Apache 2.0), `cross-encoder/ms-marco-MiniLM-L-6-v2` (Apache 2.0)
- Source document: SP 21 (2005), Bureau of Indian Standards (public document)
- No GPU required — everything runs on CPU
