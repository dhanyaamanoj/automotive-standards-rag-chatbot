import os
from dotenv import load_dotenv

load_dotenv()

# LLM
GROQ_API_KEY     = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL       = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Embeddings
EMBEDDING_MODEL  = os.getenv("EMBEDDING_MODEL", "all-mpnet-base-v2")

# ChromaDB
CHROMA_PATH               = os.getenv("CHROMA_PATH", "backend/data/chroma_db")
CHROMA_COLLECTION         = os.getenv("CHROMA_COLLECTION", "ais_documents")
CHROMA_MEMORY_COLLECTION  = os.getenv("CHROMA_MEMORY_COLLECTION", "conversation_memory")

# Retrieval
TOP_K             = int(os.getenv("TOP_K", 5))
SEMANTIC_WEIGHT   = float(os.getenv("SEMANTIC_WEIGHT", 0.6))
BM25_WEIGHT       = float(os.getenv("BM25_WEIGHT", 0.4))

# Paths
PDF_DIR           = os.getenv("PDF_DIR", "backend/data/raw_pdfs")
BM25_INDEX_PATH   = os.getenv("BM25_INDEX_PATH", "backend/data/bm25_index.pkl")

# Memory
SHORT_TERM_MAX_TURNS = 6

# Query types
QUERY_TYPES = ["chitchat", "out_of_scope", "document_query"]

GREETINGS = {
    "hi", "hello", "hey", "good morning", "good afternoon",
    "good evening", "thanks", "thank you", "bye", "goodbye", "ok", "okay"
}

OUT_OF_SCOPE_KEYWORDS = [
    "weather", "stock", "cricket", "football", "news",
    "recipe", "movie", "song", "politics", "covid"
]
