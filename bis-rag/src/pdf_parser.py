"""
Parse SP 21 (2005) PDF into per-standard text blocks.

Strategy:
  1. Extract all text pages with PyMuPDF.
  2. Concatenate into one string (preserving page breaks as newlines).
  3. Split on the "SUMMARY OF" marker — each segment = one standard.
  4. Extract standard code and title from the first 3 lines of each segment.
  5. Determine section_name from the nearest preceding section header.
"""
import re
from pathlib import Path
from typing import Iterator

import pdfplumber

from src.code_normalizer import try_normalize, extract_codes

# Section headers in the PDF — used to assign section_name to each standard
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

# Pattern that starts every standard summary
_SUMMARY_MARKER = re.compile(r"SUMMARY\s+OF\b", re.IGNORECASE)

# First-line IS code pattern
_CODE_LINE_RE = re.compile(
    r"(IS\s+\d+(?:\s*\(\s*Part\s*\d+\s*\))?)\s*:\s*(\d{4})\s+(.*)",
    re.IGNORECASE,
)


def _extract_text(pdf_path: Path) -> str:
    """Return full text of the PDF with page breaks as single newlines."""
    pages = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages.append(text)
    return "\n".join(pages)


def _assign_section(text_before: str) -> str:
    """Find the last section header that appears before this position."""
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
    """
    Extract (standard_code, title) from the opening lines of a segment.
    The segment begins immediately after the "SUMMARY OF" text.
    """
    lines = [l.strip() for l in segment.splitlines() if l.strip()]
    # First non-empty line after SUMMARY OF should be "IS XXXX : YYYY  TITLE"
    for line in lines[:5]:
        m = _CODE_LINE_RE.match(line)
        if m:
            raw_code = f"{m.group(1)}: {m.group(2)}"
            canonical = try_normalize(raw_code)
            title = m.group(3).strip()
            # Title may continue on next lines until a line starting with "("
            if canonical:
                return canonical, title
    # Fallback: try joining first two lines
    joined = " ".join(lines[:2])
    m = _CODE_LINE_RE.match(joined)
    if m:
        raw_code = f"{m.group(1)}: {m.group(2)}"
        canonical = try_normalize(raw_code)
        if canonical:
            return canonical, m.group(3).strip()
    return "", ""


def iter_standard_blocks(pdf_path: Path) -> Iterator[dict]:
    """
    Yield dicts with keys:
        standard_code, title, section_name, full_text, related_codes
    """
    full_text = _extract_text(pdf_path)

    # Split on every SUMMARY OF occurrence; skip index 0 (pre-amble)
    parts = _SUMMARY_MARKER.split(full_text)

    # Build a rough position index for section assignment
    # We iterate parts[1:] — each preceded by the text up to its split
    cumulative = parts[0]

    for segment in parts[1:]:
        section = _assign_section(cumulative)
        cumulative += segment  # grow for next iteration

        code, title = _parse_header(segment)
        if not code:
            # Segment has no parseable IS code — skip (table-of-contents noise)
            continue

        # Clean up the segment: strip page footers like "SP 21 : 2005  1.10"
        cleaned = re.sub(r"SP\s*21\s*:\s*2005\s+[\d.]+\n?", "", segment)
        # Strip the "For detailed information..." trailer for embedding
        cleaned = re.sub(
            r"For detailed information,?\s*refer.*?IS\s*\d+.*?\n?",
            "",
            cleaned,
            flags=re.IGNORECASE | re.DOTALL,
        )
        cleaned = cleaned.strip()

        related = extract_codes(cleaned)
        # Remove self-reference
        related = [c for c in related if c != code]

        yield {
            "standard_code": code,
            "title": title,
            "section_name": section,
            "full_text": cleaned,
            "related_codes": related,
        }
