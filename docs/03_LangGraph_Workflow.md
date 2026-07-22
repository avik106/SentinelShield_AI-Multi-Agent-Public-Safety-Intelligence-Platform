# 🔀 03. LangGraph Orchestration & Workflows

This document explains the State Machine and Orchestration logic coordinating **SentinelShield AI** sub-agents.

---

## 🧭 1. LangGraph State Machine Structure

The coordinations of the safety agents are defined in `services/orchestrator/graph.py` via a `StateGraph`.

```text
              [ START ]
                  │
                  ▼
          route_evidence() ──── (Fan-Out Conditional Router)
         /   /    │     \   \
        ▼   ▼     ▼      ▼   ▼
     Scam Graph  Geo   [Voice] [Counterfeit]
        \   \     │      /   /
         ▼   ▼    ▼     ▼   ▼
            risk_aggregation_node()
                  │
                  ▼
          should_run_rag() ──── (Conditional Gate)
                /   \
  (If Query)   ▼     ▼  (No Query)
         rag_agent   │
               \     │
                ▼    ▼
          evidence_agent_node()
                  │
                  ▼
               [ END ]
```

---

## 📋 2. Global State Variable Model (`AgentState`)

The graph holds state variables across executions inside the thread. Defined in `shared/schemas.py` as a dictionary:

```python
class AgentState(TypedDict):
    case_id: str
    text_input: Optional[str]
    audio_path: Optional[str]
    image_path: Optional[str]
    pdf_path: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    
    # Ingest details
    complainant_name: Optional[str]
    complainant_contact: Optional[str]
    
    # Sub-agent results
    scam_result: Optional[ScamDetectionResult]
    voice_result: Optional[VoiceIntelligenceResult]
    counterfeit_result: Optional[CounterfeitDetectionResult]
    graph_result: Optional[FraudGraphResult]
    geo_result: Optional[GeoIntelligenceResult]
    rag_result: Optional[RAGCopilotResult]
    
    # Aggregated threat results
    overall_risk_score: float
    risk_level: RiskLevel
    evidence_package: Optional[EvidencePackage]
    errors: List[str]
```

---

## 🔀 3. Routing Rules & Gates

### A. Conditional Evidence Router (`route_evidence`)
Before spawning nodes, the router parses the active `AgentState` variables:
- **Scam Agent**: Runs if `text_input` is present.
- **Voice Agent**: Runs only if `audio_path` is present.
- **Counterfeit Agent**: Runs only if `image_path` (currency snapshot) is present.
- **Graph Agent**: Runs for all cases to link complainant variables.
- **Geo Agent**: Runs for all cases to map coordinates.

```python
def route_evidence(state: dict) -> List[str]:
    active_nodes = ["scam_agent", "graph_agent", "geo_agent"]
    if state.get("audio_path"):
        active_nodes.append("voice_agent")
    if state.get("image_path"):
        active_nodes.append("counterfeit_agent")
    return active_nodes
```

### B. Conditional RAG Gate (`should_run_rag`)
Following risk aggregation, the graph checks if the officer asked a legal or case question:
- If `state.get("officer_query")` is present -> routes to `rag_agent`.
- Else -> routes directly to `evidence_agent_node`.
