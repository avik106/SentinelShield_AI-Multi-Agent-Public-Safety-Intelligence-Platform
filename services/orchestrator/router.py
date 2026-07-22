"""
LangGraph Orchestrator — Evidence Router
Decides which agents to invoke based on available inputs.
"""

from __future__ import annotations
from shared.schemas import InputType


def route_evidence(state: dict) -> list[str]:
    """
    Conditional edge routing function for LangGraph.
    Returns list of next node names to invoke (parallel fan-out).
    Considers files, text content, complaint type, and input type.
    """
    routes = []
    
    # Extract details
    text = state.get("text_input") or ""
    audio_path = state.get("audio_path")
    image_path = state.get("image_path")
    pdf_path = state.get("pdf_path")
    
    # Support checking inside metadata dictionary if present
    metadata = state.get("metadata") or {}
    complaint_type = state.get("complaint_type") or metadata.get("complaint_type")
    input_type = state.get("input_type") or metadata.get("input_type")

    # 1. SCAM DETECTION AGENT
    # Run if text, image, or PDF are provided
    if text.strip() or image_path or pdf_path or input_type in ("text", "image", "pdf", "document"):
        routes.append("scam_agent")

    # 2. VOICE INTELLIGENCE AGENT
    # Run if audio is provided or if complaint is categorized as voice phishing
    if audio_path or input_type == "audio" or complaint_type in ("voice_phishing", "deepfake_audio"):
        routes.append("voice_agent")

    # 3. COUNTERFEIT CURRENCY AGENT
    # Run if an image is provided AND it is explicitly related to currency/counterfeiting.
    # This avoids running YOLO currency note analysis on chat screenshots.
    is_counterfeit_case = (
        complaint_type == "counterfeit_currency" or
        input_type == "counterfeit" or
        "counterfeit" in text.lower() or
        "fake note" in text.lower() or
        "currency" in text.lower()
    )
    if image_path and is_counterfeit_case:
        routes.append("counterfeit_agent")

    # 4. FRAUD GRAPH AGENT
    # Run if text/entities are present to link, unless it is a pure counterfeit case
    # that doesn't mention phone numbers/UPIs.
    if complaint_type != "counterfeit_currency" or text.strip():
        routes.append("graph_agent")

    # 5. GEOSPATIAL INTELLIGENCE AGENT
    # Run if coordinates or district are available
    if state.get("lat") is not None or state.get("lon") is not None or state.get("district") or state.get("state"):
        routes.append("geo_agent")

    # Fallback to scam_agent if no routes were selected
    if not routes:
        routes.append("scam_agent")

    return routes


def should_run_rag(state: dict) -> str:
    """Returns 'rag_agent' if officer query present, else skip to evidence generation."""
    if state.get("officer_query"):
        return "rag_agent"
    return "evidence_agent"

