from backend.tools.vector_store import VectorStore
from backend.tools.bm25_index import BM25Index
from backend.tools.embedder import Embedder
from backend.config import TOP_K, SEMANTIC_WEIGHT, BM25_WEIGHT

class HybridRetriever:
    """
    Combines ChromaDB semantic search + BM25 keyword search.
    Formula: 0.6 * semantic_score + 0.4 * bm25_score (normalised)
    """
    def __init__(self):
        self.store   = VectorStore()
        self.bm25    = BM25Index()
        self.embedder= Embedder()
        self.bm25.load()

    def search(self, query: str, k: int = TOP_K) -> list:
        # Check if query mentions a specific standard
        import re
        std_filter = re.search(r"AIS[-\s]?(\d+)", query.upper())
        target_std = f"AIS-{std_filter.group(1).zfill(3)}" if std_filter else None

        qvec      = self.embedder.encode([query])[0]
        sem_hits  = self.store.query(qvec, k=k*2)
        bm25_hits = self.bm25.search(query, k=k*2)

        combined  = {}
        max_sem   = max((h["score"] for h in sem_hits),  default=1)
        max_bm25  = max((h["score"] for h in bm25_hits), default=1)

        for h in sem_hits:
            cid = self._chunk_id(h)
            combined.setdefault(cid, {"chunk": h, "sem": 0.0, "bm25": 0.0})
            combined[cid]["sem"] = h["score"] / (max_sem or 1)

        for h in bm25_hits:
            cid = self._chunk_id(h)
            combined.setdefault(cid, {"chunk": h, "sem": 0.0, "bm25": 0.0})
            combined[cid]["bm25"] = h["score"] / (max_bm25 or 1)

        def final_score(x):
            base = SEMANTIC_WEIGHT * x["sem"] + BM25_WEIGHT * x["bm25"]
            # Boost chunks from the specifically mentioned standard
            if target_std and x["chunk"].get("metadata",{}).get("std_id") == target_std:
                base += 0.3
            return base

        ranked = sorted(combined.values(), key=final_score, reverse=True)
        return [r["chunk"] for r in ranked[:k]]

    # def search(self, query: str, k: int = TOP_K) -> list:
    #     # Semantic search
    #     qvec      = self.embedder.encode([query])[0]
    #     sem_hits  = self.store.query(qvec, k=k*2)

    #     # BM25 keyword search
    #     bm25_hits = self.bm25.search(query, k=k*2)

    #     # Merge by chunk id
    #     combined  = {}

    #     max_sem   = max((h["score"] for h in sem_hits),  default=1)
    #     max_bm25  = max((h["score"] for h in bm25_hits), default=1)

    #     for h in sem_hits:
    #         cid = self._chunk_id(h)
    #         combined.setdefault(cid, {"chunk": h, "sem": 0.0, "bm25": 0.0})
    #         combined[cid]["sem"] = h["score"] / (max_sem or 1)

    #     for h in bm25_hits:
    #         cid = self._chunk_id(h)
    #         combined.setdefault(cid, {"chunk": h, "sem": 0.0, "bm25": 0.0})
    #         combined[cid]["bm25"] = h["score"] / (max_bm25 or 1)

    #     # Compute final score
    #     ranked = sorted(
    #         combined.values(),
    #         key=lambda x: SEMANTIC_WEIGHT * x["sem"] + BM25_WEIGHT * x["bm25"],
    #         reverse=True
    #     )
    #     return [r["chunk"] for r in ranked[:k]]

    def _chunk_id(self, hit: dict) -> str:
        m = hit.get("metadata", {})
        return f"{m.get('std_id')}-{m.get('clause_id')}-{m.get('page_number')}"
