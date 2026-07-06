"""RAG Investigation Copilot Agent — LangGraph Node + CLI."""

from __future__ import annotations
import argparse
import json
from loguru import logger

from services.rag_agent.pipeline import run_rag_pipeline


def rag_agent_node(state: dict) -> dict:
    """LangGraph node — only runs if officer_query is present in state."""
    query = state.get("officer_query")
    if not query:
        return {}
    try:
        result = run_rag_pipeline(
            query=query,
            case_id=state.get("case_id"),
        )
        return {"rag_result": result}
    except Exception as e:
        logger.error(f"[RAGAgent] Node error: {e}")
        errors = list(state.get("errors", []))
        errors.append(f"rag_agent: {str(e)}")
        return {"errors": errors}


def run(query: str, case_id: str | None = None, top_k: int = 5):
    return run_rag_pipeline(query=query, case_id=case_id, top_k=top_k)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SentinelShield — RAG Copilot Agent")
    parser.add_argument("--query", required=True, type=str)
    parser.add_argument("--case-id", type=str, default="CLI_TEST")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()
    result = run(query=args.query, case_id=args.case_id, top_k=args.top_k)
    print(json.dumps(result.model_dump(mode="json"), indent=2, ensure_ascii=False))
