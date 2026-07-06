"""
Counterfeit Currency Detection Agent — Core Pipeline
YOLOv11 detection → security feature analysis → ensemble scoring.
"""

from __future__ import annotations
import time
import os
from functools import lru_cache
from loguru import logger

from shared.config import get_settings
from shared.schemas import (
    CounterfeitDetectionResult, SecurityFeatureCheck, RiskLevel
)
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
        # Replace head for binary classification (genuine/fake)
        import torch.nn as nn
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, 2)
        model.eval()
        logger.info("EfficientNetV2 classifier initialized (random weights — fine-tune for production).")
        return model
    except Exception as e:
        logger.warning(f"EfficientNetV2 unavailable: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Steps
# ─────────────────────────────────────────────────────────────────────────────

def _detect_note_region(img, image_path: str):
    """Detect banknote bounding box via YOLO. Returns (roi_array, bbox_dict)."""
    import numpy as np
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
    """
    Returns 'genuine' probability from EfficientNetV2.
    Falls back to 0.5 (uncertain) if model unavailable.
    """
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
    t0 = time.time()

    try:
        img = preprocess_image(image_path)
    except Exception as e:
        elapsed = (time.time() - t0) * 1000
        return CounterfeitDetectionResult(
            error=str(e),
            processing_time_ms=elapsed,
        )

    # Note detection
    roi, bbox = _detect_note_region(img, image_path)

    # Security features
    security_thread = detect_security_thread(roi)
    watermark = detect_watermark(roi)
    denomination = estimate_denomination_from_size(roi)
    serial_number = extract_serial_number(roi)

    security_features = SecurityFeatureCheck(
        security_thread=security_thread,
        watermark=watermark,
        serial_pattern="pass" if serial_number else "fail",
        microprint="unknown",    # requires high-res scanner
        color_shift="unknown",   # requires UV camera
        uv_feature="unknown",
    )

    # Classification
    genuine_prob = _classify_roi(roi)

    # Ensemble risk
    risk_score = compute_ensemble_score(security_thread, watermark, serial_number, genuine_prob)
    is_counterfeit = risk_score >= settings.SCAM_RISK_THRESHOLD  # reuse threshold
    risk_level = _risk_level(risk_score)

    # Explanation
    fails = [k for k, v in security_features.model_dump().items() if v == "fail"]
    explanation_parts = []
    if fails:
        explanation_parts.append(f"Failed security checks: {', '.join(fails)}.")
    if denomination:
        explanation_parts.append(f"Estimated denomination: ₹{denomination}.")
    if serial_number:
        explanation_parts.append(f"Serial number: {serial_number}.")
    if is_counterfeit:
        explanation_parts.append(f"Note assessed as LIKELY COUNTERFEIT (risk={risk_score:.2f}).")
    else:
        explanation_parts.append(f"Note appears GENUINE (risk={risk_score:.2f}).")
    explanation = " ".join(explanation_parts)

    elapsed = (time.time() - t0) * 1000
    logger.info(f"[CounterfeitAgent] case={case_id} counterfeit={is_counterfeit} denom={denomination} risk={risk_score:.2f} t={elapsed:.0f}ms")

    return CounterfeitDetectionResult(
        is_counterfeit=is_counterfeit,
        confidence=round(1.0 - genuine_prob, 4),
        denomination=denomination,
        serial_number=serial_number,
        security_features=security_features,
        risk_score=risk_score,
        risk_level=risk_level,
        explanation=explanation,
        processing_time_ms=elapsed,
    )
