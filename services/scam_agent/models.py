"""
Scam Detection Agent — Local Models
Agent-specific intermediate types used inside the pipeline.
The final output type is `ScamDetectionResult` from shared/schemas.py.
"""

from pydantic import BaseModel


class ClassifierPrediction(BaseModel):
    """Raw output from the HuggingFace zero-shot classifier."""
    label: str
    score: float


class PreprocessedInput(BaseModel):
    """Holds cleaned text and extracted raw context before ML inference."""
    original_text: str
    cleaned_text: str
    ocr_text: str | None = None
    language: str = "en"
    source: str = "text"     # "text" | "image" | "pdf"
