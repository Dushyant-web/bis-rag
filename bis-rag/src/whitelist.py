import json
from pathlib import Path

from src.config import VALID_CODES_FILE
from src.schema import BISChunk

_whitelist_cache: set[str] | None = None

def build_whitelist(chunks: list[BISChunk]) -> set[str]:
    codes: set[str] = set()
    for chunk in chunks:
        codes.add(chunk.standard_code)
        codes.update(chunk.related_codes)
    return codes

def save_whitelist(codes: set[str], path: Path = VALID_CODES_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sorted(codes), f, ensure_ascii=False, indent=2)

def load_whitelist(path: Path = VALID_CODES_FILE) -> set[str]:
    with open(path, encoding="utf-8") as f:
        return set(json.load(f))

def get_whitelist(chunks: list[BISChunk] | None = None) -> set[str]:
    global _whitelist_cache
    if _whitelist_cache is not None:
        return _whitelist_cache
    if VALID_CODES_FILE.exists():
        _whitelist_cache = load_whitelist()
        return _whitelist_cache
    if chunks is None:
        raise RuntimeError(
            "Whitelist not built yet. Run scripts/build_index.py first."
        )
    _whitelist_cache = build_whitelist(chunks)
    save_whitelist(_whitelist_cache)
    return _whitelist_cache

def filter_codes(codes: list[str], whitelist: set[str]) -> list[str]:
    return [c for c in codes if c in whitelist]
