"""
SQLite-backed observability tracker.
Logs every pipeline trace, computes P50/P95 latency percentiles,
citation coverage rates, cost accumulation, and failure analysis.
"""

import sqlite3
import json
import time
from pathlib import Path
from typing import Optional

import numpy as np

BASE_DIR = Path(__file__).parent.parent
DB_PATH = str(BASE_DIR / "data" / "traces.db")


def _get_conn() -> sqlite3.Connection:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    _init_schema(conn)
    return conn


def _init_schema(conn: sqlite3.Connection):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS traces (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp       REAL NOT NULL,
            query           TEXT,
            response        TEXT,
            context         TEXT,
            prompt          TEXT,
            model           TEXT,
            prompt_version  TEXT,
            tokens_input    INTEGER DEFAULT 0,
            tokens_output   INTEGER DEFAULT 0,
            cost_usd        REAL DEFAULT 0.0,
            latency_ms      REAL DEFAULT 0,
            sufficiency_ms  REAL DEFAULT 0,
            llm_ms          REAL DEFAULT 0,
            vector_ms       REAL DEFAULT 0,
            bm25_ms         REAL DEFAULT 0,
            rerank_ms       REAL DEFAULT 0,
            citation_count  INTEGER DEFAULT 0,
            citation_coverage REAL DEFAULT 0.0,
            refused         INTEGER DEFAULT 0,
            error           TEXT,
            citations_json  TEXT,
            retrieval_meta  TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS eval_runs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp       REAL NOT NULL,
            faithfulness    REAL,
            answer_relevancy REAL,
            pass_gate       INTEGER,
            details_json    TEXT,
            model           TEXT
        )
    """)
    conn.commit()


def log_trace(generation_result: dict, retrieval_result: dict = None) -> int:
    """Persist a full pipeline trace to SQLite. Returns the row id."""
    conn = _get_conn()
    r_timings = retrieval_result.get("timings", {}) if retrieval_result else {}
    g_timings = generation_result.get("timings", {})

    citations = generation_result.get("citations", [])
    citation_coverage = generation_result.get("citation_coverage", 0.0)

    reranked = (retrieval_result or {}).get("reranked", [])

    cursor = conn.execute("""
        INSERT INTO traces (
            timestamp, query, response, context, prompt, model, prompt_version,
            tokens_input, tokens_output, cost_usd, latency_ms,
            sufficiency_ms, llm_ms, vector_ms, bm25_ms, rerank_ms,
            citation_count, citation_coverage, refused, error,
            citations_json, retrieval_meta
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        time.time(),
        generation_result.get("query", ""),
        generation_result.get("response", ""),
        generation_result.get("context", "")[:4000],
        generation_result.get("prompt", "")[:4000],
        generation_result.get("model", ""),
        generation_result.get("prompt_version", ""),
        generation_result.get("tokens_input", 0),
        generation_result.get("tokens_output", 0),
        generation_result.get("cost_usd", 0.0),
        generation_result.get("latency_ms", 0),
        g_timings.get("sufficiency_ms", 0),
        g_timings.get("llm_ms", 0),
        r_timings.get("vector_ms", 0),
        r_timings.get("bm25_ms", 0),
        r_timings.get("rerank_ms", 0),
        len(citations),
        citation_coverage,
        1 if generation_result.get("refused") else 0,
        generation_result.get("error"),
        json.dumps(citations),
        json.dumps([{
            "id": c.get("id"), "source": c.get("metadata", {}).get("source"),
            "ce_score": c.get("ce_score"), "rrf_score": c.get("rrf_score"),
        } for c in reranked]),
    ))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def log_eval_run(faithfulness: float, answer_relevancy: float, details: list, model: str) -> int:
    from pathlib import Path
    cfg_path = BASE_DIR / "config" / "prompts.yaml"
    import yaml
    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)
    threshold = cfg["thresholds"]["faithfulness_min"]
    passed = faithfulness >= threshold

    conn = _get_conn()
    cursor = conn.execute("""
        INSERT INTO eval_runs (timestamp, faithfulness, answer_relevancy, pass_gate, details_json, model)
        VALUES (?,?,?,?,?,?)
    """, (time.time(), faithfulness, answer_relevancy, 1 if passed else 0, json.dumps(details), model))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def get_latency_percentiles() -> dict:
    conn = _get_conn()
    rows = conn.execute("SELECT latency_ms FROM traces ORDER BY timestamp DESC LIMIT 500").fetchall()
    conn.close()
    if not rows:
        return {"p50": 0, "p95": 0, "count": 0}
    latencies = [r["latency_ms"] for r in rows]
    return {
        "p50": float(np.percentile(latencies, 50)),
        "p95": float(np.percentile(latencies, 95)),
        "count": len(latencies),
    }


def get_summary_stats() -> dict:
    conn = _get_conn()
    rows = conn.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN refused=1 THEN 1 ELSE 0 END) as refusals,
            SUM(CASE WHEN error IS NOT NULL THEN 1 ELSE 0 END) as errors,
            AVG(latency_ms) as avg_latency,
            AVG(citation_coverage) as avg_citation_coverage,
            SUM(cost_usd) as total_cost,
            SUM(tokens_input + tokens_output) as total_tokens
        FROM traces
    """).fetchone()
    conn.close()
    if not rows or rows["total"] == 0:
        return {
            "total": 0, "refusals": 0, "errors": 0,
            "avg_latency": 0, "avg_citation_coverage": 0,
            "total_cost": 0, "total_tokens": 0,
            "refusal_rate": 0, "error_rate": 0,
        }
    total = rows["total"] or 1
    return {
        "total": rows["total"] or 0,
        "refusals": rows["refusals"] or 0,
        "errors": rows["errors"] or 0,
        "avg_latency": round(rows["avg_latency"] or 0, 1),
        "avg_citation_coverage": round((rows["avg_citation_coverage"] or 0) * 100, 1),
        "total_cost": round(rows["total_cost"] or 0, 6),
        "total_tokens": rows["total_tokens"] or 0,
        "refusal_rate": round(((rows["refusals"] or 0) / total) * 100, 1),
        "error_rate": round(((rows["errors"] or 0) / total) * 100, 1),
    }


def get_recent_traces(limit: int = 50) -> list[dict]:
    conn = _get_conn()
    rows = conn.execute("""
        SELECT * FROM traces ORDER BY timestamp DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_latency_history(limit: int = 100) -> list[dict]:
    conn = _get_conn()
    rows = conn.execute("""
        SELECT timestamp, latency_ms, llm_ms, vector_ms, bm25_ms, rerank_ms
        FROM traces ORDER BY timestamp DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]


def get_eval_history(limit: int = 20) -> list[dict]:
    conn = _get_conn()
    rows = conn.execute("""
        SELECT * FROM eval_runs ORDER BY timestamp DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_cost_history(limit: int = 100) -> list[dict]:
    conn = _get_conn()
    rows = conn.execute("""
        SELECT timestamp, cost_usd,
               SUM(cost_usd) OVER (ORDER BY timestamp) as cumulative_cost
        FROM traces ORDER BY timestamp DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]


def clear_traces():
    conn = _get_conn()
    conn.execute("DELETE FROM traces")
    conn.execute("DELETE FROM eval_runs")
    conn.commit()
    conn.close()
