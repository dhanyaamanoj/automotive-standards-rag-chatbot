from fastapi import APIRouter
from pydantic import BaseModel
from backend.agents import orchestrator

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str
    query: str

class ChatResponse(BaseModel):
    session_id: str
    answer: str
    citations: list
    scores: dict
    query_type: str

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    result = orchestrator.run(req.session_id, req.query)
    return ChatResponse(
        session_id=req.session_id,
        answer=result["answer"],
        citations=result["citations"],
        scores=result["scores"],
        query_type=result["query_type"],
    )
