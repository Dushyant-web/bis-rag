import re
from typing import Optional

_CODE_RE = re.compile(
    r"IS\s*(\d+)"
    r"(?:\s*\(\s*Part\s*(\d+)\s*\))?"
    r"\s*:\s*(\d{4})",
    re.IGNORECASE,
)

def normalize(code: str) -> str:
    m = _CODE_RE.search(code)
    if not m:
        raise ValueError(f"Cannot parse BIS code: {code!r}")
    num, part, year = m.group(1), m.group(2), m.group(3)
    if part:
        return f"IS {num} (Part {part}): {year}"
    return f"IS {num}: {year}"

def try_normalize(code: str) -> Optional[str]:
    try:
        return normalize(code)
    except ValueError:
        return None

def extract_codes(text: str) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for m in _CODE_RE.finditer(text):
        raw = m.group(0)
        norm = try_normalize(raw)
        if norm and norm not in seen:
            seen.add(norm)
            result.append(norm)
    return result

def eval_key(code: str) -> str:
    return code.replace(" ", "").lower()
