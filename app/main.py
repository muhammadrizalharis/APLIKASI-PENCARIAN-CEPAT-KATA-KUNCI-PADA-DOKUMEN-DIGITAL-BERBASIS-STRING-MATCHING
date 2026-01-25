from __future__ import annotations

import csv
import time
from pathlib import Path

from fastapi import FastAPI, Query, Request, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import (
    BASE_DIR,
    MAX_RESULTS,
    MAX_POSITIONS_SHOWN,
    MAX_SNIPPETS_SHOWN,
    PDF_DIR,
    MAX_UPLOAD_MB,
)
from .index_store import build_or_update_index, load_all_docs
from .normalize import normalize_text
from .search_algos import ALGOS
from .snippets import make_snippet
from .upload_utils import save_uploaded_pdf

app = FastAPI(title="PDF Keyword Search (String Matching)")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

_DOCS_CACHE = []

def _safe_pdf_path(filename: str) -> Path:
    candidate = (PDF_DIR / filename).resolve()
    pdf_dir = PDF_DIR.resolve()
    if pdf_dir not in candidate.parents:
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not candidate.exists() or not candidate.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    if candidate.suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Not a PDF")
    return candidate

def _load_benchmark_csv() -> dict | None:
    bench_path = BASE_DIR / "data" / "benchmark.csv"
    if not bench_path.exists():
        return None

    labels: list[str] = []
    avg_ms: list[float] = []
    total_ms: list[float] = []

    try:
        with bench_path.open("r", encoding="utf-8", newline="") as f:
            r = csv.DictReader(f)
            for row in r:
                labels.append(row["algo"])
                avg_ms.append(float(row["avg_ms_per_query"]))
                total_ms.append(float(row["total_ms"]))
    except Exception:
        return None

    return {"labels": labels, "avg_ms": avg_ms, "total_ms": total_ms}

@app.on_event("startup")
def _startup() -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    build_or_update_index()
    global _DOCS_CACHE
    _DOCS_CACHE = load_all_docs()

def _base_context(request: Request) -> dict:
    return {
        "request": request,
        "algos": list(ALGOS.values()),
        "pdf_count": len(_DOCS_CACHE),
        "max_upload_mb": MAX_UPLOAD_MB,
        "bench": _load_benchmark_csv(),
    }

@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    ctx = _base_context(request)
    ctx.update({"q": "", "algo": "bmh", "results": None, "stats": None})
    return templates.TemplateResponse("index.html", ctx)

@app.post("/upload", response_class=HTMLResponse)
async def upload(request: Request, pdf: UploadFile = File(...)) -> HTMLResponse:
    max_bytes = int(MAX_UPLOAD_MB * 1024 * 1024)

    t0 = time.perf_counter()
    saved_path = await save_uploaded_pdf(pdf, PDF_DIR, max_bytes=max_bytes)

    updated = build_or_update_index()
    global _DOCS_CACHE
    _DOCS_CACHE = load_all_docs()

    dt_ms = (time.perf_counter() - t0) * 1000.0

    ctx = _base_context(request)
    ctx.update(
        {
            "q": "",
            "algo": "bmh",
            "results": [],
            "stats": {"message": f"Upload OK: {saved_path.name}. Reindex updated {updated} file. {dt_ms:.2f} ms"},
        }
    )
    return templates.TemplateResponse("index.html", ctx)

@app.get("/reindex", response_class=HTMLResponse)
def reindex(request: Request) -> HTMLResponse:
    t0 = time.perf_counter()
    updated = build_or_update_index()
    global _DOCS_CACHE
    _DOCS_CACHE = load_all_docs()
    dt_ms = (time.perf_counter() - t0) * 1000.0

    ctx = _base_context(request)
    ctx.update(
        {
            "q": "",
            "algo": "bmh",
            "results": [],
            "stats": {"message": f"Reindex selesai: updated {updated} file, {dt_ms:.2f} ms"},
        }
    )
    return templates.TemplateResponse("index.html", ctx)

@app.get("/pdf/{filename}", response_class=FileResponse)
def view_pdf(filename: str) -> FileResponse:
    path = _safe_pdf_path(filename)
    return FileResponse(
        path=str(path),
        media_type="application/pdf",
        filename=path.name,
        headers={"Content-Disposition": f'inline; filename="{path.name}"'},
    )

@app.get("/search", response_class=HTMLResponse)
def search(
    request: Request,
    q: str = Query(..., min_length=1, max_length=200),
    algo: str = Query("bmh"),
) -> HTMLResponse:
    qn = normalize_text(q)
    chosen = ALGOS.get(algo) or ALGOS["bmh"]

    t0 = time.perf_counter()
    results = []

    for doc in _DOCS_CACHE:
        positions = chosen.fn(doc.text_norm, qn)
        if not positions:
            continue

        snippets = [make_snippet(doc.text_raw, p, len(qn)) for p in positions[:MAX_SNIPPETS_SHOWN]]
        results.append(
            {
                "filename": doc.filename,
                "count": len(positions),
                "positions": positions[:MAX_POSITIONS_SHOWN],
                "snippets": snippets,
            }
        )

    results.sort(key=lambda r: r["count"], reverse=True)
    results = results[:MAX_RESULTS]

    dt_ms = (time.perf_counter() - t0) * 1000.0
    stats = {
        "algo": chosen.name,
        "docs_scanned": len(_DOCS_CACHE),
        "matches_docs": len(results),
        "ms": dt_ms,
    }

    ctx = _base_context(request)
    ctx.update({"q": q, "algo": chosen.key, "results": results, "stats": stats})
    return templates.TemplateResponse("index.html", ctx)
