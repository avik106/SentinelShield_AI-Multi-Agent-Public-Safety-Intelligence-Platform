"""Evidence Generation Agent — Local model types."""
from pydantic import BaseModel, Field



class AgentResultsSummary(BaseModel):
    """Consolidated summary from all agent outputs for report generation."""
    fraud_types: list[str] = Field(default_factory=list)
    all_phones: list[str] = Field(default_factory=list)
    all_upi_ids: list[str] = Field(default_factory=list)
    all_amounts: list[str] = Field(default_factory=list)
    all_urls: list[str] = Field(default_factory=list)
    all_scores: list[float] = Field(default_factory=list)

    transcript: str | None = None
    rag_answer: str | None = None
