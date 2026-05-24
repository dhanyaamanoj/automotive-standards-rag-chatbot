"""
Run this ONCE before starting the server:
    python scripts/ingest.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from backend.agents.ingestion import IngestionAgent

if __name__ == "__main__":
    agent = IngestionAgent()
    agent.ingest_all()
    print("Ingestion complete.")
