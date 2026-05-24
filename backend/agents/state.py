from typing import TypedDict, Optional

class AgentState(TypedDict):
    session_id:        str
    query:             str
    query_type:        str           # chitchat | out_of_scope | document_query
    retrieved_chunks:  list          # list of chunk dicts from retriever
    answer:            str           # final answer text
    citations:         list          # [{std_id, clause_id, page, pdf_url}]
    scores:            dict          # {faithfulness, answer_relevance}
    short_term_memory: list          # last N {role, content} turns
    error:             Optional[str] # set if any agent fails
