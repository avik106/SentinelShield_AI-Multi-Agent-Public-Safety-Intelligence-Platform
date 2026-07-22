"""
LangGraph Orchestrator — Node Wrappers
Each node wraps a corresponding agent and handles state in/out.
Also includes the risk aggregation node wrapper.
"""

from __future__ import annotations
from loguru import logger

from shared.schemas import RiskLevel
from shared.fusion import calculate_aggregated_risk

# Import all agent nodes
from services.scam_agent.agent import scam_agent_node
from services.voice_agent.agent import voice_agent_node
from services.counterfeit_agent.agent import counterfeit_agent_node
from services.graph_agent.agent import graph_agent_node
from services.geo_agent.agent import geo_agent_node
from services.rag_agent.agent import rag_agent_node
from services.evidence_agent.agent import evidence_agent_node


# ─────────────────────────────────────────────────────────────────────────────
# LangGraph Node
# ─────────────────────────────────────────────────────────────────────────────

def risk_aggregation_node(state: dict) -> dict:
    """
    LangGraph Node Wrapper for risk aggregation.
    Combines agent scores and stores correlation details in the metadata.
    """
    overall, level, correlations, fused_entities, overall_confidence = calculate_aggregated_risk(state)
    
    metadata = dict(state.get("metadata", {}))
    metadata["correlations"] = correlations
    metadata["fused_entities"] = fused_entities
    metadata["overall_confidence"] = overall_confidence


    logger.info(
        f"[Orchestrator] Aggregated Risk: score={overall:.4f}, level={level.value}, "
        f"correlations={len(correlations)}"
    )

    return {
        "overall_risk_score": overall,
        "risk_level": level,
        "metadata": metadata,
    }
