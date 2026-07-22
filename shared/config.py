"""
SentinelShield AI — Shared Configuration
Loads all environment variables and exposes a single Settings object.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────────────────────
    APP_NAME: str = "SentinelShield AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = ""  # If empty, a random key is generated on startup.
    CORS_ORIGINS: list[str] = ["*"]

    # ── Database Connection Settings ─────────────────────────────────────────
    DB_CONNECT_TIMEOUT: float = 5.0
    DB_MAX_RETRIES: int = 3
    DB_RETRY_DELAY_SEC: float = 1.0

    # ── File Upload Limits ────────────────────────────────────────────────────
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS_SCAM: list[str] = [".jpg", ".jpeg", ".png", ".webp", ".pdf"]
    ALLOWED_MIME_TYPES_SCAM: list[str] = ["image/jpeg", "image/png", "image/webp", "application/pdf"]
    ALLOWED_EXTENSIONS_VOICE: list[str] = [".wav", ".mp3", ".ogg", ".m4a", ".flac"]
    ALLOWED_MIME_TYPES_VOICE: list[str] = [
        "audio/wav", "audio/mpeg", "audio/ogg", "audio/mp4",
        "audio/x-m4a", "audio/flac", "audio/x-wav"
    ]
    ALLOWED_EXTENSIONS_COUNTERFEIT: list[str] = [".jpg", ".jpeg", ".png", ".webp"]
    ALLOWED_MIME_TYPES_COUNTERFEIT: list[str] = ["image/jpeg", "image/png", "image/webp"]

    # ── LLM Models & Emotion Models ──────────────────────────────────────────
    VOICE_EMOTION_MODEL: str = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"

    # ── Risk Aggregation Settings ─────────────────────────────────────────────
    # Configurable weights for agents (Scam, Voice, Counterfeit, Graph, Geo)
    RISK_WEIGHT_SCAM: float = 0.40
    RISK_WEIGHT_VOICE: float = 0.25
    RISK_WEIGHT_COUNTERFEIT: float = 0.15
    RISK_WEIGHT_GRAPH: float = 0.10
    RISK_WEIGHT_GEO: float = 0.10

    # Risk Level thresholds
    RISK_THRESHOLD_CRITICAL: float = 0.80
    RISK_THRESHOLD_HIGH: float = 0.55
    RISK_THRESHOLD_MEDIUM: float = 0.30


    # ── PostgreSQL ────────────────────────────────────────────────────────────
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "sentinelshield"
    POSTGRES_USER: str = "sentinel"
    POSTGRES_PASSWORD: str = "sentinel_pass"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # ── Neo4j ─────────────────────────────────────────────────────────────────
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "neo4j_pass"

    # ── Qdrant ────────────────────────────────────────────────────────────────
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str = ""

    # ── MinIO / Object Storage ────────────────────────────────────────────────
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_EVIDENCE: str = "evidence"
    MINIO_BUCKET_REPORTS: str = "reports"
    MINIO_SECURE: bool = False

    # ── LangSmith ────────────────────────────────────────────────────────────
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "sentinelshield-ai"

    # ── LLM ──────────────────────────────────────────────────────────────────
    # Provider: "huggingface" | "groq" | "openai" | "gemini" | "local"
    LLM_PROVIDER: str = "huggingface"
    # Free HF Inference API model (good quality, fast, no cost)
    LLM_MODEL_NAME: str = "mistralai/Mistral-7B-Instruct-v0.3"
    LLM_MAX_NEW_TOKENS: int = 512
    LLM_TEMPERATURE: float = 0.1
    # API keys (loaded from .env)
    HUGGINGFACEHUB_API_TOKEN: str = ""
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # ── Embedding Model ───────────────────────────────────────────────────────
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    EMBEDDING_DIMENSION: int = 1024

    # ── Whisper ───────────────────────────────────────────────────────────────
    WHISPER_MODEL_SIZE: str = "base"      # "tiny" | "base" | "small" | "medium"
    WHISPER_DEVICE: str = "cpu"           # "cpu" | "cuda"

    # ── YOLO ─────────────────────────────────────────────────────────────────
    YOLO_MODEL_PATH: str = "shared/weights/yolo_currency.pt"
    YOLO_CONFIDENCE: float = 0.6

    # ── AASIST (Deepfake) ─────────────────────────────────────────────────────
    AASIST_WEIGHTS_PATH: str = "shared/weights/aasist.pth"
    AASIST_AVAILABLE: bool = False        # set True when weights are present

    # ── Scam Agent ────────────────────────────────────────────────────────────
    SCAM_CLASSIFIER_MODEL: str = "joeddav/xlm-roberta-large-xnli"
    SCAM_RISK_THRESHOLD: float = 0.5

    # ── RAG ───────────────────────────────────────────────────────────────────
    RAG_TOP_K: int = 5
    RAG_MIN_CONFIDENCE: float = 0.20
    RAG_RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    QDRANT_COLLECTION_CASES: str = "cases"
    QDRANT_COLLECTION_EVIDENCE: str = "evidence"
    QDRANT_COLLECTION_LEGAL: str = "legal_precedents"

    # ── File paths ────────────────────────────────────────────────────────────
    UPLOAD_DIR: str = "uploads"
    REPORTS_DIR: str = "reports"
    WEIGHTS_DIR: str = "shared/weights"


@lru_cache()
def get_settings() -> Settings:
    """Cached singleton settings instance."""
    return Settings()
