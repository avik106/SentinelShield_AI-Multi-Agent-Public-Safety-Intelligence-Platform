# 📚 SentinelShield AI — System Design & API Manual

This document provides a comprehensive technical reference for system architects, developers, and safety teams deploying, auditing, or extending **SentinelShield AI**.

---

## 🏗️ 1. Architecture & Design Decisions

The design of SentinelShield balances **asynchronous multi-modal analysis** with **graceful fail-safe execution** to ensure the platform remains online even during network or database outages.

### Design Tradeoffs & Technology Selections

| Technology | Role | Why Selected | Tradeoffs & Fallbacks |
|---|---|---|---|
| **FastAPI** | REST API Gateway | High performance, native async/await, automatic OpenAPI schemas, and ease of file upload streaming. | Synchronous framework code is isolated in background worker threads to prevent event-loop blocks. |
| **LangGraph** | Multi-Agent Orchestration | StateGraph allows parallel node execution, cycles, conditional routing gates, and unified session state. | Higher complexity than basic LangChain chains; state updates require strict Pydantic schemas. |
| **Neo4j** | Fraud Graph Database | Property graph modeling allows query-level relationship paths, PageRank centralities, and community clustering. | Can be heavy to host; falls back automatically to an in-memory **NetworkX** instance on failure. |
| **Qdrant** | Vector Search Engine | Extremely fast dense retrieval, cargo-payload filters, and BM25 sparse matching support. | Requires embedding pipelines; falls back to local BM25 keyword matching models if offline. |
| **OpenAI Whisper** | Audio Transcription | High accuracy multilingual speech-to-text models, segment-level timestamp outputs. | CPU execution can be slow; falls back to skipped state alerts if sound files are not uploaded. |
| **Ultralytics YOLO** | Counterfeit currency checks | Rapid real-time bounding box detection for security bands and watermarks. | Requires model weight hosting; falls back gracefully to warning status if image inputs are missing. |
| **React + Vite** | Operations Portal | Fast HMR, single-page reactive dashboard, interactive canvas drawing via SVG for high rendering performance. | Client-side calculations of coordinates are memoized to prevent re-render delays. |

---

## 📂 2. Folder Layout & Responsibilities

```text
sentinelshield-ai/
├── main.py                     # FastAPI REST API Gateway entrypoint
├── requirements.txt            # Python dependency manifest
├── services/                   # Multi-agent services
│   ├── orchestrator/           # LangGraph State Machine (graph.py, nodes.py, router.py)
│   ├── scam_agent/             # Text classification & EasyOCR pipeline
│   ├── voice_agent/            # Audio transcription & deepfake spectral checks
│   ├── counterfeit_agent/      # Rupee banknote security checks
│   ├── graph_agent/            # Neo4j and NetworkX fraud ring detection
│   ├── geo_agent/              # DBSCAN geospatial coordinate clustering
│   ├── rag_agent/              # Embedding generation & Qdrant statute search
│   └── evidence_agent/         # SHA256 custody logging & FIR compiler
├── shared/                     # Configuration and Pydantic schemas
│   ├── config.py               # Environments variable loader (.env)
│   ├── db.py                   # Connectors for Neo4j, Qdrant, PostgreSQL
│   └── schemas.py              # Cross-agent type declarations
└── frontend/                   # React dashboard
    ├── index.html              # HTML shell & font preconnect links
    ├── src/
    │   ├── App.jsx             # React dashboard operations console
    │   ├── index.css           # CSS theme and animations
    │   └── main.jsx            # DOM renderer
```

---

## 🔌 3. Complete API Specifications

### Ingest & Execute Full Multi-Agent Pipeline
- **Endpoint**: `POST /api/pipeline/upload`
- **Content-Type**: `multipart/form-data`
- **Request Parameters**:
  - `text_input` (string, required): Core incident description.
  - `complainant_name` (string, optional)
  - `complainant_contact` (string, optional)
  - `lat` (float, optional): Case latitude.
  - `lon` (float, optional): Case longitude.
  - `audio_file` (binary, optional): Wave call recording.
  - `image_file` (binary, optional): Rupee note photo.
- **Example Response (Success 200 OK)**:
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
- **Error Response (400 Bad Request)**:
  ```json
  {
    "detail": "Failed to parse coordinate values."
  }
  ```

### RAG Copilot Chat
- **Endpoint**: `POST /api/agents/rag`
- **Content-Type**: `application/json`
- **Request Payload**:
  ```json
  {
    "query": "What sections of BNS cover digital arrest impersonation?",
    "case_id": "CASE-2026-7890",
    "top_k": 3
  }
  ```
- **Response Payload (Success 200 OK)**:
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

---

## 🛠️ 4. Local Deployment & Run Instructions

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/SentinelShield.git
cd SentinelShield
```

### Step 2: Backend Setup
Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
Copy environment file:
```bash
cp .env.example .env
```

### Step 3: Run Backend
Start the FastAPI app:
```bash
python main.py
```
*Verify server starts on `http://localhost:8000`.*

### Step 4: Run Frontend
In a new terminal, build and run Vite React client:
```bash
cd frontend
npm install
npm run dev
```
*Open your web browser at `http://localhost:5173/`.*

---

## 🛟 5. Troubleshooting Guide

- **Error: "No module named 'psycopg2'"**
  *Reason*: PostgreSQL drivers missing.
  *Fix*: Run in graceful PostgreSQL fallback mode automatically, or install binary drivers: `pip install psycopg2-binary`.
- **Error: "Failed to connect to bolt://localhost:7687"**
  *Reason*: Neo4j database is offline or not installed.
  *Fix*: SentinelShield handles this gracefully, switching automatically to **NetworkX local graph** models. No manual recovery action is required.
- **Error: "sentence_transformers missing"**
  *Reason*: Deep learning embedding libraries uninstalled.
  *Fix*: The RAG copilot falls back to standard BM25 keyword matching search.
- **Error: "fitz missing (PyMuPDF)"**
  *Reason*: PDF library uninstalled.
  *Fix*: The Evidence Agent falls back to standard text output reports (`reports/report_*.txt`).
