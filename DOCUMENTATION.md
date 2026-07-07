# 📚 SentinelShield AI — Complete Developer & System Documentation

This documentation provides a deep-dive technical manual for developers, system architects, and investigators deploying, extending, or maintaining **SentinelShield AI**.

---

## 1. System Architecture & Core Design Goals
SentinelShield AI is designed around a **multi-agent, parallel fan-out orchestration architecture** built for high availability, graceful degradation, and explainable intelligence. 

### Key System Goals:
*   **Explainable AI (XAI)**: All agent verdicts must generate confidence scores, intent indicators, and human-readable reasoning to ensure legal and operational transparency.
*   **Multimodal Fusion**: The platform dynamically routes and aggregates unstructured texts, call recordings, currency photo coordinates, and transaction vectors.
*   **High Performance**: Agents execute in parallel to minimize response times.
*   **Graceful Degradation**: If advanced database servers (Neo4j, Qdrant) or heavy deep learning models are unavailable, services fall back automatically to local computations (NetworkX, local keyword indexes, DBSCAN).

---

## 2. LangGraph State Machine Orchestration
The coordination of the safety agents is governed by a **StateGraph State Machine** (defined in [graph.py](file:///c:/Users/nikhi/OneDrive/Desktop/genai2/SentinelShield_AI-Multi-Agent-Public-Safety-Intelligence-Platform/services/orchestrator/graph.py)).

```text
              [ START ]
                  │
                  ▼
          route_evidence() (Conditional Fan-Out)
         /        │       \             \            \
        ▼         ▼        ▼             ▼            ▼
   scam_agent  graph_agent  geo_agent  [voice_agent]  [counterfeit_agent]
        \         │        /             /            /
         ▼        ▼       ▼             ▼            ▼
             risk_aggregation_node()
                  │
                  ▼
          should_run_rag() (Conditional Gate)
                /   \
  (If query)   ▼     ▼   (No query)
        rag_agent    │
               \     │
                ▼    ▼
          evidence_agent_node()
                  │
                  ▼
               [ END ]
```

### LangGraph State Variables (`AgentState`)
The global thread state is defined in [schemas.py](file:///c:/Users/nikhi/OneDrive/Desktop/genai2/SentinelShield_AI-Multi-Agent-Public-Safety-Intelligence-Platform/shared/schemas.py):
*   `case_id`: Core UUID tracking the session.
*   `text_input` / `audio_path` / `image_path` / `pdf_path`: Input evidence locations.
*   `lat` / `lon`: GPS coordinates of the report.
*   `scam_result` / `voice_result` / `counterfeit_result` / `graph_result` / `geo_result` / `rag_result`: Individual agent payloads.
*   `overall_risk_score`: Aggregated score between `0.0` and `1.0`.
*   `risk_level`: Enumerated severity (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).

---

## 3. Specialized Multi-Agent Pipelines & Algorithms

### A. Scam Detection Agent
*   **Source File**: [pipeline.py (Scam Agent)](file:///c:/Users/nikhi/OneDrive/Desktop/genai2/SentinelShield_AI-Multi-Agent-Public-Safety-Intelligence-Platform/services/scam_agent/pipeline.py)
*   **Workflow**: Extracts text using EasyOCR (on images) or PyMuPDF (on documents). Cleans textual syntax, runs entity regex scanners, and executes a zero-shot XLM-RoBERTa model to classify intent flags (threat, urgency, payment requests).
*   **Fallback**: Standardizes on regex and keyword frequency classification if transformers are uninstalled.

### B. Voice Intelligence Agent
*   **Source File**: [pipeline.py (Voice Agent)](file:///c:/Users/nikhi/OneDrive/Desktop/genai2/SentinelShield_AI-Multi-Agent-Public-Safety-Intelligence-Platform/services/voice_agent/pipeline.py)
*   **Workflow**: Converts audio to text using OpenAI Whisper. Computes spectrographic anomalies via Librosa/Soundfile to audit for synthetic speech (AASIST deepfake check) and analyzes speaker count and coercive emotional tone.

### C. Counterfeit Currency Agent
*   **Source File**: [pipeline.py (Counterfeit Agent)](file:///c:/Users/nikhi/OneDrive/Desktop/genai2/SentinelShield_AI-Multi-Agent-Public-Safety-Intelligence-Platform/services/counterfeit_agent/pipeline.py)
*   **Workflow**: Evaluates currency note photos using a custom YOLO object detection network (`yolo_currency.pt`). Checks security bands, watermark segments, serial number alignment, and microtext blur.

### D. Fraud Graph Agent
*   **Source File**: [pipeline.py (Graph Agent)](file:///c:/Users/nikhi/OneDrive/Desktop/genai2/SentinelShield_AI-Multi-Agent-Public-Safety-Intelligence-Platform/services/graph_agent/pipeline.py)
*   **Workflow**: Normalizes phone numbers/UPIs and ingests them into Neo4j. Executes local NetworkX PageRank centrality calculations to find high-influence nodes and Louvain Community Detection to group linked profiles into suspect fraud rings.

### E. Geospatial Intelligence Agent
*   **Source File**: [pipeline.py (Geo Agent)](file:///c:/Users/nikhi/OneDrive/Desktop/genai2/SentinelShield_AI-Multi-Agent-Public-Safety-Intelligence-Platform/services/geo_agent/pipeline.py)
*   **Workflow**: IngestsGPS coordinates, applying DBSCAN (Density-Based Spatial Clustering of Applications with Noise) with haversine metrics. Groups coordinates within a $2\text{ km}$ radius to extract high-risk hotspots and drafts deployment coordinates.

### F. Hybrid RAG Copilot Agent
*   **Source File**: [pipeline.py (RAG Agent)](file:///c:/Users/nikhi/OneDrive/Desktop/genai2/SentinelShield_AI-Multi-Agent-Public-Safety-Intelligence-Platform/services/rag_agent/pipeline.py)
*   **Workflow**: Embeds query sentences via BGE-M3. Executes a dual-pass search: dense retrieval via Qdrant and sparse retrieval via BM25. Combines them using Reciprocal Rank Fusion (RRF), filters them through a Cross-Encoder reranker, and outputs the final answer with source citations.

---

## 4. API Endpoints Reference

### Ingest & Execute Full Multi-Agent Pipeline
*   **Endpoint**: `POST /api/pipeline/upload`
*   **Headers**: `Content-Type: multipart/form-data`
*   **Request Body**:
    *   `text_input` (string): Text content or WhatsApp statement
    *   `complainant_name` (string, optional)
    *   `complainant_contact` (string, optional)
    *   `lat` (float, optional)
    *   `lon` (float, optional)
    *   `audio_file` (binary, optional): Suspect audio call file
    *   `image_file` (binary, optional): Currency image file
*   **Response Payload (`200 OK`)**:
    ```json
    {
      "case_id": "CASE-2026-9081",
      "overall_risk_score": 0.88,
      "risk_level": "HIGH",
      "evidence_package": {
        "fir_draft": "...",
        "executive_summary": "...",
        "ipc_sections": ["Section 66D IT Act", "Section 318 BNS"],
        "recommended_actions": ["..."]
      },
      "scam_result": { "risk_score": 0.9, "scam_type": "digital_arrest", "entities": {} },
      "voice_result": null,
      "counterfeit_result": null,
      "graph_result": { "fraud_rings": [], "pagerank_scores": {} },
      "geo_result": { "hotspots": [], "patrol_recommendations": [] },
      "errors": []
    }
    ```

### Ask Copilot (Hybrid RAG Search)
*   **Endpoint**: `POST /api/agents/rag`
*   **Headers**: `Content-Type: application/json`
*   **Request Body**:
    ```json
    {
      "query": "Which BNS sections apply to impersonating a CBI officer?",
      "case_id": "CASE-2026-9081",
      "top_k": 5
    }
    ```
*   **Response Payload (`200 OK`)**:
    ```json
    {
      "answer": "Under BNS guidelines, impersonating a public officer is covered under Section 319 (Impersonation)...",
      "citations": [
        {
          "source_id": "legal_precedent_sec_319",
          "chunk_text": "Section 319 BNS details cheating by impersonation using standard identity claims...",
          "relevance_score": 0.924,
          "source_type": "legal"
        }
      ],
      "similar_cases": ["CASE-2025-4421"],
      "confidence": 0.924,
      "tokens_used": 284
    }
    ```

---

## 5. Frontend Portal Workspaces

The React + Vite portal is implemented inside [App.jsx](file:///c:/Users/nikhi/OneDrive/Desktop/genai2/SentinelShield_AI-Multi-Agent-Public-Safety-Intelligence-Platform/frontend/src/App.jsx).

*   **State Management**: Tracks current case details, pipeline stages, individual agent responses, and message histories. Features a connection toggle pointing to `http://localhost:8000`.
*   **Vibrant Gauges**: Implements dynamic badges reflecting risk severity:
    *   $\ge 80\%$: Critical (Rose border/text).
    *   $30\% - 79\%$: Medium-High (Amber border/text).
    *   $< 30\%$: Low (Emerald border/text).
*   **Interactive SVG Fraud Graph**:
    *   Distributes entity nodes radially around a central Case node using angular divisions:
        $$\theta = \frac{2\pi \times \text{index}}{\text{total\_entities}}$$
        $$X = 300 + R \times \cos(\theta),\quad Y = 200 + R \times \sin(\theta)$$
    *   Tracks hovers/clicks to project details on the Graph Inspector Card, mapping suspect PageRank centralities.
*   **Crime Trends**: Draws daily crime temporal metrics via **Recharts** `<BarChart>` and `<Bar>` nodes.
*   **Legal Copilot Messenger**: Displays RAG response streams with citation expanders.

---

## 6. Developer Deployment Guide

### Manual Local Run
1.  **Clone & Verify Paths**:
    Ensure paths match your workspace configuration (e.g. `c:/Users/nikhi/OneDrive/Desktop/genai2/...`).
2.  **Start API Gateway (Terminal 1)**:
    ```powershell
    cd SentinelShield_AI-Multi-Agent-Public-Safety-Intelligence-Platform
    C:\Users\nikhi\AppData\Local\Python\pythoncore-3.14-64\python.exe main.py
    ```
3.  **Start Dev Client (Terminal 2)**:
    ```bash
    cd SentinelShield_AI-Multi-Agent-Public-Safety-Intelligence-Platform/frontend
    npm run dev
    ```
4.  **Audit Logs**: Check server terminal logs (`main:lifespan` initialization checkpoints) and check web dashboard views on `http://localhost:5173`.
