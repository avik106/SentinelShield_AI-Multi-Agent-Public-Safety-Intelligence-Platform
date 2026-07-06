"""
LangGraph Orchestrator — Node Wrappers
Each node wraps a corresponding agent and handles state in/out.
Also includes the risk aggregation node.
"""

from __future__ import annotations
from loguru import logger

from shared.schemas import RiskLevel

# Import all agent nodes
from services.scam_agent.agent import scam_agent_node
from services.voice_agent.agent import voice_agent_node
from services.counterfeit_agent.agent import counterfeit_agent_node
from services.graph_agent.agent import graph_agent_node
from services.geo_agent.agent import geo_agent_node
from services.rag_agent.agent import rag_agent_node
from services.evidence_agent.agent import evidence_agent_node


def risk_aggregation_node(state: dict) -> dict:
    """
    Combines risk scores from completed agents into overall_risk_score and risk_level.
    Called after the parallel fan-out phase completes.
    """
    scores = []
    for key in ["scam_result", "voice_result", "counterfeit_result", "graph_result"]:
        result = state.get(key)
        if result and hasattr(result, "risk_score") and result.risk_score is not None:
            scores.append(result.risk_score)

    if not scores:
        overall = 0.0
    else:
        # Weighted: highest score gets the most influence
        scores_sorted = sorted(scores, reverse=True)
        weights = [1 / (2**i) for i in range(len(scores_sorted))]
        overall = sum(s * w for s, w in zip(scores_sorted, weights)) / sum(weights)
        overall = round(overall, 4)

    if overall >= 0.80:
        level = RiskLevel.CRITICAL
    elif overall >= 0.55:
        level = RiskLevel.HIGH
    elif overall >= 0.30:
        level = RiskLevel.MEDIUM
    else:
        level = RiskLevel.LOW

    logger.info(f"[Orchestrator] Risk aggregation: score={overall:.2f}, level={level.value}")
    return {"overall_risk_score": overall, "risk_level": level}
