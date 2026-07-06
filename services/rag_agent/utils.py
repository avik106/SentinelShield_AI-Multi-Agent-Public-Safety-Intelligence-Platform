"""
RAG Investigation Copilot Agent — Utilities
Embedding, BM25 sparse retrieval, reciprocal rank fusion, reranking helpers.
"""

from __future__ import annotations
from loguru import logger
from functools import lru_cache


# ─────────────────────────────────────────────────────────────────────────────
# Embedding
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _load_embedding_model():
    from shared.config import get_settings
    settings = get_settings()
    try:
        from sentence_transformers import SentenceTransformer
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        return SentenceTransformer(settings.EMBEDDING_MODEL)
    except Exception as e:
        logger.warning(f"Embedding model unavailable: {e}")
        return None


def embed_query(text: str) -> list[float] | None:
    model = _load_embedding_model()
    if model is None:
        return None
    try:
        vec = model.encode(text, normalize_embeddings=True)
        return vec.tolist()
    except Exception as e:
        logger.warning(f"Embedding failed: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Reranking
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _load_reranker():
    from shared.config import get_settings
    settings = get_settings()
    try:
        from sentence_transformers import CrossEncoder
        logger.info(f"Loading reranker: {settings.RAG_RERANKER_MODEL}")
        return CrossEncoder(settings.RAG_RERANKER_MODEL)
    except Exception as e:
        logger.warning(f"Reranker unavailable: {e}")
        return None


def rerank(query: str, passages: list[dict]) -> list[dict]:
    """Rerank passages using cross-encoder. Returns sorted list."""
    reranker = _load_reranker()
    if reranker is None or not passages:
        return passages
    try:
        pairs: list[tuple[str, str]] = [(query, str(p.get("text", ""))) for p in passages]
        scores = reranker.predict(pairs)  # type: ignore[arg-type]
        for i, p in enumerate(passages):
            p["relevance_score"] = float(scores[i])
        return sorted(passages, key=lambda p: p.get("relevance_score", 0.0), reverse=True)
    except Exception as e:
        logger.warning(f"Reranking failed: {e}")
        return passages


# ─────────────────────────────────────────────────────────────────────────────
# Reciprocal Rank Fusion
# ─────────────────────────────────────────────────────────────────────────────

def reciprocal_rank_fusion(
    dense_results: list[dict],
    sparse_results: list[dict],
    k: int = 60,
) -> list[dict]:
    """
    Merge dense and sparse retrieval results using RRF.
    Each result must have: id, text, score.
    """
    scores: dict[str, float] = {}
    id_to_doc: dict[str, dict] = {}

    for rank, doc in enumerate(dense_results):
        doc_id = doc.get("id", str(rank))
        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
        id_to_doc[doc_id] = doc

    for rank, doc in enumerate(sparse_results):
        doc_id = doc.get("id", str(rank))
        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
        id_to_doc[doc_id] = doc

    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    merged = []
    for doc_id in sorted_ids:
        doc = dict(id_to_doc[doc_id])
        doc["rrf_score"] = round(scores[doc_id], 6)
        merged.append(doc)
    return merged



# ─────────────────────────────────────────────────────────────────────────────
# LLM Generation Helper  — HuggingFace Inference API (free)
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _load_llm():
    """
    Provider priority (all free / already in .env):
      1. huggingface  — HF Inference API  (HUGGINGFACEHUB_API_TOKEN)
      2. groq         — Groq free tier     (GROQ_API_KEY, Llama-3-8B)
      3. None         — keyword fallback
    """
    from shared.config import get_settings
    settings = get_settings()

    # ── 1. HuggingFace Inference API ─────────────────────────────────────────
    if settings.HUGGINGFACEHUB_API_TOKEN:
        try:
            from huggingface_hub import InferenceClient
            client = InferenceClient(
                model=settings.LLM_MODEL_NAME,
                token=settings.HUGGINGFACEHUB_API_TOKEN,
            )
            logger.info(f"HuggingFace InferenceClient loaded → {settings.LLM_MODEL_NAME}")
            return ("huggingface", client, settings)
        except Exception as e:
            logger.warning(f"HuggingFace Inference API load failed: {e}")

    # ── 2. Groq free tier (Llama-3-8B-8192) ──────────────────────────────────
    if settings.GROQ_API_KEY:
        try:
            from groq import Groq
            client = Groq(api_key=settings.GROQ_API_KEY)
            logger.info("Groq LLM client loaded (llama-3.1-8b-instant).")
            return ("groq", client, settings)
        except Exception as e:
            logger.warning(f"Groq load failed: {e}")

    logger.warning("No LLM provider available — using keyword fallback.")
    return None


def generate_answer(prompt: str, context: str, max_tokens: int = 512) -> tuple[str, int]:
    """Generate answer using HuggingFace Inference API or Groq. Returns (answer, tokens_used)."""
    llm = _load_llm()

    system_msg = (
        "You are SentinelShield AI, a police investigation copilot for digital fraud cases. "
        "Answer the officer's question based only on the provided context. "
        "Be concise and cite your sources."
    )
    user_msg = f"CONTEXT:\n{context}\n\nOFFICER QUESTION: {prompt}\n\nANSWER:"

    # ── Keyword fallback (no LLM) ─────────────────────────────────────────────
    if llm is None:
        answer = (
            f"Based on the available case information: {context[:300]}... "
            f"Regarding your query '{prompt}': This requires further investigation. "
            "Please consult the full case report for detailed findings."
        )
        return answer, 0

    provider, client, settings = llm

    try:
        # ── HuggingFace Inference API ─────────────────────────────────────────
        if provider == "huggingface":
            messages = [
                {"role": "system", "content": system_msg},
                {"role": "user",   "content": user_msg},
            ]
            response = client.chat_completion(  # type: ignore[union-attr]
                messages=messages,
                max_tokens=max_tokens,
                temperature=settings.LLM_TEMPERATURE,
            )
            text = response.choices[0].message.content or ""
            tokens = getattr(response, "usage", None)
            total_tokens = getattr(tokens, "total_tokens", len(text.split()))
            return text.strip(), total_tokens

        # ── Groq ──────────────────────────────────────────────────────────────
        elif provider == "groq":
            resp = client.chat.completions.create(
                model="llama-3.1-8b-instant",   # best free Groq model
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user",   "content": user_msg},
                ],
                max_tokens=max_tokens,
                temperature=settings.LLM_TEMPERATURE,
            )
            text = resp.choices[0].message.content or ""
            return text.strip(), (resp.usage.total_tokens if resp.usage else len(text.split()))

    except Exception as e:
        logger.warning(f"LLM generation failed ({provider}): {e}")
        return f"Analysis unavailable: {str(e)}", 0

    return "No answer generated.", 0




