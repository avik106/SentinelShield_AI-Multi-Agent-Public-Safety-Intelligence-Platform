"""
Scam Detection Agent — Core Pipeline
Orchestrates OCR → text cleaning → entity extraction → classification → risk scoring.
All heavy models are loaded lazily and cached after first use.
"""

from __future__ import annotations
import time
from pathlib import Path
from loguru import logger
from functools import lru_cache

from shared.config import get_settings
from shared.schemas import ScamDetectionResult, ExtractedEntities, RiskLevel, ScamType
from services.scam_agent.utils import (
    clean_text, extract_entities, detect_intent_flags,
    keyword_risk_score, classify_scam_type_by_keywords, detect_language_simple
)

settings = get_settings()


# ─────────────────────────────────────────────────────────────────────────────
# Lazy Model Loaders
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _load_ocr():
    """Load EasyOCR reader (lazy, cached)."""
    try:
        import easyocr
        logger.info("Loading EasyOCR reader (en, hi)…")
        reader = easyocr.Reader(["en", "hi"], gpu=False, verbose=False)
        return reader
    except Exception as e:
        logger.warning(f"EasyOCR unavailable: {e}. OCR disabled.")
        return None


@lru_cache(maxsize=1)
def _load_classifier():
    """Load zero-shot XLM-RoBERTa classifier (lazy, cached)."""
    try:
        from transformers import pipeline
        logger.info(f"Loading zero-shot classifier: {settings.SCAM_CLASSIFIER_MODEL}")
        clf = pipeline(
            "zero-shot-classification",
            model=settings.SCAM_CLASSIFIER_MODEL,
            device=-1,  # CPU
        )
        return clf
    except Exception as e:
        logger.warning(f"HuggingFace classifier unavailable: {e}. Keyword fallback active.")
        return None


@lru_cache(maxsize=1)
def _load_langdetect():
    """Return langdetect.detect function or None."""
    try:
        from langdetect import detect as _detect
        return _detect
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Step Functions
# ─────────────────────────────────────────────────────────────────────────────

def _ocr_image(image_path: str) -> str:
    """Run EasyOCR on an image/PDF page and return concatenated text."""
    reader = _load_ocr()
    if reader is None:
        return ""
    try:
        results = reader.readtext(image_path, detail=0, paragraph=True)
        return " ".join(results)
    except Exception as e:
        logger.warning(f"OCR failed on {image_path}: {e}")
        return ""


def _ocr_pdf(pdf_path: str) -> str:
    """Extract text from PDF using PyMuPDF (pymupdf)."""
    try:
        import fitz  # pymupdf
        doc = fitz.open(pdf_path)
        pages = []
        for page in doc:
            pages.append(page.get_text())
        return " ".join(pages)
    except Exception as e:
        logger.warning(f"PDF extraction failed on {pdf_path}: {e}")
        return ""


def _detect_language(text: str) -> str:
    detect_fn = _load_langdetect()
    if detect_fn:
        try:
            return detect_fn(text[:500])  # first 500 chars to avoid slow processing
        except Exception:
            pass
    return detect_language_simple(text)


def _classify_with_llm(text: str) -> tuple[str, float]:
    """
    Use zero-shot classifier to get scam vs not-scam + confidence.
    Returns (label, score) where label is one of ScamType values.
    """
    clf = _load_classifier()
    candidate_labels = [st.value for st in ScamType if st != ScamType.UNKNOWN]

    if clf is None:
        # Pure keyword fallback
        scam_type = classify_scam_type_by_keywords(text)
        kw_score = keyword_risk_score(text)
        return scam_type, kw_score

    try:
        result = clf(text[:512], candidate_labels, multi_label=False)
        top_label = result["labels"][0]
        top_score = result["scores"][0]
        return top_label, top_score
    except Exception as e:
        logger.warning(f"Classifier inference failed: {e}. Using keyword fallback.")
        scam_type = classify_scam_type_by_keywords(text)
        kw_score = keyword_risk_score(text)
        return scam_type, kw_score


def _compute_risk_score(
    clf_score: float,
    intent_flags: dict[str, bool],
    keyword_score: float,
    entity_count: int,
) -> float:
    """
    Weighted ensemble risk score [0.0, 1.0].
    - 50% classifier confidence
    - 25% keyword score
    - 15% intent flags (urgency + impersonation + payment)
    - 10% entity density
    """
    intent_score = sum(intent_flags.values()) / max(len(intent_flags), 1)
    entity_score = min(entity_count / 5.0, 1.0)

    score = (
        0.50 * clf_score
        + 0.25 * keyword_score
        + 0.15 * intent_score
        + 0.10 * entity_score
    )
    return round(min(max(score, 0.0), 1.0), 4)


