"""
Counterfeit Currency Detection Agent — Core Pipeline
YOLOv11 detection → security feature analysis → ensemble scoring.
Returns feature confidence scores and detailed explainability profiles.
"""

from __future__ import annotations
import time
import os
from functools import lru_cache
from loguru import logger

from shared.config import get_settings
from shared.schemas import CounterfeitDetectionResult, SecurityFeatureCheck, RiskLevel
from services.counterfeit_agent.utils import (
    preprocess_image, detect_security_thread, detect_watermark,
    estimate_denomination_from_size, extract_serial_number, compute_ensemble_score
)

settings = get_settings()


# ─────────────────────────────────────────────────────────────────────────────
# Lazy Loaders
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _load_yolo():
    yolo_path = settings.YOLO_MODEL_PATH
    if not os.path.exists(yolo_path):
        logger.warning(f"YOLO weights not found at {yolo_path}. Detection skipped.")
        return None
    try:
        from ultralytics import YOLO
        model = YOLO(yolo_path)
        logger.info(f"YOLO model loaded from {yolo_path}")
        return model
    except Exception as e:
        logger.warning(f"YOLO load failed: {e}")
        return None


@lru_cache(maxsize=1)
def _load_classifier():
    """EfficientNetV2 for denomination / authentic classification (from torchvision)."""
    try:
        import torch
        import torchvision.models as models
        model = models.efficientnet_v2_s(pretrained=False)
        import torch.nn as nn
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, 2)  # type: ignore[arg-type]
        model.eval()
        logger.info("EfficientNetV2 classifier initialized (random weights).")
        return model
    except Exception as e:
        logger.warning(f"EfficientNetV2 unavailable: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Steps
# ─────────────────────────────────────────────────────────────────────────────

def _detect_note_region(img, image_path: str):
    """Detect banknote bounding box via YOLO. Returns (roi_array, bbox_dict)."""
    yolo = _load_yolo()
    if yolo is None:
        return img, None

    try:
        results = yolo(image_path, conf=settings.YOLO_CONFIDENCE, verbose=False)
        if not results or len(results[0].boxes) == 0:
            return img, None
        box = results[0].boxes[0].xyxy[0].tolist()
        x1, y1, x2, y2 = [int(c) for c in box]
        roi = img[y1:y2, x1:x2]
        return roi, {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
    except Exception as e:
        logger.warning(f"YOLO detection failed: {e}")
        return img, None


def _classify_roi(roi) -> float:
    """Returns 'genuine' probability from EfficientNetV2."""
    clf = _load_classifier()
    if clf is None:
        return 0.5
    try:
        import torch
        from torchvision import transforms
        transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        tensor = transform(roi).unsqueeze(0)
        with torch.no_grad():
            logits = clf(tensor)
            probs = torch.softmax(logits, dim=1)
            genuine_prob = probs[0, 0].item()
        return round(genuine_prob, 4)
    except Exception as e:
        logger.warning(f"Classification failed: {e}")
        return 0.5


def _risk_level(score: float) -> RiskLevel:
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

def run_counterfeit_pipeline(
    image_path: str,
    case_id: str | None = None,
) -> CounterfeitDetectionResult:
    """
    Main counterfeit currency pipeline. Returns a fully explained CounterfeitDetectionResult.
    Never throws unhandled exceptions.
    """
    t0 = time.time()
    warnings = []

    try:
        img = preprocess_image(image_path)
    except Exception as e:
        elapsed = (time.time() - t0) * 1000
        return CounterfeitDetectionResult(
            status="FAILED",
            reason=str(e),
            risk_score=0.0,
            risk_level=RiskLevel.LOW,
            explanation="Failed to load and preprocess currency image.",
            processing_time_ms=elapsed,
            execution_time_ms=elapsed,
        )

    try:
        # 1. Banknote region localization
        roi, bbox = _detect_note_region(img, image_path)
        if bbox is None:
            warnings.append("Could not localize banknote bounding box. Running analysis on full image.")

        # 2. Run security feature extraction
        security_thread = detect_security_thread(roi)
        watermark = detect_watermark(roi)
        denomination = estimate_denomination_from_size(roi)
        serial_number = extract_serial_number(roi)

        # 3. Formulate feature confidence values
        thread_conf = 0.85 if security_thread == "pass" else (0.75 if security_thread == "fail" else 0.50)
        watermark_conf = 0.80 if watermark == "pass" else (0.70 if watermark == "fail" else 0.50)
        serial_conf = 0.90 if serial_number else 0.50
        microprint_conf = 0.50
        color_shift_conf = 0.50
        uv_conf = 0.50

        security_features = SecurityFeatureCheck(
            security_thread=security_thread,
            watermark=watermark,
            serial_pattern="pass" if serial_number else "fail",
            microprint="unknown",
            color_shift="unknown",
            uv_feature="unknown",
            security_thread_conf=thread_conf,
            watermark_conf=watermark_conf,
            serial_pattern_conf=serial_conf,
            microprint_conf=microprint_conf,
            color_shift_conf=color_shift_conf,
            uv_feature_conf=uv_conf,
        )

        # 4. Neural Network authentic score
        genuine_prob = _classify_roi(roi)

        # 5. Risk score assembly & classification
        risk_score = compute_ensemble_score(security_thread, watermark, serial_number, genuine_prob)
        is_counterfeit = risk_score >= settings.SCAM_RISK_THRESHOLD
        risk_level = _risk_level(risk_score)

        # 6. Detailed Feature Explainability Summary
        explanation_parts = []
        explanation_parts.append(f"Security Thread Check: {security_thread.upper()} (conf={thread_conf:.2f}).")
        explanation_parts.append(f"Watermark FFT Check: {watermark.upper()} (conf={watermark_conf:.2f}).")
        explanation_parts.append(f"Serial Pattern Check: {'PASS' if serial_number else 'FAIL'} (conf={serial_conf:.2f}).")
        
        if denomination:
            explanation_parts.append(f"Detected denomination Aspect Ratio: ₹{denomination}.")
        if serial_number:
            explanation_parts.append(f"Extracted Serial Number: {serial_number}.")

        if is_counterfeit:
            explanation_parts.append(f"VERDICT: LIKELY COUNTERFEIT currency note detected (overall risk={risk_score:.2f}).")
        else:
            explanation_parts.append(f"VERDICT: Banknote appears GENUINE (overall risk={risk_score:.2f}).")
        explanation = " ".join(explanation_parts)

        elapsed = (time.time() - t0) * 1000
        logger.info(f"[CounterfeitAgent] case={case_id} counterfeit={is_counterfeit} risk={risk_score:.2f} t={elapsed:.0f}ms")

        # Expose execution metrics
        metrics = {
            "bbox_localized": bbox is not None,
            "efficientnet_genuine_prob": genuine_prob,
            "image_size": img.shape[:2],
        }

        return CounterfeitDetectionResult(
            status="SUCCESS",
            is_counterfeit=is_counterfeit,
            confidence=round(1.0 - genuine_prob, 4),
            denomination=denomination,
            serial_number=serial_number,
            security_features=security_features,
            risk_score=risk_score,
            risk_level=risk_level,
            explanation=explanation,
            warnings=warnings,
            warning=warnings[0] if warnings else None,
            processing_time_ms=elapsed,
            execution_time_ms=elapsed,
            metrics=metrics,
        )

    except Exception as e:
        elapsed = (time.time() - t0) * 1000
        logger.error(f"[CounterfeitAgent] Pipeline failure: {e}", exc_info=True)
        return CounterfeitDetectionResult(
            status="FAILED",
            reason=str(e),
            risk_score=0.0,
            risk_level=RiskLevel.LOW,
            explanation="Failed to execute counterfeit currency check due to internal exception.",
            processing_time_ms=elapsed,
            execution_time_ms=elapsed,
        )
