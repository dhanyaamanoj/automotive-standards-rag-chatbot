import json, os
from groq import Groq
from backend.tools.vector_store import VectorStore
from backend.config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)
store  = VectorStore()

PROMPT = """You are an expert creating evaluation questions for an AIS automotive standards chatbot.
Given the following document chunk, generate {n} questions of type '{qtype}' at '{difficulty}' difficulty.
Return ONLY a JSON array of objects: [{{"question": "...", "answer": "...", "type": "{qtype}", "difficulty": "{difficulty}"}}]
No markdown, no extra text.

Document chunk:
{chunk}"""

def generate_qa(output_path: str = "backend/data/synthetic_qa.json", total: int = 50):
    chunks = store.get_all_chunks()
    if not chunks:
        print("No chunks found. Run ingestion first.")
        return

    configs = [
        {"qtype": "factual",    "difficulty": "easy",   "n": 20},
        {"qtype": "reasoning",  "difficulty": "medium",  "n": 20},
        {"qtype": "multi-hop",  "difficulty": "hard",    "n": 10},
    ]

    all_qa = []
    #chunk_pool = [c for c in chunks if c["metadata"].get("chunk_type") == "clause"]
    chunk_pool = [
        c for c in chunks
        if c["metadata"].get("chunk_type") in ("clause", "definition", "table")
        and len(c["text"]) > 200          # skip short cover page chunks
        and c["metadata"].get("clause_id", "") != ""  # must have a clause ID
        and not any(skip in c["text"].lower() for skip in [
            "status chart", "printed by", "automotive research association",
            "ministry of road", "on behalf of", "committee composition"
        ])]
    step = max(1, len(chunk_pool) // total)

    idx = 0
    for cfg in configs:
        generated = 0
        while generated < cfg["n"] and idx < len(chunk_pool):
            chunk = chunk_pool[idx]
            idx += step
            prompt = PROMPT.format(
                n=min(5, cfg["n"] - generated),
                qtype=cfg["qtype"],
                difficulty=cfg["difficulty"],
                chunk=chunk["text"][:1200],
            )
            try:
                resp = client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=800,
                )
                raw = resp.choices[0].message.content.strip()
                raw = raw.replace("```json","").replace("```","").strip()
                qa_list = json.loads(raw)
                for qa in qa_list:
                    qa["source_std"]    = chunk["metadata"].get("std_id","")
                    qa["source_clause"] = chunk["metadata"].get("clause_id","")
                    qa["source_page"]   = chunk["metadata"].get("page_number",1)
                    all_qa.append(qa)
                    generated += 1
                    if generated >= cfg["n"]:
                        break
            except Exception as e:
                print(f"  Error: {e}")
                continue

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(all_qa[:total], f, indent=2)
    print(f"Generated {len(all_qa[:total])} QA pairs → {output_path}")
    return all_qa[:total]
