"""
SentinelShield AI — FastAPI Application Entry Point
Exposes REST API endpoints for all 7 agents + orchestrated pipeline.
"""

from __future__ import annotations
import uuid
import time
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel

from shared.config import get_settings
from shared.schemas import (
    ScamDetectionInput, VoiceIntelligenceInput,
    CounterfeitDetectionInput, FraudGraphInput,
    GeoIntelligenceInput, RAGCopilotInput, EvidenceGenerationInput,
    ExtractedEntities,
)

settings = get_settings()


# ─────────────────────────────────────────────────────────────────────────────
# Lifespan
# ─────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    # Ensure upload/report dirs exist
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.REPORTS_DIR).mkdir(parents=True, exist_ok=True)
    yield
    logger.info("Shutting down SentinelShield AI.")


# ─────────────────────────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="SentinelShield AI",
    description="Multi-Agent Public Safety Intelligence Platform for Digital Fraud Detection.",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────────────────
# Middleware: Request timing
# ─────────────────────────────────────────────────────────────────────────────

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    t0 = time.time()
    response = await call_next(request)
    elapsed = round((time.time() - t0) * 1000, 2)
    response.headers["X-Process-Time-Ms"] = str(elapsed)
    return response


# ─────────────────────────────────────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/", tags=["Health"])
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}. Visit /docs for the API reference."}


# ─────────────────────────────────────────────────────────────────────────────
# Agent 1 — Scam Detection
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/agents/scam", tags=["Scam Detection"])
async def detect_scam(payload: ScamDetectionInput):
    """Analyze text, image, or PDF for scam/fraud signals."""
    from services.scam_agent.pipeline import run_scam_pipeline
    result = run_scam_pipeline(
        text=payload.text,
        image_path=payload.image_path,
        pdf_path=payload.pdf_path,
        case_id=payload.case_id or str(uuid.uuid4()),
    )
    return result.model_dump(mode="json")


@app.post("/api/agents/scam/upload", tags=["Scam Detection"])
async def detect_scam_upload(
    file: UploadFile = File(...),
    case_id: str = Form(default=None),
):
    """Upload an image or PDF for scam detection."""
    case_id = case_id or str(uuid.uuid4())
    save_path = Path(settings.UPLOAD_DIR) / f"{case_id}_{file.filename}"
    with open(save_path, "wb") as f:
        f.write(await file.read())

    from services.scam_agent.pipeline import run_scam_pipeline
    suffix = save_path.suffix.lower()
    result = run_scam_pipeline(
        image_path=str(save_path) if suffix in [".jpg", ".jpeg", ".png", ".webp"] else None,
        pdf_path=str(save_path) if suffix == ".pdf" else None,
        case_id=case_id,
    )
    return result.model_dump(mode="json")


# ─────────────────────────────────────────────────────────────────────────────
# Agent 2 — Voice Intelligence
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/agents/voice", tags=["Voice Intelligence"])
async def analyze_voice(payload: VoiceIntelligenceInput):
    """Analyze an audio file for voice fraud, deepfakes, and emotional manipulation."""
    from services.voice_agent.pipeline import run_voice_pipeline
    result = run_voice_pipeline(audio_path=payload.audio_path, case_id=payload.case_id)
    return result.model_dump(mode="json")


@app.post("/api/agents/voice/upload", tags=["Voice Intelligence"])
async def analyze_voice_upload(
    file: UploadFile = File(...),
    case_id: str = Form(default=None),
):
    """Upload an audio file for voice intelligence analysis."""
    case_id = case_id or str(uuid.uuid4())
    save_path = Path(settings.UPLOAD_DIR) / f"{case_id}_{file.filename}"
    with open(save_path, "wb") as f:
        f.write(await file.read())
    from services.voice_agent.pipeline import run_voice_pipeline
    result = run_voice_pipeline(audio_path=str(save_path), case_id=case_id)
    return result.model_dump(mode="json")


