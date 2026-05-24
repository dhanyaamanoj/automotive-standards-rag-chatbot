import re
import fitz   # PyMuPDF

class PDFParser:
    """
    Extracts pages with text + page numbers from a PDF.
    Detects amendment-only documents.
    """
    def parse(self, path: str) -> list:
        """Returns list of {page_number, text}"""
        doc = fitz.open(path)
        pages = []
        for i, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            if text:
                pages.append({"page_number": i, "text": text})
        doc.close()
        return pages

    def is_amendment(self, pages: list) -> bool:
        """True if this doc is an amendment-only file."""
        if not pages:
            return False
        first_text = pages[0]["text"].upper()
        return bool(re.search(r"AMENDMENT\s+NO\.", first_text))

    def extract_std_id(self, filename: str) -> str:
        """Extract standard ID from filename e.g. AIS-018 from AIS_018.pdf"""
        name = filename.replace("_", "-").upper()
        match = re.search(r"AIS-?0*(\d+)", name)
        return f"AIS-{match.group(1).zfill(3)}" if match else filename.replace(".pdf","")
