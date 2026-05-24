from groq import Groq
from backend.config import GROQ_API_KEY, GROQ_MODEL
import json

EVAL_MODEL = "llama-3.1-8b-instant"  # smaller and cheaper than the 70b used for generation

client = Groq(api_key=GROQ_API_KEY)

def compute_both_metrics(query: str, answer: str, context: str) -> dict:
    """
    Single LLM call for BOTH faithfulness and relevance.
    Saves 50 calls (1 call per question instead of 2).
    """
    prompt = f"""Rate this RAG response. Return ONLY valid JSON, no extra text.

Context: {context[:1500]}
Question: {query}
Answer: {answer[:500]}

Return exactly this JSON:
{{
  "faithfulness": <0.0-1.0, are all claims supported by context?>,
  "answer_relevance": <0.0-1.0, does answer address the question?>
}}"""
    try:
        resp = client.chat.completions.create(
            model=EVAL_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=60,   # tiny — just needs 2 numbers
        )
        raw = resp.choices[0].message.content.strip()
        raw = raw.replace("```json","").replace("```","").strip()
        return json.loads(raw)
    except Exception:
        return {"faithfulness": 0.0, "answer_relevance": 0.0}

# Keep these as pure math — NO LLM calls
def compute_precision_at_k(retrieved_ids: list, relevant_ids: set) -> float:
    if not retrieved_ids:
        return 0.0
    return sum(1 for r in retrieved_ids if r in relevant_ids) / len(retrieved_ids)

def compute_recall_at_k(retrieved_ids: list, relevant_ids: set) -> float:
    if not relevant_ids:
        return 0.0
    return sum(1 for r in retrieved_ids if r in relevant_ids) / len(relevant_ids)

def compute_mrr(retrieved_ids: list, relevant_ids: set) -> float:
    for rank, rid in enumerate(retrieved_ids, 1):
        if rid in relevant_ids:
            return 1.0 / rank
    return 0.0