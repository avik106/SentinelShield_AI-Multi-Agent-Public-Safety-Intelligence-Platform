"""
Fraud Graph Intelligence Agent — Core Pipeline
Neo4j entity ingestion → NetworkX graph algorithms → fraud ring detection.
Exposes detailed edge metadata and graph explanations.
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


def _upsert_edge(session, src_id: str, tgt_id: str, relation: str, confidence: float, source_agent: str, evidence: str):
    cypher = (
        "MATCH (a {id: $src}), (b {id: $tgt}) "
        f"MERGE (a)-[r:{relation}]->(b) "
        "SET r.updated_at = datetime(), r.confidence = $conf, r.source_agent = $agent, r.evidence = $ev"
    )
    session.run(cypher, src=src_id, tgt=tgt_id, conf=confidence, agent=source_agent, ev=evidence)


def _neo4j_ingest(
    entities: ExtractedEntities,
    complaint_id: str,
    fraud_type: str,
    edge_metadata_list: list[dict],
) -> tuple[list[str], int, list[dict]]:
    """
    Upsert all entity nodes and complaint edges into Neo4j.
    Also returns a list of external cross-complaint matches found in Neo4j.
    """
    session = _try_neo4j_session()
    entity_ids: list[str] = []
    edges = 0
    cross_matches = []

    if session is None:
        logger.warning("[GraphAgent] Neo4j unavailable — skipping graph persistence.")
        return entity_ids, edges, cross_matches

    try:
        with session:
            complaint_node_id = entity_id("Complaint", complaint_id)
            _upsert_node(session, "Complaint", complaint_node_id, complaint_id)

            # Ingestion helper
            def ingest_list(values, node_type, normalize_fn=None):
                nonlocal edges
                for val in values:
                    norm = normalize_fn(val) if normalize_fn else val
                    nid = entity_id(node_type, norm)
                    _upsert_node(session, node_type, nid, norm)
                    
                    # Locate corresponding edge metadata to persist
                    meta = next((m for m in edge_metadata_list if m["target"] == nid), None)
                    conf = meta["confidence"] if meta else 0.95
                    agent = meta["source_agent"] if meta else "scam_agent"
                    evidence = meta["evidence"] if meta else "Extracted from case text"
                    
                    _upsert_edge(session, complaint_node_id, nid, "MENTIONS", conf, agent, evidence)
                    entity_ids.append(nid)
                    edges += 1

                    # Check if this entity is connected to other previous complaints
                    query = (
                        "MATCH (e {id: $nid})<-[:MENTIONS]-(c:Complaint) "
                        "WHERE c.id <> $cid "
                        "RETURN c.id LIMIT 5"
                    )
                    res = session.run(query, nid=nid, cid=complaint_node_id)
                    for r in res:
                        cross_matches.append({
                            "entity_id": nid,
                            "value": norm,
                            "type": node_type,
                            "connected_complaint_id": r[0]
                        })

            ingest_list(entities.phone_numbers, "Phone", normalize_phone)
            ingest_list(entities.upi_ids, "UPI", normalize_upi)
            ingest_list(entities.bank_accounts, "BankAccount")

    except Exception as e:
        logger.warning(f"[GraphAgent] Neo4j ingestion error: {e}")

    return entity_ids, edges, cross_matches


def _build_local_graph(entities: ExtractedEntities, complaint_id: str, edge_metadata_list: list[dict]):
    """Build a local NetworkX graph from entities, attaching metadata to edges."""
    import networkx as nx
    G = nx.DiGraph()
    complaint_nid = entity_id("Complaint", complaint_id)
    G.add_node(complaint_nid, type="Complaint")

    def add_local_edges(values, node_type, normalize_fn=None):
        for val in values:
            norm = normalize_fn(val) if normalize_fn else val
            nid = entity_id(node_type, norm)
            G.add_node(nid, type=node_type)
            
            # Match edge metadata
            meta = next((m for m in edge_metadata_list if m["target"] == nid), None)
            conf = meta["confidence"] if meta else 0.95
            agent = meta["source_agent"] if meta else "scam_agent"
            evidence = meta["evidence"] if meta else "Extracted from complaint"
            
            G.add_edge(complaint_nid, nid, relation="MENTIONS", confidence=conf, source_agent=agent, evidence=evidence)

    add_local_edges(entities.phone_numbers, "Phone", normalize_phone)
    add_local_edges(entities.upi_ids, "UPI", normalize_upi)
    add_local_edges(entities.bank_accounts, "BankAccount")

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
    """
    Ingest, analyze, and build community risk maps for entities.
    Never throws unhandled exceptions.
    """
    t0 = time.time()
    warnings = []

    try:
        total_entities = len(entities.phone_numbers) + len(entities.upi_ids) + len(entities.bank_accounts)


        if total_entities == 0:
            elapsed = (time.time() - t0) * 1000
            return FraudGraphResult(
                status="SKIPPED",
                reason="No graph-linkable entities provided.",
                explanation="No phone numbers, UPI IDs, or bank accounts extracted. Skipping graph generation.",
                processing_time_ms=elapsed,
                execution_time_ms=elapsed,
            )

        # 1. Build local edge metadata manifest
        edge_metadata_list = []
        complaint_nid = entity_id("Complaint", complaint_id)

        for phone in entities.phone_numbers:
            norm = normalize_phone(phone)
            nid = entity_id("Phone", norm)
            edge_metadata_list.append({
                "source": complaint_nid,
                "target": nid,
                "relationship": "MENTIONS",
                "confidence": 0.95,
                "source_agent": "scam_agent",
                "evidence": f"Extracted phone {phone} from complaint text"
            })
        for upi in entities.upi_ids:
            norm = normalize_upi(upi)
            nid = entity_id("UPI", norm)
            edge_metadata_list.append({
                "source": complaint_nid,
                "target": nid,
                "relationship": "MENTIONS",
                "confidence": 0.95,
                "source_agent": "scam_agent",
                "evidence": f"Extracted UPI {upi} from transaction statement"
            })


        for acct in entities.bank_accounts:
            nid = entity_id("BankAccount", acct)
            edge_metadata_list.append({
                "source": complaint_nid,
                "target": nid,
                "relationship": "MENTIONS",
                "confidence": 0.95,
                "source_agent": "scam_agent",
                "evidence": f"Extracted bank account {acct} from statement files"
            })

        # 2. Neo4j Ingestion with cross-case matching
        entity_ids, edges_added, cross_matches = _neo4j_ingest(entities, complaint_id, fraud_type, edge_metadata_list)

        # 3. Local networkx processing
        G = _build_local_graph(entities, complaint_id, edge_metadata_list)
        all_node_ids = list(G.nodes)

        # 4. PageRank & Community detection
        pr_scores = pagerank_local(G)
        communities = louvain_communities(G)
        fraud_rings_raw = build_fraud_ring_summary(communities)
        fraud_rings = [FraudRing(**r) for r in fraud_rings_raw]

        # 5. Identify high-risk nodes (Top 20% by local PageRank influence)
        if pr_scores:
            threshold = sorted(pr_scores.values(), reverse=True)[:max(1, len(pr_scores) // 5)][-1]
            high_risk = [n for n, s in pr_scores.items() if s >= threshold]
        else:
            high_risk = []

        # 6. Graph explanations generator
        graph_explanations = []
        for match in cross_matches:
            msg = f"Suspect {match['type']} '{match['value']}' links this case to past complaint {match['connected_complaint_id']}."
            graph_explanations.append(msg)
            warnings.append(f"Linked entity connection found: {match['value']}")

        for ring in fraud_rings:
            graph_explanations.append(
                f"Fraud Ring detected containing {ring.size} connected nodes, classified as {ring.risk_level.value} risk."
            )

        if not graph_explanations:
            graph_explanations.append("All entities are local to this complaint. No past connections discovered.")

        # 7. Risk calculation (Entities density + community presence)
        max_ring_size = max((r.size for r in fraud_rings), default=0)
        entity_risk = min(total_entities / 10.0, 1.0)
        ring_risk = min(max_ring_size / 20.0, 1.0)
        
        # Cross-complaint connection multiplier
        connection_multiplier = 1.0 + (0.15 * len(cross_matches))
        risk_score = round(min((0.5 * entity_risk + 0.5 * ring_risk) * connection_multiplier, 1.0), 4)
        risk_level = _risk_level(risk_score)

        explanation = f"Graph analysis complete. Ingested {total_entities} nodes. " + " ".join(graph_explanations)

        elapsed = (time.time() - t0) * 1000
        logger.info(f"[GraphAgent] case={case_id} nodes={len(all_node_ids)} risk={risk_score:.2f} t={elapsed:.0f}ms")

        # Expose execution metrics
        metrics = {
            "total_nodes": G.number_of_nodes(),
            "total_edges": G.number_of_edges(),
            "neo4j_synchronized": len(entity_ids) > 0,
            "cross_complaint_connections": len(cross_matches),
        }

        return FraudGraphResult(
            status="SUCCESS",
            entities_added=entity_ids if entity_ids else all_node_ids,
            edges_added=edges_added or G.number_of_edges(),
            fraud_rings=fraud_rings,
            pagerank_scores={k: round(v, 6) for k, v in list(pr_scores.items())[:50]},
            connected_complaints=[complaint_id],
            high_risk_nodes=high_risk[:20],
            risk_score=risk_score,
            risk_level=risk_level,
            explanation=explanation,
            graph_explanations=graph_explanations,
            edges_metadata=edge_metadata_list,
            warnings=warnings,
            warning=warnings[0] if warnings else None,
            processing_time_ms=elapsed,
            execution_time_ms=elapsed,
            metrics=metrics,
        )

    except Exception as e:
        elapsed = (time.time() - t0) * 1000
        logger.error(f"[GraphAgent] Pipeline failure: {e}", exc_info=True)
        return FraudGraphResult(
            status="FAILED",
            reason=str(e),
            risk_score=0.0,
            risk_level=RiskLevel.LOW,
            explanation="Failed to execute fraud graph analysis due to internal exception.",
            processing_time_ms=elapsed,
            execution_time_ms=elapsed,
        )
