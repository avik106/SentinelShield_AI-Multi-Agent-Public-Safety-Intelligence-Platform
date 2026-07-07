"""
Voice Intelligence Agent — Utilities
Audio preprocessing helpers, spectral feature extraction, spectral anomaly detection fallback.
"""

from __future__ import annotations
import numpy as np
from loguru import logger


SUPPORTED_AUDIO_EXTS = {".wav", ".mp3", ".ogg", ".m4a", ".flac", ".webm"}

# ─────────────────────────────────────────────────────────────────────────────
# Audio Loading & Preprocessing
# ─────────────────────────────────────────────────────────────────────────────

def load_audio(audio_path: str, target_sr: int = 16000) -> tuple[np.ndarray, int]:
    """
    Load an audio file and resample to target_sr, mono.
    Returns (waveform_float32, sample_rate).
    """
    import librosa
    waveform, sr = librosa.load(audio_path, sr=target_sr, mono=True)
    return waveform.astype(np.float32), int(sr)


def get_duration(waveform: np.ndarray, sr: int) -> float:
    """Return audio duration in seconds."""
    return len(waveform) / sr


# ─────────────────────────────────────────────────────────────────────────────
# Spectral Anomaly — Deepfake Fallback
# ─────────────────────────────────────────────────────────────────────────────

def spectral_anomaly_score(waveform: np.ndarray, sr: int) -> float:
    """
    Lightweight spectral deepfake heuristic.
    Synthetic voices often show unnaturally regular MFCC variance
    and excess energy in high-frequency bands.
    Returns a score in [0.0, 1.0] (higher = more likely AI-generated).
    """
    try:
        import librosa
        mfcc = librosa.feature.mfcc(y=waveform, sr=sr, n_mfcc=13)
        mfcc_var = float(np.var(mfcc))

        # Spectral flatness — AI voices are often spectrally flat
        flatness = librosa.feature.spectral_flatness(y=waveform)
        mean_flatness = float(np.mean(flatness))

        # Zero-crossing rate
        zcr = librosa.feature.zero_crossing_rate(waveform)
        mean_zcr = float(np.mean(zcr))

        # Heuristic normalization (empirically tuned thresholds)
        flatness_score = min(mean_flatness * 10.0, 1.0)        # high flatness → synthetic
        zcr_score = 1.0 - min(mean_zcr / 0.3, 1.0)             # very smooth → synthetic
        var_score = 1.0 - min(mfcc_var / 500.0, 1.0)           # low MFCCvar → synthetic

        score = 0.4 * flatness_score + 0.3 * zcr_score + 0.3 * var_score
        return round(min(max(score, 0.0), 1.0), 4)
    except Exception as e:
        logger.warning(f"Spectral anomaly scoring failed: {e}")
        return 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Speaker Count Estimation
# ─────────────────────────────────────────────────────────────────────────────

def estimate_speaker_count(waveform: np.ndarray, sr: int) -> int:
    """
    Very simple speaker count estimator using pitch-based segmentation.
    Returns 1 or 2 (multi-speaker detection without diarization).
    """
    try:
        import librosa
        pitches, magnitudes = librosa.piptrack(y=waveform, sr=sr)
        # Find dominant pitch per frame
        voiced_pitches = []
        for t in range(pitches.shape[1]):
            active = magnitudes[:, t] > magnitudes[:, t].max() * 0.5
            if active.any():
                voiced_pitches.append(pitches[:, t][active].mean())
        if not voiced_pitches:
            return 1
        arr = np.array(voiced_pitches)
        # Rough grouping: two distinct pitch clusters = 2 speakers
        low = arr < np.percentile(arr, 33)
        high = arr > np.percentile(arr, 67)
        if low.sum() > 20 and high.sum() > 20:
            return 2
        return 1
    except Exception as e:
        logger.warning(f"Speaker count estimation failed: {e}")
        return 1


# ─────────────────────────────────────────────────────────────────────────────
# Risk Aggregation
# ─────────────────────────────────────────────────────────────────────────────

def aggregate_voice_risk(
    deepfake_score: float,
    scam_risk: float,
    emotion: str,
) -> float:
    """Combine deepfake probability, scam text risk, and emotion into a single score."""
    # Fear/urgency emotions add risk
    emotion_boost = 0.1 if emotion in ("fear", "anger", "disgust") else 0.0

    score = (
        0.35 * deepfake_score
        + 0.50 * scam_risk
        + 0.15 * emotion_boost
    )
    return round(min(max(score, 0.0), 1.0), 4)
