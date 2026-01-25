# filepath: d:\AI Learn\pdf-search-ta\app\normalize.py
def normalize_text(s: str) -> str:
    """
    Normalisasi minimal untuk menjaga offset stabil:
    - lower() saja (panjang string tidak berubah)
    """
    return (s or "").lower()
