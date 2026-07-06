"""
Scam Detection Agent — Utilities
Text cleaning, regex-based entity extraction, language detection helpers.
"""

from __future__ import annotations
import re
from loguru import logger


# ─────────────────────────────────────────────────────────────────────────────
# Regex Patterns for Indian Fraud Context
# ─────────────────────────────────────────────────────────────────────────────

_PHONE_RE = re.compile(r"(?:\+91[-\s]?)?[6-9]\d{9}")
_UPI_RE = re.compile(r"[\w.\-]+@(?:okaxis|okhdfcbank|okicici|oksbi|ybl|ibl|axl|paytm|upi|apl|waicici)\b", re.I)
_AMOUNT_RE = re.compile(r"(?:Rs\.?|INR|₹)\s?\d[\d,]*(?:\.\d{1,2})?", re.I)
_URL_RE = re.compile(r"https?://[^\s]+|www\.[^\s]+", re.I)
_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_BANK_ACCT_RE = re.compile(r"\b\d{9,18}\b")
_IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

# High-signal scam keywords (multilingual common terms transliterated)
SCAM_KEYWORDS = [
    # English
    "arrest", "warrant", "narcotics", "cbi", "iti", "cybercrime", "aadhaar linked",
    "account blocked", "kyc expired", "send money", "urgent", "legal action", "court case",
    "otp", "pin", "cvv", "password", "verify account", "cryptocurrency",
    "digital arrest", "money laundering", "interpol",
    # Transliterated Hindi
    "girftari", "kanuni karyawahi", "paisa bhejo", "khata band", "aadhar",
]

URGENCY_KEYWORDS = ["urgent", "immediately", "within 24 hours", "or else", "last warning",
                    "do not tell anyone", "keep this confidential", "time is running out"]

IMPERSONATION_KEYWORDS = ["officer", "inspector", "commissioner", "judge", "cbi", "iti",
                           "income tax", "enforcement directorate", "trai", "rbi", "sebi",
                           "supreme court", "high court", "police", "narcotics"]

PAYMENT_KEYWORDS = ["send money", "transfer", "deposit", "pay", "wire", "upi", "neft",
                    "rtgs", "wallet", "paytm", "gpay", "phonepe", "cryptocurrency", "bitcoin"]


def clean_text(text: str) -> str:
    """Basic text normalisation: strip extra whitespace, normalise unicode."""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    # Replace common unicode confusables
    text = text.replace("\u00a0", " ").replace("\u200b", "")
    return text


def extract_entities(text: str) -> dict[str, list[str]]:
    """
    Pure regex-based entity extraction.
    Returns phone numbers, UPI IDs, amounts, URLs, emails, bank accounts, IPs.
    """
    return {
        "phone_numbers": list(set(_PHONE_RE.findall(text))),
        "upi_ids": list(set(_UPI_RE.findall(text))),
        "amounts": list(set(_AMOUNT_RE.findall(text))),
        "urls": list(set(_URL_RE.findall(text))),
        "emails": list(set(_EMAIL_RE.findall(text))),
        "bank_accounts": list(set(_BANK_ACCT_RE.findall(text)))[:10],  # limit noise
        "ip_addresses": list(set(_IP_RE.findall(text))),
    }


def detect_intent_flags(text: str) -> dict[str, bool]:
    """Check for presence of urgency, impersonation, and payment request signals."""
    lower = text.lower()
    return {
        "urgency": any(kw in lower for kw in URGENCY_KEYWORDS),
        "impersonation": any(kw in lower for kw in IMPERSONATION_KEYWORDS),
        "payment_request": any(kw in lower for kw in PAYMENT_KEYWORDS),
    }


def keyword_risk_score(text: str) -> float:
    """
    Simple keyword-overlap score [0.0, 1.0].
    Acts as a fallback when ML models are unavailable.
    """
    lower = text.lower()
    hits = sum(1 for kw in SCAM_KEYWORDS if kw in lower)
    # Normalise: 5+ keywords → max score
    score = min(hits / 5.0, 1.0)
    return round(score, 3)


def detect_language_simple(text: str) -> str:
    """
    Lightweight language guesser without external deps.
    Returns 'hi', 'en', or 'unknown'.
    Proper detection is done via langdetect in pipeline.py.
    """
    hindi_chars = sum(1 for ch in text if "\u0900" <= ch <= "\u097F")
    if hindi_chars > 10:
        return "hi"
    return "en"


def classify_scam_type_by_keywords(text: str) -> str:
    """
    Rule-based scam type classifier using keyword lists.
    Returns one of the ScamType enum string values.
    """
    lower = text.lower()

    rules = [
        (["digital arrest", "cybercrime", "cbi", "police", "narcotics"], "digital_arrest"),
        (["upi", "gpay", "phonepe", "paytm", "qr", "scan"], "upi_fraud"),
        (["bank account", "account blocked", "kyc", "otp", "net banking"], "banking_fraud"),
        (["whatsapp", "message", "sms"], "whatsapp_fraud"),
        (["call", "voice", "phone"], "voice_phishing"),
        (["government", "income tax", "trai", "rbi", "sebi"], "government_impersonation"),
        (["invest", "stock", "crypto", "bitcoin", "returns"], "investment_fraud"),
        (["lottery", "prize", "won", "winner"], "lottery_scam"),
    ]

    for keywords, scam_type in rules:
        if any(kw in lower for kw in keywords):
            return scam_type

    return "unknown"
