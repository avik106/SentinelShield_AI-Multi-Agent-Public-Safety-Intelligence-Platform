# 🤖 02. Specialized AI Agents Reference

This guide details the inputs, machine learning models, outputs, and parameters for all seven cognitive agents inside **SentinelShield AI**.

---

## 🔍 1. Scam Detection Agent
- **Source Code**: `services/scam_agent/pipeline.py`
- **Role**: Evaluates textual statement data or document OCR files to classify malicious intent.
- **Model / Engine**: Zero-shot XLM-RoBERTa (`joeddav/xlm-roberta-large-xnli`) and EasyOCR.
- **Output Parameters**:
  - `risk_score`: Float between `0.0` and `1.0`.
  - `intent_flags`: Dictionary indicating `urgency`, `impersonation`, and `payment_request` presence.
  - `confidence_breakdown`: Point maps showing keyword, pattern, and entity contributions.
  - `entities`: Extracted phones, emails, UPI IDs, urls, bank accounts, and locations.

---

## 🎙️ 2. Voice Intelligence Agent
- **Source Code**: `services/voice_agent/pipeline.py`
- **Role**: Audits call recordings for synthetic speech deepfakes, emotional signatures, and suspicious phrases.
- **Model / Engine**: OpenAI Whisper transcription and Librosa spectral RMS calculations (AASIST cloned-voice audits).
- **Output Parameters**:
  - `is_deepfake`: Boolean flag indicating synthetic speech presence.
  - `deepfake_confidence`: Accuracy rate of cloning checks.
  - `emotion`: Coercion tone checks (`aggressive`, `urgent`, `panic`, `neutral`).
  - `suspicious_timestamps`: Timestamps mapping warning keyword matches (e.g. "digital arrest").
  - `audio_quality`: Signal assessment (`excellent`, `good`, `average`, `poor`).

---

## 💵 3. Counterfeit Currency Agent
- **Source Code**: `services/counterfeit_agent/pipeline.py`
- **Role**: Audits visual Rupee banknote uploads for security band and watermark defects.
- **Model / Engine**: Ultralytics YOLO object detection (`yolo_currency.pt`).
- **Output Parameters**:
  - `is_counterfeit`: Boolean alert status.
  - `confidence`: Average features check rating.
  - `security_features`: Watermark, security thread, microprint, color shift check statuses (`pass` / `fail`).

---

## 🕸️ 4. Fraud Graph Agent
- **Source Code**: `services/graph_agent/pipeline.py`
- **Role**: Maps entity links across cases, identifies active fraud ring communities, and highlights high-influence collection variables.
- **Model / Engine**: Neo4j Graph DB with Cypher transaction queries, falling back to local NetworkX PageRank and Louvain community algorithms.
- **Output Parameters**:
  - `fraud_rings`: Groups indicating size, members, and threat rating.
  - `pagerank_scores`: Dictionary mapping node influence rankings.
  - `graph_explanations`: Text explanations of cross-case suspect links.
  - `edges_metadata`: Detailed edge metrics tracking confidence, source agent, and snippet evidence.

---

## 🗺️ 5. Geospatial Agent
- **Source Code**: `services/geo_agent/pipeline.py`
- **Role**: Groups complaint coordinate points within a district to compile hotspots and patrol routes.
- **Model / Engine**: Scikit-learn DBSCAN (Haversine metrics, 2 km radius limits).
- **Output Parameters**:
  - `hotspots`: Zones tracking complaint counts, radius, and threat level.
  - `patrol_recommendations`: Action text logs with coordinates.
  - `temporal_trend`: Hourly crime densities.
  - `confidence_interval`: GPS boundaries representing hotspot centers.

---

## 📚 6. Hybrid RAG Copilot Agent
- **Source Code**: `services/rag_agent/pipeline.py`
- **Role**: Intercepts investigator questions regarding legal statutes and matches them against case dockets and regulations.
- **Model / Engine**: BGE-M3 text embeddings, dense Qdrant searches, sparse BM25 indexing, Reciprocal Rank Fusion (RRF), and Cross-Encoder reranking.
- **Output Parameters**:
  - `answer`: Fact-checked answer.
  - `citations`: Extracted chunks tracking relevance score and source documents.
  - `hallucination_guard_triggered`: Intercept status if relevance scores fall below `RAG_MIN_CONFIDENCE` (0.20).

---

## 📄 7. Evidence Generator Agent
- **Source Code**: `services/evidence_agent/pipeline.py`
- **Role**: Compiles final investigation dossiers, BNS-mapped FIR drafts, and custody manifests.
- **Model / Engine**: Logarithmic risk calculators and PDF document builders.
- **Output Parameters**:
  - `fir_draft`: Complete Section 154 CrPC legal draft.
  - `chain_of_custody`: SHA256 hashes tracking source agent, confidence, and timestamps.
  - `skipped_agents`: Directory tracking failed or skipped agent branches with reasons.
