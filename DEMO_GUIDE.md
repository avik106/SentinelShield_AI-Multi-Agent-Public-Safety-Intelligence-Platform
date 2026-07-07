# 🎬 SentinelShield AI — Live Demonstration Script & Guide

This guide provides a structured, step-by-step script to showcase the core capabilities of **SentinelShield AI** during live demonstrations, evaluation audits, or presentations.

---

## 📋 Pre-Demo Configuration Checklist
Ensure the local servers are running (they are currently live in the background of your workspace):
1.  **FastAPI Backend**: Running on `http://localhost:8000` (Verify in settings).
2.  **Vite React Frontend**: Loaded at `http://localhost:5173/` (already active in your web browser).
3.  **Connection Badge**: Look at the top left of the dashboard. Confirm the badge shows **`AGENT HOST ONLINE`** (or `SIMULATION MODE` if backend is stopped).

---

## 🎭 The Demonstration Narrative: "WhatsApp Digital Arrest"
We will demo a realistic public safety scenario:
> **The Incident**: Complainant **Rajesh Kumar** receives a high-pressure WhatsApp call from a suspect claiming to be a CBI officer. The fraudster threatens him with "digital arrest" for money laundering and extorts ₹50,000 via UPI. Rajesh records the audio, takes a screenshot of a suspect banknote, and files a report.

---

## 🚶 Step-by-Step Demo Journey

### Scene 1: The Initial Entry & Docket Review
1.  Open **`http://localhost:5173/`** in your browser.
2.  **Show the Overview Dashboard**:
    *   Point out the aggregated risk dials, risk level (HIGH), and charges chips.
    *   Explain that this dashboard is dynamic and displays the collated evidence package of the selected case session.
    *   Show the **FIR Draft Terminal** at the right. Point out the line numbers and explain that this is an official draft generated under BNS (Bharatiya Nyaya Sanhita) guidelines, ready for law enforcement audit.

---

### Scene 2: Evidence Ingestion & Live Execution (File Analyzer)
1.  Click the **`File Analyzer & Run`** tab in the left sidebar.
2.  **Enter Complainant Details**:
    *   Complainant Name: `Ananya Singh`
    *   Contact Number: `+91 99887 76655`
3.  **Set Location**:
    *   Click the **`Jamshedpur`** quick preset button. Explain that this pre-fills latitude/longitude parameters (`22.8046`, `86.2029`) to map regional geospatial coordinates.
4.  **Describe the Incident Statement**:
    *   The text area contains the core extortion event details.
5.  **Simulate File Uploads (Optional)**:
    *   Upload a sample audio file under *Voice Evidence* (to check voice deepfake metrics).
    *   Upload a sample image under *Visual Evidence* (to verify suspect banknote authenticity).
6.  **Run the Pipeline**:
    *   Click **`Execute Multi-Agent Pipeline`**.
    *   **Direct attention to the "Orchestrator Node Pipeline Progress" panel** on the right.
    *   Explain that LangGraph is spawning parallel agent nodes (Scam Detection, Voice cloning, Counterfeit checks, Fraud rings, Geo hotspots) and aggregating them into the final report.
    *   Once execution completes (all nodes turn green), expand the **Scam Analysis** card at the bottom right to show the classified risk score and urgency intent flags.

---

### Scene 3: Ingested Entity Network (Fraud Graph)
1.  Click the **`Fraud Graph Analyzer`** tab in the sidebar.
2.  **Demonstrate the Interactive SVG Graph**:
    *   Show the central Case node linked radially to suspect entities (UPI IDs, bank details, phone numbers).
    *   **Hover over the nodes** (e.g. `UPI_cbi.officer@ybl`). Show how the *Entity Graph Inspector* card on the right updates instantly with node properties and calculated PageRank scores.
    *   Explain that this PageRank centrality highlights high-influence nodes where funds are being consolidated.
    *   Scroll down to the **Louvain Detected Fraud Rings** list. Point out that the community algorithm has clustered the entities into active fraud ring groups (`RING-401`).

---

### Scene 4: Regional Geospatial Density (Crime Hotspots)
1.  Click the **`Geospatial Hotspots`** tab in the sidebar.
2.  **Audit regional hotspots**:
    *   Show the visual safety radar indicating pulsing coordinates where DBSCAN has grouped past crime clusters.
    *   Point out the **Patrol Advisories list** on the right, providing automated dispatch coordinates for police teams.
    *   Direct attention to the **Hour-of-Day Crime Density** chart. Explain that this **Recharts** graphic maps temporal trends, showing peaks when cybercrimes are most frequently reported in the district.

---

### Scene 5: Legal Case RAG Copilot
1.  Click the **`Investigation Copilot`** tab in the sidebar.
2.  **Interact with the Chatbot**:
    *   Type: `Which BNS sections apply to this impersonation scam?` and hit send.
    *   **Show the Citations panel** on the right. Explain that the hybrid RAG pipeline has searched the legal database chunks, returning exact source snippets and relevance scores.
    *   Type a second question: `Which fraud rings are active here?`
    *   Show that the copilot replies using details from the active Fraud Graph, showing associated case dossiers.

---

## 🎯 Demo Summary Checklist (What to say)
Wrap up the demo by highlighting these four pillars of the project:
*   **Speed**: Heterogeneous evidence is ingested, cross-referenced, and summarized in seconds.
*   **Explainability**: Instead of standard classifications, investigators get granular intent badges, deepfake confidence rates, and PageRank scores.
*   **Preemption**: DBSCAN coordinates and louvain communities map proactive safety hotspots instead of reactive reports.
*   **Operational Readiness**: PDF reports and BNS FIR drafts are generated instantly to reduce administrative workload.
