# AIS Standards Chatbot — Multi-Agent RAG System

> AI-powered chatbot that answers questions from ARAI Automotive Industry Standard (AIS) documents using a Multi-Agent RAG architecture.

---

## 📹 Demo Video

**[Full demo on Google Drive](https://drive.google.com/file/d/1OBDI-h77dyYWeP46WvpPCvbv8xJVBoh4/view?usp=sharing)**

---

## Architecture Diagram

[System Architecture]

---

## System Flowchart

```
                        [ User Query ]
                               │
                               ▼
               ┌──────────────────────────────┐
               │      Orchestrator Agent       │──(Chitchat / Off-topic)──▶ [ Friendly Reply ]
               │    (Classifies & Routes)      │
               └──────────────────────────────┘
                               │
                               │  (AIS Documentation Query)
                               ▼
               ┌──────────────────────────────┐
               │       Retriever Agent         │
               │   • ChromaDB (Semantic)       │
               │   • BM25  (Keyword Match)     │
               └──────────────────────────────┘
                               │
                               ▼
                        [ Top-5 Chunks ]
                               │
                               ▼
               ┌──────────────────────────────┐
               │       Generator Agent         │ ◀── [ Short-Term Memory ]
               │    (Groq LLaMA 3.3 70B)       │      (Last 6 turns)
               └──────────────────────────────┘
                               │
                               ▼
                    [ Grounded Response ]
                               │
                               ▼
               ┌──────────────────────────────┐
               │       Evaluator Agent         │
               │   • Scores Faithfulness       │
               │   • Scores Relevance          │
               └──────────────────────────────┘
                               │
                               ▼
               ┌──────────────────────────────┐
               │       Long-Term Memory        │
               │  (Saves to Session History)   │
               └──────────────────────────────┘
                               │
                               ▼
                  [ Final Answer + Citations + Scores ]
```

---

## Overview

| Item | Detail |
|---|---|
| **LLM** | Groq `llama-3.3-70b-versatile` |
| **Embeddings** | `all-mpnet-base-v2` (local) |
| **Vector DB** | ChromaDB (persistent) |
| **Keyword Search** | BM25 via `rank-bm25` |
| **Agent Framework** | LangGraph StateGraph |
| **Backend** | FastAPI + Uvicorn |
| **Frontend** | Next.js 14 + React 18 |
| **PDF Parsing** | PyMuPDF (fitz) |

---

## Agent Roles

| Agent | Objective | Input | Output |
|---|---|---|---|
| **OrchestratorAgent** | Classify query and coordinate all agents via LangGraph | User query + session_id | Final response with citations |
| **RetrieverAgent** | Find relevant chunks using hybrid search | Query string | Top-K chunks with scores |
| **GeneratorAgent** | Generate grounded answers using Groq LLaMA | Query + chunks + memory | Answer text + citations |
| **EvaluatorAgent** | Score answer quality | Query + answer + context | Faithfulness + relevance |
| **IngestionAgent** | Process PDFs into vector store (offline) | PDF files | ChromaDB + BM25 index |

---

## Memory Design

| Type | Implementation | Purpose |
|---|---|---|
| **Short-term** | In-memory Python list per `session_id` | Holds last 6 turns — gives LLM conversation context |
| **Long-term** | ChromaDB `conversation_memory` collection | Persists all Q&A pairs — powers the session history sidebar |

---

## Retrieval Design

Hybrid retrieval combines two methods:

```
final_score = 0.6 × semantic_score  +  0.4 × BM25_score
```

- **Semantic (ChromaDB)** — captures meaning and paraphrases
- **Keyword (BM25)** — exact clause number and standard ID matching
- **Standard boost** — queries mentioning a specific standard (e.g. AIS-018) get +0.3 boost
- **Query expansion** — acronyms expanded before retrieval (SLD → "Speed Limitation Device AIS-018")

---

## Chunking Strategy

AIS documents have strict hierarchical clause structures. Fixed-size chunking destroys clause boundaries so we use clause-aware chunking:

| Section Type | Strategy | Reason |
|---|---|---|
| Clause | One chunk per leaf clause | Preserves full technical meaning |
| Definition | One chunk per defined term | Makes each term individually retrievable |
| Table | Whole table as one chunk | Rows are meaningless when split |
| Amendment | Full amendment text | Legal amendments must not be truncated |
| Summary | One per document | Answers high-level queries |

---

## K-Value Justification (K=5)

Evaluated K=3, K=5, and K=8:
**Conclusion:** K=5 captures enough context for multi-clause questions without introducing irrelevant noise that degrades generation quality.

---

## Evaluation Results

| Metric | Score | Interpretation |
|---|---|---|
| Faithfulness | 0.71 | 71% of claims grounded in retrieved context |
| Answer Relevance | 0.70 | 70% of answers directly address the question |
| Precision@5 | 0.05 | Low — caused by cover-page questions in synthetic QA (fixed after filtering) |
| Recall@5 | 0.24 | Correct chunks present but not always top-ranked |
| MRR | 0.15 | Correct chunk typically appears around rank 4–5 |

---

## System Improvements Log

| # | Area | What Changed | Why | Impact |
|---|---|---|---|---|
| 1 | Ingestion | Rewrote `structure_detector.py` regex | Original regex missed AIS-018 clause IDs | AIS-018 chunks now retrieved correctly |
| 2 | Retrieval | Added +0.3 boost for standard-specific queries | Queries mentioning AIS-018 returned AIS-012 results | Standard-specific queries surface correct document |
| 3 | Retrieval | Added query expansion for acronyms | SLD/SLF queries missed AIS-018 | Definition queries now retrieve correct standard |
| 4 | Ingestion | Preserved full amendment text in chunker | Amendment text was truncated at 800 chars | Amendments retrieved with score 22.3 vs 0.5 before |
| 5 | Evaluation | Combined faithfulness + relevance into one LLM call | Two separate calls × 50 questions exceeded token limit | Evaluation completes without hitting rate limits |
| 6 | Evaluation | `sleep(1.5)` + 15s pause every 10 questions | Rate limit errors caused mid-run failures | Full 50-question evaluation completes reliably |
| 7 | Evaluation | Unique session ID per eval question | Shared session contaminated scores via memory | Eval scores now independent per question |
| 8 | Evaluation | Filtered QA generation to exclude cover-page chunks | LLM generated trivial questions with no clause ID | Precision@5 improved after regeneration |
| 9 | Retrieval | Hybrid scoring 0.6/0.4 | Pure semantic missed exact clause number queries | Hybrid outperforms either method alone |
| 10 | Generator | Added explicit grounding instruction to system prompt | Early answers contained information beyond context | Faithfulness improved from ~0.55 to 0.71 |

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API key — free at [console.groq.com](https://console.groq.com)

### Step-by-step

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/ais-chatbot.git
cd ais-chatbot

# 2. Create and activate virtual environment
python -m venv rag-venv

# Windows
rag-venv\Scripts\activate

# Mac / Linux
source rag-venv/bin/activate

# 3. Install Python dependencies
pip install -r backend/requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Open .env and add your GROQ_API_KEY

# 5. Add AIS PDF documents
# Place PDF files in: backend/data/raw_pdfs/
# Download from: https://www.araiindia.com/downloads/ais-downloads

# 6. Run ingestion  (one-time — takes 2–5 minutes)
python scripts\ingest.py

# 7. Start backend  (run from project root, NOT from backend/ folder)
uvicorn backend.main:app --reload --port 8000

# 8. Start frontend  (new terminal)
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

### Generate evaluation data

```bash
# Generate 50 synthetic Q&A pairs
python scripts\generate_qa.py

# Run full evaluation (~7 minutes)
python scripts\run_eval.py

# Quick test with fewer questions
python scripts\run_eval.py 10
```

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `GROQ_API_KEY` | Groq Cloud API key | — |
| `GROQ_MODEL` | LLM for generation | `llama-3.3-70b-versatile` |
| `EMBEDDING_MODEL` | Sentence transformer | `all-mpnet-base-v2` |
| `CHROMA_PATH` | ChromaDB storage path | `backend/data/chroma_db` |
| `TOP_K` | Chunks to retrieve | `5` |
| `PDF_DIR` | AIS PDFs directory | `backend/data/raw_pdfs` |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Send message, get grounded answer + citations |
| `GET` | `/api/sessions` | List all past sessions |
| `GET` | `/api/sessions/{id}` | Restore full session history |
| `DELETE` | `/api/sessions/{id}` | Delete a session |
| `GET` | `/api/documents` | List all loaded AIS documents |
| `GET` | `/api/evaluation/results` | Get latest eval metrics |
| `POST` | `/api/evaluation/run` | Trigger background evaluation |

---

## Common Issues

| Error | Cause | Fix |
|---|---|---|
| `No module named 'backend'` | Running uvicorn from inside `backend/` folder | `cd ..` then run from project root |
| `TypeError: proxies` on startup | groq/httpx version conflict | `pip install --upgrade groq httpx` |
| `ECONNREFUSED` in frontend | Backend not running | Start backend first on port 8000 |
| `next.config.ts not supported` | Next.js 14 doesn't support `.ts` config | Rename to `next.config.js`, use `module.exports` |

---

## Project Structure

```
ais-chatbot/
├── backend/
│   ├── main.py                  # FastAPI app, CORS, static PDF serving
│   ├── config.py                # All env vars and constants
│   ├── requirements.txt
│   ├── agents/
│   │   ├── state.py             # AgentState TypedDict
│   │   ├── orchestrator.py      # LangGraph graph + routing logic
│   │   ├── retriever.py         # RetrieverAgent
│   │   ├── generator.py         # GeneratorAgent (Groq)
│   │   ├── evaluator.py         # EvaluatorAgent (scoring)
│   │   └── ingestion.py         # IngestionAgent (offline)
│   ├── memory/
│   │   ├── short_term.py        # In-memory per-session list
│   │   └── long_term.py         # ChromaDB conversation_memory
│   ├── tools/
│   │   ├── pdf_parser.py        # PyMuPDF extraction
│   │   ├── structure_detector.py# Clause / table / amendment detection
│   │   ├── chunker.py           # Clause-aware chunking strategies
│   │   ├── embedder.py          # Singleton all-mpnet-base-v2
│   │   ├── vector_store.py      # ChromaDB wrapper
│   │   ├── bm25_index.py        # BM25 keyword index
│   │   └── hybrid_retriever.py  # Semantic + BM25 combined search
│   ├── evaluation/
│   │   ├── synthetic_qa.py      # Generate 50 Q&A pairs
│   │   ├── metrics.py           # Precision, Recall, MRR, Faithfulness
│   │   └── run_eval.py          # Full evaluation runner
│   ├── api/
│   │   ├── chat.py              # POST /api/chat
│   │   ├── sessions.py          # Session management
│   │   ├── documents.py         # Document listing
│   │   └── evaluation.py        # Evaluation endpoints
│   └── data/
│       ├── raw_pdfs/            # AIS PDFs (not in git)
│       ├── chroma_db/           # Vector store (not in git)
│       ├── synthetic_qa.json    # Generated Q&A pairs
│       └── eval_results.json    # Latest evaluation results
├── frontend/
│   ├── app/
│   │   ├── chat/[sessionId]/    # Main 3-panel chat page
│   │   ├── dashboard/           # Evaluation dashboard
│   │   └── documents/           # Loaded documents list
│   ├── components/
│   │   ├── chat/                # ChatWindow, MessageBubble, SourceChip,
│   │   │                        # SessionSidebar, DocumentPanel
│   │   └── evaluation/          # MetricCard, QATable, EvalChart
│   ├── lib/
│   │   ├── api.ts               # All FastAPI fetch calls
│   │   └── utils.ts             # Helpers
│   └── types/index.ts           # TypeScript interfaces
├── scripts/
│   ├── ingest.py                # python scripts\ingest.py
│   ├── generate_qa.py           # python scripts\generate_qa.py
│   └── run_eval.py              # python scripts\run_eval.py [N]
├── docs/
│   ├── architecture.png         # Architecture diagram
│   └── sample_qa_50.csv         # 50 Q&A pairs (auto-generated)
├── .env.example
├── .gitignore
└── README.md
```

---

