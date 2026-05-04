from typing import Optional
from pydantic import BaseModel, Field

class BISChunk(BaseModel):
    chunk_id: str
    standard_code: str
    title: str
    section_name: str
    full_text: str
    related_codes: list[str] = Field(default_factory=list)

class RetrievedStandard(BaseModel):
    standard_code: str
    title: str
    confidence: float = 0.0
    rationale: str = ""
    section_name: str = ""

class QueryResult(BaseModel):
    id: str
    query: str
    expected_standards: list[str]
    retrieved_standards: list[str]
    latency_seconds: float
    details: list[RetrievedStandard] = Field(default_factory=list)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    results: list[RetrievedStandard]
    latency_seconds: float
