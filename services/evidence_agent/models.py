"""Evidence Generation Agent — Local model types."""
from pydantic import BaseModel


class AgentResultsSummary(BaseModel):
    """Consolidated summary from all agent outputs for report generation."""
    fraud_types: list[str] = []
    all_phones: list[str] = []
    all_upi_ids: list[str] = []
    all_amounts: list[str] = []
    all_urls: list[str] = []
    all_scores: list[float] = []
    transcript: str | None = None
    rag_answer: str | None = None
