from groq import Groq
from backend.config import GROQ_API_KEY, GROQ_MODEL
import json

client = Groq(api_key=GROQ_API_KEY)

class EvaluatorAgent:
    """
    Objective : Score the generated answer for quality.
    Input     : query, answer, retrieved chunks
    Output    : {faithfulness: float, answer_relevance: float}
    """
    def evaluate(self, query: str, answer: str, chunks: list) -> dict:
        context = "\n".join([c["text"] for c in chunks])
        prompt = f"""Score this RAG response. Return only valid JSON.

Context: {context[:2000]}
Question: {query}
Answer: {answer}

Return:
{{
  "faithfulness": <0.0-1.0, is every claim supported by context?>,
  "answer_relevance": <0.0-1.0, does answer address the question?>
}}"""
        try:
            resp = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=100,
            )
            raw = resp.choices[0].message.content.strip()
            # strip markdown fences if present
            raw = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(raw)
        except Exception:
            return {"faithfulness": 0.0, "answer_relevance": 0.0}
