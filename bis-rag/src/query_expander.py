"""
Zero-latency query expansion using the domain synonym dictionary.
No LLM call — purely deterministic string manipulation.

Strategy:
  1. Tokenise query on whitespace + punctuation.
  2. For each token (and 2-grams), look up synonyms.
  3. Append unique synonym terms to the query.
  4. Return expanded string used for BM25 + vector retrieval.
"""
import re
from src.synonyms import get_synonyms, SYNONYM_MAP


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z]+", text.lower())


def expand_query(query: str) -> str:
    """Return query with synonym expansions appended."""
    tokens = _tokenize(query)
    additions: list[str] = []
    seen = set(tokens)

    # Single tokens
    for tok in tokens:
        for syn in get_synonyms(tok):
            if syn.lower() not in seen and syn.lower() != tok:
                additions.append(syn)
                seen.add(syn.lower())

    # Bigrams (catches "white cement", "slag cement", "ready mix")
    for i in range(len(tokens) - 1):
        bigram = f"{tokens[i]} {tokens[i+1]}"
        if bigram in SYNONYM_MAP:
            for syn in SYNONYM_MAP[bigram]:
                if syn.lower() not in seen:
                    additions.append(syn)
                    seen.add(syn.lower())

    # Trigrams (catches "portland pozzolana cement")
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
