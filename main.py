"""
SentinelShield AI — FastAPI Application Entry Point
Exposes REST API endpoints for all 7 agents + orchestrated pipeline.
"""

from __future__ import annotations
import uuid
import time
import mimetypes
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger
from pydantic import BaseModel, Field

from shared.config import get_settings
from shared.db import close_databases, check_all_db_health
from shared.schemas import (
    ScamDetectionInput, ScamDetectionResult, VoiceIntelligenceInput, VoiceIntelligenceResult,
    CounterfeitDetectionInput, CounterfeitDetectionResult, FraudGraphInput, FraudGraphResult,
    GeoIntelligenceInput, GeoIntelligenceResult, RAGCopilotInput, RAGCopilotResult,
    EvidenceGenerationInput, EvidencePackage, ExtractedEntities, RiskLevel,
)

settings = get_settings()


# ─────────────────────────────────────────────────────────────────────────────
# Response model for full pipeline run
# ─────────────────────────────────────────────────────────────────────────────

class PipelineRunResult(BaseModel):
    case_id: str
    overall_risk_score: float
    risk_level: RiskLevel
    evidence_package: EvidencePackage | None = None
    scam_result: ScamDetectionResult | None = None
    voice_result: VoiceIntelligenceResult | None = None
    counterfeit_result: CounterfeitDetectionResult | None = None
    graph_result: FraudGraphResult | None = None
    geo_result: GeoIntelligenceResult | None = None
    rag_result: RAGCopilotResult | None = None
    errors: list[str] = Field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# Lifespan
# ─────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # 1. Enforce dynamic SECRET_KEY if not provided
    if not settings.SECRET_KEY or settings.SECRET_KEY == "change-me-in-production":
        settings.SECRET_KEY = str(uuid.uuid4())
        logger.warning(f"No SECRET_KEY set. Generated a dynamic UUID secret key for this session: {settings.SECRET_KEY}")

    # 2. Ensure upload/report dirs exist
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.REPORTS_DIR).mkdir(parents=True, exist_ok=True)

    # 3. Perform database health checks and initialize schemas
    try:
        logger.info("Performing database connectivity audit…")
        db_status = check_all_db_health()
        for db, online in db_status.items():
            status_str = "ONLINE" if online else "OFFLINE (Graceful Degradation Fallbacks Active)"
            logger.info(f"  - {db.upper()}: {status_str}")

        # Automatically initialize database structures & seeds
        from shared.init_db import initialize_all_databases
        initialize_all_databases()
    except Exception as e:
        logger.warning(f"Database health check/initialization skipped or failed during startup: {e}")


    yield

    # 4. Graceful shutdown
    logger.info("Shutting down SentinelShield AI.")
    close_databases()


# ─────────────────────────────────────────────────────────────────────────────
# App & CORS
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
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────────────────
# Upload File Validation Helper
# ─────────────────────────────────────────────────────────────────────────────

async def validate_uploaded_file(
    file: UploadFile,
    allowed_extensions: list[str],
    allowed_mime_types: list[str],
):
    """Memory-efficient validation checking file extensions, MIME types, and sizes."""
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="Invalid file upload.")

    filename = file.filename
    suffix = Path(filename).suffix.lower()

    # 1. Extension Validation
    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file extension '{suffix}'. Allowed: {', '.join(allowed_extensions)}"
        )

    # 2. MIME Type Validation
    mime_type = file.content_type
    if not mime_type:
        mime_type, _ = mimetypes.guess_type(filename)

    if not mime_type or mime_type.lower() not in allowed_mime_types:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported media type '{mime_type}'. Allowed: {', '.join(allowed_mime_types)}"
        )

    # 3. File Size Validation
    size = 0
    chunk_size = 8192
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        size += len(chunk)
        if size > settings.MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds size limit of {settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)}MB."
            )
    
    # Rewind file seek pointer for downstream usage
    await file.seek(0)


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
# Global Exception Handlers
# ─────────────────────────────────────────────────────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Request validation failed on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "detail": "Request validation failed.",
            "errors": exc.errors(),
            "type": "RequestValidationError",
            "status_code": 422,
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP {exc.status_code} exception on {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "detail": exc.detail,
            "type": "HTTPException",
            "status_code": exc.status_code,
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "detail": str(exc),
            "type": type(exc).__name__,
            "status_code": 500,
        }
    )