# ─────────────────────────────────────────────────────────────────────────────
# Agent 3 — Counterfeit Currency
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/agents/counterfeit", tags=["Counterfeit Detection"])
async def detect_counterfeit(payload: CounterfeitDetectionInput):
    """Analyze a currency note image for counterfeiting."""
    from services.counterfeit_agent.pipeline import run_counterfeit_pipeline
    result = run_counterfeit_pipeline(image_path=payload.image_path, case_id=payload.case_id)
    return result.model_dump(mode="json")


@app.post("/api/agents/counterfeit/upload", tags=["Counterfeit Detection"])
async def detect_counterfeit_upload(
    file: UploadFile = File(...),
    case_id: str = Form(default=None),
):
    case_id = case_id or str(uuid.uuid4())
    save_path = Path(settings.UPLOAD_DIR) / f"{case_id}_{file.filename}"
    with open(save_path, "wb") as f:
        f.write(await file.read())
    from services.counterfeit_agent.pipeline import run_counterfeit_pipeline
    result = run_counterfeit_pipeline(image_path=str(save_path), case_id=case_id)
    return result.model_dump(mode="json")


# ─────────────────────────────────────────────────────────────────────────────
# Agent 4 — Fraud Graph
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/agents/graph", tags=["Fraud Graph"])
async def analyze_graph(payload: FraudGraphInput):
    """Ingest fraud entities into Neo4j graph and detect fraud rings."""
    from services.graph_agent.pipeline import run_graph_pipeline
    result = run_graph_pipeline(
        entities=payload.entities,
        complaint_id=payload.complaint_id,
        case_id=payload.case_id,
        fraud_type=payload.fraud_type,
    )
    return result.model_dump(mode="json")


# ─────────────────────────────────────────────────────────────────────────────
# Agent 5 — Geospatial Intelligence
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/agents/geo", tags=["Geospatial Intelligence"])
async def analyze_geo(payload: GeoIntelligenceInput):
    """Cluster complaint locations, generate heatmaps, and recommend patrol zones."""
    from services.geo_agent.pipeline import run_geo_pipeline
    result = run_geo_pipeline(
        complaints=[],
        lat=payload.lat,
        lon=payload.lon,
        district=payload.district,
        time_window_days=payload.time_window_days,
    )
    return result.model_dump(mode="json")


# ─────────────────────────────────────────────────────────────────────────────
# Agent 6 — RAG Copilot
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/agents/rag", tags=["RAG Copilot"])
async def query_copilot(payload: RAGCopilotInput):
    """Ask the AI copilot a question about a case using hybrid RAG retrieval."""
    from services.rag_agent.pipeline import run_rag_pipeline
    result = run_rag_pipeline(
        query=payload.query,
        case_id=payload.case_id,
        officer_id=payload.officer_id,
        top_k=payload.top_k,
    )
    return result.model_dump(mode="json")


# ─────────────────────────────────────────────────────────────────────────────
# Agent 7 — Evidence Generation
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/agents/evidence", tags=["Evidence Generation"])
async def generate_evidence(payload: EvidenceGenerationInput):
    """Generate FIR draft, investigation report, and evidence package for a case."""
    from services.evidence_agent.pipeline import run_evidence_pipeline
    result = run_evidence_pipeline(
        case_id=payload.case_id,
        scam_result=payload.scam_result,
        voice_result=payload.voice_result,
        counterfeit_result=payload.counterfeit_result,
        graph_result=payload.graph_result,
        geo_result=payload.geo_result,
        rag_result=payload.rag_result,
        complainant_name=payload.complainant_name,
        complainant_contact=payload.complainant_contact,
    )
    return result.model_dump(mode="json")


# ─────────────────────────────────────────────────────────────────────────────
# Orchestrated Full Pipeline
# ─────────────────────────────────────────────────────────────────────────────

class FullPipelineRequest(BaseModel):
    case_id: str | None = None
    text_input: str | None = None
    audio_path: str | None = None
    image_path: str | None = None
    pdf_path: str | None = None
    officer_query: str | None = None
    lat: float | None = None
    lon: float | None = None
    complainant_name: str | None = None
    complainant_contact: str | None = None


