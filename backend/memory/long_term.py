import uuid
import time
import json
import chromadb
from backend.config import CHROMA_PATH, CHROMA_MEMORY_COLLECTION

class LongTermMemory:
    """
    Persistent Q&A history in ChromaDB.
    Each record: session_id, timestamp, query, answer, citations.
    Used to restore past sessions in the sidebar.
    """
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.col = self.client.get_or_create_collection(CHROMA_MEMORY_COLLECTION)

    def save(self, session_id: str, query: str, answer: str, citations: list):
        doc_id = f"{session_id}_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        self.col.add(
            documents=[f"Q: {query}\nA: {answer}"],
            metadatas=[{
                "session_id": session_id,
                "timestamp":  int(time.time()),
                "query":      query[:500],
                "answer":     answer[:1000],
                "citations":  json.dumps(citations),
            }],
            ids=[doc_id],
        )

    def get_sessions(self) -> list:
        """Return list of {session_id, title, timestamp} sorted by latest."""
        results = self.col.get(include=["metadatas"])
        sessions: dict = {}
        for meta in results["metadatas"]:
            sid = meta["session_id"]
            # Skip evaluation sessions (those starting with "eval_" or containing "eval").
            if sid.startswith("eval_") or "eval" in sid.lower():
                continue
            ts  = meta["timestamp"]
            if sid not in sessions or ts > sessions[sid]["timestamp"]:
                sessions[sid] = {
                    "session_id": sid,
                    "title":      meta["query"][:60],
                    "timestamp":  ts,
                }
        return sorted(sessions.values(), key=lambda x: -x["timestamp"])

    def get_history(self, session_id: str) -> list:
        """Return ordered Q&A pairs for a session."""
        results = self.col.get(
            where={"session_id": session_id},
            include=["metadatas"],
        )
        metas = sorted(results["metadatas"], key=lambda x: x["timestamp"])
        history = []
        for m in metas:
            history.append({"role": "user",      "content": m["query"]})
            history.append({"role": "assistant",  "content": m["answer"],
                            "citations": json.loads(m.get("citations","[]"))})
        return history

    def delete_session(self, session_id: str):
        results = self.col.get(where={"session_id": session_id})
        if results["ids"]:
            self.col.delete(ids=results["ids"])
