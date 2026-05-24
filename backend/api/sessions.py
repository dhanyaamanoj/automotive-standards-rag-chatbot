from fastapi import APIRouter
from backend.memory.long_term import LongTermMemory
from backend.memory.short_term import ShortTermMemory

router = APIRouter()
ltm = LongTermMemory()
stm = ShortTermMemory()

@router.get("/sessions")
def get_sessions():
    return ltm.get_sessions()

@router.get("/sessions/{session_id}")
def get_session(session_id: str):
    return ltm.get_history(session_id)

@router.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    ltm.delete_session(session_id)
    stm.clear(session_id)
    return {"status": "deleted"}
