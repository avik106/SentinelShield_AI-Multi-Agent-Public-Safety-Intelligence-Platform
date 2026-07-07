"""
Fraud Graph Intelligence Agent — Core Pipeline
Neo4j entity ingestion → NetworkX graph algorithms → fraud ring detection.
"""

from __future__ import annotations
import time
from loguru import logger

from shared.config import get_settings
from shared.schemas import FraudGraphResult, FraudRing, RiskLevel, ExtractedEntities
from services.graph_agent.utils import (
    normalize_phone, normalize_upi, entity_id,
    pagerank_local, louvain_communities, build_fraud_ring_summary
)

settings = get_settings()


# ─────────────────────────────────────────────────────────────────────────────
# Neo4j helpers (lazy, graceful fallback to NetworkX)
# ─────────────────────────────────────────────────────────────────────────────

def _try_neo4j_session():
    try:
        from shared.db import get_neo4j_driver
        driver = get_neo4j_driver()
        return driver.session()
    except Exception:
        return None


def _upsert_node(session, node_type: str, node_id: str, value: str):
    cypher = (
        f"MERGE (n:{node_type} {{id: $id}}) "
        "SET n.value = $value, n.updated_at = datetime() "
        "RETURN n"
    )
    session.run(cypher, id=node_id, value=value)


def _upsert_edge(session, src_id: str, tgt_id: str, relation: str):
    cypher = (
        "MATCH (a {id: $src}), (b {id: $tgt}) "
        f"MERGE (a)-[r:{relation}]->(b) "
        "SET r.updated_at = datetime()"
    )
    session.run(cypher, src=src_id, tgt=tgt_id)


def _neo4j_ingest(entities: ExtractedEntities, complaint_id: str, fraud_type: str) -> tuple[list[str], int]:
    """
    Upsert all entity nodes and complaint edges into Neo4j.
    Returns (entity_ids_added, edges_count).
    Falls back silently if Neo4j is unavailable.
    """
    session = _try_neo4j_session()
    entity_ids: list[str] = []
    edges = 0

    if session is None:
        logger.warning("[GraphAgent] Neo4j unavailable — skipping graph persistence.")
        return entity_ids, edges

    try:
        with session:
            complaint_node_id = entity_id("Complaint", complaint_id)
            _upsert_node(session, "Complaint", complaint_node_id, complaint_id)

            for phone in entities.phone_numbers:
                norm = normalize_phone(phone)
                nid = entity_id("Phone", norm)
                _upsert_node(session, "Phone", nid, norm)
                _upsert_edge(session, complaint_node_id, nid, "MENTIONS")
                entity_ids.append(nid)
                edges += 1

            for upi in entities.upi_ids:
                norm = normalize_upi(upi)
                nid = entity_id("UPI", norm)
                _upsert_node(session, "UPI", nid, norm)
                _upsert_edge(session, complaint_node_id, nid, "MENTIONS")
                entity_ids.append(nid)
                edges += 1

            for acct in entities.bank_accounts:
                nid = entity_id("BankAccount", acct)
                _upsert_node(session, "BankAccount", nid, acct)
                _upsert_edge(session, complaint_node_id, nid, "MENTIONS")
                entity_ids.append(nid)
                edges += 1

    except Exception as e:
        logger.warning(f"[GraphAgent] Neo4j ingestion error: {e}")

    return entity_ids, edges


def _build_local_graph(entities: ExtractedEntities, complaint_id: str):
    """Build a local NetworkX graph from entities."""
    import networkx as nx
    G = nx.DiGraph()
    complaint_nid = entity_id("Complaint", complaint_id)
    G.add_node(complaint_nid, type="Complaint")

    for phone in entities.phone_numbers:
        nid = entity_id("Phone", normalize_phone(phone))
        G.add_node(nid, type="Phone")
        G.add_edge(complaint_nid, nid, relation="MENTIONS")

    for upi in entities.upi_ids:
        nid = entity_id("UPI", normalize_upi(upi))
        G.add_node(nid, type="UPI")
        G.add_edge(complaint_nid, nid, relation="MENTIONS")

    for acct in entities.bank_accounts:
        nid = entity_id("BankAccount", acct)
        G.add_node(nid, type="BankAccount")
        G.add_edge(complaint_nid, nid, relation="MENTIONS")

    return G


def _risk_level(score: float) -> RiskLevel:
    if score >= 0.80:
        return RiskLevel.CRITICAL
    elif score >= 0.55:
        return RiskLevel.HIGH
    elif score >= 0.30:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


# ─────────────────────────────────────────────────────────────────────────────
# Public Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def run_graph_pipeline(
    entities: ExtractedEntities,
    complaint_id: str,
    case_id: str | None = None,
    fraud_type: str = "unknown",
) -> FraudGraphResult:
    t0 = time.time()

    # 1. Neo4j ingestion
    entity_ids, edges_added = _neo4j_ingest(entities, complaint_id, fraud_type)

    # 2. Local graph for analysis
    G = _build_local_graph(entities, complaint_id)
    all_node_ids = list(G.nodes)

    # 3. PageRank
    pr_scores = pagerank_local(G)

    # 4. Community detection
    communities = louvain_communities(G)
    fraud_rings_raw = build_fraud_ring_summary(communities)
    fraud_rings = [FraudRing(**r) for r in fraud_rings_raw]

    # 5. High-risk nodes (top 20% PageRank)
    if pr_scores:
        threshold = sorted(pr_scores.values(), reverse=True)[:max(1, len(pr_scores) // 5)][-1]
        high_risk = [n for n, s in pr_scores.items() if s >= threshold]
    else:
        high_risk = []

    # 6. Risk score based on entity count + ring sizes
    total_entities = (
        len(entities.phone_numbers) + len(entities.upi_ids) + len(entities.bank_accounts)
    )
    max_ring_size = max((r.size for r in fraud_rings), default=0)
    entity_risk = min(total_entities / 10.0, 1.0)
    ring_risk = min(max_ring_size / 20.0, 1.0)
    risk_score = round(0.5 * entity_risk + 0.5 * ring_risk, 4)
    risk_level = _risk_level(risk_score)

    # 7. Explanation
    parts = [f"Graph analysis of complaint {complaint_id}: {total_entities} entities ingested."]
    if fraud_rings:
        parts.append(f"Detected {len(fraud_rings)} fraud ring(s), largest has {max_ring_size} members.")
    if high_risk:
        parts.append(f"{len(high_risk)} high-influence nodes identified via PageRank.")
    explanation = " ".join(parts)

    elapsed = (time.time() - t0) * 1000
    logger.info(f"[GraphAgent] case={case_id} entities={total_entities} rings={len(fraud_rings)} risk={risk_score:.2f} t={elapsed:.0f}ms")

    return FraudGraphResult(
        entities_added=entity_ids if entity_ids else all_node_ids,
        edges_added=edges_added or G.number_of_edges(),
        fraud_rings=fraud_rings,
        pagerank_scores={k: round(v, 6) for k, v in list(pr_scores.items())[:50]},
        connected_complaints=[complaint_id],
        high_risk_nodes=high_risk[:20],
        risk_score=risk_score,
        risk_level=risk_level,
        explanation=explanation,
        processing_time_ms=elapsed,
    )
