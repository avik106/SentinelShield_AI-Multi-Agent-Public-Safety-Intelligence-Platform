"""
Evidence Generation Agent — Core Pipeline
Aggregates all agent results → FIR draft → investigation report → evidence package.
Uses the unified config-based risk aggregation, cross-agent evidence fusion, and chain of custody tracking.
"""

from __future__ import annotations
import hashlib
import time
from datetime import datetime, timezone

from loguru import logger

from shared.schemas import (
    EvidencePackage, EvidenceItem, RiskLevel,
    ScamDetectionResult, VoiceIntelligenceResult,
    CounterfeitDetectionResult, FraudGraphResult,
    GeoIntelligenceResult, RAGCopilotResult,
)
from services.evidence_agent.utils import (
    get_ipc_sections, sha256_file,
    generate_fir_template, try_generate_pdf
)
from services.evidence_agent.models import AgentResultsSummary
from shared.fusion import calculate_aggregated_risk


def _deduplicate_entities(
    scam_result: ScamDetectionResult | None,
    voice_result: VoiceIntelligenceResult | None,
    fused_entities: dict[str, list[str]],
) -> AgentResultsSummary:
    """Collect and deduplicate entities across agent outputs using fused entity lists."""
    summary = AgentResultsSummary()
    
    if scam_result:
        summary.fraud_types.append(scam_result.scam_type.value)
        summary.all_amounts.extend(scam_result.entities.amounts)

    if voice_result:
        summary.transcript = voice_result.transcript
        if voice_result.scam_analysis:
            summary.fraud_types.append(voice_result.scam_analysis.scam_type.value)
            summary.all_amounts.extend(voice_result.scam_analysis.entities.amounts)

    # Use fused entities from cross-agent evidence fusion
    summary.all_phones = list(fused_entities.get("phone_numbers", []))[:10]
    summary.all_upi_ids = list(fused_entities.get("upi_ids", []))[:10]
    summary.all_urls = list(fused_entities.get("urls", []))[:10]
    summary.all_amounts = list(set(summary.all_amounts))[:10]
    summary.fraud_types = list(set(summary.fraud_types))

    return summary


