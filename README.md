<div align="center">

# 🛡️ SentinelShield AI
### AI-Powered Multi-Agent Public Safety Intelligence Platform

**Predict. Prevent. Protect.**

[![FastAPI Backend](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React Frontend](https://img.shields.io/badge/React-19_Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![LangGraph Orchestrator](https://img.shields.io/badge/LangGraph-Orchestration-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)](https://github.com/langchain-ai/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/your-username/SentinelShield-AI?style=for-the-badge&color=blue)](https://github.com/your-username/SentinelShield-AI)

SentinelShield AI ingests citizen fraud reports (text statements, audio recordings, currency snapshots, and location coordinates) and processes them in parallel to output risk scores, connected fraud graph networks, geospatial hotspots, and legally compliant FIR drafts in seconds.

[System Architecture](#-system-architecture) • [Multi-Agent Workflow](#-ai-agent-workflow) • [Installation](#-installation--setup) • [Developer Docs](DOCUMENTATION.md) • [Demo Presets Guide](DEMO_GUIDE.md)

</div>

---

## 📖 Table of Contents
1. [Problem Statement](#-problem-statement)
2. [Solution Overview](#-solution-overview)
3. [Key Features](#-key-features)
4. [Technology Stack](#-technology-stack)
5. [System Architecture](#-system-architecture)
6. [AI Agent Workflow](#-ai-agent-workflow)
7. [Project Folder Layout](#-project-folder-layout)
8. [Installation & Setup](#-installation--setup)
9. [Environment Variables](#-environment-variables)
10. [API Gateway Endpoints](#-api-gateway-endpoints)
11. [Design Decisions & Tradeoffs](#-design-decisions--tradeoffs)
12. [Limitations & Roadmap](#-limitations--roadmap)
13. [Contributing](#-contributing)
14. [License](#-license)

---

## 🎯 Problem Statement

Digital fraud (UPI scams, "digital arrest" extortion calls, counterfeit currency, and organized cyber rings) is outpacing citizen helplines and cyber cells. Today, public safety faces severe bottlenecks:

- **Fragmented Evidence**: Incidents generate disparate inputs (text, voice recordings, note screenshots, GPS coordinates). Reviews are conducted separately with no automated system-level correlation.
- **Manual Investigation**: Triage is slow. Officers spend valuable hours transcribing audio, checking coordinates, and checking serial numbers manually.
- **Invisible Fraud Networks**: Shared phone numbers, bank accounts, and UPI IDs link many victims, but complaints are reviewed in isolation, leaving major fraud rings undetected.
- **Reactive Patrols**: Crime cells lack automated clustering to identify regional high-density zones, preventing proactive patrolling.
- **Inconsistent FIR Drafting**: Identifying applicable sections of BNS (Bharatiya Nyaya Sanhita) or IT Act and drafting official dockets takes time.

### How SentinelShield Solves These Problems
SentinelShield AI coordinates specialized cognitive agents using an asynchronous **parallel fan-out StateGraph**. It parses multi-modal inputs, cross-references suspects against historical complaints, visualizes fraud ring networks, maps regional hotspots, and generates an official BNS-compliant FIR draft with a secure SHA256 Chain of Custody.

---

## ✨ Key Features

| Feature | Description | Core Engine | Fallback Strategy |
|---|---|---|---|
| **Multi-Agent AI** | Parallel fan-out execution of specialty agents | LangGraph StateGraph | Sequential fallback pipeline |
| **Fraud Graph Analysis** | Visualizes connections & identifies fraud ring members | Neo4j Graph DB & PageRank | Local **NetworkX** in-memory graph |
| **Voice Intelligence** | Audio transcription & spectral deepfake checks | Whisper STT & Librosa spectral RMS | Skipped warnings if files missing |
| **Counterfeit Detection** | Rupee banknote security thread & watermark audit | Custom **YOLO** Object Detector | Skipped warnings if images missing |
| **Geo Intelligence** | Clusters locations to find regional hotspots | DBSCAN with haversine metrics | Coordinate focal point baseline |
| **Evidence Generation** | Automatically drafts FIRs & compiles Case Reports | Weighted Risk Aggregation | Local text file output (`reports/`) |
| **Explainable AI (XAI)** | Displays confidence breakdown and intent badges | Granular score matrices | Rule-based keyword/intent scoring |

---

## 🛠️ Technology Stack

- **Backend & Core**: Python, FastAPI, LangGraph, Uvicorn, SQLAlchemy, Pydantic, Loguru
- **Frontend Console**: React 19, Vite, TailwindCSS v4, Recharts, Lucide Icons, Custom SVG viewports
- **AI & Document Processing**: Zero-shot XLM-RoBERTa, OpenAI Whisper, EasyOCR, Ultralytics YOLO, Librosa, PyMuPDF
- **Databases**: PostgreSQL (Relational), Redis (Caching), Neo4j (Graph), Qdrant (Vector)
- **Deployment**: Docker, docker-compose, Github Actions

---

## 🏗️ System Architecture

```text
  [ Citizen / Officer ] ──► [ React Investigation Console ] ──► [ API Gateway (FastAPI) ]
                                                                          │
                                                                          ▼
                                                                [ LangGraph Orchestrator ]
                                                                          │
                                         ┌────────────────────────────────┴────────────────────────────────┐
                                         ▼                                                                 ▼
                                [ Parallel Agents ]                                              [ Aggregation & Outputs ]
                                         │                                                                 │
  ┌──────────────────────────────────────┼──────────────────────────────────────┐                          │
  │ • Scam Detection Agent (EasyOCR)     │ • Fraud Graph Agent (PageRank/Louvain)│                          ▼
  │ • Voice Intelligence Agent (Whisper) │ • Geospatial Agent (DBSCAN Hotspots) │                  [ Risk Aggregator ]
  │ • Counterfeit Agent (YOLO check)     │ • Legal RAG Assistant (Qdrant Search)│                          │
  └──────────────────────────────────────┴──────────────────────────────────────┘                          ▼
                                                                                                  [ Evidence compiler ]
                                                                                                           │
                                                                                                           ▼
                                                                                                  [ BNS FIR Report ]
```

### System Layers:
1.  **Ingestion & Client Gateway (React Dashboard)**: Initiates inputs and displays live progress, risk indicators, interactive fraud ring SVGs, maps, and RAG chats.
2.  **API Gateway Routing (FastAPI)**: Handles request parsing, triggers database pipelines, and forwards streams to the LangGraph engine.
3.  **State Machine Orchestrator (LangGraph)**: Executes conditional fan-out. Runs only the agents matching uploaded evidence (e.g. runs Voice Agent only if audio file is uploaded).
4.  **Specialist Cognitive Agents**: Execute specialized analysis in parallel.
5.  **Risk Aggregator & Correlation (Fusion)**: Cross-references suspect phone/UPI numbers, propagates confidence weights, deducts safety penalties, and computes the final risk index.
6.  **Evidence & Report Compiler**: Generates FIR drafts, legal section maps, and attaches a SHA256 Chain of Custody hashes manifest.

---

## 🤖 AI Agent Workflow

```text
 [ Incident Complaint Ingestion ]
               │
               ▼
       [ state Router ] ─── (Fan-Out) ───► [ Scam Agent (Text NLP / OCR) ]
               │                          ► [ Voice Agent (Whisper transcription & Deepfake checks) ]
               │                          ► [ Counterfeit Agent (YOLO check on banknote images) ]
               │                          ► [ Fraud Graph Agent (Neo4j PageRank community clustering) ]
               │                          ► [ Geospatial Agent (DBSCAN hotspot coordinates mapping) ]
               │                                       │
               ▼                                       ▼
      [ Converge Node ] ◄──────────────────────── (Gather)
               │
               ▼
     [ Risk Aggregator ] ───► [ RAG Copilot Gate ] ───► [ Evidence Compiler (FIR Report) ]
```

1.  **Complaint Ingestion**: Input case data is mapped to the global thread `AgentState`.
2.  **State Routing**: The state router analyzes present fields and executes active sub-agent branches asynchronously.
3.  **Parallel Specialist Executions**: Agents return confidence rates, execution times, and logs.
4.  **Convergence & Risk Aggregation**: Results are parsed, cross-referenced, and overall risk levels (CRITICAL, HIGH, etc.) are computed.
5.  **RAG Copilot Gate**: Intercepts active queries. If an officer asks a legal query, embeddings retrieve BNS/IT Act precedents.
6.  **Evidence Compilation**: Custody SHA256 hashes are recorded and reports are exported.

---

## 📂 Project Folder Layout

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
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/SentinelShield.git
cd SentinelShield
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` in the root directory:
```bash
cp .env.example .env
```
*SentinelShield operates in graceful fallback/simulation mode if keys are omitted.*

### 3. Backend Setup & Run
Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
Start the FastAPI server:
```bash
python main.py
```
*Gateway starts at `http://localhost:8000`.*

### 4. Frontend Setup & Run
In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
*React app loads at `http://localhost:5173/`.*

---

## 🔑 Environment Variables

Selected configuration variables (see [.env.example](.env.example) for a complete list):

- `DEBUG`: Toggle FastAPI debug mode (`true`/`false`).
- `NEO4J_URI` / `USER` / `PASSWORD`: Bolt connection parameters for the Neo4j Graph DB.
- `QDRANT_HOST` / `PORT`: Qdrant vector database parameters.
- `LLM_PROVIDER`: Selected LLM Gateway (`huggingface`/`groq`/`openai`/`gemini`).
- `HUGGINGFACEHUB_API_TOKEN` / `GROQ_API_KEY` / `OPENAI_API_KEY`: Selected gateway provider keys.

---

## 🔌 API Gateway Endpoints

- `POST /api/pipeline/upload` — Multipart form upload. Evaluates statement text, lat/lon, audio, and image evidence. Returns risk metrics and BNS FIR drafts.
- `POST /api/agents/rag` — JSON payload. Queries RAG Legal Copilot.
- `GET /health` — API health check.

*See complete specifications in [DOCUMENTATION.md](DOCUMENTATION.md#-3-complete-api-specifications).*

---

## 🏗️ Design Decisions & Tradeoffs

- **Why FastAPI & Uvicorn**: Selected for high-concurrency async capabilities. Multi-part form stream parser allows simultaneous audio and image uploads.
- **Why LangGraph State Machine**: Basic sequential chains crash if intermediate nodes fail. LangGraph allows conditional routing and converges gracefully to aggregation nodes.
- **Why In-Memory Fallbacks**: For hackathons and deployability, requiring a complete suite of active databases (Neo4j, Qdrant, Postgres) raises developer friction. Auto-degradation to NetworkX and local BM25 guarantees a 100% functional portal offline.

---

## 🛣️ Limitations & Roadmap

### Current Limitations:
1.  **Prototype Dataset**: Local databases index simulated case dockets and regional coordinates.
2.  **Static RAG Corpus**: legal corpus includes selected BNS and IT Act sections; it does not represent the complete Indian penal code.
3.  **Simulation Mode default**: Complex deep learning models (XLM-RoBERTa, Librosa deepfake checks) use heuristics if local GPU weights are uninstalled.

### Future Roadmap:
- **v1.0 (Hackathon Release)**: Interactive React dashboard, multi-agent parallel LangGraph execution, and core fallbacks. *(Current Version)*
- **v2.0 (Law Enforcement Beta)**: Integration with live bank transactional feeds and cellular trace logs. Role-based login panels.
- **v3.0 (Government Deployment)**: Production connection to national crime record networks. Live CCTV spatial tracking.

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on coding standards, commit messages, and branch naming conventions.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
