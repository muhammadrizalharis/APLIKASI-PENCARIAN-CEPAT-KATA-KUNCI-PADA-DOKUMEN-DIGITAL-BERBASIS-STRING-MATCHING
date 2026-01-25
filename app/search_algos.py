# filepath: d:\AI Learn\pdf-search-ta\app\search_algos.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List

FindAllFn = Callable[[str, str], List[int]]

def naive_find_all(text: str, pattern: str) -> List[int]:
    if not pattern:
        return []
    n, m = len(text), len(pattern)
    if m > n:
        return []
    out: List[int] = []
    for i in range(n - m + 1):
        if text[i : i + m] == pattern:
            out.append(i)
    return out

def kmp_find_all(text: str, pattern: str) -> List[int]:
    if not pattern:
        return []
    n, m = len(text), len(pattern)
    if m > n:
        return []

    # LPS array
    lps = [0] * m
    j = 0
    for i in range(1, m):
        while j > 0 and pattern[i] != pattern[j]:
            j = lps[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
            lps[i] = j

    out: List[int] = []
    i = 0
    j = 0
    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == m:
                out.append(i - m)
                j = lps[j - 1]
        else:
            if j > 0:
                j = lps[j - 1]
            else:
                i += 1
    return out

def bmh_find_all(text: str, pattern: str) -> List[int]:
    """
    Boyer–Moore–Horspool (BMH) - sering cepat untuk teks natural.
    """
    if not pattern:
        return []
    n, m = len(text), len(pattern)
    if m > n:
        return []

    shift: dict[str, int] = {}
    for i in range(m - 1):
        shift[pattern[i]] = m - 1 - i

    out: List[int] = []
    i = 0
    while i <= n - m:
        j = m - 1
        while j >= 0 and text[i + j] == pattern[j]:
            j -= 1
        if j < 0:
            out.append(i)
            i += 1  # allow overlaps
        else:
            i += shift.get(text[i + m - 1], m)
    return out

@dataclass(frozen=True)
class Algo:
    key: str
    name: str
    fn: FindAllFn

ALGOS: dict[str, Algo] = {
    "naive": Algo("naive", "Naive", naive_find_all),
    "kmp": Algo("kmp", "KMP", kmp_find_all),
    "bmh": Algo("bmh", "Boyer-Moore-Horspool", bmh_find_all),
}