def _build_executive_summary(
    case_id: str,
    overall_risk: float,
    entity_summary: AgentResultsSummary,
    scam_result: ScamDetectionResult | None,
    voice_result: VoiceIntelligenceResult | None,
    counterfeit_result: CounterfeitDetectionResult | None,
    graph_result: FraudGraphResult | None,
    geo_result: GeoIntelligenceResult | None,
    rag_result: RAGCopilotResult | None,
    correlations: list[dict],
    skipped_agents: list[dict],
    timestamp: datetime,
) -> str:
    parts = [
        f"SENTINELSHIELD AI — CASE EXECUTIVE SUMMARY",
        f"Case ID: {case_id} | Generated: {timestamp.strftime('%Y-%m-%d %H:%M UTC')}",
        f"Overall Risk Score: {overall_risk:.2f} ({'CRITICAL' if overall_risk >= 0.8 else 'HIGH' if overall_risk >= 0.55 else 'MEDIUM' if overall_risk >= 0.3 else 'LOW'})",
        "",
    ]
    if scam_result and scam_result.status == "SUCCESS":
        parts.append(f"SCAM DETECTION: Risk={scam_result.risk_score:.2f} | Type={scam_result.scam_type.value} | {scam_result.explanation[:200]}")
    if voice_result and voice_result.status == "SUCCESS" and voice_result.transcript:
        parts.append(f"VOICE ANALYSIS: Deepfake={'YES' if voice_result.is_deepfake else 'NO'} | Quality={voice_result.audio_quality} | Risk={voice_result.risk_score:.2f}")
    if counterfeit_result and counterfeit_result.status == "SUCCESS" and counterfeit_result.denomination:
        parts.append(f"COUNTERFEIT CHECK: {'COUNTERFEIT DETECTED' if counterfeit_result.is_counterfeit else 'GENUINE'} | Denom=₹{counterfeit_result.denomination} | {counterfeit_result.explanation[:150]}")
    if graph_result and graph_result.status == "SUCCESS":
        parts.append(f"FRAUD GRAPH: {len(graph_result.entities_added)} entities | {len(graph_result.fraud_rings)} ring(s) detected")
    if geo_result and geo_result.status == "SUCCESS":
        parts.append(f"GEOSPATIAL: Analyzed {geo_result.total_complaints_analyzed} reports | Risk={geo_result.risk_score:.2f} | {len(geo_result.hotspots)} hotspots detected")
    
    # Ingest correlations from cross-agent evidence fusion
    if correlations:
        parts.append("\nCROSS-AGENT EVIDENCE CORRELATIONS DETECTED (CONFIDENCE BOOST APPLIED):")
        for c in correlations:
            parts.append(f"  - {c['trace_message']}")

    # Ingest skipped agents list
    if skipped_agents:
        parts.append("\nSKIPPED / UNEXPOSED ANALYSES:")
        for s in skipped_agents:
            parts.append(f"  - [{s['agent_name'].replace('_', ' ').title()}] Reason: {s['reason']}")
            
    if rag_result and rag_result.status == "SUCCESS" and rag_result.answer:
        parts.append(f"\nCOPILOT INSIGHTS:\n{rag_result.answer[:500]}")
        
    return "\n".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Public Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def run_evidence_pipeline(
    case_id: str,
    scam_result: ScamDetectionResult | None = None,
    voice_result: VoiceIntelligenceResult | None = None,
    counterfeit_result: CounterfeitDetectionResult | None = None,
    graph_result: FraudGraphResult | None = None,
    geo_result: GeoIntelligenceResult | None = None,
    rag_result: RAGCopilotResult | None = None,
    complainant_name: str | None = None,
    complainant_contact: str | None = None,
) -> EvidencePackage:
    now = datetime.now(timezone.utc)
    warnings = []


    # Reconstruct state dictionary for unified config-based risk aggregation
    state = {
        "case_id": case_id,
        "scam_result": scam_result,
        "voice_result": voice_result,
        "counterfeit_result": counterfeit_result,
        "graph_result": graph_result,
        "geo_result": geo_result,
    }
    
    # 1. Compute unified risk score, risk level, fuse/correlate entities, and propagate confidence
    overall_risk, risk_level, correlations, fused_entities, overall_confidence = calculate_aggregated_risk(state)

    if overall_confidence < 0.50:
        warnings.append(f"Low overall case confidence ({overall_confidence:.2f}). Core agent branches skipped or failed.")

    # 2. Skipped/failed agents traceback tracking
    skipped_agents = []
    agent_mapping = {
        "scam_result": ("scam_detection_agent", "Scam detection text/image was not uploaded."),
        "voice_result": ("voice_intelligence_agent", "Voice recording file was not uploaded."),
        "counterfeit_result": ("counterfeit_detection_agent", "Note image was not uploaded for counterfeit detection."),
        "graph_result": ("fraud_graph_agent", "Graph ring analytics skipped due to lack of entities."),
        "geo_result": ("geo_intelligence_agent", "Geospatial clustering skipped (no complaint location passed)."),
        "rag_result": ("rag_copilot_agent", "RAG Copilot query was not invoked.")
    }

    for key, (agent_name, default_reason) in agent_mapping.items():
        res = state.get(key) if key != "rag_result" else rag_result
        if res is None:
            skipped_agents.append({"agent_name": agent_name, "reason": default_reason})
        elif hasattr(res, "status") and res.status in ("FAILED", "SKIPPED"):
            skipped_agents.append({
                "agent_name": agent_name,
                "reason": getattr(res, "reason", "Agent execution did not complete successfully.")
            })

    # 3. Entity summary population
    entity_summary = _deduplicate_entities(scam_result, voice_result, fused_entities)

    # 4. Fraud types
    fraud_types = entity_summary.fraud_types or ["unknown"]
    if counterfeit_result and counterfeit_result.status == "SUCCESS" and counterfeit_result.is_counterfeit:
        fraud_types.append("counterfeit_currency")

    # 5. IPC sections
    ipc_sections = get_ipc_sections(fraud_types)

    # 6. Executive summary
    exec_summary = _build_executive_summary(
        case_id, overall_risk, entity_summary,
        scam_result, voice_result, counterfeit_result, graph_result, geo_result, rag_result,
        correlations, skipped_agents, now
    )

    # 7. FIR draft
    entities_raw = {
        "phone_numbers": entity_summary.all_phones,
        "upi_ids": entity_summary.all_upi_ids,
        "urls": entity_summary.all_urls,
        "amounts": entity_summary.all_amounts,
    }
    fir = generate_fir_template(
        case_id=case_id,
        complainant_name=complainant_name,
        complainant_contact=complainant_contact,
        fraud_type=fraud_types[0],
        risk_score=overall_risk,
        entities=entities_raw,
        summary=exec_summary[:600],
        ipc_sections=ipc_sections,
        timestamp=now,
    )

    # 8. Full investigation report content
    full_report = f"{exec_summary}\n\n{'='*60}\n\nFIR DRAFT\n{'='*60}\n\n{fir}"

    # 9. PDF/text save
    report_path = try_generate_pdf(full_report, case_id)

    # 10. Evidence manifest & Chain of Custody generation
    evidence_manifest: list[EvidenceItem] = []
    chain_of_custody: list[EvidenceItem] = []

    if report_path:
        # File evidence item
        file_item = EvidenceItem(
            file_path=report_path,
            file_type="pdf" if report_path.endswith(".pdf") else "txt",
            sha256=sha256_file(report_path),
            description="Full investigation report with FIR draft",
            source_agent="evidence_generation_agent",
            confidence=overall_confidence,
            timestamp=now,
            case_id=case_id,
            evidence_type="case_report",
            version="1.0"
        )
        evidence_manifest.append(file_item)
        chain_of_custody.append(file_item)

    # Map sub-agent metadata as custody artifacts
    for key, (agent_name, _) in agent_mapping.items():
        res = state.get(key) if key != "rag_result" else rag_result
        if res and hasattr(res, "status") and res.status == "SUCCESS":
            # Generate a pseudo hash of the model dump for trace verification
            dump_str = str(res.model_dump(exclude={"timestamp"})).encode()
            res_hash = hashlib.sha256(dump_str).hexdigest()
            
            chain_of_custody.append(EvidenceItem(
                file_path="N/A",
                file_type="metadata",
                sha256=res_hash,
                description=f"Ingested custody metadata from {agent_name}",
                source_agent=agent_name,
                confidence=getattr(res, "confidence", 0.0),
                timestamp=getattr(res, "timestamp", now),
                case_id=case_id,
                evidence_type="subagent_result",
                version="1.0"
            ))

    # 11. Recommended actions
    actions = []
    if overall_risk >= 0.7:
        actions.append("URGENT: File FIR immediately and escalate to cyber cell.")
        actions.append("Freeze flagged bank accounts and UPI IDs.")
    if correlations:
        actions.append("URGENT: Cross-channel entity correlation detected. Flag entity values for multi-device interception.")
    if entity_summary.all_phones:
        actions.append(f"Request call records for: {', '.join(entity_summary.all_phones[:3])}")
    if counterfeit_result and counterfeit_result.status == "SUCCESS" and counterfeit_result.is_counterfeit:
        actions.append("Seize suspected counterfeit notes and send to currency authentication lab.")
    if graph_result and graph_result.status == "SUCCESS" and graph_result.fraud_rings:
        actions.append(f"Investigate {len(graph_result.fraud_rings)} suspected fraud ring(s) identified in graph analysis.")
    if not actions:
        actions.append("Monitor case. Low risk detected but continue investigation.")

    elapsed = (time.time() - t0) * 1000
    logger.info(
        f"[EvidenceAgent] case={case_id} risk={overall_risk:.2f} confidence={overall_confidence:.2f} t={elapsed:.0f}ms"
    )

    metrics = {
        "evidence_items_count": len(evidence_manifest),
        "custody_steps_count": len(chain_of_custody),
        "skipped_agents_count": len(skipped_agents),
    }

    return EvidencePackage(
        status="SUCCESS",
        case_id=case_id,
        overall_risk_score=overall_risk,
        risk_level=risk_level,
        fir_draft=fir,
        executive_summary=exec_summary,
        investigation_report_path=report_path,
        evidence_manifest=evidence_manifest,
        ipc_sections=ipc_sections,
        recommended_actions=actions,
        chain_of_custody=chain_of_custody,
        skipped_agents=skipped_agents,
        confidence=overall_confidence,
        warnings=warnings,
        warning=warnings[0] if warnings else None,
        processing_time_ms=elapsed,
        execution_time_ms=elapsed,
        metrics=metrics,
    )
