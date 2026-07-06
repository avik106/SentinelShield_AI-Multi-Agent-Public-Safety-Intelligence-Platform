"""Counterfeit Detection Agent — Local model types."""
from pydantic import BaseModel


class YOLODetection(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    label: str = "banknote"
