"""Geo Intelligence Agent — Local model types."""
from pydantic import BaseModel


class ComplaintRecord(BaseModel):
    lat: float
    lon: float
    fraud_type: str = "unknown"
    timestamp: str | None = None
    complaint_id: str | None = None
