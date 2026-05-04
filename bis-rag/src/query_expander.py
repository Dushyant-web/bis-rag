import re
from src.synonyms import get_synonyms, SYNONYM_MAP

def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z]+", text.lower())

def expand_query(query: str) -> str:
    tokens = _tokenize(query)
    additions: list[str] = []
    seen = set(tokens)

    for tok in tokens:
        for syn in get_synonyms(tok):
            if syn.lower() not in seen and syn.lower() != tok:
                additions.append(syn)
                seen.add(syn.lower())

    for i in range(len(tokens) - 1):
        bigram = f"{tokens[i]} {tokens[i+1]}"
        if bigram in SYNONYM_MAP:
            for syn in SYNONYM_MAP[bigram]:
                if syn.lower() not in seen:
                    additions.append(syn)
                    seen.add(syn.lower())

    for i in range(len(tokens) - 2):
        trigram = f"{tokens[i]} {tokens[i+1]} {tokens[i+2]}"
        if trigram in SYNONYM_MAP:
            for syn in SYNONYM_MAP[trigram]:
                if syn.lower() not in seen:
                    additions.append(syn)
                    seen.add(syn.lower())

    if additions:
        return query + " " + " ".join(additions)
    return query
