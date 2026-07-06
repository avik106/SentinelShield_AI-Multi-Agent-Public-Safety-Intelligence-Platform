"""Counterfeit Detection Agent — LangGraph Node + CLI."""

from __future__ import annotations
import argparse
import json
from loguru import logger

from services.counterfeit_agent.pipeline import run_counterfeit_pipeline


def counterfeit_agent_node(state: dict) -> dict:
    """LangGraph node for counterfeit detection."""
    image_path = state.get("image_path")
    if not image_path:
        return {}
    try:
        result = run_counterfeit_pipeline(
            image_path=image_path,
            case_id=state.get("case_id"),
        )
        return {"counterfeit_result": result}
    except Exception as e:
        logger.error(f"[CounterfeitAgent] Node error: {e}")
        errors = list(state.get("errors", []))
        errors.append(f"counterfeit_agent: {str(e)}")
        return {"errors": errors}


def run(image_path: str, case_id: str | None = None):
    return run_counterfeit_pipeline(image_path=image_path, case_id=case_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SentinelShield — Counterfeit Detection Agent")
    parser.add_argument("--image", required=True, type=str)
    parser.add_argument("--case-id", type=str, default="CLI_TEST")
    args = parser.parse_args()
    result = run(image_path=args.image, case_id=args.case_id)
    print(json.dumps(result.model_dump(mode="json"), indent=2, ensure_ascii=False))
