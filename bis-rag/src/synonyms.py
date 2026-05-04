"""
Domain synonym dictionary for BIS building materials vocabulary.
Maps user-facing terms to PDF-vocabulary equivalents.
All lookups are lowercase.
"""

SYNONYM_MAP: dict[str, list[str]] = {
    # Cement variants
    "cement": ["portland", "opc", "hydraulic cement", "binding", "slag cement",
               "pozzolana", "masonry cement", "supersulphated"],
    "opc": ["ordinary portland cement", "portland cement"],
    "ppc": ["portland pozzolana cement", "pozzolana cement", "fly ash", "calcined clay"],
    "psc": ["portland slag cement", "slag cement", "ground granulated blast"],
    "white cement": ["white portland cement"],
    "rapid hardening cement": ["high early strength"],
    "low heat cement": ["low heat portland"],

    # Aggregates
    "aggregate": ["coarse aggregate", "fine aggregate", "sand", "gravel",
                  "crushed stone", "natural sources", "all-in-aggregate"],
    "sand": ["fine aggregate", "natural sand"],
    "gravel": ["coarse aggregate", "natural gravel"],
    "crushed stone": ["coarse aggregate", "machine crushed"],

    # Concrete
    "concrete": ["rcc", "pcc", "ready mix", "masonry", "precast concrete",
                 "hollow blocks", "solid blocks"],
    "precast": ["precast concrete", "factory made"],
    "rcc": ["reinforced cement concrete"],
    "ready mix": ["ready mixed concrete"],

    # Blocks and masonry
    "block": ["masonry unit", "concrete masonry", "hollow blocks",
              "solid blocks", "paving blocks"],
    "brick": ["burnt clay brick", "fly ash brick", "sand lime brick"],
    "masonry": ["brickwork", "masonry unit", "concrete masonry"],

    # Steel
    "steel": ["rebar", "tmt bar", "structural steel", "reinforcement",
              "mild steel", "high strength deformed"],
    "rebar": ["reinforcing bar", "deformed bar", "tor steel"],
    "tmt": ["thermo-mechanically treated", "high strength deformed"],
    "structural steel": ["rolled steel", "i-section", "channel", "angle"],

    # Pipes
    "pipe": ["conduit", "water main", "sewer pipe", "drainage pipe"],
    "water pipe": ["water main", "precast concrete pipe", "asbestos cement pipe"],

    # Roofing
    "roofing": ["roof sheet", "cladding", "roof tile", "corrugated sheet"],
    "asbestos cement": ["ac sheet", "corrugated", "fibre cement"],
    "sheet": ["corrugated sheet", "flat sheet", "profiled sheet"],

    # Lime
    "lime": ["quick lime", "hydrated lime", "fat lime", "hydraulic lime",
             "calcium oxide"],

    # Glass
    "glass": ["flat glass", "sheet glass", "safety glass", "wired glass"],

    # Wood / Timber
    "wood": ["timber", "plywood", "particle board", "fibre board", "hardwood"],
    "plywood": ["commercial plywood", "marine plywood", "structural plywood"],

    # Paints
    "paint": ["coating", "varnish", "enamel", "primer", "distemper"],

    # General
    "grade": ["strength class", "category", "type"],
    "standard": ["specification", "code", "requirement"],
}


def get_synonyms(term: str) -> list[str]:
    """Return synonyms for a term (case-insensitive), including the term itself."""
    lower = term.lower()
    result = [lower]
    if lower in SYNONYM_MAP:
        result.extend(SYNONYM_MAP[lower])
    # Reverse lookup — if term matches any value, add its key
    for key, vals in SYNONYM_MAP.items():
        if lower in [v.lower() for v in vals] and key not in result:
            result.append(key)
    return list(dict.fromkeys(result))  # deduplicate, preserve order
