"""
LangGraph Orchestrator — StateGraph Definition
Wires all 7 agents into a parallel fan-out → aggregation → RAG → evidence pipeline.
"""

from __future__ import annotations
from loguru import logger

try:
    from langgraph.graph import StateGraph, END
    _LANGGRAPH = True
except ImportError:
    logger.warning("langgraph not installed. Orchestrator will use sequential fallback.")
    _LANGGRAPH = False

from services.orchestrator.nodes import (
    scam_agent_node,
    voice_agent_node,
    counterfeit_agent_node,
    graph_agent_node,
    geo_agent_node,
    rag_agent_node,
    evidence_agent_node,
    risk_aggregation_node,
)
from services.orchestrator.router import route_evidence, should_run_rag
from shared.schemas import AgentState


# ─────────────────────────────────────────────────────────────────────────────
# LangGraph Graph
# ─────────────────────────────────────────────────────────────────────────────

def build_graph():
    """
    Build and compile the SentinelShield LangGraph.

    Graph structure:
    START → evidence_router (conditional fan-out)
      → [scam_agent | voice_agent | counterfeit_agent | graph_agent | geo_agent] (parallel)
      → risk_aggregation
      → should_run_rag (conditional)
        → rag_agent → evidence_agent → END
        → evidence_agent → END
    """
    if not _LANGGRAPH:
        return None

    graph = StateGraph(AgentState)

    # Register nodes
    graph.add_node("scam_agent", scam_agent_node)
    graph.add_node("voice_agent", voice_agent_node)
    graph.add_node("counterfeit_agent", counterfeit_agent_node)
    graph.add_node("graph_agent", graph_agent_node)
    graph.add_node("geo_agent", geo_agent_node)
    graph.add_node("risk_aggregation", risk_aggregation_node)
    graph.add_node("rag_agent", rag_agent_node)
    graph.add_node("evidence_agent", evidence_agent_node)

    # Entry: conditional fan-out from START
    graph.set_conditional_entry_point(
        route_evidence,
        {
            "scam_agent": "scam_agent",
            "voice_agent": "voice_agent",
            "counterfeit_agent": "counterfeit_agent",
            "graph_agent": "graph_agent",
            "geo_agent": "geo_agent",
        }
    )

    # All parallel agents converge onto risk_aggregation
    for agent in ["scam_agent", "voice_agent", "counterfeit_agent", "graph_agent", "geo_agent"]:
        graph.add_edge(agent, "risk_aggregation")

    # After aggregation: conditional RAG gate
    graph.add_conditional_edges(
        "risk_aggregation",
        should_run_rag,
        {"rag_agent": "rag_agent", "evidence_agent": "evidence_agent"},
    )

    graph.add_edge("rag_agent", "evidence_agent")
    graph.add_edge("evidence_agent", END)

    return graph.compile()


# ─────────────────────────────────────────────────────────────────────────────
# Sequential Fallback (when langgraph not available)
# ─────────────────────────────────────────────────────────────────────────────

def run_sequential(state: dict) -> dict:
    """
    Fallback sequential pipeline (no LangGraph dependency).
    Useful for testing or environments without langgraph.
    """
    logger.info("[Orchestrator] Running sequential fallback pipeline.")

    state.update(scam_agent_node(state))

    if state.get("audio_path"):
        state.update(voice_agent_node(state))

    if state.get("image_path"):
        state.update(counterfeit_agent_node(state))

    state.update(graph_agent_node(state))
    state.update(geo_agent_node(state))
    state.update(risk_aggregation_node(state))

    if state.get("officer_query"):
        state.update(rag_agent_node(state))

    state.update(evidence_agent_node(state))
    return state


# ─────────────────────────────────────────────────────────────────────────────
# Public Runner
# ─────────────────────────────────────────────────────────────────────────────

_compiled_graph = None


def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


def invoke(state: dict) -> dict:
    """
    Main orchestrator entry point.
    Tries LangGraph first; falls back to sequential.
    """
    graph = get_graph()
    if graph is not None:
        logger.info(f"[Orchestrator] Invoking LangGraph pipeline for case_id={state.get('case_id')}")
        return graph.invoke(state)
    else:
        return run_sequential(state)
