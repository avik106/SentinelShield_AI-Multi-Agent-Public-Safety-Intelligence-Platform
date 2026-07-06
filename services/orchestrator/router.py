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
    """
    routes = ["scam_agent", "graph_agent", "geo_agent"]

    # Only invoke voice agent if audio provided
    if state.get("audio_path"):
        routes.append("voice_agent")

    # Only invoke counterfeit if image provided AND no audio (image or text mode)
    if state.get("image_path"):
        routes.append("counterfeit_agent")

    return routes


def should_run_rag(state: dict) -> str:
    """Returns 'rag_agent' if officer query present, else skip to evidence generation."""
    if state.get("officer_query"):
        return "rag_agent"
    return "evidence_agent"
