"""
Scam Detection Agent — LangGraph Node + CLI Entry Point
"""

from __future__ import annotations
import argparse
import json
from loguru import logger

from shared.schemas import AgentState, ScamDetectionInput
from services.scam_agent.pipeline import run_scam_pipeline


# ─────────────────────────────────────────────────────────────────────────────
# LangGraph Node
# ─────────────────────────────────────────────────────────────────────────────

def scam_agent_node(state: dict) -> dict:
    """
    LangGraph node function.
    Reads text_input / image_path / pdf_path from AgentState,
    runs the scam detection pipeline, and returns updated state dict.
    """
    try:
        result = run_scam_pipeline(
            text=state.get("text_input"),
            image_path=state.get("image_path"),
            pdf_path=state.get("pdf_path"),
            case_id=state.get("case_id"),
        )
        return {"scam_result": result}
    except Exception as e:
        logger.error(f"[ScamAgent] Node error: {e}")
        from shared.schemas import ScamDetectionResult, RiskLevel, ScamType
        result = ScamDetectionResult(
            status="FAILED",
            reason=str(e),
            risk_score=0.0,
            risk_level=RiskLevel.LOW,
            scam_type=ScamType.UNKNOWN,
            confidence=0.0,
            explanation=f"Scam agent node encountered exception: {str(e)}"
        )
        errors = list(state.get("errors", []))
        errors.append(f"scam_agent: {str(e)}")
        return {"scam_result": result, "errors": errors}



# ─────────────────────────────────────────────────────────────────────────────
# Standalone Runner
# ─────────────────────────────────────────────────────────────────────────────

def run(
    text: str | None = None,
    image_path: str | None = None,
    pdf_path: str | None = None,
    case_id: str | None = None,
):
    """Public function callable by other modules (e.g., the orchestrator, tests)."""
    return run_scam_pipeline(
        text=text,
        image_path=image_path,
        pdf_path=pdf_path,
        case_id=case_id,
    )


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SentinelShield — Scam Detection Agent")
    parser.add_argument("--input", type=str, help="Raw text to analyze")
    parser.add_argument("--image", type=str, help="Path to screenshot/image")
    parser.add_argument("--pdf", type=str, help="Path to PDF document")
    parser.add_argument("--case-id", type=str, default="CLI_TEST")
    args = parser.parse_args()

    result = run(
        text=args.input,
        image_path=args.image,
        pdf_path=args.pdf,
        case_id=args.case_id,
    )
    print(json.dumps(result.model_dump(mode="json"), indent=2, ensure_ascii=False))
