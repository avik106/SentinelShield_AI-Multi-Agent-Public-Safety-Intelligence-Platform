"""
SentinelShield AI — Shared Pydantic Schemas
All agent input/output types are defined here for cross-agent consistency.
"""

from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


# ─────────────────────────────────────────────────────────────────────────────
# Enumerations
# ─────────────────────────────────────────────────────────────────────────────

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ScamType(str, Enum):
    DIGITAL_ARREST = "digital_arrest"
    UPI_FRAUD = "upi_fraud"
    BANKING_FRAUD = "banking_fraud"
    QR_CODE_SCAM = "qr_code_scam"
    WHATSAPP_FRAUD = "whatsapp_fraud"
    VOICE_PHISHING = "voice_phishing"
    GOVERNMENT_IMPERSONATION = "government_impersonation"
    INVESTMENT_FRAUD = "investment_fraud"
    LOTTERY_SCAM = "lottery_scam"
    UNKNOWN = "unknown"


class InputType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    PDF = "pdf"
    DOCUMENT = "document"


# ─────────────────────────────────────────────────────────────────────────────
# Base
# ─────────────────────────────────────────────────────────────────────────────

class BaseAgentResult(BaseModel):
    """Common fields on every agent output."""
    agent_name: str
    processing_time_ms: float = 0.0
    error: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ─────────────────────────────────────────────────────────────────────────────
# Agent 1 — Scam Detection
# ─────────────────────────────────────────────────────────────────────────────

class ExtractedEntities(BaseModel):
    phone_numbers: list[str] = []
    upi_ids: list[str] = []
    bank_accounts: list[str] = []
    urls: list[str] = []
    amounts: list[str] = []
    names: list[str] = []
    emails: list[str] = []
    ip_addresses: list[str] = []


class ScamDetectionResult(BaseAgentResult):
    agent_name: str = "scam_detection_agent"
    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: RiskLevel
    scam_type: ScamType
    confidence: float = Field(..., ge=0.0, le=1.0)
    entities: ExtractedEntities = Field(default_factory=ExtractedEntities)
    explanation: str
    language: str = "en"
    ocr_text: str | None = None
    intent_flags: dict[str, bool] = {}   # urgency, impersonation, payment_request


class ScamDetectionInput(BaseModel):
    text: str | None = None
    image_path: str | None = None
    pdf_path: str | None = None
    case_id: str | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Agent 2 — Voice Intelligence
# ─────────────────────────────────────────────────────────────────────────────

class VoiceIntelligenceResult(BaseAgentResult):
    agent_name: str = "voice_intelligence_agent"
    transcript: str = ""
    language: str = "en"
    is_deepfake: bool = False
    deepfake_confidence: float = Field(0.0, ge=0.0, le=1.0)
    emotion: str = "neutral"
    emotion_confidence: float = Field(0.0, ge=0.0, le=1.0)
    speaker_count: int = 1
    audio_duration_seconds: float = 0.0
    scam_analysis: ScamDetectionResult | None = None
    risk_score: float = Field(0.0, ge=0.0, le=1.0)
    risk_level: RiskLevel = RiskLevel.LOW
    explanation: str = ""


class VoiceIntelligenceInput(BaseModel):
    audio_path: str
    case_id: str | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Agent 3 — Counterfeit Currency Detection
# ─────────────────────────────────────────────────────────────────────────────

class SecurityFeatureCheck(BaseModel):
    security_thread: str = "unknown"     # "pass" | "fail" | "unknown"
    watermark: str = "unknown"
    microprint: str = "unknown"
    color_shift: str = "unknown"
    serial_pattern: str = "unknown"
    uv_feature: str = "unknown"


class CounterfeitDetectionResult(BaseAgentResult):
    agent_name: str = "counterfeit_detection_agent"
    is_counterfeit: bool = False
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    denomination: str | None = None      # "500" | "200" | "100" | "50" ...
    serial_number: str | None = None
    security_features: SecurityFeatureCheck = Field(default_factory=SecurityFeatureCheck)
    risk_score: float = Field(0.0, ge=0.0, le=1.0)
    risk_level: RiskLevel = RiskLevel.LOW
    explanation: str = ""
    annotated_image_path: str | None = None


class CounterfeitDetectionInput(BaseModel):
    image_path: str
    case_id: str | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Agent 4 — Fraud Graph Intelligence
# ─────────────────────────────────────────────────────────────────────────────

class FraudRing(BaseModel):
    ring_id: str
    members: list[str]
    size: int
    risk_level: RiskLevel
    fraud_types: list[str] = []


