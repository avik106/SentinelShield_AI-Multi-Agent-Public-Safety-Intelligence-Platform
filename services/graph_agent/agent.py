"""Fraud Graph Intelligence Agent — LangGraph Node + CLI."""

from __future__ import annotations
import argparse
import json
from loguru import logger

from shared.schemas import ExtractedEntities
from services.graph_agent.pipeline import run_graph_pipeline


def graph_agent_node(state: dict) -> dict:
    """LangGraph node — extracts entities from scam result and runs graph analysis."""
    try:
        scam_result = state.get("scam_result")
        entities = None
        if scam_result and hasattr(scam_result, "entities"):
            entities = scam_result.entities
        if entities is None:
            entities = ExtractedEntities()
        result = run_graph_pipeline(
            entities=entities,
            complaint_id=state.get("case_id", "unknown"),
            case_id=state.get("case_id"),
        )
        return {"graph_result": result}
    except Exception as e:
        logger.error(f"[GraphAgent] Node error: {e}")
        errors = list(state.get("errors", []))
        errors.append(f"graph_agent: {str(e)}")
        return {"errors": errors}


def run(entities: ExtractedEntities, complaint_id: str, case_id: str | None = None):
    return run_graph_pipeline(entities=entities, complaint_id=complaint_id, case_id=case_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SentinelShield — Fraud Graph Agent")
    parser.add_argument("--complaint-id", default="TEST_001")
    parser.add_argument("--phones", nargs="*", default=[])
    parser.add_argument("--upis", nargs="*", default=[])
    args = parser.parse_args()
    entities = ExtractedEntities(phone_numbers=args.phones, upi_ids=args.upis)
    result = run(entities=entities, complaint_id=args.complaint_id)
    print(json.dumps(result.model_dump(mode="json"), indent=2, ensure_ascii=False))
