import re
import uuid

DEF_RE = re.compile(
    r"(\d+\.\d+(?:\.\d+)*)\s+([A-Z][^\n]{5,80})\n((?:.|\n){20,600}?)(?=\n\d+\.\d+|\Z)",
    re.MULTILINE
)

class Chunker:
    """
    Routes each section to the right chunking strategy.
    Returns list of {id, text, metadata} dicts ready for ChromaDB.
    """
    def chunk(self, doc_tree: dict, is_amendment: bool = False) -> list:
        chunks = []
        std_id = doc_tree["std_id"]
        for section in doc_tree["sections"]:
            stype = section["type"]
            if stype == "definitions":
                chunks.extend(self._definition_chunks(section, std_id))
            elif stype == "table":
                chunks.extend(self._table_chunk(section, std_id))
            elif stype == "amendment":
                chunks.extend(self._amendment_chunk(section, std_id))
            elif stype in ("appendix",):
                pass   # skip appendices (committee lists etc.)
            else:
                chunks.extend(self._clause_chunk(section, std_id))

        # Add one summary chunk per document
        chunks.append(self._summary_chunk(doc_tree))
        return chunks

    def _clause_chunk(self, section: dict, std_id: str) -> list:
        """One chunk per detected leaf clause."""
        text = section["text"].strip()
        if not text:
            return []
        return [self._make(
            text=text,
            std_id=std_id,
            clause_id=section.get("clause_id",""),
            section_title=section.get("title",""),
            page_number=section.get("page_number",1),
            chunk_type="clause",
        )]

    def _definition_chunks(self, section: dict, std_id: str) -> list:
        """One chunk per definition term."""
        chunks = []
        for m in DEF_RE.finditer(section["text"]):
            clause_id = m.group(1)
            title     = m.group(2).strip()
            defn_text = f"{clause_id} {title}\n{m.group(3).strip()}"
            chunks.append(self._make(
                text=defn_text,
                std_id=std_id,
                clause_id=clause_id,
                section_title=title,
                page_number=section.get("page_number",1),
                chunk_type="definition",
            ))
        if not chunks:
            chunks.append(self._clause_chunk(section, std_id)[0]
                          if section["text"] else None)
            chunks = [c for c in chunks if c]
        return chunks

    def _table_chunk(self, section: dict, std_id: str) -> list:
        """Whole table as one chunk."""
        return [self._make(
            text=section["text"].strip(),
            std_id=std_id,
            clause_id=section.get("clause_id",""),
            section_title=section.get("title",""),
            page_number=section.get("page_number",1),
            chunk_type="table",
        )]

    def _amendment_chunk(self, section: dict, std_id: str) -> list:
        """Amendment patch as one chunk."""
        return [self._make(
            text=section["text"].strip(),
            std_id=std_id,
            clause_id=section.get("clause_id",""),
            section_title=section.get("title","Amendment"),
            page_number=section.get("page_number",1),
            chunk_type="amendment",
            amendment_no=section.get("amendment_no",""),
        )]

    def _summary_chunk(self, doc_tree: dict) -> dict:
        std_id   = doc_tree["std_id"]
        sections = doc_tree["sections"]
        # Use actual clause titles not just amendment names
        clause_titles = [
            f"Cl.{s['clause_id']} {s['title']}"
            for s in sections
            if s.get('clause_id') and s.get('title')
            and 'Amendment' not in s.get('title','')
        ][:12]
        text = f"{std_id} document summary. Topics covered: " + "; ".join(clause_titles)
        return self._make(
            text=text[:800],
            std_id=std_id,
            clause_id="summary",
            section_title="Document summary",
            page_number=1,
            chunk_type="summary",
        )

    def _make(self, text, std_id, clause_id, section_title,
              page_number, chunk_type, amendment_no="") -> dict:
        return {
            "id":   f"{std_id}_{clause_id}_{page_number}_{uuid.uuid4().hex[:6]}",
            "text": text,
            "metadata": {
                "std_id":        std_id,
                "clause_id":     clause_id,
                "section_title": section_title,
                "page_number":   page_number,
                "chunk_type":    chunk_type,
                "amendment_no":  amendment_no,
            },
        }
