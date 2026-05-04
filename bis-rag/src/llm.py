from openai import OpenAI

from src.config import (
    NVIDIA_API_KEY,
    NVIDIA_BASE_URL,
    NVIDIA_LLM_MODEL,
    LLM_BACKEND,
)

def _template_rationale(code: str, title: str, query: str) -> str:
    return (
        f"{code} — '{title}' directly specifies requirements "
        f"relevant to: {query[:80]}."
    )

def _nvidia_rationale(query: str, standards: list[dict]) -> list[str]:
    client = OpenAI(api_key=NVIDIA_API_KEY, base_url=NVIDIA_BASE_URL)

    standards_block = "\n".join(
        f"{i+1}. {s['standard_code']} — {s['title']}"
        for i, s in enumerate(standards)
    )

    prompt = (
        "You are a BIS standards expert. For each standard below, write exactly "
        "ONE sentence (max 20 words) explaining why it is relevant to the user's query.\n\n"
        f"User query: {query}\n\n"
        f"Standards:\n{standards_block}\n\n"
        "Respond with exactly 5 lines, one per standard, numbered 1-5. "
        "No extra text."
    )

    response = client.chat.completions.create(
        model=NVIDIA_LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=300,
    )

    text = response.choices[0].message.content.strip()
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    clean: list[str] = []
    for line in lines[:5]:
        stripped = line.lstrip("0123456789").lstrip(". )").strip()
        clean.append(stripped)

    while len(clean) < len(standards):
        i = len(clean)
        s = standards[i]
        clean.append(_template_rationale(s["standard_code"], s["title"], query))

    return clean

def generate_rationales(
    query: str,
    standards: list[dict],
    backend: str = LLM_BACKEND,
) -> list[str]:
    if not standards:
        return []
    if backend == "nvidia" and NVIDIA_API_KEY:
        try:
            return _nvidia_rationale(query, standards)
        except Exception as e:
            print(f"[llm] NVIDIA API failed ({e}), using template fallback.")
    return [
        _template_rationale(s["standard_code"], s["title"], query)
        for s in standards
    ]
