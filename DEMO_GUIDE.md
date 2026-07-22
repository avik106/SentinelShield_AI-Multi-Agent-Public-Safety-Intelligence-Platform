# 🎬 SentinelShield AI — Production & Hackathon Demo Guide

This guide details the end-to-end demonstration scripts, presentation talk tracks, target metrics, and recovery strategies to present **SentinelShield AI** to judges, clients, and technical panels.

---

## 📋 1. Pre-Demo Setup Checklist

1.  **FastAPI Backend Host**: Start the API server:
    ```bash
    python main.py
    ```
    *Ensure Terminal indicates successful lifespan startup on port `8000`.*
2.  **React Frontend Client**: Start the dev client:
    ```bash
    cd frontend && npm run dev
    ```
    *Open the dashboard in your web browser at `http://localhost:5173/`.*
3.  **Core Connectivity Badge**: Confirm the badge at the top left reads **`AGENT HOST ONLINE`**.
4.  **Database Fail-Safes Verified**: If Neo4j, Qdrant, or PostgreSQL are not active, confirm the backend console displays connection warnings but continues operation using standard local fallback engines.

---

## 🎭 2. Story-Based Demonstration Narrative: "WhatsApp Digital Arrest"

### The Story Context
> **The Crime**: Citizen **Rohan Verma** receives a high-pressure WhatsApp call from a suspect claiming to be DCP Sanjay Sharma of the Delhi Crime Branch. Rohan is threatened with "digital arrest" inside his room, claiming his Aadhaar ID was linked to cross-border money laundering cartels. Coerced, Rohan transfers ₹50,000 via UPI to payment.police@paytm. Under panic, he uploads the audio recording, transaction screenshot, and GPS coordinates to the police helpline.

---

### Step-by-Step Demo Walkthrough

#### Stage 1: The Hackathon One-Click Demo Mode (sidebar)
- **Action**: Click the **`Digital Arrest`** quick demo preset button in the left sidebar.
- **Visuals**:
  1. Input fields (Complainant details, coordinates, statement statement text) are populated immediately.
  2. The system executes the simulated agent fan-out workflow in 2 seconds.
  3. The **Case Activity Stream** (Timeline) updates live, logging timestamps for agent starts/finishes.
  4. Dials update to show **92% Risk Level (CRITICAL)**.
- **Judge Talking Points**:
  > "Instead of forcing judges or users to copy-paste mock strings, SentinelShield integrates one-click demo presets representing Digital Arrest and Phishing loan scams. This triggers real multi-agent fan-out orchestration, compiling evidence packages in under 2 seconds."

---

#### Stage 2: Live Multi-Agent Board & Explanations (Overview Dashboard)
- **Action**: Direct attention to the **Live Multi-Agent Execution Board** and **Risk Explainer**.
- **Visuals**:
  - The status table lists Scam Agent (`SUCCESS`), Voice Agent (`SUCCESS`), Counterfeit Agent (`SKIPPED`), Graph Agent (`SUCCESS`), Geo Agent (`SUCCESS`), and Evidence Generator (`SUCCESS`).
  - Point out the individual execution times (e.g. `650 ms`) and agent-level confidences.
  - Show the **Risk Factor checks** mapping the active threats (Scam Pattern, Fraud Ring, Urgency, Multi-case connections).
  - Review the **Human-Readable Explainer** (e.g. "...deepfake voice verified, suspect UPI shares connections with previous complaints").
- **Judge Talking Points**:
  > "SentinelShield does not expose raw JSON fields. We offer absolute explainability: we display execution metrics, warnings, and confidence scores for every single sub-agent, alongside structured risk factors and human-readable summaries."

---

#### Stage 3: The Fraud Network Graph Inspector
- **Action**: Navigate to the **`Fraud Graph Network`** tab.
- **Visuals**:
  - Distributes the suspect UPI (`payment.police@paytm`) and phone (`+91 81302 99421`) radially around the central case node.
  - Hover or click the suspect UPI node to show its **PageRank score** (`0.380`) in the Inspector sidebar.
  - Point out the red pulsing rings around nodes identified within the **Louvain Fraud Ring community (`RING-990`)**.
- **Judge Talking Points**:
  > "Cybercrimes are rarely isolated. SentinelShield ingests suspect variables into Neo4j and NetworkX. Our PageRank analysis alerts investigators to high-influence money collection nodes. The Louvain community detection algorithm instantly groups shared accounts to map active fraud rings."

---

#### Stage 4: Safety Hotspots & Patrol Advisories
- **Action**: Navigate to the **`Geospatial Hotspots`** tab.
- **Visuals**:
  - Pulses concentric hotspot zones where DBSCAN has grouped past case coords.
  - Review the **Hour-of-Day Crime Density** chart showing peak hourly activity.
  - Show the **Patrol Advisories list** providing automated coordinates and deployment directions.
- **Judge Talking Points**:
  > "Using DBSCAN clustering on GPS coordinates, we compile safety hotspots. Instead of static data, the Geospatial Agent outputs active patrol coordinates and temporal peak analysis to help police cells deploy resources effectively."

---

#### Stage 5: Hybrid Legal RAG Copilot
- **Action**: Navigate to the **`Investigation Copilot`** tab.
- **Visuals**:
  - Ask: `Which BNS sections apply to impersonating police?`
  - The chatbot answers citing exact legal statutes (Section 319 BNS - Impersonation, Section 66D IT Act - Identity Personation).
  - The **Citations sidebar** populates with dense documents and similarity metrics.
- **Judge Talking Points**:
  > "Our RAG Copilot integrates a Hallucination Guard. If embedding searches return zero relevant documents, the guard intercepts the flow, preventing the LLM from fabricating legal advice and returning a safe fallback. This ensures legal compliance."

---

## 🛟 3. System Fail-Safe Recovery Plan

SentinelShield has been built with production-grade graceful degradation. Here is how to recover during live presentations if services go offline:

| Service Failure | Impact on System | Automated Recovery Action | Demo Visual Outcome |
|---|---|---|---|
| **Neo4j DB Offline** | Cannot query global fraud graphs | Backend catches connection error, logs warnings, and switches to **NetworkX local graph** | Fraud Graph operates identically in memory using current case variables. |
| **Qdrant DB Offline** | Vector search query failure | Hallucination Guard catches empty returns, falling back to **local keyword BM25 search index** | Copilot continues to answer questions using static legal dataset definitions. |
| **PostgreSQL DB Offline** | Cannot load historical GPS points | Geo Agent catches psycopg2/conn errors, switching to **in-memory case array** | Hotspots pulse on radar grid using active cases coordinates. |
| **EasyOCR/YOLO Missing** | PDF text parsing / Note checking fails | Core exception trap sets sub-agent status to `FAILED` with details | Dashboard continues to function; failed agent lists the error reason on the boards. |
