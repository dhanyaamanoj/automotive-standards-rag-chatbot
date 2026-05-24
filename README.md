# AIS Standards Chatbot — Multi-Agent RAG System

AI-powered chatbot for ARAI Automotive Industry Standard (AIS) documents using
LangGraph multi-agent architecture, Groq LLaMA 3.3 70B, ChromaDB, and hybrid retrieval.

## Architecture
- **OrchestratorAgent** — LangGraph StateGraph, routes and coordinates all agents
- **RetrieverAgent** — Hybrid semantic (all-mpnet-base-v2) + BM25 search
- **GeneratorAgent** — Groq llama-3.3-70b-versatile with grounded prompting
- **EvaluatorAgent** — LLM-based faithfulness + relevance scoring
- **IngestionAgent** — Clause-aware PDF parsing with amendment merging

## Quick Start

### 1. Clone and set up backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env
# Add your GROQ_API_KEY to .env
```

### 2. Add PDF documents
Place your AIS PDF files in: `backend/data/raw_pdfs/`
Download from: https://www.araiindia.com/downloads/ais-downloads

### 3. Run ingestion (once)
```bash
python scripts/ingest.py
```

### 4. Start backend
```bash
uvicorn backend.main:app --reload --port 8000
```

### 5. Start frontend
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

### 6. Generate evaluation data
```bash
python scripts/generate_qa.py   # generates 50 synthetic QA pairs
python scripts/run_eval.py      # runs evaluation, saves results
```

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/chat | Send a message |
| GET | /api/sessions | List all sessions |
| GET | /api/sessions/{id} | Get session history |
| DELETE | /api/sessions/{id} | Delete session |
| GET | /api/documents | List loaded documents |
| GET | /api/evaluation/results | Get eval metrics |
| POST | /api/evaluation/run | Trigger evaluation |

## Tech Stack
- **LLM**: Groq Cloud — llama-3.3-70b-versatile
- **Embeddings**: sentence-transformers/all-mpnet-base-v2
- **Vector DB**: ChromaDB (persistent)
- **Keyword Search**: BM25 (rank-bm25)
- **Agent Framework**: LangGraph
- **Backend**: FastAPI + Uvicorn
- **Frontend**: Next.js 14 + React 18
- **PDF Parsing**: PyMuPDF (fitz)
