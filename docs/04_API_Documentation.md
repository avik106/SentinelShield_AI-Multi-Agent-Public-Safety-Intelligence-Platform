# 🔌 04. API Documentation

This guide provides specifications for the **SentinelShield AI** gateway endpoints.

---

## 🗃️ 1. Endpoint Index

| Endpoint | Method | Content-Type | Purpose |
|---|---|---|---|
| `/api/pipeline/upload` | `POST` | `multipart/form-data` | Upload text, coordinates, call recordings, and banknote images to run full multi-agent triage. |
| `/api/agents/rag` | `POST` | `application/json` | Query the RAG Copilot regarding legal sections and case connections. |
| `/health` | `GET` | — | Check API server connection status. |

---

## 📂 2. Endpoint Specifications

### Ingest & Execute Full Multi-Agent Pipeline
- **Path**: `/api/pipeline/upload`
- **Method**: `POST`
- **Headers**:
  - `Content-Type: multipart/form-data`
- **Request Parameters**:
  - `text_input` (string, required): Incident text or statement.
  - `complainant_name` (string, optional)
  - `complainant_contact` (string, optional)
  - `lat` (float, optional): Case latitude.
  - `lon` (float, optional): Case longitude.
  - `audio_file` (binary, optional): Recording `.wav`/`.mp3` file.
  - `image_file` (binary, optional): Rupee note photo `.jpg`/`.png` file.
- **Success Response (200 OK)**:
  ```json
  {
    "case_id": "CASE-2026-7890",
    "overall_risk_score": 0.92,
    "risk_level": "CRITICAL",
    "confidence": 0.94,
    "scam_result": {
      "status": "SUCCESS",
      "risk_score": 0.95,
      "risk_level": "CRITICAL",
      "scam_type": "digital_arrest",
      "confidence": 0.96,
      "entities": {
        "phone_numbers": ["+91 99887 76655", "+91 81302 99421"],
        "upi_ids": ["payment.police@paytm"]
      },
      "explanation": "Digital arrest scam pattern detected."
    },
    "voice_result": {
      "status": "SUCCESS",
      "transcript": "Transfer fifty thousand rupees...",
      "is_deepfake": true,
      "deepfake_confidence": 0.98,
      "audio_quality": "excellent"
    },
    "counterfeit_result": {
      "status": "SKIPPED",
      "reason": "No banknote image uploaded."
    },
    "errors": []
  }
  ```

---

### RAG Legal Copilot Query
- **Path**: `/api/agents/rag`
- **Method**: `POST`
- **Headers**:
  - `Content-Type: application/json`
- **Request Payload**:
  ```json
  {
    "query": "What sections of BNS cover digital arrest impersonation?",
    "case_id": "CASE-2026-7890",
    "top_k": 3
  }
  ```
- **Success Response (200 OK)**:
  ```json
  {
    "answer": "Section 319 BNS covers cheating by impersonation...",
    "citations": [
      {
        "source_id": "legal_precedent_sec_319",
        "chunk_text": "Section 319 BNS details cheating by impersonation using standard identity claims...",
        "relevance_score": 0.92,
        "source_type": "legal"
      }
    ],
    "similar_cases": ["CASE-2026-4011"],
    "confidence": 0.92,
    "tokens_used": 280,
    "hallucination_guard_triggered": false
  }
  ```
