# AIS Standards Chatbot — Project Documentation

**Project:** Multi-Agent RAG Chatbot System  
**Dataset:** ARAI Automotive Industry Standards (AIS) PDFs  

## Results

| Metric | Score |
|--------|-------|
| Faithfulness | **0.752** |
| Answer Relevance | **0.800** |
| Recall@5 | **0.800** |
| MRR | **0.720** |
| Precision@5 | 0.160 |

> **Key insight:** The retriever finds the right chunks (Recall=0.80, MRR=0.72), but includes extra irrelevant ones (Precision=0.16). Adding metadata filtering is the highest-impact next step.

---

## Architecture

```
User Query
    │
    ▼
FastAPI  →  OrchestratorAgent (LangGraph StateGraph)
                │
                ├── chitchat       → direct reply
                ├── out_of_scope   → redirect reply
                └── document_query →
                        RetrieverAgent   (hybrid: ChromaDB + BM25)
                        GeneratorAgent   (Llama-3.3-70B, grounded)
                        EvaluatorAgent   (Llama-3.1-8B, LLM-as-judge)
                        MemorySaver      (ChromaDB long-term store)
```

**Shared state** flows through every node as a typed `AgentState`:
`session_id · query · query_type · retrieved_chunks · answer · citations · scores · short_term_memory`

---

## The Five Agents

| Agent | File | Responsibility |
|-------|------|---------------|
| **OrchestratorAgent** *(mandatory)* | `agents/orchestrator.py` | LangGraph coordinator. Classifies query, routes pipeline, expands acronyms (SLD → "Speed Limitation Device AIS-018"), manages retry. |
| **RetrieverAgent** | `agents/retriever.py` | Calls HybridRetriever. Applies +0.3 score boost when a specific standard is named in the query. |
| **GeneratorAgent** | `agents/generator.py` | Calls Groq Llama-3.3-70B at temp=0.1. System prompt enforces context-only answering with inline citations. |
| **EvaluatorAgent** | `agents/evaluator.py` | Scores faithfulness + relevance in one Groq call using Llama-3.1-8B (separate rate-limit bucket). |
| **IngestionAgent** | `agents/ingestion.py` | Offline pipeline: PDF → parse → structure detect → chunk → embed → upsert. Run once. |

### Generator Grounding Prompt
```
Answer ONLY based on the provided context.
ALWAYS start with: "According to [STD_ID], Clause [X.X.X],"
If context is insufficient: "I could not find this information in the loaded AIS documents."
```

---

## Memory Design

| Type | Implementation | Purpose |
|------|---------------|---------|
| **Short-term** | In-memory dict, last 6 turns, keyed by `session_id` | Follow-up questions work without repeating the standard name |
| **Long-term** | ChromaDB `conversation_memory` collection (persistent) | Session history sidebar; only saves answers with quality_score ≥ 3 |

---

## Retrieval & Chunking

### Hybrid Retrieval
```
final_score = 0.6 × normalised_semantic + 0.4 × normalised_BM25
            + 0.3 boost  (if standard ID mentioned in query)
```
- **Semantic (ChromaDB):** Captures paraphrases — *"what happens when the speed limiter fails"*
- **BM25:** Exact term matching — *"Clause 5.7.3.4.2"*, *"AIS-018"*

### Clause-Aware Chunking
Fixed-size chunking was rejected — splitting *"5.7.3.4.2 Acceptance Criteria"* mid-sentence destroys meaning.

| Chunk Type | Strategy |
|-----------|----------|
| Clause | One chunk per leaf clause |
| Definition | One chunk per defined term |
| Table | Whole table as one chunk (rows are meaningless without headers) |
| Amendment | Full amendment page (legal text must not be truncated) |
| Appendix | Skipped (committee lists add retrieval noise) |

Every chunk carries: `std_id · clause_id · section_title · page_number · chunk_type · amendment_no`

---

## Evaluation

### Why K = 5
Tested K ∈ {3, 5, 8}. K=3 missed multi-clause answers. K=8 added noise and confused the generator. **K=5** gave the best precision-recall balance and kept context within ~5,000 chars.

### Metrics

| Metric | Definition |
|--------|-----------|
| **Precision@5** | `relevant chunks in top-5 / 5` — chunk-level relevance by clause_id match |
| **Recall@5** | `relevant chunks in top-5 / total relevant` |
| **MRR** | `mean(1 / rank of first relevant chunk)` — rewards early surfacing |
| **Faithfulness** | LLM-as-judge: every claim traceable to context (0→1) |
| **Answer Relevance** | LLM-as-judge: answer addresses the question (0→1) |

### Results by Question Type

| Type | Faithfulness | Relevance | MRR | Precision@5 | Recall@5 |
|------|:---:|:---:|:---:|:---:|:---:|
| Factual | 0.78 | 0.82 | 0.75 | 0.18 | 0.82 |
| Reasoning | 0.74 | 0.79 | 0.71 | 0.15 | 0.78 |
| Multi-hop | 0.71 | 0.76 | 0.68 | 0.12 | 0.74 |

### Sample Q&A

**Q:** *"What is the maximum height of the bottom edge of a rain flap from the ground?"*  
**A:** According to AIS-013 (Rev.1):2014, Clause 6.3.3, the maximum height shall not exceed 200mm (300mm for the last axle where the outer valance radius ≤ tyre radius).  
→ Faithfulness: 1.0 | Relevance: 1.0

**Q:** *"What EMC requirement was added to AIS-018 by Amendment No.5?"*  
**A:** Amendment No.5 (December 2017) to AIS-018:2001 added Clause 4.11 — the Speed Limitation Device must now conform to AIS:004 (Part 3) EMC requirements.  
→ Faithfulness: 0.93 | Relevance: 0.89

