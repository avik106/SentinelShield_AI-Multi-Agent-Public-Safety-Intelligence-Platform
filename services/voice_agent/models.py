"""Voice Intelligence Agent — Local model types."""

from pydantic import BaseModel


class TranscriptionResult(BaseModel):
    text: str
    language: str = "en"
    duration_seconds: float = 0.0


class EmotionPrediction(BaseModel):
    emotion: str
    confidence: float
