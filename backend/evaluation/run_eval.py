import json, os, time, sys
from backend.agents import orchestrator
from backend.evaluation.metrics import (
    compute_both_metrics,
    compute_precision_at_k,
    compute_recall_at_k,
    compute_mrr
)

QA_PATH      = "backend/data/synthetic_qa.json"
RESULTS_PATH = "backend/data/eval_results.json"

# Allow running with fewer questions: python scripts/run_eval.py 25
SAMPLE_SIZE = 25

def run_evaluation():
    if not os.path.exists(QA_PATH):
        print("Run generate_qa.py first")
        return

    with open(QA_PATH) as f:
        qa_pairs = json.load(f)[:SAMPLE_SIZE]

    print(f"Running evaluation on {len(qa_pairs)} questions...")
    rows = []

    for i, qa in enumerate(qa_pairs):
        print(f"Evaluating {i+1}/{len(qa_pairs)}: {qa['question'][:60]}")

        # Fresh session per question — avoids memory contamination
        state = orchestrator.run(f"eval_{i}", qa["question"])

        chunks  = state.get("retrieved_chunks", [])
        answer  = state.get("answer", "")
        context = "\n".join(c["text"] for c in chunks)

        # Retrieval metrics — pure math, no LLM calls
        relevant = {qa.get("source_clause", "")}
        ret_ids  = [c["metadata"].get("clause_id", "") for c in chunks]
        prec     = compute_precision_at_k(ret_ids, relevant)
        rec      = compute_recall_at_k(ret_ids, relevant)
        mrr      = compute_mrr(ret_ids, relevant)

        # Generation metrics — single combined LLM call (not 2 separate calls)
        scores = compute_both_metrics(qa["question"], answer, context)
        faith  = scores.get("faithfulness", 0.0)
        relev  = scores.get("answer_relevance", 0.0)

        rows.append({
            "query":             qa["question"],
            "expected":          qa.get("answer", ""),
            "generated":         answer,
            "retrieved_context": context[:500],
            "faithfulness":      round(faith, 3),
            "answer_relevance":  round(relev, 3),
            "precision_at_k":    round(prec, 3),
            "recall_at_k":       round(rec, 3),
            "mrr":               round(mrr, 3),
            "type":              qa.get("type", ""),
            "difficulty":        qa.get("difficulty", ""),
        })

        time.sleep(1.5)  # avoid rate limits

        # Extra pause every 10 questions
        if (i + 1) % 10 == 0:
            print(f"  Pausing 15s to reset rate limit window...")
            time.sleep(15)

    # Summary
    avg = lambda key: round(sum(r[key] for r in rows) / len(rows), 3)
    summary = {
        "total_questions":     len(rows),
        "avg_faithfulness":    avg("faithfulness"),
        "avg_answer_relevance":avg("answer_relevance"),
        "avg_precision_at_5":  avg("precision_at_k"),
        "avg_recall_at_5":     avg("recall_at_k"),
        "avg_mrr":             avg("mrr"),
        "rows":                rows,
    }

    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(summary, f, indent=2)

    # Also save as CSV for submission
    import csv
    csv_path = "docs/sample_qa_50.csv"
    os.makedirs("docs", exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nEval done → {RESULTS_PATH}")
    print(f"CSV saved → {csv_path}")
    print(f"Faithfulness:    {summary['avg_faithfulness']}")
    print(f"Relevance:       {summary['avg_answer_relevance']}")
    print(f"Precision@5:     {summary['avg_precision_at_5']}")
    print(f"Recall@5:        {summary['avg_recall_at_5']}")
    print(f"MRR:             {summary['avg_mrr']}")

if __name__ == "__main__":
    run_evaluation()