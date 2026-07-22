"""
Voice Intelligence Agent — Core Pipeline
Whisper STT → emotion detection → deepfake detection → scam text analysis.
Exposes speaker, transcription, emotion, and deepfake confidences, plus suspicious timestamps.
"""

from __future__ import annotations
import time
import math
from functools import lru_cache
from loguru import logger

from shared.config import get_settings
from shared.schemas import VoiceIntelligenceResult, RiskLevel
from services.voice_agent.utils import (
    load_audio, get_duration, spectral_anomaly_score,
    estimate_speaker_count, aggregate_voice_risk, estimate_audio_quality
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

def _transcribe_with_timestamps(audio_path: str) -> tuple[str, str, float, list[dict[str, str]]]:
    """Transcribes audio, computing transcription confidence and finding suspicious timestamps."""
    whisper_model = _load_whisper()
    if whisper_model is None:
        return "", "en", 0.0, []
    try:
        # Run Whisper transcription
        result = whisper_model.transcribe(audio_path, task="transcribe")
        transcript = result.get("text", "")
        language = result.get("language", "en")

        segments = result.get("segments", [])
        avg_probs = []
        suspicious_timestamps = []

        # High risk public safety keywords
        scam_keywords = {"otp", "pin", "cvv", "password", "bank", "arrest", "police", "money", "card", "lottery", "urgent"}

        for seg in segments:
            logprob = seg.get("avg_logprob", 0.0)
            prob = round(math.exp(logprob), 4) if logprob else 1.0
            avg_probs.append(prob)

            start_sec = seg.get("start", 0.0)
            text = seg.get("text", "")

            # Check if text contains any scam keyword
            words = set(text.lower().replace(",", "").replace(".", "").replace("!", "").split())
            if words.intersection(scam_keywords):
                timestamp_str = f"{int(start_sec)//60:02d}:{int(start_sec)%60:02d}"
                suspicious_timestamps.append({
                    "timestamp": timestamp_str,
                    "phrase": text.strip()
                })

        trans_conf = round(sum(avg_probs) / len(avg_probs), 4) if avg_probs else 1.0
        return transcript, language, trans_conf, suspicious_timestamps
    except Exception as e:
        logger.warning(f"Transcription failed: {e}")
        return "", "en", 0.0, []


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
    Main voice intelligence pipeline. Returns a fully explained VoiceIntelligenceResult.
    Never throws unhandled exceptions.
    """
    t0 = time.time()
    warnings = []

    try:
        # 1. Load & estimate duration
        waveform, sr = load_audio(audio_path)
        duration = get_duration(waveform, sr)
        
        # 2. Audio quality check
        audio_quality = estimate_audio_quality(waveform, sr)
        if audio_quality == "poor":
            warnings.append("Poor audio quality detected. Analysis accuracy may be affected.")

        # 3. Transcription & Timestamps
        transcript, language, trans_conf, suspicious_timestamps = _transcribe_with_timestamps(audio_path)

        # 4. Emotion analysis
        emotion, emotion_conf = _detect_emotion(audio_path)

        # 5. Deepfake detection
        deepfake_score = spectral_anomaly_score(waveform, sr)
        is_deepfake = deepfake_score >= 0.60

        # 6. Speaker count estimation & confidence
        speaker_count = estimate_speaker_count(waveform, sr)
        speaker_conf = 0.90 if speaker_count > 0 else 0.0

        # 7. Scam text analysis on transcript
        scam_result = None
        scam_risk = 0.0
        if transcript.strip():
            from services.scam_agent.pipeline import run_scam_pipeline
            scam_result = run_scam_pipeline(text=transcript, case_id=case_id)
            scam_risk = scam_result.risk_score
        else:
            scam_risk = 0.0
            warnings.append("Audio is silent or transcription returned no text.")

        # 8. Risk score aggregation
        risk_score = aggregate_voice_risk(deepfake_score, scam_risk, emotion)
        risk_level = _risk_level_from_score(risk_score)

        # 9. Overall confidence (average of transcription, deepfake, and emotion confidences)
        overall_conf = round((trans_conf + (1.0 - abs(deepfake_score - 0.5)*2) + emotion_conf) / 3.0, 4)
        overall_conf = min(max(overall_conf, 0.0), 1.0)

        # 10. Human-readable explanation
        parts = []
        if is_deepfake:
            parts.append(f"AI-Generated voice detected (deepfake confidence={deepfake_score:.2f}).")
        if emotion not in ("neutral", "calm"):
            parts.append(f"Emotion detected: {emotion} (emotion confidence={emotion_conf:.2f}).")
        if suspicious_timestamps:
            parts.append(f"Suspicious words/phrases detected: {len(suspicious_timestamps)} found.")
        if scam_result and scam_result.risk_score > 0.30:
            parts.append(f"Risk flagged in transcript: {scam_result.explanation}")
        if not parts:
            parts.append("Audio is clear of obvious deepfake, emotion or scam indicators.")
        explanation = " ".join(parts)

        elapsed = (time.time() - t0) * 1000
        logger.info(f"[VoiceAgent] case={case_id} risk={risk_score:.2f} deepfake={is_deepfake} emotion={emotion} t={elapsed:.0f}ms")

        # Expose execution metrics
        metrics = {
            "duration_seconds": round(duration, 2),
            "sample_rate": sr,
            "transcription_length_chars": len(transcript),
            "suspicious_timestamps_count": len(suspicious_timestamps),
        }

        return VoiceIntelligenceResult(
            status="SUCCESS",
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
            audio_quality=audio_quality,
            suspicious_timestamps=suspicious_timestamps,
            speaker_confidence=speaker_conf,
            transcription_confidence=trans_conf,
            confidence=overall_conf,
            warnings=warnings,
            warning=warnings[0] if warnings else None,
            processing_time_ms=elapsed,
            execution_time_ms=elapsed,
            metrics=metrics,
        )

    except Exception as e:
        elapsed = (time.time() - t0) * 1000
        logger.error(f"[VoiceAgent] Pipeline failure: {e}", exc_info=True)
        return VoiceIntelligenceResult(
            status="FAILED",
            reason=str(e),
            risk_score=0.0,
            risk_level=RiskLevel.LOW,
            explanation="Failed to execute voice intelligence pipeline due to internal exception.",
            processing_time_ms=elapsed,
            execution_time_ms=elapsed,
        )
