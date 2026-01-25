from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import List

from .config import PDF_DIR, SQLITE_PATH
from .normalize import normalize_text
from .pdf_extract import extract_text_from_pdf

@dataclass
class DocRecord:
    filename: str
    path: str
    mtime_ns: int
    text_raw: str
    text_norm: str

def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db_path))
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA synchronous=NORMAL;")
    return con

def _has_column(con: sqlite3.Connection, table: str, col: str) -> bool:
    rows = con.execute(f"PRAGMA table_info({table});").fetchall()
    return any(r[1] == col for r in rows)

def init_db() -> None:
    con = _connect(SQLITE_PATH)
    try:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS docs (
                filename TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                mtime_ns INTEGER NOT NULL,
                text_raw TEXT NOT NULL,
                text_norm TEXT NOT NULL
            );
            """
        )
        # migrasi ringan untuk DB lama
        if not _has_column(con, "docs", "text_raw"):
            con.execute("ALTER TABLE docs ADD COLUMN text_raw TEXT NOT NULL DEFAULT '';")
        if not _has_column(con, "docs", "text_norm"):
            con.execute("ALTER TABLE docs ADD COLUMN text_norm TEXT NOT NULL DEFAULT '';")
        con.commit()
    finally:
        con.close()

def list_pdf_files(pdf_dir: Path = PDF_DIR) -> List[Path]:
    if not pdf_dir.exists():
        return []
    return sorted([p for p in pdf_dir.glob("*.pdf") if p.is_file()])

def get_doc_meta(filename: str) -> tuple[str, int] | None:
    con = _connect(SQLITE_PATH)
    try:
        row = con.execute(
            "SELECT path, mtime_ns FROM docs WHERE filename=?;",
            (filename,),
        ).fetchone()
        if not row:
            return None
        return str(row[0]), int(row[1])
    finally:
        con.close()

def upsert_doc(rec: DocRecord) -> None:
    con = _connect(SQLITE_PATH)
    try:
        con.execute(
            """
            INSERT INTO docs(filename, path, mtime_ns, text_raw, text_norm)
            VALUES(?, ?, ?, ?, ?)
            ON CONFLICT(filename) DO UPDATE SET
                path=excluded.path,
                mtime_ns=excluded.mtime_ns,
                text_raw=excluded.text_raw,
                text_norm=excluded.text_norm;
            """,
            (rec.filename, rec.path, rec.mtime_ns, rec.text_raw, rec.text_norm),
        )
        con.commit()
    finally:
        con.close()

def load_all_docs() -> List[DocRecord]:
    con = _connect(SQLITE_PATH)
    try:
        rows = con.execute(
            "SELECT filename, path, mtime_ns, text_raw, text_norm FROM docs ORDER BY filename;"
        ).fetchall()
        return [DocRecord(r[0], r[1], int(r[2]), r[3], r[4]) for r in rows]
    finally:
        con.close()

def build_or_update_index() -> int:
    init_db()
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    updated = 0
    for pdf in list_pdf_files():
        stat = pdf.stat()
        meta = get_doc_meta(pdf.name)
        if meta and meta[1] == stat.st_mtime_ns:
            continue

        raw = extract_text_from_pdf(pdf)
        norm = normalize_text(raw)

        upsert_doc(
            DocRecord(
                filename=pdf.name,
                path=str(pdf),
                mtime_ns=stat.st_mtime_ns,
                text_raw=raw,
                text_norm=norm,
            )
        )
        updated += 1

    return updated
