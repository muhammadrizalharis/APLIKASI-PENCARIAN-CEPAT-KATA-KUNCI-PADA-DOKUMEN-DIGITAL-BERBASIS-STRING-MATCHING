from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

PDF_DIR = BASE_DIR / "data" / "pdfs"
SQLITE_PATH = BASE_DIR / "data" / "index.sqlite3"

SNIPPET_RADIUS = 60
MAX_RESULTS = 200
MAX_POSITIONS_SHOWN = 20
MAX_SNIPPETS_SHOWN = 3

MAX_UPLOAD_MB = 25
