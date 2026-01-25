from __future__ import annotations

import re
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

_PDF_MAGIC = b"%PDF-"
_SAFE_CHARS = re.compile(r"[^a-zA-Z0-9._-]+")

def _safe_filename(original: str) -> str:
    name = (original or "upload.pdf").strip()
    name = name.replace("\\", "_").replace("/", "_")
    name = _SAFE_CHARS.sub("_", name)
    if not name.lower().endswith(".pdf"):
        name += ".pdf"
    return name

async def save_uploaded_pdf(file: UploadFile, dest_dir: Path, max_bytes: int) -> Path:
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    safe = _safe_filename(file.filename)
    if not safe.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF is allowed")

    dest_dir.mkdir(parents=True, exist_ok=True)

    stem = Path(safe).stem
    out_path = dest_dir / f"{stem}_{uuid4().hex}.pdf"

    size = 0
    first_chunk = True

    try:
        with out_path.open("wb") as f:
            while True:
                chunk = await file.read(1024 * 1024)  # 1MB
                if not chunk:
                    break

                if first_chunk:
                    first_chunk = False
                    if not chunk.startswith(_PDF_MAGIC):
                        raise HTTPException(status_code=400, detail="Invalid PDF file")

                size += len(chunk)
                if size > max_bytes:
                    raise HTTPException(status_code=413, detail="File too large")

                f.write(chunk)
    except HTTPException:
        out_path.unlink(missing_ok=True)
        raise
    except Exception:
        out_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Failed to save file")
    finally:
        await file.close()

    return out_path
