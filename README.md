<div align="center">

# 🛡️ SentinelShield AI
### **A Production-Grade Multi-Agent AI Platform for Public Safety Intelligence**

**Predict. Prevent. Protect.**

![Python](https://img.shields.io/badge/Python-3.12%20%7C%203.14-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-v4-06B6D4?style=for-the-badge&logo=tailwindcss)
![Status](https://img.shields.io/badge/Status-Fully%20Integrated-success?style=for-the-badge)

*SentinelShield AI is an intelligent Multi-Agent safety platform that assists law enforcement agencies, cybercrime investigators, and citizens by automatically analyzing multimodal evidence, mapping fraud networks, identifying crime hotspots, and drafting First Information Reports (FIR).*

</div>

---

## 📖 Table of Contents
1. [System Architecture](#-system-architecture)
2. [Specialized Multi-Agent Workflow](#-specialized-multi-agent-workflow)
3. [Interactive Frontend Portal](#-interactive-frontend-portal)
4. [Backend API Interface](#-backend-api-interface)
5. [Installation & Setup](#-installation--setup)
6. [Running the Application](#-running-the-application)
7. [Simulation Mode & Graceful Fallbacks](#-simulation-mode--graceful-fallbacks)
8. [Directory Structure](#-directory-structure)

---

## 🏗️ System Architecture

SentinelShield AI operates by coordinating heterogeneous inputs (voice, text statements, currency screenshots, coordinate locations) through a parallel fan-out multi-agent flow. 

```text
                           Citizen / Police / Bank Portal
                                       │
                                       ▼
                                 API Gateway (FastAPI)
                                       │
                                       ▼
                      Multi-Agent AI Orchestrator (LangGraph)
                                       │
         ┌────────────────────────────────────────────────────────────┐
         │                                                            │
         ▼                                                            ▼
  Evidence Ingestion                                           Investigation Layer
         │                                                            │
         ▼                                                            ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │                    Specialized AI Agents (Parallel Fan-Out)               │
  │                                                                           │
  │ • Scam Detection Agent (Zero-shot NLP Classifier / OCR)                  │
  │ • Voice Intelligence Agent (Cloned Voice Auditing / Deepfakes)            │
  │ • Counterfeit Detection Agent (Security Thread / Watermark Check)         │
  │ • Fraud Graph Intelligence Agent (PageRank Centrals / Louvain Rings)       │
  │ • Geospatial Intelligence Agent (DBSCAN Regional Hotspot Clustering)      │
  │ • Hybrid RAG Investigation Copilot (Legal precedent matching)             │
  │ • Evidence Generation Agent (Report compiling / FIR Drafting)            │
  └───────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
                            Risk Aggregation Engine
                                       │
                                       ▼
                     Reports • Alerts • Dashboards • APIs
```

---

## 🤖 Specialized Multi-Agent Workflow

1. **Scam Detection Agent**: Ingests statements and OCR outputs to flag intent markers (Urgency, Threat, Financial request) and classify fraud categories (UPI fraud, digital arrest, government impersonation) using zero-shot classifiers.
2. **Voice Intelligence Agent**: Evaluates suspect call recordings using speech models, analyzing emotional manipulation indices and audio spectra for speech synthesis cloning indicators.
3. **Counterfeit currency Agent**: Evaluates suspect banknotes for color-shift thresholds, microprinting anomalies, serial format errors, and watermark validity.
4. **Fraud Graph Agent**: Ingests extracted numbers, bank details, and UPI IDs into a localized graph, executing NetworkX algorithms to rank node centrality (PageRank) and group suspect entities (Louvain community rings).
5. **Geospatial Agent**: Maps incident coordinates against regional baselines using DBSCAN to cluster crime density zones and draft patrol deployment coordinates.
6. **RAG Copilot Agent**: Searches collection chunks to match legal sections and details for investigator queries.
7. **Evidence Agent**: Collates aggregated risk indexes (weighted logarithmic formula) to output formal BNS-mapped FIR drafts and case summaries.

---

## 💻 Interactive Frontend Portal

The portal is styled with a sleek cyber-defense dark layout featuring five dedicated sections:

*   **Overview Dashboard**: Displaying aggregated risk scores, risk levels, and a terminal-style editor showing the generated **FIR Draft** and **Executive Summary** with one-click print and copy utilities.
*   **File Analyzer & Run**: Upload files (image currency checks, call audio) and enter complainant text with coordinate sliders. Shows a step-by-step pipeline status tracker detailing the active agent processing states.
*   **Fraud Graph Analyzer**: Renders an interactive radial SVG graph layout mapping the case nodes to suspect entities. Includes details inspectors when nodes are hovered/clicked, PageRank centrality scores, and Louvain fraud rings.
*   **Geospatial Hotspots**: Plots regional hotspots on a simulated radar display and renders temporal daily densities using **Recharts** bar charts.
*   **Investigation Copilot**: Chatbot utility connecting to the hybrid RAG endpoint to inspect laws, displaying RAG citations (source text and score) and similar case IDs in collapsible side panels.

---

## 🔌 Backend API Interface

The API gateway exposes production-ready REST endpoints:

*   `POST /api/pipeline/upload`: Full multi-agent workflow accepting `multipart/form-data` uploads (audio files, image files, statement texts, and lat/lon values) returning the full case payload.
*   `POST /api/agents/rag`: Ask questions based on case contexts, yielding custom citations and answers.
*   `POST /api/agents/scam/upload`: Standalone image/text scam classification.
*   `POST /api/agents/voice/upload`: Standalone deepfake voice classification.
*   `POST /api/agents/counterfeit/upload`: Standalone currency note verification.

---

## 🛠️ Installation & Setup

### Prerequisites
- Node.js (v18+)
- Python (3.12 or 3.14)

### 1. Backend Setup
Install core python dependencies. The backend uses lazy-loading mechanics, allowing the server to boot up even without starting databases:
```bash
# Navigate to backend directory and install core modules
pip install fastapi uvicorn pydantic pydantic-settings python-multipart loguru networkx sqlalchemy
```

### 2. Frontend Setup
Navigate into the `frontend` folder and install NPM packages:
```bash
cd frontend
npm install
```

---

## 🚀 Running the Application

### Step 1: Start Backend API
Run the Python FastAPI server. It is recommended to use the Python instance where the packages were installed:
```powershell
# From the project root folder
C:\Users\nikhi\AppData\Local\Python\pythoncore-3.14-64\python.exe main.py
```
*The server will spin up on **`http://localhost:8000`**.*

### Step 2: Start Frontend
From a second terminal, spin up the Vite React server:
```bash
cd frontend
npm run dev
```
*The portal will boot up on **`http://localhost:5173`**.*

---

## 🔄 Simulation Mode & Graceful Fallbacks

SentinelShield AI is designed with an **adaptive safety architecture**. If the heavy external AI weights (such as EasyOCR, PyTorch, Hugging Face Transformers) or databases (PostgreSQL, Neo4j, Qdrant) are offline or missing:

- **Scam Classifier Fallback**: Uses rule-based keyword triggers to assess intent flags and classify scam types.
- **Fraud Graph Fallback**: Falls back from Neo4j server nodes to in-memory local NetworkX graphs to execute PageRank and Louvain communities.
- **Geospatial Fallback**: If coordinate historical baselines are empty, the pipeline dynamically generates local simulated complaints, enabling DBSCAN to successfully cluster hotspots.
- **RAG Fallback**: Uses a local keyword search index over retrieved evidence nodes when vector database clusters are offline.

This ensures the portal is **100% interactive, testable, and functional** out of the box.

---

## 📂 Directory Structure

```bash
sentinelshield-ai/
├── main.py                     # FastAPI REST API Gateway Entrypoint
├── requirements.txt            # Project python dependencies manifest
├── services/                   # Multi-Agent logic
│   ├── orchestrator/           # LangGraph state machine configuration
│   ├── scam_agent/             # Text & OCR scam classifier agent
│   ├── voice_agent/            # deepfake audio detection agent
│   ├── counterfeit_agent/      # banknote verification agent
│   ├── graph_agent/            # PageRank / Louvain fraud network mapping
│   ├── geo_agent/              # DBSCAN coordinate clustering & hotspots
│   ├── rag_agent/              # Legal search RAG copilot agent
│   └── evidence_agent/         # FIR generator and report compiler
├── shared/                     # Shared models, schemas, and configurations
│   ├── config.py               # Singleton Settings loader
│   ├── db.py                   # SQL, Redis, Neo4j, Qdrant connectors
│   └── schemas.py              # Cross-agent shared Pydantic schemas
└── frontend/                   # React web portal
    ├── index.html              # Main HTML entrypoint (Google Fonts setup)
    ├── package.json            # React & Vite packages manifest
    └── src/
        ├── App.jsx             # Dashboard workspace panel views
        ├── index.css           # Tailwind v4 directives and theme fonts
        └── main.jsx            # React root renderer
```
