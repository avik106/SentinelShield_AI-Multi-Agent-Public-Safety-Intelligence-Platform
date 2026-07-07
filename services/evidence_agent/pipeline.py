"""
Evidence Generation Agent — Core Pipeline
Aggregates all agent results → FIR draft → investigation report → evidence package.
"""

from __future__ import annotations
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
    aggregate_risk_scores, get_ipc_sections, sha256_file,
    generate_fir_template, try_generate_pdf
)
from services.evidence_agent.models import AgentResultsSummary


def _deduplicate_entities(
    scam_result: ScamDetectionResult | None,
    voice_result: VoiceIntelligenceResult | None,
) -> AgentResultsSummary:
    """Collect and deduplicate entities across agent outputs."""
    summary = AgentResultsSummary()
    all_scores = []

    if scam_result:
        summary.fraud_types.append(scam_result.scam_type.value)
        summary.all_phones.extend(scam_result.entities.phone_numbers)
        summary.all_upi_ids.extend(scam_result.entities.upi_ids)
        summary.all_amounts.extend(scam_result.entities.amounts)
        summary.all_urls.extend(scam_result.entities.urls)
        all_scores.append(scam_result.risk_score)

    if voice_result:
        summary.transcript = voice_result.transcript
        all_scores.append(voice_result.risk_score)
        if voice_result.scam_analysis:
            summary.all_phones.extend(voice_result.scam_analysis.entities.phone_numbers)

    summary.all_scores = all_scores
    # Deduplicate
    summary.all_phones = list(set(summary.all_phones))[:10]
    summary.all_upi_ids = list(set(summary.all_upi_ids))[:10]
    summary.all_urls = list(set(summary.all_urls))[:10]

    return summary


def _collect_all_scores(
    scam_result, voice_result, counterfeit_result, graph_result, geo_result
) -> list[float]:
    scores = []
    for r in [scam_result, voice_result, counterfeit_result, graph_result]:
        if r and hasattr(r, "risk_score") and r.risk_score is not None:
            scores.append(r.risk_score)
    return scores


def _risk_level(score: float) -> RiskLevel:
    if score >= 0.80:
        return RiskLevel.CRITICAL
    elif score >= 0.55:
        return RiskLevel.HIGH
    elif score >= 0.30:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def _build_executive_summary(
    case_id: str,
    overall_risk: float,
    entity_summary: AgentResultsSummary,
    scam_result: ScamDetectionResult | None,
    voice_result: VoiceIntelligenceResult | None,
    counterfeit_result: CounterfeitDetectionResult | None,
    graph_result: FraudGraphResult | None,
    rag_result: RAGCopilotResult | None,
    timestamp: datetime,
) -> str:
    parts = [
        f"SENTINELSHIELD AI — CASE EXECUTIVE SUMMARY",
        f"Case ID: {case_id} | Generated: {timestamp.strftime('%Y-%m-%d %H:%M UTC')}",
        f"Overall Risk Score: {overall_risk:.2f} ({'CRITICAL' if overall_risk >= 0.8 else 'HIGH' if overall_risk >= 0.55 else 'MEDIUM' if overall_risk >= 0.3 else 'LOW'})",
        "",
    ]
    if scam_result:
        parts.append(f"SCAM DETECTION: Risk={scam_result.risk_score:.2f} | Type={scam_result.scam_type.value} | {scam_result.explanation[:200]}")
    if voice_result and voice_result.transcript:
        parts.append(f"VOICE ANALYSIS: Deepfake={'YES' if voice_result.is_deepfake else 'NO'} | Emotion={voice_result.emotion} | Risk={voice_result.risk_score:.2f}")
    if counterfeit_result and counterfeit_result.denomination:
        parts.append(f"COUNTERFEIT CHECK: {'COUNTERFEIT DETECTED' if counterfeit_result.is_counterfeit else 'GENUINE'} | Denom=₹{counterfeit_result.denomination} | {counterfeit_result.explanation[:150]}")
    if graph_result:
        parts.append(f"FRAUD GRAPH: {len(graph_result.entities_added)} entities | {len(graph_result.fraud_rings)} ring(s) detected")
    if rag_result and rag_result.answer:
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
    t0 = time.time()
    now = datetime.now(timezone.utc)

    # 1. Entity deduplication
    entity_summary = _deduplicate_entities(scam_result, voice_result)

    # 2. Risk aggregation
    scores = _collect_all_scores(scam_result, voice_result, counterfeit_result, graph_result, geo_result)
    overall_risk = aggregate_risk_scores(scores)
    risk_level = _risk_level(overall_risk)

    # 3. Fraud types
    fraud_types = entity_summary.fraud_types or ["unknown"]
    if counterfeit_result and counterfeit_result.is_counterfeit:
        fraud_types.append("counterfeit_currency")

    # 4. IPC sections
    ipc_sections = get_ipc_sections(fraud_types)

    # 5. Executive summary
    exec_summary = _build_executive_summary(
        case_id, overall_risk, entity_summary,
        scam_result, voice_result, counterfeit_result, graph_result, rag_result, now
    )

    # 6. FIR draft
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
        summary=exec_summary[:500],
        ipc_sections=ipc_sections,
        timestamp=now,
    )

    # 7. Full investigation report content
    full_report = f"{exec_summary}\n\n{'='*60}\n\nFIR DRAFT\n{'='*60}\n\n{fir}"

    # 8. PDF/text save
    report_path = try_generate_pdf(full_report, case_id)

    # 9. Evidence manifest
    evidence_manifest: list[EvidenceItem] = []
    if report_path:
        evidence_manifest.append(EvidenceItem(
            file_path=report_path,
            file_type="pdf" if report_path.endswith(".pdf") else "txt",
            sha256=sha256_file(report_path),
            description="Full investigation report with FIR draft",
        ))

    # 10. Recommended actions
    actions = []
    if overall_risk >= 0.7:
        actions.append("URGENT: File FIR immediately and escalate to cyber cell.")
        actions.append("Freeze flagged bank accounts and UPI IDs.")
    if entity_summary.all_phones:
        actions.append(f"Request call records for: {', '.join(entity_summary.all_phones[:3])}")
    if counterfeit_result and counterfeit_result.is_counterfeit:
        actions.append("Seize suspected counterfeit notes and send to currency authentication lab.")
    if graph_result and graph_result.fraud_rings:
        actions.append(f"Investigate {len(graph_result.fraud_rings)} suspected fraud ring(s) identified in graph analysis.")
    if not actions:
        actions.append("Monitor case. Low risk detected but continue investigation.")

    elapsed = (time.time() - t0) * 1000
    logger.info(
        f"[EvidenceAgent] case={case_id} risk={overall_risk:.2f} ipc={len(ipc_sections)} report={report_path} t={elapsed:.0f}ms"
    )

    return EvidencePackage(
        case_id=case_id,
        overall_risk_score=overall_risk,
        risk_level=risk_level,
        fir_draft=fir,
        executive_summary=exec_summary,
        investigation_report_path=report_path,
        evidence_manifest=evidence_manifest,
        ipc_sections=ipc_sections,
        recommended_actions=actions,
        processing_time_ms=elapsed,
    )
