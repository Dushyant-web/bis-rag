"""
Canonicalize BIS standard codes to the form used in eval_script.py normalization.

Target canonical form:
  "IS 269: 1989"
  "IS 1489 (Part 1): 1991"
  "IS 2185 (Part 2): 1983"

eval_script normalizes by: str(s).replace(" ", "").lower()
So spacing is forgiving, but we still output clean canonical form.
"""
import re
from typing import Optional

# Matches:  IS 269 : 1989  /  IS 1489 (Part 1) : 1991  /  IS2185(Part2):1983
# \s* (not \s+) after IS so compact forms like "IS2185" are accepted too.
_CODE_RE = re.compile(
    r"IS\s*(\d+)"
    r"(?:\s*\(\s*Part\s*(\d+)\s*\))?"
    r"\s*:\s*(\d{4})",
    re.IGNORECASE,
)


def normalize(code: str) -> str:
    """Return canonical string; raises ValueError if not parseable."""
    m = _CODE_RE.search(code)
    if not m:
        raise ValueError(f"Cannot parse BIS code: {code!r}")
    num, part, year = m.group(1), m.group(2), m.group(3)
    if part:
        return f"IS {num} (Part {part}): {year}"
    return f"IS {num}: {year}"


def try_normalize(code: str) -> Optional[str]:
    """Like normalize() but returns None on failure."""
    try:
        return normalize(code)
    except ValueError:
        return None


def extract_codes(text: str) -> list[str]:
    """Extract and normalize all IS codes found in a block of text."""
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
    """Key used by eval_script.py normalization for equality comparison."""
    return code.replace(" ", "").lower()
