# 🎬 05. Live Demonstration Script & Guide

This guide provides a structured presentation journey for presenting **SentinelShield AI** during hackathon evaluations or technical audits.

---

## 🎭 1. Demo Narrative: "WhatsApp Digital Arrest"
- **The Context**: Victim **Rohan Verma** receives a WhatsApp video call from a suspect claiming to be DCP Sanjay Sharma of the Delhi Police. He is threatened with digital arrest inside his room and extorted for ₹50,000 via UPI. Rohan records the call, takes a screenshot of a suspect banknote, and files a report.
- **Goal**: Ingest this multimodal evidence, cross-reference it against pending cases, map active regional rings, and compile an official BNS FIR draft in under 2 seconds.

---

## 🚶 2. Step-by-Step Demo Journey

### Scene 1: The Initial Entry & Presets
- **Action**: Open `http://localhost:5173/` in your browser. Point to the **⚡ Presets shortcuts** in the sidebar. Click the **`Digital Arrest`** button.
- **Talking Track**:
  > "Instead of copy-pasting mock details during a quick demo, we integrate presets in the sidebar. Clicking 'Digital Arrest' populates the complainant's text statement, coordinates, and contact details, and automatically runs the asynchronous multi-agent pipeline in 2 seconds."

---

### Scene 2: Live Orchestrator Board (Overview Dashboard)
- **Action**: Direct attention to the **Live Multi-Agent Execution Board** and **Timeline** in the dashboard.
- **Talking Track**:
  > "SentinelShield does not run sequentially. Using a LangGraph orchestrator, we route evidence to specialized sub-agents in parallel. The live board tracks the execution state, timings, and confidences of each agent, updating dynamically."

---

### Scene 3: The Fraud Graph Inspector
- **Action**: Navigate to the **`Fraud Graph Network`** tab. Click the suspect UPI node (`payment.police@paytm`).
- **Talking Track**:
  > "SentinelShield models cases as property graph relationships. Clicking any node projects PageRank scores and case connections on the Inspector. The Louvain community algorithm has clustered these nodes into active fraud ring RING-990, linking this session to previous complaints."

---

### Scene 4: Geospatial safety radar
- **Action**: Navigate to the **`Geospatial Hotspots`** tab.
- **Talking Track**:
  > "Using DBSCAN coordinate clustering, the Geospatial Agent pulses high-density hotspot centers and maps hourly density trends. It then compiles automated patrol dispatch routes for police teams."

---

### Scene 5: Legal RAG Copilot Chat
- **Action**: Navigate to the **`Investigation Copilot`** tab. Type: `Which BNS sections apply to impersonating a CBI officer?`
- **Talking Track**:
  > "The Copilot searches legal statutes. To ensure safety, our Hallucination Guard monitors search relevance. If scores fall below 0.20, the guard intercepts the flow, returning a warning instead of LLM fabrication."

---

## 🛟 3. Presentation Recovery Plan

If external services are offline during a presentation:
- **Neo4j DB Offline**: Code automatically downgrades to **NetworkX local graph** models. The graph updates dynamically.
- **Qdrant DB Offline**: RAG agent switches to **local BM25 keyword search index**. Copilot chat remains 100% responsive.
- **EasyOCR / PyTorch weight errors**: Boundary exception traps catch the error, write `FAILED` to the board table, and allow the remaining system-level compiling to finish.
