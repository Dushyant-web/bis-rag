"""Pydantic models for pipeline I/O and API responses."""
from typing import Optional
from pydantic import BaseModel, Field


class BISChunk(BaseModel):
    """One atomic standard block parsed from the PDF."""
    chunk_id: str
    standard_code: str                  # canonical: "IS 269: 1989"
    title: str
    section_name: str
    full_text: str
    related_codes: list[str] = Field(default_factory=list)


class RetrievedStandard(BaseModel):
    standard_code: str
    title: str
    confidence: float = 0.0            # rerank score, 0-1
    rationale: str = ""                # LLM-generated 1-liner
    section_name: str = ""


class QueryResult(BaseModel):
    """Schema written to output JSON — must match eval_script.py expectations."""
    id: str
    query: str
    expected_standards: list[str]      # passed through from input
    retrieved_standards: list[str]     # canonical strings, top-5
    latency_seconds: float
    # extra (eval_script ignores unknown fields)
    details: list[RetrievedStandard] = Field(default_factory=list)


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    query: str
    results: list[RetrievedStandard]
    latency_seconds: float
