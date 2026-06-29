"""
Offline evaluation suite using a golden Q&A dataset.
Scores pipeline output via Ragas (Faithfulness + Answer Relevancy).
Implements a CI/CD gate: fails if faithfulness < threshold.
"""

import json
import sys
import time
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).parent.parent
GOLDEN_SET_PATH = BASE_DIR / "data" / "golden_set.json"

import yaml
with open(BASE_DIR / "config" / "prompts.yaml") as f:
    _cfg = yaml.safe_load(f)

FAITHFULNESS_THRESHOLD = _cfg["thresholds"]["faithfulness_min"]
DEFAULT_MODEL = _cfg["thresholds"]["ollama_model"]


def load_golden_set() -> list[dict]:
    with open(GOLDEN_SET_PATH) as f:
        return json.load(f)


def run_pipeline_on_question(question: str, model: str = DEFAULT_MODEL) -> dict:
    """Run the full RAG pipeline on a single question and return trace."""
    from core.retrieval import retrieve
    from core.generation import generate

    retrieval = retrieve(question)
    generation = generate(question, retrieval["reranked"], model=model, skip_sufficiency_check=True)
    return {
        "question": question,
        "answer": generation["response"],
        "contexts": [c["text"] for c in retrieval["reranked"]],
        "latency_ms": generation["latency_ms"],
        "refused": generation["refused"],
        "error": generation["error"],
    }


def evaluate_with_ragas(samples: list[dict], model: str = DEFAULT_MODEL) -> dict:
    """Score samples using Ragas metrics with Ollama as the judge LLM."""
    try:
        from ragas import evaluate, EvaluationDataset, SingleTurnSample
        from ragas.metrics import Faithfulness, ResponseRelevancy
        from langchain_ollama import ChatOllama
        from ragas.llms import LangchainLLMWrapper

        llm = LangchainLLMWrapper(ChatOllama(model=model, temperature=0))

        ragas_samples = []
        for s in samples:
            if s.get("error") or not s.get("answer"):
                continue
            ragas_samples.append(SingleTurnSample(
                user_input=s["question"],
                response=s["answer"],
                retrieved_contexts=s["contexts"],
            ))

        if not ragas_samples:
            return {"faithfulness": 0.0, "answer_relevancy": 0.0, "error": "No valid samples"}

        dataset = EvaluationDataset(samples=ragas_samples)
        metrics = [
            Faithfulness(llm=llm),
            ResponseRelevancy(llm=llm),
        ]
        result = evaluate(dataset=dataset, metrics=metrics)
        df = result.to_pandas()

        faithfulness = float(df["faithfulness"].mean()) if "faithfulness" in df else 0.0
        relevancy = float(df["answer_relevancy"].mean()) if "answer_relevancy" in df else 0.0

        return {
            "faithfulness": faithfulness,
            "answer_relevancy": relevancy,
            "sample_scores": df.to_dict(orient="records"),
            "error": None,
        }
    except ImportError as e:
        return {"faithfulness": 0.0, "answer_relevancy": 0.0, "error": f"Ragas import error: {e}"}
    except Exception as e:
        return {"faithfulness": 0.0, "answer_relevancy": 0.0, "error": str(e)}


def run_full_evaluation(
    model: str = DEFAULT_MODEL,
    progress_callback=None,
) -> dict:
    """
    Run the full evaluation suite against the golden dataset.
    Returns metrics and a CI/CD gate pass/fail verdict.
    """
    golden = load_golden_set()
    results = []
    errors = []

    for i, item in enumerate(golden):
        question = item["question"]
        if progress_callback:
            progress_callback(i, len(golden), question)
        try:
            result = run_pipeline_on_question(question, model=model)
            result["golden_answer"] = item.get("answer", "")
            results.append(result)
        except Exception as e:
            errors.append({"question": question, "error": str(e)})

    ragas_scores = evaluate_with_ragas(results, model=model)

    faithfulness = ragas_scores.get("faithfulness", 0.0)
    relevancy = ragas_scores.get("answer_relevancy", 0.0)
    gate_passed = faithfulness >= FAITHFULNESS_THRESHOLD

    from observability.tracker import log_eval_run
    log_eval_run(faithfulness, relevancy, results, model)

    return {
        "total_questions": len(golden),
        "answered": len([r for r in results if not r.get("refused")]),
        "refused": len([r for r in results if r.get("refused")]),
        "errors": len(errors),
        "faithfulness": round(faithfulness, 4),
        "answer_relevancy": round(relevancy, 4),
        "gate_passed": gate_passed,
        "faithfulness_threshold": FAITHFULNESS_THRESHOLD,
        "ragas_error": ragas_scores.get("error"),
        "sample_details": results,
        "pipeline_errors": errors,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run RAG evaluation suite")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Ollama model name")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print("  RAG PIPELINE EVALUATION SUITE")
    print(f"{'='*60}")
    print(f"  Model:               {args.model}")
    print(f"  Faithfulness gate:   >= {FAITHFULNESS_THRESHOLD}")
    print(f"{'='*60}\n")

    def progress(i, total, q):
        print(f"  [{i+1}/{total}] {q[:60]}...")

    result = run_full_evaluation(model=args.model, progress_callback=progress)

    print(f"\n{'='*60}")
    print("  EVALUATION RESULTS")
    print(f"{'='*60}")
    print(f"  Questions run:     {result['total_questions']}")
    print(f"  Answered:          {result['answered']}")
    print(f"  Refused:           {result['refused']}")
    print(f"  Errors:            {result['errors']}")
    print(f"  Faithfulness:      {result['faithfulness']:.4f}  (threshold: {FAITHFULNESS_THRESHOLD})")
    print(f"  Answer Relevancy:  {result['answer_relevancy']:.4f}")

    if result.get("ragas_error"):
        print(f"\n  ⚠  Ragas error: {result['ragas_error']}")

    gate = "✅  PASS" if result["gate_passed"] else "❌  FAIL — REGRESSION DETECTED"
    print(f"\n  CI/CD Gate: {gate}")
    print(f"{'='*60}\n")

    sys.exit(0 if result["gate_passed"] else 1)