# ─────────────────────────────────────────────────────────────────────────────
# Health Check Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health():
    db_status = {}
    try:
        db_status = check_all_db_health()
    except Exception as e:
        logger.warning(f"Failed to fetch database health metrics: {e}")
        
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database_connectivity": db_status
    }


@app.get("/", tags=["Health"])
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}. Visit /docs for the API reference."}


# ─────────────────────────────────────────────────────────────────────────────
# Agent 1 — Scam Detection
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/agents/scam", response_model=ScamDetectionResult, tags=["Scam Detection"])
async def detect_scam(payload: ScamDetectionInput):
    """Analyze text, image, or PDF for scam/fraud signals."""
    from services.scam_agent.pipeline import run_scam_pipeline
    result = run_scam_pipeline(
        text=payload.text,
        image_path=payload.image_path,
        pdf_path=payload.pdf_path,
        case_id=payload.case_id or str(uuid.uuid4()),
    )
    return result


@app.post("/api/agents/scam/upload", response_model=ScamDetectionResult, tags=["Scam Detection"])
async def detect_scam_upload(
    file: UploadFile = File(...),
    case_id: str = Form(default=None),
):
    """Upload an image or PDF for scam detection."""
    # 1. Validate file extension, MIME type, and size
    await validate_uploaded_file(
        file=file,
        allowed_extensions=settings.ALLOWED_EXTENSIONS_SCAM,
        allowed_mime_types=settings.ALLOWED_MIME_TYPES_SCAM,
    )

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
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Agent 2 — Voice Intelligence
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/agents/voice", response_model=VoiceIntelligenceResult, tags=["Voice Intelligence"])
async def analyze_voice(payload: VoiceIntelligenceInput):
    """Analyze an audio file for voice fraud, deepfakes, and emotional manipulation."""
    from services.voice_agent.pipeline import run_voice_pipeline
    result = run_voice_pipeline(audio_path=payload.audio_path, case_id=payload.case_id)
    return result


@app.post("/api/agents/voice/upload", response_model=VoiceIntelligenceResult, tags=["Voice Intelligence"])
async def analyze_voice_upload(
    file: UploadFile = File(...),
    case_id: str = Form(default=None),
):
    """Upload an audio file for voice intelligence analysis."""
    # 1. Validate file extension, MIME type, and size
    await validate_uploaded_file(
        file=file,
        allowed_extensions=settings.ALLOWED_EXTENSIONS_VOICE,
        allowed_mime_types=settings.ALLOWED_MIME_TYPES_VOICE,
    )

    case_id = case_id or str(uuid.uuid4())
    save_path = Path(settings.UPLOAD_DIR) / f"{case_id}_{file.filename}"
    with open(save_path, "wb") as f:
        f.write(await file.read())

    from services.voice_agent.pipeline import run_voice_pipeline
    result = run_voice_pipeline(audio_path=str(save_path), case_id=case_id)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Agent 3 — Counterfeit Currency
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/agents/counterfeit", response_model=CounterfeitDetectionResult, tags=["Counterfeit Detection"])
async def detect_counterfeit(payload: CounterfeitDetectionInput):
    """Analyze a currency note image for counterfeiting."""
    from services.counterfeit_agent.pipeline import run_counterfeit_pipeline
    result = run_counterfeit_pipeline(image_path=payload.image_path, case_id=payload.case_id)
    return result


