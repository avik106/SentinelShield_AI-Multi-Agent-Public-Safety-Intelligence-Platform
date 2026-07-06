"""
Voice Intelligence Agent — Core Pipeline
Whisper STT → emotion detection → deepfake detection → scam text analysis.
"""

from __future__ import annotations
import time
from functools import lru_cache
from loguru import logger

from shared.config import get_settings
from shared.schemas import VoiceIntelligenceResult, RiskLevel
from services.voice_agent.utils import (
    load_audio, get_duration, spectral_anomaly_score,
    estimate_speaker_count, aggregate_voice_risk
)

settings = get_settings()


# ─────────────────────────────────────────────────────────────────────────────
# Lazy Loaders
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _load_whisper():
    try:
        import whisper
        logger.info(f"Loading Whisper model: {settings.WHISPER_MODEL_SIZE}")
        model = whisper.load_model(settings.WHISPER_MODEL_SIZE, device=settings.WHISPER_DEVICE)
        return model
    except Exception as e:
        logger.warning(f"Whisper unavailable: {e}")
        return None


@lru_cache(maxsize=1)
def _load_emotion_classifier():
    try:
        from transformers import pipeline
        clf = pipeline(
            "audio-classification",
            model="ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition",
            device=-1,
        )
        logger.info("Emotion classifier loaded.")
        return clf
    except Exception as e:
        logger.warning(f"Emotion classifier unavailable: {e}. Defaulting to 'neutral'.")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Step Functions
# ─────────────────────────────────────────────────────────────────────────────

def _transcribe(audio_path: str) -> tuple[str, str]:
    """Return (transcript, language)."""
    whisper_model = _load_whisper()
    if whisper_model is None:
        return "", "en"
    try:
        result = whisper_model.transcribe(audio_path, task="transcribe")
        return result.get("text", ""), result.get("language", "en")
    except Exception as e:
        logger.warning(f"Transcription failed: {e}")
        return "", "en"


def _detect_emotion(audio_path: str) -> tuple[str, float]:
    """Return (emotion_label, confidence)."""
    clf = _load_emotion_classifier()
    if clf is None:
        return "neutral", 0.0
    try:
        results = clf(audio_path)
        top = results[0]
        return top["label"].lower(), round(float(top["score"]), 4)
    except Exception as e:
        logger.warning(f"Emotion detection failed: {e}")
        return "neutral", 0.0


def _risk_level_from_score(score: float) -> RiskLevel:
    if score >= 0.80:
        return RiskLevel.CRITICAL
    elif score >= 0.55:
        return RiskLevel.HIGH
    elif score >= 0.30:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


# ─────────────────────────────────────────────────────────────────────────────
# Public Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def run_voice_pipeline(
    audio_path: str,
    case_id: str | None = None,
) -> VoiceIntelligenceResult:
    """
    Full voice intelligence pipeline.

    Steps:
    1. Load & preprocess audio (librosa)
    2. Transcription (Whisper)
    3. Language detection from transcript
    4. Emotion detection (wav2vec2)
    5. Deepfake detection (spectral heuristic / AASIST)
    6. Speaker count estimation
    7. Scam text analysis (reuses scam_agent pipeline)
    8. Aggregate risk score
    """
    t0 = time.time()

    # 1. Load audio
    try:
        waveform, sr = load_audio(audio_path)
        duration = get_duration(waveform, sr)
    except Exception as e:
        elapsed = (time.time() - t0) * 1000
        return VoiceIntelligenceResult(
            error=str(e),
            processing_time_ms=elapsed,
        )

    # 2. Transcription
    transcript, language = _transcribe(audio_path)

    # 3. Emotion detection
    emotion, emotion_conf = _detect_emotion(audio_path)

    # 4. Deepfake detection
    deepfake_score = spectral_anomaly_score(waveform, sr)
    is_deepfake = deepfake_score >= 0.60

    # 5. Speaker count
    speaker_count = estimate_speaker_count(waveform, sr)

    # 6. Scam text analysis on transcript
    scam_result = None
    if transcript.strip():
        from services.scam_agent.pipeline import run_scam_pipeline
        scam_result = run_scam_pipeline(text=transcript, case_id=case_id)
        scam_risk = scam_result.risk_score
    else:
        scam_risk = 0.0

    # 7. Aggregate risk
    risk_score = aggregate_voice_risk(deepfake_score, scam_risk, emotion)
    risk_level = _risk_level_from_score(risk_score)

    # 8. Explanation
    parts = []
    if is_deepfake:
        parts.append(f"Audio shows synthetic/AI-generated voice characteristics (score={deepfake_score:.2f}).")
    if emotion not in ("neutral", "calm"):
        parts.append(f"Detected elevated emotion: {emotion} (confidence={emotion_conf:.2f}).")
    if scam_result and scam_result.risk_score > 0.3:
        parts.append(f"Transcript content is high-risk: {scam_result.explanation}")
    if not parts:
        parts.append("No significant fraud signals detected in audio.")
    explanation = " ".join(parts)

    elapsed = (time.time() - t0) * 1000
    logger.info(f"[VoiceAgent] case={case_id} risk={risk_score:.2f} deepfake={is_deepfake} emotion={emotion} t={elapsed:.0f}ms")

    return VoiceIntelligenceResult(
        transcript=transcript,
        language=language,
        is_deepfake=is_deepfake,
        deepfake_confidence=deepfake_score,
        emotion=emotion,
        emotion_confidence=emotion_conf,
        speaker_count=speaker_count,
        audio_duration_seconds=round(duration, 2),
        scam_analysis=scam_result,
        risk_score=risk_score,
        risk_level=risk_level,
        explanation=explanation,
        processing_time_ms=elapsed,
    )
