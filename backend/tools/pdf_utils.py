import os
from glob import glob
from backend.config import PDF_DIR


def _scan_pdf_files() -> list[str]:
    if not os.path.exists(PDF_DIR):
        return []
    return [os.path.basename(path) for path in glob(os.path.join(PDF_DIR, "*.pdf"))]


PDF_FILENAMES = _scan_pdf_files()


def resolve_pdf_filename(std_id: str) -> str:
    std_id = (std_id or "").strip()
    if not std_id:
        return ""

    exact_name = f"{std_id}.pdf"
    if exact_name in PDF_FILENAMES:
        return exact_name

    candidates = [name for name in PDF_FILENAMES if std_id.lower() in name.lower()]
    if candidates:
        # Prefer a filename that contains the std_id as a standalone segment.
        candidates.sort(key=lambda n: (std_id.lower() not in n.lower(), len(n)))
        return candidates[0]

    return exact_name


def get_pdf_url(std_id: str, page: int = 1) -> str:
    filename = resolve_pdf_filename(std_id)
    if not filename:
        return ""
    return f"/static/pdfs/{filename}#page={page}"