---

## System Improvements Log

| # | Area | What Changed | Impact |
|---|------|-------------|--------|
| 1 | Ingestion | Rewrote `structure_detector.py` regex for clause extraction | AIS-018 chunks now store correct clause_id |
| 2 | Retrieval | Added +0.3 score boost for standard-specific queries | Standard-specific queries no longer surface wrong documents |
| 3 | Retrieval | Query expansion for acronyms (SLD, SLF, COP, GVW) | Acronym-only queries retrieve correct standard |
| 4 | Ingestion | Removed 800-char truncation on amendment text | Amendment BM25 score: 0.5 → 22.3 |
| 5 | Evaluation | Combined faithfulness + relevance into one LLM call | Full 50-question eval completes within rate limits |
| 6 | Evaluation | Fixed synthetic QA to exclude cover page chunks | Precision@5: 0.05 → 0.16 |
| 7 | Retrieval | Tuned hybrid weights to 0.6/0.4 semantic/BM25 | Hybrid outperforms either method alone |
| 8 | Generator | Explicit grounding instruction in system prompt | Faithfulness: ~0.55 → 0.752 |
| 9 | Chunking | Rewrote clause detection regex | Recall@5: 0.24 → 0.800 |

---

## Tech Stack

| Component | Choice | Why |
|-----------|--------|-----|
| LLM | Groq llama-3.3-70b-versatile | ~300 tok/s, 128K context, free tier |
| Eval LLM | Groq llama-3.1-8b-instant | Separate rate-limit bucket; 8B sufficient for scoring |
| Embeddings | all-mpnet-base-v2 | Top MTEB semantic similarity; runs locally, no API cost |
| Vector DB | ChromaDB | Zero-config, persistent, supports metadata filtering |
| Keyword | BM25 (rank-bm25) | Exact clause number and standard ID matching |
| Orchestration | LangGraph | Typed shared state, conditional routing, audit trace |
| Backend | FastAPI + Uvicorn | Async, auto-docs at /docs |
| Frontend | Next.js 14 + React 18 | 3-panel chat UI, session sidebar, eval dashboard |
| PDF Parsing | PyMuPDF (fitz) | Best table/layout extraction for technical PDFs |

---

## Quick Start

```bash
# 1. Clone & install
git clone https://github.com/YOUR_USERNAME/ais-chatbot.git && cd ais-chatbot
python -m venv rag-venv && source rag-venv/bin/activate   # Windows: rag-venv\Scripts\activate
pip install -r backend/requirements.txt

# 2. Configure
cp .env.example .env   # add GROQ_API_KEY=gsk_xxxx...

# 3. Add PDFs & ingest (one-time, 2-5 min)
# Place 15-20 AIS PDFs in: backend/data/raw_pdfs/
python scripts/ingest.py

# 4. Start backend
uvicorn backend.main:app --reload --port 8000

# 5. Start frontend (new terminal)
cd frontend && npm install && npm run dev
# → http://localhost:3000

# 6. Run evaluation
python scripts/generate_qa.py   # generate 50 Q&A pairs
python scripts/run_eval.py      # full eval (~7 min)
# Results: backend/data/eval_results.json  |  docs/sample_qa_50.csv
```

### Environment Variables

| Variable | Example |
|----------|---------|
| `GROQ_API_KEY` | `gsk_xxxx...` |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` |
| `EMBEDDING_MODEL` | `all-mpnet-base-v2` |
| `CHROMA_PATH` | `backend/data/chroma_db` |
| `TOP_K` | `5` |
| `PDF_DIR` | `backend/data/raw_pdfs` |

### Common Issues

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'backend'` | Run uvicorn from project root, not from `backend/` |
| `TypeError: Client.__init__() got unexpected keyword argument 'proxies'` | `pip install --upgrade groq httpx` |
| `ECONNREFUSED` in frontend | Start backend first |
| `next.config.ts not supported` | Rename to `next.config.js`, use `module.exports` |

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Submit query → answer + citations + scores |
| `/api/sessions` | GET | List all past sessions |
| `/api/sessions/{id}` | GET / DELETE | Get or delete session history |
| `/api/documents` | GET | List ingested AIS docs with chunk counts |
| `/api/evaluation/results` | GET | Latest metrics + per-question results |
| `/api/evaluation/run` | POST | Trigger background evaluation run |

---

## Project Structure

```
ais-chatbot/
├── backend/
│   ├── agents/          # orchestrator · retriever · generator · evaluator · ingestion
│   ├── memory/          # short_term.py · long_term.py
│   ├── tools/           # pdf_parser · structure_detector · chunker · embedder
│   │                    # vector_store · bm25_index · hybrid_retriever
│   ├── evaluation/      # synthetic_qa · metrics · run_eval
│   ├── api/             # chat · sessions · documents · evaluation
│   └── data/            # raw_pdfs/  chroma_db/  eval_results.json
├── frontend/
│   ├── app/             # chat/[sessionId]  dashboard  documents
│   └── components/      # ChatWindow · MessageBubble · SourceChip
│                        # SessionSidebar · MetricCard · QATable · EvalChart
├── scripts/             # ingest.py · generate_qa.py · run_eval.py
├── docs/                # architecture.png · sample_qa_50.csv
├── .env.example
└── README.md
```

---

## What I'd Improve Next

| Fix | Expected Impact | Effort |
|-----|----------------|--------|
| Metadata filtering (extract AIS number from query) | Precision@5 +20–30% | Low |
| Cross-encoder reranker (ms-marco-MiniLM) | MRR +15–20% | Medium |
| Load cross-referenced standards (AIS-053 etc.) | Multi-hop recall +30% | Low |
| Table-to-natural-language conversion | Precision on spec queries +20% | Medium |
