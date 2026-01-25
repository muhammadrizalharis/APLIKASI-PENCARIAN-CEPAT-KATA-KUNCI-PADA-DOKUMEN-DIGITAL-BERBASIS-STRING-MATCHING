# filepath: d:\AI Learn\pdf-search-ta\scripts\build_index.py
from app.index_store import build_or_update_index

if __name__ == "__main__":
    updated = build_or_update_index()
    print(f"Done. Updated {updated} PDFs.")
