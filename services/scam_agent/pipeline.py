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

def _ocr_image(image_path: str) -> tuple[str, float]:
    """Run EasyOCR on an image and return (concatenated_text, avg_confidence)."""
    reader = _load_ocr()
    if reader is None:
        return "", 1.0
    try:
        # Fetch coordinates and confidences (bbox, text, conf)
        results = reader.readtext(image_path, detail=1)
        if not results:
            return "", 1.0
        texts = [r[1] for r in results]
        confs = [float(r[2]) for r in results]
        avg_conf = sum(confs) / len(confs) if confs else 1.0
        return " ".join(texts), round(avg_conf, 4)
    except Exception as e:
        logger.warning(f"OCR failed on {image_path}: {e}")
        return "", 1.0


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
    # Local fallback guesser
    from services.scam_agent.utils import detect_language_simple
    return detect_language_simple(text)


def _classify_with_llm(text: str) -> tuple[str, float]:
    """
    Use zero-shot classifier to get scam vs not-scam + confidence.
    Returns (label, score) where label is one of ScamType values.
    """
    clf = _load_classifier()
    candidate_labels = [st.value for st in ScamType if st != ScamType.UNKNOWN]

    from services.scam_agent.utils import classify_scam_type_by_keywords, keyword_risk_score
    if clf is None:
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
    has_phone: bool,
    has_upi: bool,
) -> tuple[float, dict[str, float]]:
    """
    Ensemble risk score with detailed confidence breakdown.
    - 50% classifier confidence
    - 25% keyword score
    - 15% intent flags (urgency + impersonation + payment)
    - 10% entities density (split into Phone + UPI contributions)
    """
    kw_contrib = round(0.25 * keyword_score, 4)
    pattern_contrib = round(0.50 * clf_score, 4)
    
    urgency_contrib = 0.05 if intent_flags.get("urgency") else 0.0
    impersonation_contrib = 0.05 if intent_flags.get("impersonation") else 0.0
    payment_contrib = 0.05 if intent_flags.get("payment_request") else 0.0
    
    phone_contrib = 0.05 if has_phone else 0.0
    upi_contrib = 0.05 if has_upi else 0.0

    score = (
        kw_contrib
        + pattern_contrib
        + urgency_contrib
        + impersonation_contrib
        + payment_contrib
        + phone_contrib
        + upi_contrib
    )
    score = round(min(max(score, 0.0), 1.0), 4)

    breakdown = {
        "Keyword Match": kw_contrib,
        "Known Scam Pattern": pattern_contrib,
        "Urgency Language": urgency_contrib,
        "Impersonation Language": impersonation_contrib,
        "Payment Request Language": payment_contrib,
        "Phone Detection": phone_contrib,
        "UPI Detection": upi_contrib,
    }

    return score, breakdown


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
    Main scam detection pipeline. Returns a fully explained ScamDetectionResult.
    Never throws unhandled exceptions.
    """
    t0 = time.time()
    warnings = []
    ocr_text: str | None = None
    ocr_conf: float = 1.0

    try:
        # 1. Resolve input → text
        if image_path:
            ocr_text, ocr_conf = _ocr_image(image_path)
            raw_text = ocr_text
            if ocr_conf < 0.60:
                warnings.append(f"Low OCR confidence ({ocr_conf:.2f}). Extracted text may be garbled.")
        elif pdf_path:
            ocr_text = _ocr_pdf(pdf_path)
            ocr_conf = 1.0
            raw_text = ocr_text
        else:
            raw_text = text or ""
            ocr_conf = 1.0

        if not raw_text.strip():
            elapsed = (time.time() - t0) * 1000
            return ScamDetectionResult(
                status="SKIPPED",
                reason="No input text could be extracted.",
                risk_score=0.0,
                risk_level=RiskLevel.LOW,
                scam_type=ScamType.UNKNOWN,
                confidence=0.0,
                explanation="No valid textual content found to analyze.",
                processing_time_ms=elapsed,
                execution_time_ms=elapsed,
                ocr_text=ocr_text,
            )

        # 2. Clean text
        from services.scam_agent.utils import clean_text, extract_entities, detect_intent_flags, keyword_risk_score
        cleaned = clean_text(raw_text)

        # 3. Language detection
        language = _detect_language(cleaned)

        # 4. Entity extraction
        raw_entities = extract_entities(cleaned)
        entities = ExtractedEntities(**{k: raw_entities.get(k, []) for k in ExtractedEntities.model_fields})


        # 5. Intent flags
        intent_flags = detect_intent_flags(cleaned)

        # 6. Keyword risk score (fast fallback)
        kw_score = keyword_risk_score(cleaned)

        # 7. ML classification
        scam_type_str, clf_score = _classify_with_llm(cleaned)

        # 8. Risk score aggregation and granular breakdown
        risk_score, breakdown = _compute_risk_score(
            clf_score=clf_score,
            intent_flags=intent_flags,
            keyword_score=kw_score,
            has_phone=bool(entities.phone_numbers),
            has_upi=bool(entities.upi_ids),
        )

        # Propagate uncertainty: if OCR confidence is low, penalize classification score
        final_confidence = clf_score
        if ocr_conf < 1.0:
            final_confidence = round(clf_score * ocr_conf, 4)

        # 9. Map to enum
        try:
            scam_type = ScamType(scam_type_str)
        except ValueError:
            scam_type = ScamType.UNKNOWN

        risk_level = _risk_level(risk_score)

        # 10. Build explanation
        explanation = _build_explanation(scam_type_str, risk_score, intent_flags, raw_entities, language)

        elapsed = (time.time() - t0) * 1000
        logger.info(f"[ScamAgent] case={case_id} risk={risk_score:.2f} type={scam_type} conf={final_confidence:.2f} t={elapsed:.0f}ms")

        # Expose execution metrics
        metrics = {
            "input_size_chars": len(raw_text),
            "output_entities_count": sum(len(v) for v in raw_entities.values()),
            "ocr_confidence": ocr_conf,
            "raw_classifier_score": clf_score,
        }

        return ScamDetectionResult(
            status="SUCCESS",
            risk_score=risk_score,
            risk_level=risk_level,
            scam_type=scam_type,
            confidence=final_confidence,
            entities=entities,
            explanation=explanation,
            language=language,
            ocr_text=ocr_text,
            intent_flags=intent_flags,
            confidence_breakdown=breakdown,
            ocr_confidence=ocr_conf,
            warnings=warnings,
            warning=warnings[0] if warnings else None,
            processing_time_ms=elapsed,
            execution_time_ms=elapsed,
            metrics=metrics,
        )

    except Exception as e:
        elapsed = (time.time() - t0) * 1000
        logger.error(f"[ScamAgent] Pipeline failure: {e}", exc_info=True)
        return ScamDetectionResult(
            status="FAILED",
            reason=str(e),
            risk_score=0.0,
            risk_level=RiskLevel.LOW,
            scam_type=ScamType.UNKNOWN,
            confidence=0.0,
            explanation="Failed to execute scam detection pipeline due to internal exception.",
            processing_time_ms=elapsed,
            execution_time_ms=elapsed,
        )