@app.post("/api/pipeline/run", tags=["Orchestrator"])
async def run_full_pipeline(request: FullPipelineRequest):
    """
    Run the full multi-agent pipeline:
    Scam + Voice + Counterfeit + Graph + Geo → Risk Aggregation → RAG → Evidence Package.
    """
    from services.orchestrator.graph import invoke

    state = request.model_dump(exclude_none=False)
    if not state.get("case_id"):
        state["case_id"] = str(uuid.uuid4())

    state.setdefault("errors", [])

    result_state = invoke(state)

    # Serialize evidence package
    ep = result_state.get("evidence_package")
    scam_res = result_state.get("scam_result")
    voice_res = result_state.get("voice_result")
    counterfeit_res = result_state.get("counterfeit_result")
    graph_res = result_state.get("graph_result")
    geo_res = result_state.get("geo_result")
    rag_res = result_state.get("rag_result")
    return {
        "case_id": state["case_id"],
        "overall_risk_score": result_state.get("overall_risk_score", 0.0),
        "risk_level": result_state.get("risk_level", "LOW"),
        "evidence_package": ep.model_dump(mode="json") if ep else None,
        "scam_result": scam_res.model_dump(mode="json") if scam_res else None,
        "voice_result": voice_res.model_dump(mode="json") if voice_res else None,
        "counterfeit_result": counterfeit_res.model_dump(mode="json") if counterfeit_res else None,
        "graph_result": graph_res.model_dump(mode="json") if graph_res else None,
        "geo_result": geo_res.model_dump(mode="json") if geo_res else None,
        "rag_result": rag_res.model_dump(mode="json") if rag_res else None,
        "errors": result_state.get("errors", []),
    }


@app.post("/api/pipeline/upload", tags=["Orchestrator"])
async def run_pipeline_upload(
    text_input: str = Form(default=None),
    officer_query: str = Form(default=None),
    lat: float = Form(default=None),
    lon: float = Form(default=None),
    complainant_name: str = Form(default=None),
    complainant_contact: str = Form(default=None),
    audio_file: UploadFile = File(default=None),
    image_file: UploadFile = File(default=None),
):
    """Full pipeline with file uploads (multipart/form-data)."""
    from services.orchestrator.graph import invoke

    case_id = str(uuid.uuid4())
    state: dict = {
        "case_id": case_id,
        "text_input": text_input,
        "officer_query": officer_query,
        "lat": lat,
        "lon": lon,
        "complainant_name": complainant_name,
        "complainant_contact": complainant_contact,
        "errors": [],
    }

    if audio_file and audio_file.filename:
        path = Path(settings.UPLOAD_DIR) / f"{case_id}_{audio_file.filename}"
        with open(path, "wb") as f:
            f.write(await audio_file.read())
        state["audio_path"] = str(path)

    if image_file and image_file.filename:
        path = Path(settings.UPLOAD_DIR) / f"{case_id}_{image_file.filename}"
        with open(path, "wb") as f:
            f.write(await image_file.read())
        state["image_path"] = str(path)

    result_state = invoke(state)
    ep = result_state.get("evidence_package")
    scam_res = result_state.get("scam_result")
    voice_res = result_state.get("voice_result")
    counterfeit_res = result_state.get("counterfeit_result")
    graph_res = result_state.get("graph_result")
    geo_res = result_state.get("geo_result")
    rag_res = result_state.get("rag_result")
    return {
        "case_id": case_id,
        "overall_risk_score": result_state.get("overall_risk_score", 0.0),
        "risk_level": str(result_state.get("risk_level", "LOW")),
        "evidence_package": ep.model_dump(mode="json") if ep else None,
        "scam_result": scam_res.model_dump(mode="json") if scam_res else None,
        "voice_result": voice_res.model_dump(mode="json") if voice_res else None,
        "counterfeit_result": counterfeit_res.model_dump(mode="json") if counterfeit_res else None,
        "graph_result": graph_res.model_dump(mode="json") if graph_res else None,
        "geo_result": geo_res.model_dump(mode="json") if geo_res else None,
        "rag_result": rag_res.model_dump(mode="json") if rag_res else None,
        "errors": result_state.get("errors", []),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Exception handler
# ─────────────────────────────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__},
    )


# ─────────────────────────────────────────────────────────────────────────────
# Run (dev mode)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
