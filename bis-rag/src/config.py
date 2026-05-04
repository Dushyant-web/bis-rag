"""Central configuration — loads .env and defines all paths/model names."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
CHUNKS_FILE = DATA_DIR / "chunks.json"
VALID_CODES_FILE = DATA_DIR / "valid_codes.json"
CHROMA_DIR = DATA_DIR / "chroma_db"
PDF_PATH = DATA_DIR / "bis_sp21.pdf"
PUBLIC_TEST_SET = DATA_DIR / "public_test_set.json"
PUBLIC_RESULTS = DATA_DIR / "public_results.json"

# ── NVIDIA NIM ─────────────────────────────────────────────────────────────────
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
NVIDIA_EMBED_MODEL = os.getenv("NVIDIA_EMBED_MODEL", "nvidia/nv-embedqa-e5-v5")
NVIDIA_LLM_MODEL = os.getenv("NVIDIA_LLM_MODEL", "meta/llama-3.1-70b-instruct")

# ── Backends ───────────────────────────────────────────────────────────────────
# "nvidia" uses NVIDIA NIM; "local" uses sentence-transformers fallback
EMBED_BACKEND = os.getenv("EMBED_BACKEND", "nvidia" if NVIDIA_API_KEY else "local")
LLM_BACKEND = os.getenv("LLM_BACKEND", "nvidia" if NVIDIA_API_KEY else "local")

# Local fallback embedding model (small, fast, ~130MB)
LOCAL_EMBED_MODEL = "BAAI/bge-small-en-v1.5"

# ── Retrieval settings ─────────────────────────────────────────────────────────
BM25_TOP_K = 25
VECTOR_TOP_K = 25
RERANK_TOP_K = 5          # final returned results
CHROMA_COLLECTION = "bis_standards"

# ── Embedding dimensions ───────────────────────────────────────────────────────
# nv-embedqa-e5-v5 → 1024; bge-small-en-v1.5 → 384
NVIDIA_EMBED_DIM = 1024
LOCAL_EMBED_DIM = 384
