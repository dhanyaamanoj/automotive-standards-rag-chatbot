import os
from backend.tools.pdf_parser import PDFParser
from backend.tools.structure_detector import StructureDetector
from backend.tools.chunker import Chunker
from backend.tools.embedder import Embedder
from backend.tools.vector_store import VectorStore
from backend.tools.bm25_index import BM25Index
from backend.config import PDF_DIR

class IngestionAgent:
    """
    Objective : Process all PDFs into ChromaDB + BM25 index.
    Input     : directory of PDF files
    Output    : populated vector store and BM25 index
    """
    def __init__(self):
        self.parser    = PDFParser()
        self.detector  = StructureDetector()
        self.chunker   = Chunker()
        self.embedder  = Embedder()
        self.store     = VectorStore()
        self.bm25      = BM25Index()

    def ingest_all(self, pdf_dir: str = PDF_DIR):
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]
        print(f"Found {len(pdf_files)} PDFs")
        all_chunks = []

        for pdf_file in pdf_files:
            path = os.path.join(pdf_dir, pdf_file)
            print(f"Processing: {pdf_file}")
            try:
                chunks = self._process_one(path, pdf_file)
                all_chunks.extend(chunks)
                print(f"  → {len(chunks)} chunks")
            except Exception as e:
                print(f"  ERROR: {e}")

        # Build BM25 index from all chunks
        self.bm25.build([c["text"] for c in all_chunks], all_chunks)
        self.bm25.save()
        print(f"\nDone. Total chunks: {len(all_chunks)}")

    def _process_one(self, path: str, filename: str) -> list:
        pages       = self.parser.parse(path)
        is_amend    = self.parser.is_amendment(pages)
        doc_tree    = self.detector.detect(pages, filename)
        chunks      = self.chunker.chunk(doc_tree, is_amend)
        embeddings  = self.embedder.encode([c["text"] for c in chunks])
        self.store.upsert(chunks, embeddings)
        return chunks
