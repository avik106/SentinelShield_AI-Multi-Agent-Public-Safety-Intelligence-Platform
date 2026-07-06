"""
Fraud Graph Intelligence Agent — Utilities
Entity normalization, Cypher generation helpers, graph analysis utilities.
"""

from __future__ import annotations
import hashlib
from loguru import logger


def normalize_phone(phone: str) -> str:
    """Normalize Indian phone number to +91XXXXXXXXXX format."""
    import re
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 10:
        return f"+91{digits}"
    if len(digits) == 12 and digits.startswith("91"):
        return f"+{digits}"
    return digits


def normalize_upi(upi: str) -> str:
    """Lowercase and strip whitespace from UPI ID."""
    return upi.strip().lower()


def entity_id(entity_type: str, value: str) -> str:
    """Generate a deterministic short ID for a graph node."""
    raw = f"{entity_type}:{value}"
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def build_fraud_ring_summary(communities: list[list[str]]) -> list[dict]:
    """Convert community lists into FraudRing-style dicts."""
    from shared.schemas import RiskLevel
    rings = []
    for i, community in enumerate(communities):
        size = len(community)
        risk = RiskLevel.CRITICAL if size >= 10 else RiskLevel.HIGH if size >= 5 else RiskLevel.MEDIUM
        rings.append({
            "ring_id": f"ring_{i:03d}",
            "members": community,
            "size": size,
            "risk_level": risk.value,
            "fraud_types": [],
        })
    return rings


def pagerank_local(G) -> dict[str, float]:
    """Run NetworkX PageRank on a local graph."""
    try:
        import networkx as nx
        if len(G.nodes) == 0:
            return {}
        return nx.pagerank(G, alpha=0.85, max_iter=100)
    except Exception as e:
        logger.warning(f"PageRank failed: {e}")
        return {}


def louvain_communities(G) -> list[list[str]]:
    """Detect communities using greedy modularity (networkx)."""
    try:
        import networkx as nx
        from networkx.algorithms.community import greedy_modularity_communities
        if len(G.nodes) < 3:
            return [list(G.nodes)]
        comms = greedy_modularity_communities(G.to_undirected())
        return [list(c) for c in comms]
    except Exception as e:
        logger.warning(f"Community detection failed: {e}")
        return []
