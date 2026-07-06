"""
Counterfeit Currency Detection Agent — Utilities
Image preprocessing, currency feature extraction helpers.
"""

from __future__ import annotations
import numpy as np
from loguru import logger


# Indian currency denomination templates (approximate aspect ratios)
DENOMINATION_ASPECT = {
    "500": 1.694,
    "200": 1.653,
    "100": 1.655,
    "50": 1.633,
    "20": 1.617,
    "10": 1.562,
}


def preprocess_image(image_path: str) -> "np.ndarray":
    """Load, resize, and normalize image for model inference."""
    import cv2
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")
    img = cv2.resize(img, (640, 640))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


def detect_security_thread(roi: "np.ndarray") -> str:
    """
    Heuristic: check for vertical dark band (security thread) in middle third of note.
    Returns 'pass' or 'fail'.
    """
    try:
        import cv2
        gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
        h, w = gray.shape
        middle_col = gray[:, w // 3: w // 2]
        col_mean = middle_col.mean(axis=0)
        # Security thread = significantly darker vertical band
        if any(v < 80 for v in col_mean):
            return "pass"
        return "fail"
    except Exception:
        return "unknown"


def detect_watermark(roi: "np.ndarray") -> str:
    """
    FFT-based watermark presence check.
    Genuine notes have distinct high-frequency watermark patterns.
    """
    try:
        import cv2
        import numpy as np
        gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY).astype(float)
        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)
        magnitude = 20 * np.log(np.abs(fshift) + 1)
        center_energy = magnitude[
            magnitude.shape[0]//2 - 30:magnitude.shape[0]//2 + 30,
            magnitude.shape[1]//2 - 30:magnitude.shape[1]//2 + 30,
        ].mean()
        return "pass" if center_energy > 100 else "fail"
    except Exception:
        return "unknown"


def estimate_denomination_from_size(roi: "np.ndarray") -> str | None:
    """Guess denomination from ROI aspect ratio."""
    if roi is None:
        return None
    h, w = roi.shape[:2]
    if h == 0:
        return None
    aspect = w / h
    best = min(DENOMINATION_ASPECT, key=lambda d: abs(DENOMINATION_ASPECT[d] - aspect))
    return best


def extract_serial_number(roi: "np.ndarray") -> str | None:
    """OCR-based serial number extraction from note region."""
    try:
        import easyocr
        reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        results = reader.readtext(roi, detail=0, paragraph=False)
        # Serial numbers: uppercase letter(s) + digits pattern
        import re
        pattern = re.compile(r"[A-Z]{1,3}\s?\d{6,9}")
        for text in results:
            m = pattern.search(text)
            if m:
                return m.group(0).replace(" ", "")
        return None
    except Exception as e:
        logger.warning(f"Serial number extraction failed: {e}")
        return None


def compute_ensemble_score(
    security_thread: str,
    watermark: str,
    serial_number: str | None,
    classification_score: float,
) -> float:
    """
    Weighted ensemble counterfeit risk score [0.0, 1.0].
    Higher score = more likely counterfeit.
    """
    thread_fail = 1.0 if security_thread == "fail" else 0.0
    watermark_fail = 1.0 if watermark == "fail" else 0.0
    serial_fail = 0.5 if serial_number is None else 0.0  # missing serial adds suspicion
    clf = 1.0 - classification_score  # classifier gives "genuine" confidence

    score = (
        0.30 * thread_fail
        + 0.25 * watermark_fail
        + 0.15 * serial_fail
        + 0.30 * clf
    )
    return round(min(max(score, 0.0), 1.0), 4)