@app.post("/api/agents/counterfeit/upload", response_model=CounterfeitDetectionResult, tags=["Counterfeit Detection"])
async def detect_counterfeit_upload(
    file: UploadFile = File(...),
    case_id: str = Form(default=None),
):
    """Upload an image of a banknote for counterfeiting checks."""
    # 1. Validate file extension, MIME type, and size
    await validate_uploaded_file(
        file=file,
        allowed_extensions=settings.ALLOWED_EXTENSIONS_COUNTERFEIT,
        allowed_mime_types=settings.ALLOWED_MIME_TYPES_COUNTERFEIT,
    )

    case_id = case_id or str(uuid.uuid4())
    save_path = Path(settings.UPLOAD_DIR) / f"{case_id}_{file.filename}"
    with open(save_path, "wb") as f:
        f.write(await file.read())

    from services.counterfeit_agent.pipeline import run_counterfeit_pipeline
    result = run_counterfeit_pipeline(image_path=str(save_path), case_id=case_id)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Agent 4 — Fraud Graph
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/agents/graph", response_model=FraudGraphResult, tags=["Fraud Graph"])
async def analyze_graph(payload: FraudGraphInput):
    """Ingest fraud entities into Neo4j graph and detect fraud rings."""
    from services.graph_agent.pipeline import run_graph_pipeline
    result = run_graph_pipeline(
        entities=payload.entities,
        complaint_id=payload.complaint_id,
        case_id=payload.case_id,
        fraud_type=payload.fraud_type,
    )
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Agent 5 — Geospatial Intelligence
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/agents/geo", response_model=GeoIntelligenceResult, tags=["Geospatial Intelligence"])
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
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Agent 6 — RAG Copilot
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/agents/rag", response_model=RAGCopilotResult, tags=["RAG Copilot"])
async def query_copilot(payload: RAGCopilotInput):
    """Ask the AI copilot a question about a case using hybrid RAG retrieval."""
    from services.rag_agent.pipeline import run_rag_pipeline
    result = run_rag_pipeline(
        query=payload.query,
        case_id=payload.case_id,
        officer_id=payload.officer_id,
        top_k=payload.top_k,
    )
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Agent 7 — Evidence Generation
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/agents/evidence", response_model=EvidencePackage, tags=["Evidence Generation"])
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
    return result


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


@app.post("/api/pipeline/run", response_model=PipelineRunResult, tags=["Orchestrator"])
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

    ep = result_state.get("evidence_package")
    scam_res = result_state.get("scam_result")
    voice_res = result_state.get("voice_result")
    counterfeit_res = result_state.get("counterfeit_result")
    graph_res = result_state.get("graph_result")
    geo_res = result_state.get("geo_result")
    rag_res = result_state.get("rag_result")
    
    return PipelineRunResult(
        case_id=state["case_id"],
        overall_risk_score=result_state.get("overall_risk_score", 0.0),
        risk_level=result_state.get("risk_level", RiskLevel.LOW),
        evidence_package=ep,
        scam_result=scam_res,
        voice_result=voice_res,
        counterfeit_result=counterfeit_res,
        graph_result=graph_res,
        geo_result=geo_res,
        rag_result=rag_res,
        errors=result_state.get("errors", []),
    )


@app.post("/api/pipeline/upload", response_model=PipelineRunResult, tags=["Orchestrator"])
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

    # 1. Validate uploads
    if audio_file:
        await validate_uploaded_file(
            file=audio_file,
            allowed_extensions=settings.ALLOWED_EXTENSIONS_VOICE,
            allowed_mime_types=settings.ALLOWED_MIME_TYPES_VOICE,
        )

    if image_file:
        # Determine if it's currency note or scan based on text keywords/context
        # Check standard image allowance
        await validate_uploaded_file(
            file=image_file,
            allowed_extensions=settings.ALLOWED_EXTENSIONS_SCAM,
            allowed_mime_types=settings.ALLOWED_MIME_TYPES_SCAM,
        )

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
    
    return PipelineRunResult(
        case_id=case_id,
        overall_risk_score=result_state.get("overall_risk_score", 0.0),
        risk_level=result_state.get("risk_level", RiskLevel.LOW),
        evidence_package=ep,
        scam_result=scam_res,
        voice_result=voice_res,
        counterfeit_result=counterfeit_res,
        graph_result=graph_res,
        geo_result=geo_res,
        rag_result=rag_res,
        errors=result_state.get("errors", []),
    )


@app.get("/health")
async def health_check():
    """Verify system connectivity health metrics across all databases & endpoints."""
    from shared.db import check_all_db_health
    db_status = check_all_db_health()
    
    # System health is healthy if all connections pass, degraded if fallbacks are active
    overall_status = "healthy" if all(db_status.values()) else "degraded"
    
    return {
        "status": overall_status,
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "llm_provider": settings.LLM_PROVIDER,
        "databases": db_status,
        "fallbacks_active": not all(db_status.values())
    }


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
