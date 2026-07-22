"""Voice Intelligence Agent — LangGraph Node + CLI."""

from __future__ import annotations
import argparse
import json
from loguru import logger

from services.voice_agent.pipeline import run_voice_pipeline


def voice_agent_node(state: dict) -> dict:
    """LangGraph node for voice intelligence."""
    audio_path = state.get("audio_path")
    if not audio_path:
        from shared.schemas import VoiceIntelligenceResult
        result = VoiceIntelligenceResult(
            status="SKIPPED",
            reason="No audio file path provided.",
            explanation="Voice analysis was skipped because no audio recording was uploaded."
        )
        return {"voice_result": result}
    try:
        result = run_voice_pipeline(
            audio_path=audio_path,
            case_id=state.get("case_id"),
        )
        return {"voice_result": result}
    except Exception as e:
        logger.error(f"[VoiceAgent] Node error: {e}")
        from shared.schemas import VoiceIntelligenceResult
        result = VoiceIntelligenceResult(
            status="FAILED",
            reason=str(e),
            explanation=f"Voice agent node encountered an exception: {str(e)}"
        )
        errors = list(state.get("errors", []))
        errors.append(f"voice_agent: {str(e)}")
        return {"voice_result": result, "errors": errors}



def run(audio_path: str, case_id: str | None = None):
    """Public callable for other modules and tests."""
    return run_voice_pipeline(audio_path=audio_path, case_id=case_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SentinelShield — Voice Intelligence Agent")
    parser.add_argument("--audio", required=True, type=str, help="Path to audio file")
    parser.add_argument("--case-id", type=str, default="CLI_TEST")
    args = parser.parse_args()
    result = run(audio_path=args.audio, case_id=args.case_id)
    print(json.dumps(result.model_dump(mode="json"), indent=2, ensure_ascii=False))
