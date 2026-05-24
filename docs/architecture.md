# AIS Chatbot — Architecture & File Guide

## What each file does

### backend/config.py
Central config: all env vars, model names, paths, ChromaDB settings.
Single source of truth — no hardcoded values anywhere else.

### backend/main.py
FastAPI app entry. Mounts all routers, serves static PDFs,
configures CORS for Next.js frontend.

### backend/agents/state.py
LangGraph AgentState TypedDict — the shared object passed between
all nodes in the graph. Contains: session_id, query, query_type,
retrieved_chunks, answer, citations, scores, short_term_memory.

### backend/agents/orchestrator.py
LangGraph StateGraph definition. Wires all nodes:
classify → retrieve → generate → evaluate → format_response.
Also handles chitchat and out_of_scope branches directly.

### backend/agents/retriever.py
RetrieverAgent: calls hybrid_retriever, re-ranks results,
returns top-K chunks with metadata (std_id, clause, page).

### backend/agents/generator.py
GeneratorAgent: builds prompt with retrieved context + short-term
memory, calls Groq llama-3.3-70b-versatile, returns grounded answer.

### backend/agents/evaluator.py
EvaluatorAgent: uses RAGAS or prompt-based scoring to measure
faithfulness and answer relevance. Flags uncited claims.

### backend/agents/ingestion.py
IngestionAgent: orchestrates the full PDF → ChromaDB pipeline.
Called once by scripts/ingest.py, not during chat.

### backend/memory/short_term.py
ShortTermMemory: simple list-based store per session_id.
Keeps last N (default 6) message turns in memory.
Cleared when session ends or explicitly reset.

### backend/memory/long_term.py
LongTermMemory: ChromaDB collection "conversation_memory".
Saves every completed Q&A with session_id + timestamp.
Used by SessionSidebar to show past sessions.

### backend/tools/pdf_parser.py
Uses PyMuPDF (fitz) to extract text page by page.
Preserves page numbers. Detects if doc is amendment-only
by scanning first page for "Amendment No." pattern.

### backend/tools/structure_detector.py
Detects document hierarchy: Parts, Clauses, Definitions,
Tables, Appendices, Annexures. Returns a document tree dict
that chunker uses to decide strategy per section.

### backend/tools/chunker.py
Routes each section to the right chunking strategy:
- clause_chunk(): one chunk per leaf clause
- definition_chunk(): one chunk per definition term
- table_chunk(): whole table as one chunk
- summary_chunk(): one per Part/major section
Attaches full metadata to every chunk.

### backend/tools/embedder.py
Loads sentence-transformers all-mpnet-base-v2 once.
Provides encode() method used by vector_store and retriever.

### backend/tools/vector_store.py
ChromaDB wrapper. Two collections:
- "ais_documents": all document chunks
- "conversation_memory": Q&A history
Handles upsert, query, and amendment deduplication.

### backend/tools/bm25_index.py
BM25 keyword index using rank_bm25 library.
Built from the same chunks stored in ChromaDB.
Pickled to disk so it survives server restarts.

### backend/tools/hybrid_retriever.py
Combines semantic (ChromaDB) and keyword (BM25) scores.
Formula: 0.6 * semantic_score + 0.4 * bm25_score.
Returns top-K chunks sorted by combined score.

### backend/evaluation/synthetic_qa.py
Generates 50 question-answer pairs from loaded documents
using the LLM. Covers easy/medium/hard and
factual/reasoning/multi-hop types.

### backend/evaluation/run_eval.py
Runs all 50 QA pairs through the full pipeline,
captures retrieved context + generated response,
computes Precision@K, Recall@K, MRR, Faithfulness, Relevance.

### backend/evaluation/metrics.py
Pure functions: compute_precision_at_k, compute_recall_at_k,
compute_mrr, compute_faithfulness, compute_answer_relevance.

### backend/api/chat.py
POST /api/chat — main chat endpoint.
Accepts {session_id, query}, runs LangGraph graph,
returns {answer, citations, scores, session_id}.

### backend/api/sessions.py
GET /api/sessions — returns all past sessions from long-term memory.
GET /api/sessions/{id} — returns full message history for a session.
DELETE /api/sessions/{id} — clears a session.

### backend/api/documents.py
GET /api/documents — lists all ingested PDFs with metadata.
GET /api/documents/{std_id}/chunks — lists chunks for a standard.

### backend/api/evaluation.py
GET /api/evaluation/results — returns latest eval metrics.
POST /api/evaluation/run — triggers a fresh evaluation run.

---

### frontend/types/index.ts
All TypeScript interfaces: Message, Citation, Session,
Chunk, EvalResult, DocumentMeta.

### frontend/lib/api.ts
All fetch calls to FastAPI backend. Functions:
sendMessage(), getSessions(), getSession(),
getDocuments(), getEvalResults().

### frontend/lib/utils.ts
Helpers: formatTimestamp(), truncateText(), cn() for classnames.

### frontend/app/page.tsx
Redirects to /chat/new — entry point.

### frontend/app/layout.tsx
Root layout with fonts, global styles, metadata.

### frontend/app/chat/[sessionId]/page.tsx
Main chat page. Renders ChatWindow + SessionSidebar + DocumentPanel.
sessionId="new" creates a fresh UUID session.

### frontend/app/dashboard/page.tsx
Evaluation dashboard. Shows metric cards + QATable + EvalChart.
Fetches from GET /api/evaluation/results.

### frontend/app/documents/page.tsx
Lists all loaded AIS documents with their chunk counts,
amendment status, and a link to view source PDF.

### frontend/components/chat/ChatWindow.tsx
Main chat area. Manages messages state, calls sendMessage(),
handles streaming response display.

### frontend/components/chat/MessageBubble.tsx
Renders one message. AI messages show GroundedBadge + SourceChips.
User messages show plain bubble.

### frontend/components/chat/SourceChip.tsx
Clickable citation chip. Displays "AIS-018 p.8 →".
onClick: opens PDF at page AND updates DocumentPanel state.

### frontend/components/chat/TypingIndicator.tsx
Animated 3-dot pulse while waiting for AI response.

### frontend/components/chat/SessionSidebar.tsx
Left panel. Fetches sessions from GET /api/sessions.
Shows session title (first query truncated) + date.
Click restores full conversation.

### frontend/components/chat/DocumentPanel.tsx
Right panel. Shows highlighted clause text, related standards,
and RAGAS scores for the last AI response.
Populated when user clicks a SourceChip.

### frontend/components/evaluation/MetricCard.tsx
Single metric display: label + value + color based on threshold.

### frontend/components/evaluation/QATable.tsx
Table of 50 test questions with scores per row.
Sortable by faithfulness / relevance.

### frontend/components/evaluation/EvalChart.tsx
Bar chart (Recharts) showing metric scores across question types.

### frontend/components/ui/Badge.tsx
Reusable badge: variant = "grounded" | "warning" | "info".

### frontend/components/ui/Spinner.tsx
Loading spinner used during ingestion and eval runs.

---

### scripts/ingest.py
Run once: python scripts/ingest.py
Reads all PDFs from backend/data/raw_pdfs/,
runs IngestionAgent, builds ChromaDB + BM25 index.

### scripts/generate_qa.py
Generates synthetic_qa.csv of 50 Q&A pairs.

### scripts/run_eval.py
Runs evaluation, saves results to eval_results.json.
