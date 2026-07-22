"""
SentinelShield AI — Shared Evidence Fusion & Risk Aggregation
Provides unified risk score aggregation, cross-agent evidence correlation trace,
and downstream confidence propagation.
"""

from __future__ import annotations
from loguru import logger
from shared.schemas import RiskLevel
from shared.config import get_settings


# ─────────────────────────────────────────────────────────────────────────────
# Cross-Agent Evidence Fusion
# ─────────────────────────────────────────────────────────────────────────────

def fuse_and_correlate_evidence(state: dict) -> dict:
    """
    Collects, deduplicates, and correlates entities across all active agents
    to identify overlaps (e.g. same phone number in text message and audio recording).
    Maintains complete traceability trace.
    """
    scam_res = state.get("scam_result")
    voice_res = state.get("voice_result")
    graph_res = state.get("graph_result")
    geo_res = state.get("geo_result")

    # Map entity values to the agent names and evidence that found them
    entity_sources: dict[str, dict[str, set[str]]] = {
        "phone_numbers": {},
        "upi_ids": {},
        "emails": {},
        "urls": {},
        "domains": {},
        "bank_accounts": {},
        "wallet_ids": {},
        "locations": {},
        "names": {},  # Person / Company Name
        "ip_addresses": {},
    }

    def add_entity(entity_type: str, val: str | None, source: str):
        if not val:
            return
        val = str(val).strip().lower()
        if not val:
            return
        if val not in entity_sources[entity_type]:
            entity_sources[entity_type][val] = set()
        entity_sources[entity_type][val].add(source)

    # 1. Ingest entities from Scam Agent
    if scam_res and hasattr(scam_res, "entities") and scam_res.entities:
        e = scam_res.entities
        for v in getattr(e, "phone_numbers", []): add_entity("phone_numbers", v, "scam_agent")
        for v in getattr(e, "upi_ids", []): add_entity("upi_ids", v, "scam_agent")
        for v in getattr(e, "emails", []): add_entity("emails", v, "scam_agent")
        for v in getattr(e, "urls", []): add_entity("urls", v, "scam_agent")
        for v in getattr(e, "domains", []): add_entity("domains", v, "scam_agent")
        for v in getattr(e, "bank_accounts", []): add_entity("bank_accounts", v, "scam_agent")
        for v in getattr(e, "wallet_ids", []): add_entity("wallet_ids", v, "scam_agent")
        for v in getattr(e, "locations", []): add_entity("locations", v, "scam_agent")
        for v in getattr(e, "names", []): add_entity("names", v, "scam_agent")
        for v in getattr(e, "ip_addresses", []): add_entity("ip_addresses", v, "scam_agent")

    # 2. Ingest entities from Voice Agent
    if voice_res:
        if hasattr(voice_res, "scam_analysis") and voice_res.scam_analysis and voice_res.scam_analysis.entities:
            e = voice_res.scam_analysis.entities
            for v in getattr(e, "phone_numbers", []): add_entity("phone_numbers", v, "voice_agent")
            for v in getattr(e, "upi_ids", []): add_entity("upi_ids", v, "voice_agent")
            for v in getattr(e, "emails", []): add_entity("emails", v, "voice_agent")
            for v in getattr(e, "urls", []): add_entity("urls", v, "voice_agent")
            for v in getattr(e, "domains", []): add_entity("domains", v, "voice_agent")
            for v in getattr(e, "bank_accounts", []): add_entity("bank_accounts", v, "voice_agent")
            for v in getattr(e, "wallet_ids", []): add_entity("wallet_ids", v, "voice_agent")
            for v in getattr(e, "locations", []): add_entity("locations", v, "voice_agent")
            for v in getattr(e, "names", []): add_entity("names", v, "voice_agent")
            for v in getattr(e, "ip_addresses", []): add_entity("ip_addresses", v, "voice_agent")

    # 3. Ingest entities from Graph Agent
    if graph_res:
        for v in getattr(graph_res, "high_risk_nodes", []):
            if ":" in v:
                t, val = v.split(":", 1)
                t_lower = t.lower()
                if "phone" in t_lower:
                    add_entity("phone_numbers", val, "graph_agent")
                elif "upi" in t_lower:
                    add_entity("upi_ids", val, "graph_agent")
                elif "bank" in t_lower:
                    add_entity("bank_accounts", val, "graph_agent")

    # 4. Ingest entities from Geo Agent
    if geo_res:
        for hs in getattr(geo_res, "hotspots", []):
            add_entity("locations", f"{hs.lat:.4f},{hs.lon:.4f}", "geo_agent")
        district = state.get("district")
        if district:
            add_entity("locations", district, "geo_agent")

    # Detect overlaps & construct traceability trace logs
    correlations = []
    fused_entities = {k: list(v.keys()) for k, v in entity_sources.items()}
    
    for entity_type, val_map in entity_sources.items():
        for val, sources in val_map.items():
            if len(sources) > 1:
                src_list = sorted(list(sources))
                correlations.append({
                    "entity_type": entity_type,
                    "value": val,
                    "sources": src_list,
                    "trace_message": f"Cross-channel match for [{entity_type.replace('_', ' ').title()}] '{val}' verified in both {', '.join([s.replace('_', ' ').title() for s in src_list])}."
                })

    return {
        "correlations": correlations,
        "fused_entities": fused_entities,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Configurable Risk & Confidence Propagation
# ─────────────────────────────────────────────────────────────────────────────

def calculate_aggregated_risk(state: dict) -> tuple[float, RiskLevel, list[dict], dict, float]:
    """
    Computes overall risk score using configurable weights.
    Also propagates confidence downstream, penalizing case confidence for agent failures,
    and awarding bonuses for cross-agent entity correlations.
    Returns (overall_risk, risk_level, correlations, fused_entities, overall_confidence).
    """
    settings = get_settings()

    agent_weights = {
        "scam_result": settings.RISK_WEIGHT_SCAM,
        "voice_result": settings.RISK_WEIGHT_VOICE,
        "counterfeit_result": settings.RISK_WEIGHT_COUNTERFEIT,
        "graph_result": settings.RISK_WEIGHT_GRAPH,
        "geo_result": settings.RISK_WEIGHT_GEO,
    }

    weighted_sum = 0.0
    total_weight = 0.0
    
    sub_confidences = []
    failures_penalties = 0

    for key, weight in agent_weights.items():
        result = state.get(key)
        if result:
            if hasattr(result, "status") and result.status in ("FAILED", "SKIPPED"):
                failures_penalties += 1
                continue
                
            if hasattr(result, "risk_score") and result.risk_score is not None:
                weighted_sum += result.risk_score * weight
                total_weight += weight
                
            if hasattr(result, "confidence") and result.confidence is not None:
                sub_confidences.append(result.confidence)

    if total_weight > 0:
        overall = weighted_sum / total_weight
    else:
        overall = 0.0

    # Cross-Agent Evidence Fusion & Correlation trace
    fusion = fuse_and_correlate_evidence(state)
    correlations = fusion["correlations"]
    fused_entities = fusion["fused_entities"]

    # Calculate correlation bonus (+0.05 per overlap, capped at +0.15)
    correlation_bonus = min(0.05 * len(correlations), 0.15)
    overall = round(min(overall + correlation_bonus, 1.0), 4)

    # Propagate confidence downstream & subtract safety penalty for failed/skipped nodes
    base_confidence = sum(sub_confidences) / len(sub_confidences) if sub_confidences else 0.50
    final_confidence = base_confidence + correlation_bonus - (0.10 * failures_penalties)
    final_confidence = round(min(max(final_confidence, 0.0), 1.0), 4)

    # Determine risk level based on configured thresholds
    if overall >= settings.RISK_THRESHOLD_CRITICAL:
        level = RiskLevel.CRITICAL
    elif overall >= settings.RISK_THRESHOLD_HIGH:
        level = RiskLevel.HIGH
    elif overall >= settings.RISK_THRESHOLD_MEDIUM:
        level = RiskLevel.MEDIUM
    else:
        level = RiskLevel.LOW

    return overall, level, correlations, fused_entities, final_confidence
