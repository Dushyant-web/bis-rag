import json
from pathlib import Path
from tqdm import tqdm

from src.schema import BISChunk
from src.pdf_parser import iter_standard_blocks
from src.config import CHUNKS_FILE, PDF_PATH

def build_chunks(pdf_path: Path = PDF_PATH) -> list[BISChunk]:
    chunks: list[BISChunk] = []
    seen_codes: set[str] = set()

    for i, block in enumerate(tqdm(iter_standard_blocks(pdf_path), desc="Parsing standards")):
        code = block["standard_code"]
        chunk_id = f"chunk_{i:04d}"
        if code in seen_codes:
            chunk_id = f"chunk_{i:04d}_dup"
        seen_codes.add(code)

        chunks.append(
            BISChunk(
                chunk_id=chunk_id,
                standard_code=code,
                title=block["title"],
                section_name=block["section_name"],
                full_text=block["full_text"],
                related_codes=block["related_codes"],
            )
        )

    return chunks

def save_chunks(chunks: list[BISChunk], path: Path = CHUNKS_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([c.model_dump() for c in chunks], f, ensure_ascii=False, indent=2)

def load_chunks(path: Path = CHUNKS_FILE) -> list[BISChunk]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [BISChunk(**d) for d in data]

def get_chunks(force_rebuild: bool = False) -> list[BISChunk]:
    if not force_rebuild and CHUNKS_FILE.exists():
        return load_chunks()
    if not PDF_PATH.exists():
        raise FileNotFoundError(
            f"PDF not found at {PDF_PATH}. "
            "Place bis_sp21.pdf in the data/ directory."
        )
    chunks = build_chunks()
    save_chunks(chunks)
    return chunks
