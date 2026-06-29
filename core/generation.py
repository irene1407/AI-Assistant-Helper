"""
Generation layer: loads prompts from YAML and generates citation-grounded answers.
Optimized for low latency by removing the extra LLM sufficiency check.
"""

import re
import time
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).parent.parent

with open(BASE_DIR / "config" / "prompts.yaml") as f:
    _cfg = yaml.safe_load(f)

SYSTEM_PROMPT = _cfg["system_prompt"]
RAG_TEMPLATE = _cfg["rag_template"]

DEFAULT_MODEL = _cfg["thresholds"]["ollama_model"]

INSUFFICIENT_RESPONSE = "Evidence insufficient to answer this query safely."


def _get_llm(model: str):
    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=model,
        temperature=0,
        num_ctx=2048,
        num_predict=70,
    )


def _format_context(chunks: list[dict]) -> str:
    lines = []

    for c in chunks:
        meta = c.get("metadata", {})

        src = meta.get("source", "unknown")
        cid = meta.get("chunk_id", "?")

        lines.append(
            f"[Source: {src}, Chunk #{cid}]\n{c['text']}"
        )

    return "\n\n---\n\n".join(lines)


def _extract_citations(text: str) -> list[str]:
    pattern = r"\[Source:\s*([^,\]]+),\s*Chunk\s*#(\d+)\]"

    matches = re.findall(pattern, text)

    return [
        f"[Source: {src.strip()}, Chunk #{cid}]"
        for src, cid in matches
    ]


def _count_tokens_approx(text: str) -> int:
    return max(1, len(text) // 4)


def generate(
    query: str,
    retrieved_chunks: list[dict],
    model: str = DEFAULT_MODEL,
    skip_sufficiency_check: bool = False,
) -> dict:

    t_start = time.perf_counter()

    timings = {}

    if not retrieved_chunks:
        return {
            "query": query,
            "response": INSUFFICIENT_RESPONSE,
            "citations": [],
            "context": "",
            "prompt": "",
            "tokens_input": 0,
            "tokens_output": 0,
            "latency_ms": 0,
            "timings": {},
            "refused": True,
            "error": None,
            "model": model,
            "prompt_version": _cfg.get("version", "1.0.0"),
        }

    context = _format_context(retrieved_chunks)

    prompt_text = RAG_TEMPLATE.format(
        context=context,
        query=query
    )

    tokens_input = _count_tokens_approx(
        SYSTEM_PROMPT + prompt_text
    )

    try:
        from langchain_core.messages import (
            SystemMessage,
            HumanMessage,
        )

        llm = _get_llm(model)

        t_llm = time.perf_counter()

        response = llm.invoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=prompt_text),
            ]
        )

        timings["llm_ms"] = round(
            (time.perf_counter() - t_llm) * 1000,
            1
        )

        answer = response.content.strip()

    except Exception as e:
        return {
            "query": query,
            "response": "",
            "citations": [],
            "context": context,
            "prompt": prompt_text,
            "tokens_input": tokens_input,
            "tokens_output": 0,
            "latency_ms": round(
                (time.perf_counter() - t_start) * 1000,
                1
            ),
            "timings": timings,
            "refused": False,
            "error": str(e),
            "model": model,
            "prompt_version": _cfg.get("version", "1.0.0"),
        }

    citations = _extract_citations(answer)

    tokens_output = _count_tokens_approx(answer)

    sentence_count = max(
        1,
        len(
            [
                s
                for s in answer.split(".")
                if s.strip()
            ]
        ),
    )

    citation_coverage = min(
        1.0,
        len(citations) / sentence_count,
    )

    total_ms = round(
        (time.perf_counter() - t_start) * 1000,
        1
    )

    return {
        "query": query,
        "response": answer,
        "citations": citations,
        "context": context,
        "prompt": prompt_text,
        "tokens_input": tokens_input,
        "tokens_output": tokens_output,
        "cost_usd": 0.0,
        "latency_ms": total_ms,
        "timings": timings,
        "refused": answer.strip() == INSUFFICIENT_RESPONSE,
        "error": None,
        "citation_coverage": citation_coverage,
        "model": model,
        "prompt_version": _cfg.get("version", "1.0.0"),
    }