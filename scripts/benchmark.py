from __future__ import annotations

import argparse
import csv
import statistics
import sys
import time
from pathlib import Path

# Pastikan root project masuk sys.path agar "import app...." selalu bisa
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.index_store import build_or_update_index, load_all_docs  # noqa: E402
from app.normalize import normalize_text  # noqa: E402
from app.search_algos import ALGOS  # noqa: E402

QUERIES_PATH = ROOT / "data" / "queries.txt"
OUT_CSV = ROOT / "data" / "benchmark.csv"


def load_queries() -> list[str]:
    if not QUERIES_PATH.exists():
        return ["data", "analysis", "keyword", "tidakada123"]
    return [
        line.strip()
        for line in QUERIES_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def run_once(docs, queries, algo) -> float:
    t0 = time.perf_counter()
    for q in queries:
        for d in docs:
            algo.fn(d.text_norm, q)
    return (time.perf_counter() - t0) * 1000.0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeat", type=int, default=5, help="berapa kali pengulangan per algoritma")
    ap.add_argument("--warmup", type=int, default=1, help="warmup run (tidak dicatat)")
    args = ap.parse_args()

    build_or_update_index()
    docs = load_all_docs()
    queries = [normalize_text(q) for q in load_queries()]

    if not docs:
        raise SystemExit("Tidak ada dokumen. Isi dulu data/pdfs/ atau upload PDF via web.")
    if not queries:
        raise SystemExit("Tidak ada query. Buat data/queries.txt atau pakai default.")

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["algo", "queries", "docs", "total_ms", "avg_ms_per_query", "repeat_std_ms"])

        for algo in ALGOS.values():
            for _ in range(max(0, args.warmup)):
                run_once(docs, queries, algo)

            runs = [run_once(docs, queries, algo) for _ in range(max(1, args.repeat))]
            total_ms = statistics.mean(runs)
            std_ms = statistics.pstdev(runs) if len(runs) > 1 else 0.0
            avg_ms_per_query = total_ms / max(1, len(queries))

            w.writerow([algo.key, len(queries), len(docs), f"{total_ms:.2f}", f"{avg_ms_per_query:.2f}", f"{std_ms:.2f}"])

    print(f"Wrote: {OUT_CSV}")


if __name__ == "__main__":
    main()
