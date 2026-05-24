from backend.tools.hybrid_retriever import HybridRetriever
from backend.config import TOP_K

class RetrieverAgent:
    """
    Objective : Find the most relevant chunks for a query.
    Input     : query (str)
    Output    : list of chunk dicts [{text, metadata, score}]
    """
    def __init__(self):
        self.retriever = HybridRetriever()

    def retrieve(self, query: str, k: int = TOP_K) -> list:
        chunks = self.retriever.search(query, k=k)
        print(f"[Retriever] query={query!r} k={k} returned {len(chunks)} chunks")
        for i, chunk in enumerate(chunks, 1):
            meta = chunk.get("metadata", {})
            std_id = meta.get("std_id", "unknown")
            clause_id = meta.get("clause_id", "unknown")
            score = chunk.get("score", None)
            text = chunk.get("text", "")
            snippet = text.replace("\n", " ")[:150]
            print(
                f"  [{i}] std_id={std_id} clause_id={clause_id} score={score} text={snippet!r}"
            )
        return chunks
