from __future__ import annotations

from .config import SNIPPET_RADIUS

def make_snippet(text: str, pos: int, m: int) -> str:
    start = max(0, pos - SNIPPET_RADIUS)
    end = min(len(text), pos + m + SNIPPET_RADIUS)
    snippet = text[start:end]
    rel = pos - start
    return snippet[:rel] + "[[" + snippet[rel : rel + m] + "]]" + snippet[rel + m :]
