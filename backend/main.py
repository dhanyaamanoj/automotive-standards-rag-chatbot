from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.api import chat, sessions, documents, evaluation
from backend.api import debug
from backend.config import PDF_DIR
import os

app = FastAPI(title="AIS Chatbot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve PDFs as static files — clicking citations opens PDF at page
os.makedirs(PDF_DIR, exist_ok=True)
app.mount("/static/pdfs", StaticFiles(directory=PDF_DIR), name="pdfs")

app.include_router(chat.router,       prefix="/api")
app.include_router(sessions.router,   prefix="/api")
app.include_router(documents.router,  prefix="/api")
app.include_router(evaluation.router, prefix="/api")
app.include_router(debug.router,      prefix="/api")

@app.get("/")
def root():
    return {"status": "AIS Chatbot API running"}
