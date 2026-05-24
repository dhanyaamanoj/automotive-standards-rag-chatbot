import pickle
import os
from rank_bm25 import BM25Okapi
from backend.config import BM25_INDEX_PATH

class BM25Index:
    """
    Keyword search index over all ingested chunks.
    Pickled to disk so it survives server restarts.
    """
    def __init__(self):
        self.index  = None
        self.chunks = []     # parallel list matching index docs

    def build(self, texts: list, chunks: list):
        tokenized    = [t.lower().split() for t in texts]
        self.index   = BM25Okapi(tokenized)
        self.chunks  = chunks

    def save(self, path: str = BM25_INDEX_PATH):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump({"index": self.index, "chunks": self.chunks}, f)

    def load(self, path: str = BM25_INDEX_PATH):
        if not os.path.exists(path):
            return False
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.index  = data["index"]
        self.chunks = data["chunks"]
        return True

    def search(self, query: str, k: int = 5) -> list:
        if self.index is None:
            self.load()
        if self.index is None:
            return []
        tokens = query.lower().split()
        scores = self.index.get_scores(tokens)
        top_k  = sorted(enumerate(scores), key=lambda x: -x[1])[:k]
        results = []
        for idx, score in top_k:
            if score > 0:
                results.append({
                    "text":     self.chunks[idx]["text"],
                    "metadata": self.chunks[idx]["metadata"],
                    "score":    float(score),
                })
        return results
