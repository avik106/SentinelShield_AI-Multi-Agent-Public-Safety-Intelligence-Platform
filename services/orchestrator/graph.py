"""
LangGraph Orchestrator — StateGraph Definition
Wires all 7 agents into a parallel fan-out → aggregation → RAG → evidence pipeline.
"""

from __future__ import annotations
from typing import TypedDict, Annotated, Any
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
# State Definition with Reducer
# ─────────────────────────────────────────────────────────────────────────────

def reduce_errors(left: list[str], right: list[str]) -> list[str]:
    """Reducer to merge concurrent list updates in parallel branches."""
    merged = list(left)
    for err in right:
        if err not in merged:
            merged.append(err)
    return merged


class OrchestratorState(TypedDict, total=False):
    """LangGraph State Definition."""
    case_id: str
    text_input: str | None
    audio_path: str | None
    image_path: str | None
    pdf_path: str | None
    officer_query: str | None
    lat: float | None
    lon: float | None
    scam_result: Any
    voice_result: Any
    counterfeit_result: Any
    graph_result: Any
    geo_result: Any
    rag_result: Any
    evidence_package: Any
    overall_risk_score: float
    risk_level: Any
    errors: Annotated[list[str], reduce_errors]
    metadata: dict[str, Any]


# ─────────────────────────────────────────────────────────────────────────────
# LangGraph Graph
# ─────────────────────────────────────────────────────────────────────────────

def build_graph():
    """
    Build and compile the SentinelShield LangGraph.

    Graph structure:
    START → route_evidence (conditional fan-out)
      → [scam_agent | voice_agent | counterfeit_agent | graph_agent | geo_agent] (parallel)
      → risk_aggregation
      → should_run_rag (conditional)
        → rag_agent → evidence_agent → END
        → evidence_agent → END
    """
    if not _LANGGRAPH:
        return None

    # Use the schema TypedDict with reducer
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
    
    if "errors" not in state:
        state["errors"] = []

    # 1. Router determines which parallel agents to run
    parallel_agents = route_evidence(state)
    logger.info(f"[Orchestrator Fallback] Routed agents: {parallel_agents}")
    
    # 2. Map route names to node functions
    node_mapping = {
        "scam_agent": scam_agent_node,
        "voice_agent": voice_agent_node,
        "counterfeit_agent": counterfeit_agent_node,
        "graph_agent": graph_agent_node,
        "geo_agent": geo_agent_node,
    }
    
    # 3. Execute agents sequentially with error handling (pipeline continues if one fails)
    for agent_name in parallel_agents:
        node_fn = node_mapping.get(agent_name)
        if node_fn:
            try:
                result = node_fn(state)
                state.update(result)
            except Exception as e:
                logger.error(f"[Orchestrator Fallback] Failed running {agent_name}: {e}", exc_info=True)
                state["errors"].append(f"{agent_name}: {str(e)}")
                
    # 4. Run risk aggregation
    try:
        state.update(risk_aggregation_node(state))
    except Exception as e:
        logger.error(f"[Orchestrator Fallback] Failed risk aggregation: {e}", exc_info=True)
        state["errors"].append(f"risk_aggregation: {str(e)}")
    
    # 5. Check if RAG is needed
    rag_route = should_run_rag(state)
    if rag_route == "rag_agent":
        try:
            state.update(rag_agent_node(state))
        except Exception as e:
            logger.error(f"[Orchestrator Fallback] Failed running rag_agent: {e}", exc_info=True)
            state["errors"].append(f"rag_agent: {str(e)}")
            
    # 6. Run final evidence generation
    try:
        state.update(evidence_agent_node(state))
    except Exception as e:
        logger.error(f"[Orchestrator Fallback] Failed running evidence_agent: {e}", exc_info=True)
        state["errors"].append(f"evidence_agent: {str(e)}")
        
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
