# filepath: d:\AI Learn\pdf-search-ta\app\pdf_extract.py
from pathlib import Path
from pypdf import PdfReader

def extract_text_from_pdf(path: Path) -> str:
    """
    Ekstraksi teks PDF (text-based) dengan pypdf.
    Untuk PDF scan gambar, hasil biasanya kosong (butuh OCR, scope berbeda).
    """
    reader = PdfReader(str(path))
    parts: list[str] = []
    for page in reader.pages:
        txt = page.extract_text() or ""
        if txt:
            parts.append(txt)
    return "\n".join(parts)
