# ⚙️ 06. Deployment Guide

This guide details deployment options for **SentinelShield AI** across container environments.

---

## 🐋 1. Docker Compose Multi-Container Deployment

SentinelShield uses a modular multi-container configuration to spin up databases (PostgreSQL, Redis, Neo4j, Qdrant) alongside the FastAPI gateway.

### Service Port Allocations
- **FastAPI Gateway**: `8000`
- **React Frontend Console**: `5173`
- **Qdrant Vector DB**: `6333` (HTTP) / `6334` (gRPC)
- **Neo4j Graph DB**: `7474` (HTTP) / `7687` (Bolt)
- **PostgreSQL Database**: `5432`
- **Redis Cache**: `6379`

### Deployment Command
```bash
# Clone the repository
git clone https://github.com/your-username/SentinelShield.git
cd SentinelShield

# Spin up all containers in detached mode
docker-compose up -d --build
```

---

## 🛠️ 2. Manual Local Development Setup

If running locally on your device without Docker:

### A. Backend Setup
```bash
# Create and activate python virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Python dependency libraries
pip install -r requirements.txt

# Run the backend API server
python main.py
```

### B. Frontend Setup
```bash
# Enter frontend directory
cd frontend

# Install node dependencies
npm install

# Run the local Vite dev server
npm run dev
```
- Open `http://localhost:5173/` in your browser.

---

## 🔑 3. Configuration Management

Environment variables are loaded from `.env` at startup. Refer to the table below for core parameters:

| Variable | Default Value | Purpose |
|---|---|---|
| `DEBUG` | `false` | Enable verbose FastAPI logs. |
| `LLM_PROVIDER` | `huggingface` | selected LLM model provider (`huggingface`/`groq`/`openai`/`gemini`). |
| `NEO4J_URI` | `bolt://localhost:7687` | Connection endpoint for the property graph. |
| `QDRANT_HOST` | `localhost` | Host location of Qdrant vector database. |
