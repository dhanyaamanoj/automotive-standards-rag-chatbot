from fastapi import APIRouter, Query
from backend.agents.retriever import RetrieverAgent

router = APIRouter()
retriever = RetrieverAgent()

@router.get("/debug/chunks")
def debug_chunks(query: str = Query(..., description="The question to retrieve chunks for."), k: int = Query(5, description="Number of chunks to retrieve.")):
    """Return retrieval candidates for a query, including metadata and truncated text."""
    chunks = retriever.retrieve(query, k=k)
    debug_rows = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk.get("metadata", {})
        debug_rows.append({
            "rank": i,
            "std_id": meta.get("std_id", "unknown"),
            "clause_id": meta.get("clause_id", "unknown"),
            "page_number": meta.get("page_number", None),
            "score": chunk.get("score", None),
            "text_snippet": chunk.get("text", "")[:300].replace("\n", " "),
        })
    return {"query": query, "k": k, "chunks": debug_rows}
