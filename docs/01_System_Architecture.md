# 🏛️ 01. System Architecture

This document details the high-level system design, decoupling patterns, and database connections of the **SentinelShield AI** safety platform.

---

## 🛰️ 1. High-Level Design Overview

SentinelShield AI divides public safety analysis into three logical tiers:
1.  **Ingestion & Presentation (React Console)**: Provides real-time execution tracking, interactive fraud ring clustering graphs, spatial hotspots, and a RAG legal chatbot.
2.  **Gateway Routing & Orchestration (FastAPI & LangGraph)**: Acts as the core orchestrator, accepting file and text dockets, spawning parallel execution nodes, and compiling reports.
3.  **Specialist Agent Layer**: Purpose-built Python nodes that compute specific risk parameters (Text intent classification, Whisper call audits, Banknote check models, Neo4j linkages, DBSCAN coordinate clusters).

---

## 🔀 2. Architectural Data Flow

```text
[ Citizen / Police Portal ]
            │
            ▼ (Upload Multipart Statement, Call Audio, Note Image, Coords)
[ API Gateway (FastAPI) ]
            │
            ▼ (Trigger Graph Session)
[ Orchestrator (LangGraph State Machine) ] ── (Parallel Fan-Out)
            │
            ├──► [ Scam Agent (Text NLP / OCR) ]
            ├──► [ Voice Agent (Whisper transcription & Deepfake checks) ]
            ├──► [ Counterfeit Agent (YOLO check on banknotes) ]
            ├──► [ Fraud Graph Agent (Neo4j PageRank community detection) ]
            └──► [ Geospatial Agent (DBSCAN coordinates hotspots) ]
            │
            ▼ (Converge & Correlation)
[ Risk Aggregation Engine ] (shared/fusion.py)
            │
            ▼ (Gate Check)
[ legal RAG Copilot Agent ] (Mistral LLM / Qdrant)
            │
            ▼
[ Evidence Agent Node ] (Final FIR compiled with SHA256 Custody hashes)
            │
            ▼ (Render JSON payload results)
[ React dashboard Web View ]
```

---

## 🛟 3. Graceful Degradation (Production Readiness)

A primary architectural requirement is **fault isolation**. SentinelShield must remain functional even if external databases or heavy deep learning models are offline.

| Service Component | Full Mode | Graceful Fallback Mode |
|---|---|---|
| **Graph Database** | Neo4j property nodes matching historical cases | In-memory **NetworkX** instance processing active case entities |
| **Vector Database** | Qdrant statute dense embeddings search | In-memory **BM25** sparse keyword matching search |
| **NLP Transformer** | zero-shot XLM-RoBERTa intent classifier | Regex & frequency-based keyword checks |
| **Geospatial DB** | PostgreSQL historical coords ingestion | Local array clustering using current GPS focal points |
| **Document Export** | PyMuPDF PDF builder | Plain text file reports (`reports/report_*.txt`) |

---

## 🔒 4. Database Connectors

All database connectors are centralized in `shared/db.py`, utilizing Pydantic config validators:
- **SQLAlchemy Engine**: Integrates PostgreSQL connection pools with 3 recovery retries.
- **Neo4j Driver**: Provides transaction protocols to ingest nodes (`Phone`, `UPI`, `BankAccount`) and merge case links.
- **Qdrant Vector Client**: Configured to query dense BGE-M3 text vectors with custom relevance scores.
