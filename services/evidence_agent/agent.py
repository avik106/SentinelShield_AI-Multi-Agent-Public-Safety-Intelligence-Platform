"""Evidence Generation Agent — LangGraph Node + CLI."""

from __future__ import annotations
import argparse
import json
from loguru import logger

from services.evidence_agent.pipeline import run_evidence_pipeline


def evidence_agent_node(state: dict) -> dict:
    """LangGraph node — aggregates all results into a final evidence package."""
    try:
        result = run_evidence_pipeline(
            case_id=state.get("case_id", "UNKNOWN"),
            scam_result=state.get("scam_result"),
            voice_result=state.get("voice_result"),
            counterfeit_result=state.get("counterfeit_result"),
            graph_result=state.get("graph_result"),
            geo_result=state.get("geo_result"),
            rag_result=state.get("rag_result"),
            complainant_name=state.get("complainant_name"),
            complainant_contact=state.get("complainant_contact"),
        )
        return {"evidence_package": result, "overall_risk_score": result.overall_risk_score}
    except Exception as e:
        logger.error(f"[EvidenceAgent] Node error: {e}")
        from shared.schemas import EvidencePackage, RiskLevel
        result = EvidencePackage(
            status="FAILED",
            reason=str(e),
            case_id=state.get("case_id", "UNKNOWN"),
            overall_risk_score=0.0,
            risk_level=RiskLevel.LOW,
            explanation=f"Evidence agent node encountered exception: {str(e)}"
        )
        errors = list(state.get("errors", []))
        errors.append(f"evidence_agent: {str(e)}")
        return {"evidence_package": result, "errors": errors}



def run(case_id: str, **kwargs):
    return run_evidence_pipeline(case_id=case_id, **kwargs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SentinelShield — Evidence Generation Agent")
    parser.add_argument("--case-id", required=True)
    args = parser.parse_args()
    result = run(case_id=args.case_id)
    print(json.dumps(result.model_dump(mode="json"), indent=2, ensure_ascii=False, default=str))
