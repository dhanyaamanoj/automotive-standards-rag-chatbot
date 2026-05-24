from groq import Groq
from backend.config import GROQ_API_KEY, GROQ_MODEL
from backend.tools.pdf_utils import get_pdf_url

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are an expert on ARAI Automotive Industry Standards (AIS).
Answer questions ONLY based on the provided document context.
Always cite the standard number and clause in your answer like:
  "According to AIS-018:2001, Clause 5.7.3.4.2, ..."
If the context does not contain the answer, say:
  "I could not find information on this in the loaded AIS documents."
Never hallucinate facts. Be precise and technical."""

class GeneratorAgent:
    """
    Objective : Generate a grounded answer from retrieved chunks.
    Input     : query, chunks, conversation memory
    Output    : (answer: str, citations: list)
    """
    def generate(self, query: str, chunks: list, memory: list) -> tuple:
        context = self._format_context(chunks)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for turn in memory[-6:]:            # last 6 turns for context
            messages.append(turn)
        messages.append({
            "role": "user",
            "content": f"Context from AIS documents:\n{context}\n\nQuestion: {query}"
        })

        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.1,               # low temp for factual answers
            max_tokens=1024,
        )
        answer = resp.choices[0].message.content
        citations = self._extract_citations(chunks)
        return answer, citations

    def _format_context(self, chunks: list) -> str:
        parts = []
        for i, c in enumerate(chunks, 1):
            m = c.get("metadata", {})
            parts.append(
                f"[{i}] {m.get('std_id','')} Cl.{m.get('clause_id','')} "
                f"(p.{m.get('page_number','?')}):\n{c['text']}"
            )
        return "\n\n".join(parts)

    def _extract_citations(self, chunks: list) -> list:
        seen, citations = set(), []
        for c in chunks:
            m = c.get("metadata", {})
            key = f"{m.get('std_id')}-{m.get('clause_id')}-{m.get('page_number')}"
            if key not in seen:
                seen.add(key)
                page_number = m.get('page_number', 1)
                citations.append({
                    "std_id":    m.get('std_id', ""),
                    "clause_id": m.get('clause_id', ""),
                    "page":      page_number,
                    "pdf_url":   get_pdf_url(m.get('std_id', ""), page_number),
                })
        return citations
