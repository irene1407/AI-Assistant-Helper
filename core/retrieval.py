import time
from pathlib import Path

import chromadb
import numpy as np
import yaml
from ollama import embeddings

from core.ingestion import CHROMA_DIR

BASE_DIR = Path(__file__).parent.parent

with open(BASE_DIR / "config" / "prompts.yaml") as f:
    _config = yaml.safe_load(f)

TOP_K = _config["thresholds"]["top_k_retrieval"]
TOP_K_RERANK = _config["thresholds"]["top_k_rerank"]
RRF_K = _config["thresholds"]["rrf_k"]
EMBEDDING_MODEL = _config["thresholds"]["embedding_model"]
CROSS_ENCODER_MODEL = _config["thresholds"]["cross_encoder_model"]

CHROMA_CLIENT = chromadb.PersistentClient(path=CHROMA_DIR)

_cross_encoder = None
_cross_encoder_available = None


def _get_cross_encoder():
    global _cross_encoder, _cross_encoder_available

    if _cross_encoder is not None:
        return _cross_encoder

    if _cross_encoder_available is False:
        return None

    try:
        from sentence_transformers import CrossEncoder

        _cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)
        _cross_encoder_available = True
        return _cross_encoder

    except Exception:
        _cross_encoder_available = False
        return None


def _embed_query(query: str) -> list[float]:
    response = embeddings(
        model=EMBEDDING_MODEL,
        prompt=query
    )
    return response["embedding"]


def _vector_search(query: str, top_k: int) -> list[dict]:
    client = CHROMA_CLIENT

    try:
        collection = client.get_or_create_collection("rag_documents")

        if collection.count() == 0:
            return []

        query_embed = _embed_query(query)

        results = collection.query(
            query_embeddings=[query_embed],
            n_results=min(top_k, collection.count()),
        )

        chunks = []

        for id_, doc, meta, dist in zip(
            results["ids"][0],
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            chunks.append({
                "id": id_,
                "text": doc,
                "metadata": meta,
                "vector_score": float(1 - dist),
            })

        return chunks

    except Exception:
        return []


def _bm25_search(query: str, top_k: int) -> list[dict]:
    from core.ingestion import _load_bm25

    bm25_index, all_chunks = _load_bm25()

    if bm25_index is None or not all_chunks:
        return []

    tokenized_query = query.lower().split()

    scores = bm25_index.get_scores(tokenized_query)

    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []

    for idx in top_indices:
        if scores[idx] > 0:
            chunk = all_chunks[idx].copy()
            chunk["bm25_score"] = float(scores[idx])
            results.append(chunk)

    return results


def _reciprocal_rank_fusion(result_lists, k=RRF_K):
    rrf_scores = {}
    chunk_map = {}

    for result_list in result_lists:
        for rank, chunk in enumerate(result_list):
            cid = chunk["id"]

            if cid not in rrf_scores:
                rrf_scores[cid] = 0.0
                chunk_map[cid] = chunk

            rrf_scores[cid] += 1.0 / (k + rank + 1)

    sorted_ids = sorted(
        rrf_scores,
        key=lambda x: rrf_scores[x],
        reverse=True
    )

    merged = []

    for cid in sorted_ids:
        chunk = chunk_map[cid].copy()
        chunk["rrf_score"] = rrf_scores[cid]
        merged.append(chunk)

    return merged


def _cross_encoder_rerank(query: str, chunks: list[dict], top_k: int):
    if not chunks:
        return []

    ce = _get_cross_encoder()

    if ce is None:
        for c in chunks:
            c["ce_score"] = c.get("rrf_score", 0.0)

        return sorted(
            chunks,
            key=lambda x: x["ce_score"],
            reverse=True
        )[:top_k]

    try:
        pairs = [[query, c["text"]] for c in chunks]

        scores = ce.predict(
            pairs,
            batch_size=32,
            show_progress_bar=False
        )

        for chunk, score in zip(chunks, scores):
            chunk["ce_score"] = float(score)

        reranked = sorted(
            chunks,
            key=lambda x: x["ce_score"],
            reverse=True
        )

        return reranked[:top_k]

    except Exception:
        for c in chunks:
            c["ce_score"] = c.get("rrf_score", 0.0)

        return chunks[:top_k]


def retrieve(query: str,
             top_k: int = TOP_K,
             top_k_final: int = TOP_K_RERANK):

    timings = {}

    t0 = time.perf_counter()
    vector_chunks = _vector_search(query, top_k)
    timings["vector_ms"] = round((time.perf_counter() - t0) * 1000, 1)

    t1 = time.perf_counter()
    bm25_chunks = _bm25_search(query, top_k)
    timings["bm25_ms"] = round((time.perf_counter() - t1) * 1000, 1)

    t2 = time.perf_counter()
    merged = _reciprocal_rank_fusion(
        [vector_chunks, bm25_chunks]
    )
    timings["rrf_ms"] = round((time.perf_counter() - t2) * 1000, 1)

    candidates = merged[:20]

    t3 = time.perf_counter()
    reranked = _cross_encoder_rerank(
        query,
        candidates,
        top_k_final
    )
    timings["rerank_ms"] = round((time.perf_counter() - t3) * 1000, 1)

    return {
        "query": query,
        "vector_results": vector_chunks,
        "bm25_results": bm25_chunks,
        "rrf_merged": merged,
        "reranked": reranked,
        "timings": timings,
        "total_candidates": len(merged),
    }