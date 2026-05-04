import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import PDF_PATH, CHUNKS_FILE, VALID_CODES_FILE
from src.chunker import build_chunks, save_chunks, load_chunks
from src.whitelist import build_whitelist, save_whitelist
from src.vector_store import index_chunks, collection_count
from src.bm25_store import build_bm25_index

def main():
    parser = argparse.ArgumentParser(description="Build BIS RAG index")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force rebuild even if cached chunks exist",
    )
    args = parser.parse_args()

    if args.force or not CHUNKS_FILE.exists():
        print(f"[build] Parsing PDF: {PDF_PATH}")
        if not PDF_PATH.exists():
            print(
                f"ERROR: PDF not found at {PDF_PATH}\n"
                "Download SP 21 (2005) from BIS website and place it at data/bis_sp21.pdf"
            )
            sys.exit(1)
        chunks = build_chunks(PDF_PATH)
        save_chunks(chunks)
        print(f"[build] Parsed {len(chunks)} standard chunks → {CHUNKS_FILE}")
    else:
        chunks = load_chunks()
        print(f"[build] Loaded {len(chunks)} cached chunks from {CHUNKS_FILE}")

    if len(chunks) < 400:
        print(
            f"WARNING: Only {len(chunks)} chunks found. "
            "Expected ~570. Check PDF parsing."
        )

    if args.force or not VALID_CODES_FILE.exists():
        whitelist = build_whitelist(chunks)
        save_whitelist(whitelist)
        print(f"[build] Whitelist: {len(whitelist)} valid IS codes → {VALID_CODES_FILE}")
    else:
        from src.whitelist import load_whitelist
        whitelist = load_whitelist()
        print(f"[build] Loaded whitelist: {len(whitelist)} valid IS codes")

    print("[build] Building BM25 index…")
    build_bm25_index(chunks)
    print("[build] BM25 index built.")

    existing = collection_count()
    if not args.force and existing >= len(chunks) * 0.9:
        print(f"[build] ChromaDB already has {existing} docs. Skipping re-embed.")
        print("        Use --force to re-embed.")
    else:
        print(f"[build] Embedding {len(chunks)} chunks into ChromaDB…")
        index_chunks(chunks)
        print(f"[build] ChromaDB has {collection_count()} documents.")

    print("\n" + "=" * 50)
    print("  BUILD COMPLETE")
    print("=" * 50)
    print(f"  Standards parsed:    {len(chunks)}")
    print(f"  Valid codes:         {len(whitelist)}")
    print(f"  ChromaDB docs:       {collection_count()}")
    print("=" * 50)
    print("\nNext step: python scripts/run_eval.py")

if __name__ == "__main__":
    main()
