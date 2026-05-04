
SYNONYM_MAP: dict[str, list[str]] = {
    "cement": ["portland", "opc", "hydraulic cement", "binding", "slag cement",
               "pozzolana", "masonry cement", "supersulphated"],
    "opc": ["ordinary portland cement", "portland cement"],
    "ppc": ["portland pozzolana cement", "pozzolana cement", "fly ash", "calcined clay"],
    "psc": ["portland slag cement", "slag cement", "ground granulated blast"],
    "white cement": ["white portland cement"],
    "rapid hardening cement": ["high early strength"],
    "low heat cement": ["low heat portland"],

    "aggregate": ["coarse aggregate", "fine aggregate", "sand", "gravel",
                  "crushed stone", "natural sources", "all-in-aggregate"],
    "sand": ["fine aggregate", "natural sand"],
    "gravel": ["coarse aggregate", "natural gravel"],
    "crushed stone": ["coarse aggregate", "machine crushed"],

    "concrete": ["rcc", "pcc", "ready mix", "masonry", "precast concrete",
                 "hollow blocks", "solid blocks"],
    "precast": ["precast concrete", "factory made"],
    "rcc": ["reinforced cement concrete"],
    "ready mix": ["ready mixed concrete"],

    "block": ["masonry unit", "concrete masonry", "hollow blocks",
              "solid blocks", "paving blocks"],
    "brick": ["burnt clay brick", "fly ash brick", "sand lime brick"],
    "masonry": ["brickwork", "masonry unit", "concrete masonry"],

    "steel": ["rebar", "tmt bar", "structural steel", "reinforcement",
              "mild steel", "high strength deformed"],
    "rebar": ["reinforcing bar", "deformed bar", "tor steel"],
    "tmt": ["thermo-mechanically treated", "high strength deformed"],
    "structural steel": ["rolled steel", "i-section", "channel", "angle"],

    "pipe": ["conduit", "water main", "sewer pipe", "drainage pipe"],
    "water pipe": ["water main", "precast concrete pipe", "asbestos cement pipe"],

    "roofing": ["roof sheet", "cladding", "roof tile", "corrugated sheet"],
    "asbestos cement": ["ac sheet", "corrugated", "fibre cement"],
    "sheet": ["corrugated sheet", "flat sheet", "profiled sheet"],

    "lime": ["quick lime", "hydrated lime", "fat lime", "hydraulic lime",
             "calcium oxide"],

    "glass": ["flat glass", "sheet glass", "safety glass", "wired glass"],

    "wood": ["timber", "plywood", "particle board", "fibre board", "hardwood"],
    "plywood": ["commercial plywood", "marine plywood", "structural plywood"],

    "paint": ["coating", "varnish", "enamel", "primer", "distemper"],

    "grade": ["strength class", "category", "type"],
    "standard": ["specification", "code", "requirement"],
}

def get_synonyms(term: str) -> list[str]:
    lower = term.lower()
    result = [lower]
    if lower in SYNONYM_MAP:
        result.extend(SYNONYM_MAP[lower])
    for key, vals in SYNONYM_MAP.items():
        if lower in [v.lower() for v in vals] and key not in result:
            result.append(key)
    return list(dict.fromkeys(result))