class FraudGraphResult(BaseAgentResult):
    agent_name: str = "fraud_graph_agent"
    entities_added: list[str] = []
    edges_added: int = 0
    fraud_rings: list[FraudRing] = []
    pagerank_scores: dict[str, float] = {}
    connected_complaints: list[str] = []
    high_risk_nodes: list[str] = []
    risk_score: float = Field(0.0, ge=0.0, le=1.0)
    risk_level: RiskLevel = RiskLevel.LOW
    explanation: str = ""


class FraudGraphInput(BaseModel):
    entities: ExtractedEntities
    complaint_id: str
    case_id: str | None = None
    fraud_type: str = "unknown"


# ─────────────────────────────────────────────────────────────────────────────
# Agent 5 — Geospatial Intelligence
# ─────────────────────────────────────────────────────────────────────────────

class Hotspot(BaseModel):
    lat: float
    lon: float
    radius_km: float
    complaint_count: int
    dominant_fraud_type: str
    risk_level: RiskLevel


class GeoIntelligenceResult(BaseAgentResult):
    agent_name: str = "geo_intelligence_agent"
    hotspots: list[Hotspot] = []
    heatmap_html_path: str | None = None
    patrol_recommendations: list[str] = []
    temporal_trend: dict[str, int] = {}  # hour/day → count
    total_complaints_analyzed: int = 0
    risk_zones: list[dict[str, Any]] = []


class GeoIntelligenceInput(BaseModel):
    lat: float | None = None
    lon: float | None = None
    district: str | None = None
    state: str | None = None
    time_window_days: int = 30


# ─────────────────────────────────────────────────────────────────────────────
# Agent 6 — Hybrid RAG Investigation Copilot
# ─────────────────────────────────────────────────────────────────────────────

class Citation(BaseModel):
    source_id: str
    chunk_text: str
    relevance_score: float
    source_type: str = "case"      # "case" | "evidence" | "legal"


class RAGCopilotResult(BaseAgentResult):
    agent_name: str = "rag_copilot_agent"
    answer: str = ""
    citations: list[Citation] = []
    similar_cases: list[str] = []
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    tokens_used: int = 0


class RAGCopilotInput(BaseModel):
    query: str
    case_id: str | None = None
    officer_id: str | None = None
    top_k: int = 5


# ─────────────────────────────────────────────────────────────────────────────
# Agent 7 — Evidence Generation
# ─────────────────────────────────────────────────────────────────────────────

class EvidenceItem(BaseModel):
    file_path: str
    file_type: str
    sha256: str
    description: str


class EvidencePackage(BaseAgentResult):
    agent_name: str = "evidence_generation_agent"
    case_id: str
    overall_risk_score: float = Field(0.0, ge=0.0, le=1.0)
    risk_level: RiskLevel = RiskLevel.LOW
    fir_draft: str = ""
    executive_summary: str = ""
    investigation_report_path: str | None = None
    evidence_manifest: list[EvidenceItem] = []
    ipc_sections: list[str] = []
    recommended_actions: list[str] = []


class EvidenceGenerationInput(BaseModel):
    case_id: str
    scam_result: ScamDetectionResult | None = None
    voice_result: VoiceIntelligenceResult | None = None
    counterfeit_result: CounterfeitDetectionResult | None = None
    graph_result: FraudGraphResult | None = None
    geo_result: GeoIntelligenceResult | None = None
    rag_result: RAGCopilotResult | None = None
    complainant_name: str | None = None
    complainant_contact: str | None = None


# ─────────────────────────────────────────────────────────────────────────────
# LangGraph Orchestrator State
# ─────────────────────────────────────────────────────────────────────────────

class AgentState(BaseModel):
    """Full state object passed through the LangGraph pipeline."""
    case_id: str
    input_types: list[InputType] = []

    # Raw inputs
    text_input: str | None = None
    audio_path: str | None = None
    image_path: str | None = None
    pdf_path: str | None = None
    officer_query: str | None = None
    lat: float | None = None
    lon: float | None = None

    # Agent outputs
    scam_result: ScamDetectionResult | None = None
    voice_result: VoiceIntelligenceResult | None = None
    counterfeit_result: CounterfeitDetectionResult | None = None
    graph_result: FraudGraphResult | None = None
    geo_result: GeoIntelligenceResult | None = None
    rag_result: RAGCopilotResult | None = None
    evidence_package: EvidencePackage | None = None

    # Aggregated
    overall_risk_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    errors: list[str] = []
    metadata: dict[str, Any] = {}
