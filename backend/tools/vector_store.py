import chromadb
from backend.config import CHROMA_PATH, CHROMA_COLLECTION

class VectorStore:
    """ChromaDB wrapper for AIS document chunks."""
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.col    = self.client.get_or_create_collection(
            CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"}
        )

    def upsert(self, chunks: list, embeddings: list):
        if not chunks:
            return
        self.col.upsert(
            ids        =[c["id"] for c in chunks],
            documents  =[c["text"] for c in chunks],
            embeddings =embeddings,
            metadatas  =[c["metadata"] for c in chunks],
        )

    def query(self, embedding: list, k: int = 5) -> list:
        res = self.col.query(
            query_embeddings=[embedding],
            n_results=k,
            include=["documents","metadatas","distances"],
        )
        results = []
        for doc, meta, dist in zip(
            res["documents"][0], res["metadatas"][0], res["distances"][0]
        ):
            results.append({
                "text":     doc,
                "metadata": meta,
                "score":    1 - dist,    # cosine distance → similarity
            })
        return results

    def get_all_chunks(self) -> list:
        res = self.col.get(include=["documents","metadatas"])
        return [
            {"text": doc, "metadata": meta}
            for doc, meta in zip(res["documents"], res["metadatas"])
        ]

    def count(self) -> int:
        return self.col.count()
