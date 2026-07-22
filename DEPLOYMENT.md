# 🚀 SentinelShield AI — Production & Docker Deployment Manual

This guide describes how to deploy the **SentinelShield AI** platform locally, inside Docker multi-container networks, or across production environments.

---

## 📋 1. Prerequisites & Dependencies

To execute a complete deployment with all external databases active, ensure your host environment contains:
- **Docker**: Engine version `>= 20.10.0`
- **Docker Compose**: Version `>= 2.0.0`
- **Host Ports Availability**: Ensure ports `8000` (FastAPI), `5173` (Frontend), `5432` (PostgreSQL), `6379` (Redis), `7474`/`7687` (Neo4j), and `6333` (Qdrant) are not locked by other local processes.

---

## 🐋 2. One-Click Docker Compose Deployment

SentinelShield features automatic database schema initialization and mock seeding at startup. To launch the entire platform:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/SentinelShield.git
    cd SentinelShield
    ```
2.  **Configure environments variables**:
    Copy the configuration template:
    ```bash
    cp .env.example .env
    ```
    *(Optional: Ingest your custom HuggingFace / Gemini / OpenAI keys. Safe default simulations run automatically if left empty).*
3.  **Spin up the container network**:
    ```bash
    docker compose up -d --build
    ```
4.  **Confirm container health**:
    ```bash
    docker compose ps
    ```
    *Ensure `sentinel-postgres`, `sentinel-redis`, `sentinel-neo4j`, `sentinel-qdrant`, `sentinel-backend`, and `sentinel-frontend` report status as running.*

---

## 🔑 3. Environment Variables Reference

Environment configurations are managed via `.env` in the root. Refer to the table below for variable scopes:

| Variable Name | Environment Type | Default Value | Purpose |
|---|---|---|---|
| `DEBUG` | Development | `false` | Enables verbose debug API log messages. |
| `SECRET_KEY` | Production | `UUID string` | Cryptographic secret for signing tokens. If left empty, the server generates a dynamic session UUID at startup. |
| `CORS_ORIGINS` | Production | `["*"]` | Allowed CORS endpoints allowed to query the API. |
| **POSTGRES_* ** | Development | `sentinel` / `sentinel_pass` | PostgreSQL host, port, database, and credentials. |
| **REDIS_* ** | Development | `redis://localhost:6379` | Redis host, database number, and query parameters. |
| **NEO4J_* ** | Development | `bolt://localhost:7687` | Bolt connection host and authentication parameters for the Property Graph. |
| **QDRANT_* ** | Development | `qdrant:6333` | Qdrant host and client API key parameters. |
| `LLM_PROVIDER` | Production | `huggingface` | Selected provider gateway (`huggingface`/`groq`/`openai`/`gemini`). |
| `HUGGINGFACEHUB_API_TOKEN` | Optional | — | HF Inference write token for LLM summaries. |

---

## 🧪 4. Deployment Verification

Verify operations by querying the following local portals in your browser:
- **Operations Portal (Frontend)**: **[http://localhost:5173/](http://localhost:5173/)** (served via static Nginx).
- **FastAPI Core Gateway (Backend)**: **[http://localhost:8000/](http://localhost:8000/)**
- **Swagger Documentation**: **[http://localhost:8000/docs](http://localhost:8000/docs)**
- **System Health Check API**: **[http://localhost:8000/health](http://localhost:8000/health)**
  - *Returns JSON mapping connection health status of PostgreSQL, Redis, Neo4j, and Qdrant.*

---

## 🛟 5. Troubleshooting & Common Errors

- **Error: "Port conflict on 5432 / 6379 / 7687"**
  *Reason*: A local SQL, Redis, or Neo4j instance is already running on your host machine.
  *Fix*: Stop the local services first (`pg_ctl stop`, `redis-cli shutdown`), or change the outer port bindings under `ports:` in `docker-compose.yml`.
- **Error: "Failed to connect to bolt://neo4j:7687" on backend startup**
  *Reason*: Neo4j container has not completed its database engine boot process.
  *Fix*: The backend container is configured with `healthcheck: service_healthy` dependencies. If failures occur, the backend connection pool retries 3 times automatically before starting.
- **Error: "Low overall case confidence" warning in Evidence package**
  *Reason*: Sub-agents were skipped because some required file uploads (WAV audio, banknote image) were omitted.
  *Fix*: This is normal. The platform is designed with fault isolation, compiling reports from whichever inputs are present. Use the sidebar quick presets to run full multi-modal dockets.
