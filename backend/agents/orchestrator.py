from langgraph.graph import StateGraph, END
from backend.agents.state import AgentState
from backend.agents.retriever import RetrieverAgent
from backend.agents.generator import GeneratorAgent
from backend.agents.evaluator import EvaluatorAgent
from backend.memory.short_term import ShortTermMemory
from backend.memory.long_term import LongTermMemory
from backend.config import GREETINGS, OUT_OF_SCOPE_KEYWORDS

retriever  = RetrieverAgent()
generator  = GeneratorAgent()
evaluator  = EvaluatorAgent()
stm        = ShortTermMemory()
ltm        = LongTermMemory()

# ── classifier node ──────────────────────────────────────────
def classify_node(state: AgentState) -> AgentState:
    q = state["query"].lower().strip()
    words = set(q.split())
    if words & GREETINGS or len(words) <= 2:
        state["query_type"] = "chitchat"
    elif any(kw in q for kw in OUT_OF_SCOPE_KEYWORDS):
        state["query_type"] = "out_of_scope"
    else:
        state["query_type"] = "document_query"
    return state

# ── chitchat response node ───────────────────────────────────
def chitchat_node(state: AgentState) -> AgentState:
    state["answer"] = (
        "Hello! I'm the AIS Standards Assistant. I can answer questions "
        "from ARAI Automotive Industry Standard documents. What would you like to know?"
    )
    state["citations"] = []
    state["scores"] = {}
    return state

# ── out-of-scope response node ───────────────────────────────
def out_of_scope_node(state: AgentState) -> AgentState:
    state["answer"] = (
        "I'm designed specifically to answer questions from ARAI Automotive "
        "Industry Standards documents. I can't help with this topic. "
        "Try asking something like: 'What are the speed limiter requirements in AIS-018?'"
    )
    state["citations"] = []
    state["scores"] = {}
    return state

# ── retriever node ───────────────────────────────────────────
def retrieve_node(state: AgentState) -> AgentState:
    chunks = retriever.retrieve(state["query"])
    state["retrieved_chunks"] = chunks
    return state

# ── generator node ───────────────────────────────────────────
def generate_node(state: AgentState) -> AgentState:
    chunks = state["retrieved_chunks"]
    print(f"[Orchestrator] generating answer for session={state['session_id']} query={state['query']!r} using {len(chunks)} chunks")
    for i, chunk in enumerate(chunks, 1):
        meta = chunk.get("metadata", {})
        std_id = meta.get("std_id", "unknown")
        clause_id = meta.get("clause_id", "unknown")
        score = chunk.get("score", None)
        text = chunk.get("text", "")
        snippet = text.replace("\n", " ")[:150]
        print(
            f"  [{i}] std_id={std_id} clause_id={clause_id} score={score} text={snippet!r}"
        )

    answer, citations = generator.generate(
        query=state["query"],
        chunks=chunks,
        memory=state["short_term_memory"]
    )
    state["answer"]    = answer
    state["citations"] = citations
    return state

# ── evaluator node ───────────────────────────────────────────
def evaluate_node(state: AgentState) -> AgentState:
    scores = evaluator.evaluate(
        query=state["query"],
        answer=state["answer"],
        chunks=state["retrieved_chunks"]
    )
    state["scores"] = scores
    return state

# ── save to memory node ──────────────────────────────────────
def save_memory_node(state: AgentState) -> AgentState:
    sid = state["session_id"]
    stm.add(sid, "user", state["query"])
    stm.add(sid, "assistant", state["answer"])
    ltm.save(sid, state["query"], state["answer"], state["citations"])
    return state

# ── routing logic ─────────────────────────────────────────────
def route_query(state: AgentState) -> str:
    return state["query_type"]  # chitchat | out_of_scope | document_query

# ── build the graph ───────────────────────────────────────────
def build_graph() -> StateGraph:
    g = StateGraph(AgentState)
    g.add_node("classify",    classify_node)
    g.add_node("chitchat",    chitchat_node)
    g.add_node("out_of_scope",out_of_scope_node)
    g.add_node("retrieve",    retrieve_node)
    g.add_node("generate",    generate_node)
    g.add_node("evaluate",    evaluate_node)
    g.add_node("save_memory", save_memory_node)

    g.set_entry_point("classify")
    g.add_conditional_edges("classify", route_query, {
        "chitchat":      "chitchat",
        "out_of_scope":  "out_of_scope",
        "document_query":"retrieve",
    })
    g.add_edge("chitchat",     "save_memory")
    g.add_edge("out_of_scope", "save_memory")
    g.add_edge("retrieve",     "generate")
    g.add_edge("generate",     "evaluate")
    g.add_edge("evaluate",     "save_memory")
    g.add_edge("save_memory",  END)
    return g.compile()

graph = build_graph()

def run(session_id: str, query: str) -> AgentState:
    initial: AgentState = {
        "session_id":        session_id,
        "query":             query,
        "query_type":        "",
        "retrieved_chunks":  [],
        "answer":            "",
        "citations":         [],
        "scores":            {},
        "short_term_memory": stm.get(session_id),
        "error":             None,
    }
    return graph.invoke(initial)