def _risk_level(score: float) -> RiskLevel:
    if score >= 0.80:
        return RiskLevel.CRITICAL
    elif score >= 0.55:
        return RiskLevel.HIGH
    elif score >= 0.30:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def _build_explanation(
    scam_type: str,
    risk_score: float,
    intent_flags: dict[str, bool],
    entities: dict,
    language: str,
) -> str:
    parts = [f"Detected scam type: {scam_type.replace('_', ' ').title()}."]
    if intent_flags.get("urgency"):
        parts.append("Message conveys urgency to pressure the victim.")
    if intent_flags.get("impersonation"):
        parts.append("Contains authority/government impersonation signals.")
    if intent_flags.get("payment_request"):
        parts.append("Contains explicit payment or money transfer request.")
    if entities.get("phone_numbers"):
        parts.append(f"Phone numbers found: {', '.join(entities['phone_numbers'][:3])}.")
    if entities.get("upi_ids"):
        parts.append(f"UPI IDs found: {', '.join(entities['upi_ids'][:3])}.")
    if entities.get("amounts"):
        parts.append(f"Amounts mentioned: {', '.join(entities['amounts'][:3])}.")
    if language != "en":
        parts.append(f"Message language detected: {language.upper()}.")
    parts.append(f"Overall risk score: {risk_score:.2f}.")
    return " ".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Public Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def run_scam_pipeline(
    text: str | None = None,
    image_path: str | None = None,
    pdf_path: str | None = None,
    case_id: str | None = None,
) -> ScamDetectionResult:
    """
    Main scam detection pipeline.

    Args:
        text: Raw text input (WhatsApp message, SMS, etc.)
        image_path: Path to screenshot/image
        pdf_path: Path to PDF document
        case_id: Optional case identifier

    Returns:
        ScamDetectionResult with risk_score, scam_type, entities, explanation.
    """
    t0 = time.time()
    ocr_text: str | None = None

    # 1. Resolve input → text
    if image_path:
        ocr_text = _ocr_image(image_path)
        raw_text = ocr_text
    elif pdf_path:
        ocr_text = _ocr_pdf(pdf_path)
        raw_text = ocr_text
    else:
        raw_text = text or ""

    if not raw_text.strip():
        elapsed = (time.time() - t0) * 1000
        return ScamDetectionResult(
            risk_score=0.0,
            risk_level=RiskLevel.LOW,
            scam_type=ScamType.UNKNOWN,
            confidence=0.0,
            explanation="No input text could be extracted.",
            processing_time_ms=elapsed,
            error="empty_input",
            ocr_text=ocr_text,
        )

    # 2. Clean text
    cleaned = clean_text(raw_text)

    # 3. Language detection
    language = _detect_language(cleaned)

    # 4. Entity extraction
    raw_entities = extract_entities(cleaned)
    entity_count = sum(len(v) for v in raw_entities.values())
    entities = ExtractedEntities(**{k: raw_entities[k] for k in ExtractedEntities.model_fields})

    # 5. Intent flags
    intent_flags = detect_intent_flags(cleaned)

    # 6. Keyword risk score (fast fallback)
    kw_score = keyword_risk_score(cleaned)

    # 7. ML classification
    scam_type_str, clf_score = _classify_with_llm(cleaned)

    # 8. Risk score aggregation
    risk_score = _compute_risk_score(clf_score, intent_flags, kw_score, entity_count)

    # 9. Map to enum
    try:
        scam_type = ScamType(scam_type_str)
    except ValueError:
        scam_type = ScamType.UNKNOWN

    risk_level = _risk_level(risk_score)

    # 10. Build explanation
    explanation = _build_explanation(scam_type_str, risk_score, intent_flags, raw_entities, language)

    elapsed = (time.time() - t0) * 1000
    logger.info(f"[ScamAgent] case={case_id} risk={risk_score:.2f} type={scam_type} lang={language} t={elapsed:.0f}ms")

    return ScamDetectionResult(
        risk_score=risk_score,
        risk_level=risk_level,
        scam_type=scam_type,
        confidence=round(clf_score, 4),
        entities=entities,
        explanation=explanation,
        language=language,
        ocr_text=ocr_text,
        intent_flags=intent_flags,
        processing_time_ms=elapsed,
    )
