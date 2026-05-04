import re
from pathlib import Path
from typing import Iterator

import pdfplumber

from src.code_normalizer import try_normalize, extract_codes

_SECTION_HEADERS = [
    "CEMENT AND CONCRETE",
    "LIMES",
    "STONES AND STONE PRODUCTS",
    "BURNT CLAY PRODUCTS",
    "FLOORING",
    "TIMBER AND WOOD PRODUCTS",
    "BAMBOO AND CANE",
    "STEEL",
    "IRON",
    "NON-FERROUS METALS",
    "ROOFING",
    "GLASS",
    "PLASTICS",
    "ASBESTOS CEMENT PRODUCTS",
    "INSULATION",
    "PIPES AND FITTINGS",
    "DOORS AND WINDOWS",
    "PAINTS AND VARNISHES",
    "ADHESIVES",
    "SANITARY FITTINGS",
    "ELECTRICAL",
    "WATERPROOFING",
    "FASTENERS",
    "MISCELLANEOUS",
    "AGGREGATES",
    "PLASTER",
    "BLOCKS",
]

_SUMMARY_MARKER = re.compile(r"SUMMARY\s+OF\b", re.IGNORECASE)

_CODE_LINE_RE = re.compile(
    r"(IS\s+\d+(?:\s*\(\s*Part\s*\d+\s*\))?)\s*:\s*(\d{4})\s+(.*)",
    re.IGNORECASE,
)

def _extract_text(pdf_path: Path) -> str:
    pages = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages.append(text)
    return "\n".join(pages)

def _assign_section(text_before: str) -> str:
    upper = text_before.upper()
    best_pos = -1
    best_name = "GENERAL"
    for header in _SECTION_HEADERS:
        pos = upper.rfind(header)
        if pos > best_pos:
            best_pos = pos
            best_name = header.title()
    return best_name

def _parse_header(segment: str) -> tuple[str, str]:
    lines = [l.strip() for l in segment.splitlines() if l.strip()]
    for line in lines[:5]:
        m = _CODE_LINE_RE.match(line)
        if m:
            raw_code = f"{m.group(1)}: {m.group(2)}"
            canonical = try_normalize(raw_code)
            title = m.group(3).strip()
            if canonical:
                return canonical, title
    joined = " ".join(lines[:2])
    m = _CODE_LINE_RE.match(joined)
    if m:
        raw_code = f"{m.group(1)}: {m.group(2)}"
        canonical = try_normalize(raw_code)
        if canonical:
            return canonical, m.group(3).strip()
    return "", ""

def iter_standard_blocks(pdf_path: Path) -> Iterator[dict]:
    full_text = _extract_text(pdf_path)

    parts = _SUMMARY_MARKER.split(full_text)

    cumulative = parts[0]

    for segment in parts[1:]:
        section = _assign_section(cumulative)
        cumulative += segment

        code, title = _parse_header(segment)
        if not code:
            continue

        cleaned = re.sub(r"SP\s*21\s*:\s*2005\s+[\d.]+\n?", "", segment)
        cleaned = re.sub(
            r"For detailed information,?\s*refer.*?IS\s*\d+.*?\n?",
            "",
            cleaned,
            flags=re.IGNORECASE | re.DOTALL,
        )
        cleaned = cleaned.strip()

        related = extract_codes(cleaned)
        related = [c for c in related if c != code]

        yield {
            "standard_code": code,
            "title": title,
            "section_name": section,
            "full_text": cleaned,
            "related_codes": related,
        }
