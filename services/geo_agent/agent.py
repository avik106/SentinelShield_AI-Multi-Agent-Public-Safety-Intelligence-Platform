"""Geo Intelligence Agent — LangGraph Node + CLI."""

from __future__ import annotations
import argparse
import json
from loguru import logger

from services.geo_agent.pipeline import run_geo_pipeline


def geo_agent_node(state: dict) -> dict:
    """LangGraph node for geospatial intelligence."""
    try:
        result = run_geo_pipeline(
            complaints=[],
            lat=state.get("lat"),
            lon=state.get("lon"),
            case_id=state.get("case_id"),
        )
        return {"geo_result": result}
    except Exception as e:
        logger.error(f"[GeoAgent] Node error: {e}")
        errors = list(state.get("errors", []))
        errors.append(f"geo_agent: {str(e)}")
        return {"errors": errors}


def run(complaints: list[dict], lat: float | None = None, lon: float | None = None, case_id: str | None = None):
    return run_geo_pipeline(complaints=complaints, lat=lat, lon=lon, case_id=case_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SentinelShield — Geo Intelligence Agent")
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--case-id", default="CLI_TEST")
    args = parser.parse_args()
    result = run(complaints=[], lat=args.lat, lon=args.lon, case_id=args.case_id)
    print(json.dumps(result.model_dump(mode="json"), indent=2, ensure_ascii=False))
