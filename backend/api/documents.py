from fastapi import APIRouter
from backend.tools.vector_store import VectorStore
from backend.tools.pdf_utils import get_pdf_url

router = APIRouter()
store = VectorStore()

@router.get("/documents")
def get_documents():
    chunks = store.get_all_chunks()
    docs: dict = {}
    for c in chunks:
        m = c["metadata"]
        sid = m.get("std_id", "unknown")
        if sid not in docs:
            docs[sid] = {"std_id": sid, "chunk_count": 0,
                         "chunk_types": set(), "is_amended": False}
        docs[sid]["chunk_count"] += 1
        docs[sid]["chunk_types"].add(m.get("chunk_type",""))
        if m.get("amendment_no"):
            docs[sid]["is_amended"] = True
    # Convert sets to lists for JSON serialisation
    result = []
    for d in docs.values():
        d["chunk_types"] = list(d["chunk_types"])
        d["pdf_url"] = get_pdf_url(d["std_id"], 1)
        result.append(d)
    return sorted(result, key=lambda x: x["std_id"])

@router.get("/documents/{std_id}/chunks")
def get_chunks(std_id: str):
    chunks = store.get_all_chunks()
    return [c for c in chunks if c["metadata"].get("std_id") == std_id]
