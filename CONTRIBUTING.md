# 🤝 Contributing to SentinelShield AI

First off, thank you for considering contributing to **SentinelShield AI**! It is developers and safety engineers like you who help make this platform a robust tool for law enforcement and citizen public safety.

Please read through these guidelines to maintain production-grade standards and ensure a smooth review process.

---

## 🏗️ Project Architecture & Design Principles

Before writing any code, familiarize yourself with our core design principles:
1. **Explainable AI (XAI)**: All agent decisions must return raw confidence parameters, intent indicators, and human-readable logs.
2. **Parallel Fan-out Orchestration**: Sub-agent tasks are coordinated asynchronously using a LangGraph StateGraph. Avoid blocking sequential calls.
3. **Graceful Fallbacks**: If external databases (PostgreSQL, Neo4j, Qdrant) or heavy HuggingFace/YOLO checkpoints are missing, code must fallback to in-memory/NetworkX alternatives.

---

## 🛠️ Project Setup

1. **Fork & Clone**:
   ```bash
   git clone https://github.com/your-username/SentinelShield_AI-Multi-Agent-Public-Safety-Intelligence-Platform.git
   cd SentinelShield_AI-Multi-Agent-Public-Safety-Intelligence-Platform
   ```

2. **Environment Configuration**:
   Copy `.env.example` to `.env` and configure keys for your local databases or LLM providers.
   ```bash
   cp .env.example .env
   ```

3. **Backend Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Frontend Package Setup**:
   ```bash
   cd frontend
   npm install
   ```

---

## 🎨 Coding Standards

### Backend (Python)
- **Formatting**: Strictly follow **PEP 8** style conventions.
- **Type Annotations**: Always include function arguments and return type hints:
  ```python
  def run_agent_pipeline(case_id: str, payload: dict) -> AgentResult:
  ```
- **Logging**: Use the structured `loguru` module. Do not use plain `print()` statements for diagnostic output.
- **Exception Safety**: Ensure every agent pipeline is wrapped in a try-except block returning a failed schema payload instead of raising uncaught tracebacks to the orchestrator.

### Frontend (React)
- **CSS**: Use **Vanilla CSS** or standard **TailwindCSS** utilities inside `App.jsx` or component-level stylesheets.
- **State Management**: Use React Hooks (`useState`, `useEffect`, `useMemo`) efficiently. Memoize expensive operations like graph coordinate calculation.
- **Accessibility**: Provide `aria-label` elements on interactive buttons, define focus rings, and use clear contrast palettes.

---

## 🌿 Git Workflow

### Branch Naming Conventions
Create descriptive branches named with category prefixes:
- `feature/` for new agents or interface tools (e.g. `feature/voice-emotion-analysis`)
- `bugfix/` for resolving crashes or database errors (e.g. `bugfix/neo4j-null-pointer`)
- `docs/` for README or walkthrough edits (e.g. `docs/api-guide`)
- `refactor/` for optimization updates (e.g. `refactor/recharts-memoization`)

### Commit Message Standards
We enforce clear, imperative-style Git commit messages. Avoid generic summaries like "fix", "done", or "updates".

**Structured format**:
`[Scope] Action description`

**Examples**:
- `[Orchestrator] Implement LangGraph Orchestration State Machine`
- `[GeoAgent] Add DBSCAN cluster hotspots temporal density`
- `[ScamAgent] Integrate average OCR character confidence checks`
- `[Evidence] Build Chain of Custody manifest hashing`
- `[Frontend] Overwrite interactive zoom/pan SVG workspace`

---

## 🚀 Pull Request Checklist

Before submitting a Pull Request:
1. Run the local validation suite to ensure there are no import/syntax errors:
   ```bash
   python main.py --dry-run  # Or run sanity check scripts
   ```
2. Run Vite build to ensure the React assets compile successfully:
   ```bash
   cd frontend
   npm run build
   ```
3. Update relevant documentation in `DOCUMENTATION.md` or the `README.md` if changing config values or APIs.
4. Ensure your branch is rebased onto the latest `main` branch.
