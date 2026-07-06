"""RAG Copilot Agent — Local model types."""
from pydantic import BaseModel


class RetrievedChunk(BaseModel):
    id: str
    text: str
    source_type: str = "case"    # case | evidence | legal
    score: float = 0.0
    relevance_score: float = 0.0
    rrf_score: float = 0.0
