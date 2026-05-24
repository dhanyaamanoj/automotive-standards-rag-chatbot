import re
from backend.tools.pdf_parser import PDFParser

# Improved regex patterns
CLAUSE_RE    = re.compile(
    r"^(\d+(?:\.\d+)*)\s{0,10}([A-Z][A-Za-z\s\-]{3,80})", 
    re.MULTILINE
)
DEF_RE       = re.compile(r"^(\d+\.\d+)\s+([A-Z][a-z].{5,60})\n", re.MULTILINE)
AMENDMENT_RE = re.compile(r"AMENDMENT\s+NO\.?\s*(\d+)", re.IGNORECASE)
PART_RE      = re.compile(r"^PART[\s\-]+(I{1,3}|IV|V|\d+)", re.IGNORECASE | re.MULTILINE)
TABLE_RE     = re.compile(
    r"(Rated Voltage|Sr\.?\s*No\.|Table\s+\d+|^Parameter|Minimum \(cd\)|Maximum \(cd\))", 
    re.IGNORECASE | re.MULTILINE
)
DEF_SECTION  = re.compile(
    r"^\d+\.\s*DEFINITIONS|^DEFINITIONS|^1\. Definitions", 
    re.IGNORECASE | re.MULTILINE
)
SCOPE_RE     = re.compile(
    r"^\d+\.\s*SCOPE|^SCOPE|^0\. SCOPE|^1\.0 SCOPE", 
    re.IGNORECASE | re.MULTILINE
)

parser = PDFParser()

class StructureDetector:
    def detect(self, pages: list, filename: str) -> dict:
        std_id   = parser.extract_std_id(filename)
        is_amend = parser.is_amendment(pages)
        sections = []

        if is_amend:
            sections = self._parse_amendment(pages, std_id)
        else:
            sections = self._parse_base(pages, std_id)

        return {
            "std_id": std_id,
            "filename": filename,
            "is_amendment": is_amend,
            "sections": sections,
        }

    def _parse_base(self, pages: list, std_id: str) -> list:
        sections = []
        for page in pages:
            text = page["text"]
            pnum = page["page_number"]

            # Detect section type
            if DEF_SECTION.search(text):
                stype = "definitions"
            elif TABLE_RE.search(text):
                stype = "table"
            elif SCOPE_RE.search(text):
                stype = "scope"
            elif PART_RE.search(text):
                stype = "part"
            else:
                stype = "clause"

            # Extract all clause IDs from this page
            matches = list(CLAUSE_RE.finditer(text))

            if matches:
                for i, m in enumerate(matches):
                    clause_id = m.group(1).strip(".")
                    title     = m.group(2).strip()[:100]
                    start = m.start()
                    end   = matches[i+1].start() if i+1 < len(matches) else len(text)
                    chunk_text = text[start:end].strip()
                    
                    if len(chunk_text) < 20:
                        continue
                    
                    sections.append({
                        "type":        self._detect_type(chunk_text),
                        "clause_id":   clause_id,
                        "title":       title,
                        "std_id":      std_id,
                        "page_number": pnum,
                        "text":        chunk_text,
                    })
            else:
                sections.append({
                    "type":        stype,
                    "clause_id":   "",
                    "title":       text[:60].replace("\n", " "),
                    "std_id":      std_id,
                    "page_number": pnum,
                    "text":        text,
                })
        return sections

    def _detect_type(self, text: str) -> str:
        if TABLE_RE.search(text):
            return "table"
        if DEF_SECTION.search(text):
            return "definitions"
        if SCOPE_RE.search(text):
            return "scope"
        return "clause"

    def _parse_amendment(self, pages: list, std_id: str) -> list:
        sections = []
        amend_num = ""
        for page in pages:
            m = AMENDMENT_RE.search(page["text"])
            if m:
                amend_num = m.group(1)
            
            clause_matches = CLAUSE_RE.findall(page["text"])
            clause_ids = [c[0] for c in clause_matches] if clause_matches else []
            
            sections.append({
                "type":         "amendment",
                "clause_id":    ",".join(clause_ids[:3]) if clause_ids else "",
                "title":        f"Amendment No.{amend_num} to {std_id}",
                "std_id":       std_id,
                "amendment_no": amend_num,
                "page_number":  page["page_number"],
                "text":         page["text"],
            })
        return sections