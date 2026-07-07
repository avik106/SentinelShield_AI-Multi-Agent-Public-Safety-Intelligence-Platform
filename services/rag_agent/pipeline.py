"""
RAG Investigation Copilot Agent — Core Pipeline
Query embedding → Qdrant dense search + BM25 sparse → RRF fusion → rerank → LLM generation.
"""

from __future__ import annotations
import time
from loguru import logger

from shared.config import get_settings
from shared.schemas import RAGCopilotResult, Citation
from services.rag_agent.utils import (
    embed_query, rerank, reciprocal_rank_fusion, generate_answer
)

settings = get_settings()


# ─────────────────────────────────────────────────────────────────────────────
# Qdrant Dense Retrieval
# ─────────────────────────────────────────────────────────────────────────────

def _qdrant_search(query_vector: list[float], collection: str, top_k: int) -> list[dict]:
    try:
        from shared.db import get_qdrant_client
        from qdrant_client.models import Distance, VectorParams  # noqa: F401
        client = get_qdrant_client()
        # Support both legacy (.search) and new (.query_points) Qdrant client APIs
        if hasattr(client, "query_points"):
            response = client.query_points(
                collection_name=collection,
                query=query_vector,
                limit=top_k,
                with_payload=True,
            )
            raw_results = response.points
        else:
            raw_results = client.search(  # type: ignore[attr-defined]
                collection_name=collection,
                query_vector=query_vector,
                limit=top_k,
                with_payload=True,
            )
        hits = []
        for r in raw_results:
            payload = r.payload or {}
            hits.append({
                "id": str(r.id),
                "text": payload.get("text", ""),
                "source_type": payload.get("source_type", "case"),
                "score": float(r.score),
            })
        return hits
    except Exception as e:
        logger.warning(f"Qdrant search failed on {collection}: {e}")
        return []


def _dense_retrieve(query_vector: list[float], top_k: int) -> list[dict]:
    """Search across all three Qdrant collections and merge."""
    results = []
    for collection in [
        settings.QDRANT_COLLECTION_CASES,
        settings.QDRANT_COLLECTION_EVIDENCE,
        settings.QDRANT_COLLECTION_LEGAL,
    ]:
        results.extend(_qdrant_search(query_vector, collection, top_k))
    return results


# ─────────────────────────────────────────────────────────────────────────────
# BM25 Sparse Retrieval (in-memory fallback)
# ─────────────────────────────────────────────────────────────────────────────

def _bm25_search(query: str, corpus: list[dict], top_k: int) -> list[dict]:
    """Run BM25 over the locally retrieved dense results as a secondary pass."""
    if not corpus:
        return []
    try:
        from rank_bm25 import BM25Okapi
        tokenized_corpus = [doc["text"].lower().split() for doc in corpus]
        bm25 = BM25Okapi(tokenized_corpus)
        scores = bm25.get_scores(query.lower().split())
        ranked = sorted(
            [(corpus[i], float(scores[i])) for i in range(len(corpus))],
            key=lambda x: x[1], reverse=True
        )[:top_k]
        results = []
        for doc, score in ranked:
            d = dict(doc)
            d["score"] = score
            results.append(d)
        return results
    except Exception as e:
        logger.warning(f"BM25 search failed: {e}")
        return corpus[:top_k]


# ─────────────────────────────────────────────────────────────────────────────
# Public Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def run_rag_pipeline(
    query: str,
    case_id: str | None = None,
    officer_id: str | None = None,
    top_k: int | None = None,
) -> RAGCopilotResult:
    """
    Full RAG pipeline:
    1. Embed query
    2. Dense retrieval from Qdrant (3 collections)
    3. BM25 sparse retrieval on fetched corpus
    4. RRF merge
    5. Cross-encoder reranking
    6. LLM generation with citations
    """
    t0 = time.time()
    top_k = top_k or settings.RAG_TOP_K

    if not query.strip():
        elapsed = (time.time() - t0) * 1000
        return RAGCopilotResult(
            error="Empty query.",
            processing_time_ms=elapsed,
        )

    # 1. Embed
    query_vector = embed_query(query)

    # 2. Dense retrieval
    dense_results = _dense_retrieve(query_vector, top_k * 2) if query_vector else []

    # 3. BM25 sparse
    sparse_results = _bm25_search(query, dense_results, top_k * 2)

    # 4. RRF merge
    merged = reciprocal_rank_fusion(dense_results, sparse_results)

    # 5. Rerank top candidates
    top_candidates = merged[:top_k * 2]
    reranked = rerank(query, top_candidates)[:top_k]

    # 6. Build context
    context_parts = []
    citations = []
    similar_cases = []
    for i, chunk in enumerate(reranked):
        text = chunk.get("text", "")
        if text:
            context_parts.append(f"[{i+1}] {text}")
            citations.append(Citation(
                source_id=chunk.get("id", f"chunk_{i}"),
                chunk_text=text[:300],
                relevance_score=round(float(chunk.get("relevance_score") or chunk.get("rrf_score") or 0.0), 4),
                source_type=chunk.get("source_type", "case"),
            ))
            if chunk.get("source_type") == "case":
                case_ref = chunk.get("id", "")
                if case_ref and case_ref not in similar_cases:
                    similar_cases.append(case_ref)

    context = "\n\n".join(context_parts) if context_parts else "No relevant documents found in the database."

    # 7. Generate answer
    answer, tokens_used = generate_answer(query, context)

    # Confidence: mean of top reranked relevance scores
    if citations:
        confidence = round(sum(c.relevance_score for c in citations) / len(citations), 4)
        confidence = min(max(confidence, 0.0), 1.0)
    else:
        confidence = 0.0

    elapsed = (time.time() - t0) * 1000
    logger.info(
        f"[RAGAgent] case={case_id} chunks={len(reranked)} tokens={tokens_used} t={elapsed:.0f}ms"
    )

    return RAGCopilotResult(
        answer=answer,
        citations=citations,
        similar_cases=similar_cases[:5],
        confidence=confidence,
        tokens_used=tokens_used,
        processing_time_ms=elapsed,
    )
