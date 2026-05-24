from sentence_transformers import SentenceTransformer
from backend.config import EMBEDDING_MODEL

class Embedder:
    """Singleton embedding model — loaded once, reused everywhere."""
    _model = None

    def __init__(self):
        if Embedder._model is None:
            Embedder._model = SentenceTransformer(EMBEDDING_MODEL)

    def encode(self, texts: list) -> list:
        if not texts:
            return []
        vecs = Embedder._model.encode(texts, show_progress_bar=False)
        return vecs.tolist()
