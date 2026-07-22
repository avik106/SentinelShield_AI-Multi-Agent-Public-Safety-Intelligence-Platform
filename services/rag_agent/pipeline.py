"""
RAG Investigation Copilot Agent — Core Pipeline
Query embedding → Qdrant dense search + BM25 sparse → RRF fusion → rerank → LLM generation.
Includes retrieval metrics reporting and a strict hallucination guard.
"""

from __future__ import annotations
import time
from loguru import logger

from shared.config import get_settings
from shared.schemas import RAGCopilotResult, Citation

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
    Full RAG pipeline.
    If search results fall below RAG_MIN_CONFIDENCE, Hallucination Guard prevents fabrication.
    Never throws unhandled exceptions.
    """
    t0 = time.time()
    top_k = top_k or settings.RAG_TOP_K
    warnings = []

    if not query.strip():
        elapsed = (time.time() - t0) * 1000
        return RAGCopilotResult(
            status="SKIPPED",
            reason="Empty query input.",
            answer="No reliable supporting evidence found.",
            processing_time_ms=elapsed,
            execution_time_ms=elapsed,
        )

    try:
        # 1. Embed query
        query_vector = embed_query = None
        try:
            from services.rag_agent.utils import embed_query as _embed
            query_vector = _embed(query)
        except Exception as e:
            logger.warning(f"Embedding failed: {e}")
            warnings.append("Embedding generation failed. Running sparse retrieval only.")

        # 2. Dense retrieval
        dense_results = _dense_retrieve(query_vector, top_k * 2) if query_vector else []

        # 3. BM25 sparse retrieval
        sparse_results = _bm25_search(query, dense_results, top_k * 2)

        # 4. RRF merge
        from services.rag_agent.utils import reciprocal_rank_fusion
        merged = reciprocal_rank_fusion(dense_results, sparse_results)

        # 5. Cross-encoder rerank
        top_candidates = merged[:top_k * 2]
        reranked = []
        if top_candidates:
            try:
                from services.rag_agent.utils import rerank as _rerank
                reranked = _rerank(query, top_candidates)[:top_k]
            except Exception as e:
                logger.warning(f"Reranking failed: {e}")
                reranked = top_candidates[:top_k]

        # 6. Extract documents and build citations
        citations = []
        similar_cases = []
        retrieved_document_ids = []
        top_chunks = []
        context_parts = []

        for i, chunk in enumerate(reranked):
            text = chunk.get("text", "")
            doc_id = chunk.get("id", f"chunk_{i}")
            score = round(float(chunk.get("relevance_score") or chunk.get("rrf_score") or 0.0), 4)
            source_type = chunk.get("source_type", "case")
            
            retrieved_document_ids.append(doc_id)
            top_chunks.append({"id": doc_id, "text": text[:150], "score": score})

            if text:
                context_parts.append(f"[{i+1}] {text}")
                citations.append(Citation(
                    source_id=doc_id,
                    chunk_text=text[:300],
                    relevance_score=score,
                    source_type=source_type,
                ))
                if source_type == "case" and doc_id not in similar_cases:
                    similar_cases.append(doc_id)

        # Mean score of retrieved citations
        if citations:
            retrieval_confidence = round(sum(c.relevance_score for c in citations) / len(citations), 4)
            retrieval_confidence = min(max(retrieval_confidence, 0.0), 1.0)
        else:
            retrieval_confidence = 0.0

        # 7. Hallucination Guard
        hallucination_guard_triggered = False
        answer = ""
        tokens_used = 0

        # Strict checks to prevent LLM hallucinations on sparse/low-confidence inputs
        if len(citations) == 0 or retrieval_confidence < settings.RAG_MIN_CONFIDENCE:
            hallucination_guard_triggered = True
            answer = "No reliable supporting evidence found."
            warnings.append(f"Hallucination Guard triggered. Retrieval confidence {retrieval_confidence:.2f} < threshold.")
            logger.warning(f"[RAGAgent] Hallucination Guard blocked answer. confidence={retrieval_confidence:.2f}")
        else:
            context = "\n\n".join(context_parts)
            try:
                from services.rag_agent.utils import generate_answer as _gen
                answer, tokens_used = _gen(query, context)
            except Exception as e:
                logger.warning(f"LLM answer generation failed: {e}")
                answer = "Error generating answer from LLM context."

        elapsed = (time.time() - t0) * 1000
        logger.info(
            f"[RAGAgent] case={case_id} chunks={len(reranked)} guard_triggered={hallucination_guard_triggered} t={elapsed:.0f}ms"
        )

        metrics = {
            "retrieved_chunks_count": len(reranked),
            "citations_generated_count": len(citations),
            "retrieval_confidence": retrieval_confidence,
            "tokens_used": tokens_used,
        }

        return RAGCopilotResult(
            status="SUCCESS",
            answer=answer,
            citations=citations,
            similar_cases=similar_cases[:5],
            confidence=retrieval_confidence,
            tokens_used=tokens_used,
            retrieved_document_count=len(reranked),
            retrieved_document_ids=retrieved_document_ids,
            top_chunks=top_chunks,
            retrieval_confidence=retrieval_confidence,
            hallucination_guard_triggered=hallucination_guard_triggered,
            warnings=warnings,
            warning=warnings[0] if warnings else None,
            processing_time_ms=elapsed,
            execution_time_ms=elapsed,
            metrics=metrics,
        )

    except Exception as e:
        elapsed = (time.time() - t0) * 1000
        logger.error(f"[RAGAgent] Pipeline failure: {e}", exc_info=True)
        return RAGCopilotResult(
            status="FAILED",
            reason=str(e),
            answer="No reliable supporting evidence found.",
            confidence=0.0,
            processing_time_ms=elapsed,
            execution_time_ms=elapsed,
        )
