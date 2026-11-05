#!/usr/bin/env python3
"""Kontrola gotowego pliku EPUB przed wysłaniem na czytnik.

Użycie:
    python check_epub.py NAZWA.epub [--source tekst.md] [--lang pl-PL]

Kod wyjścia: 0 = wszystko OK (mogą być ostrzeżenia), 1 = są błędy.
"""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F02F\U0001F0A0-\U0001F0FF\U0001F100-\U0001F1FF]"
)
POLISH_CHARS = set("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ")


def read_epub(path: Path) -> tuple[str, str]:
    """Zwraca (połączony XHTML, zawartość pliku OPF)."""
    xhtml_parts: list[str] = []
    opf = ""
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            low = name.lower()
            if low.endswith((".xhtml", ".html", ".htm")):
                xhtml_parts.append(z.read(name).decode("utf-8", errors="replace"))
            elif low.endswith(".opf"):
                opf = z.read(name).decode("utf-8", errors="replace")
    return "\n".join(xhtml_parts), opf


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="Kontrola EPUB przed wysłaniem.")
    p.add_argument("epub", type=Path)
    p.add_argument("--source", type=Path, help="źródłowy Markdown (dokładniejsze sprawdzenie)")
    p.add_argument("--lang", default="pl-PL", help="oczekiwany język (domyślnie pl-PL)")
    args = p.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    ok: list[str] = []

    if not args.epub.is_file():
        print(f"BŁĄD: brak pliku {args.epub}", file=sys.stderr)
        return 1
    try:
        html, opf = read_epub(args.epub)
    except zipfile.BadZipFile:
        print(f"BŁĄD: {args.epub} nie jest poprawnym archiwum EPUB", file=sys.stderr)
        return 1

    src = ""
    if args.source:
        if args.source.is_file():
            src = args.source.read_text(encoding="utf-8")
        else:
            errors.append(f"brak pliku źródłowego {args.source}")

    # Nazwa pliku
    name = args.epub.name
    if " " in name or POLISH_CHARS & set(name):
        errors.append(f"nazwa pliku '{name}' zawiera spacje lub polskie znaki")
    else:
        ok.append("nazwa pliku bez spacji i polskich znaków")

    # Język
    m = re.search(r"<dc:language[^>]*>([^<]+)</dc:language>", opf)
    lang = m.group(1).strip() if m else None
    if lang == args.lang:
        ok.append(f"język {lang}")
    else:
        errors.append(f"język to '{lang}', oczekiwano '{args.lang}' (dodaj 'lang: {args.lang}' w YAML)")

    # Wzory
    n_math = len(re.findall(r"<math[\s>]", html))
    src_has_math = bool(re.search(r"\$[^$\s][^$]*\$", src)) if src else None
    if n_math:
        ok.append(f"wzory w MathML: {n_math}")
        if re.search(r'<img[^>]+class="math', html):
            warnings.append("część wzorów to obrazki zamiast MathML (czy użyto --mathml?)")
    elif src_has_math:
        errors.append("źródło zawiera wzory, a w EPUB brak <math> (czy użyto --mathml?)")
    else:
        ok.append("brak wzorów")

    # Ramki i wyróżnienia
    for cls, marker in (("wazne", "::: wazne"), ("zle", "{.zle}")):
        n = len(re.findall(rf'class="[^"]*\b{cls}\b', html))
        if n:
            ok.append(f'class="{cls}": {n}')
        elif src and marker in src:
            errors.append(f'źródło używa {marker}, a w EPUB brak class="{cls}"')

    # Pozostawione [?]{.uzup}
    n_uzup = len(re.findall(r'class="[^"]*\buzup\b', html))
    if src:
        n_uzup = max(n_uzup, src.count("{.uzup}"))
    if n_uzup:
        errors.append(f"pozostało {n_uzup} wartości do uzupełnienia ([?]{{.uzup}})")
    else:
        ok.append("brak [?]{.uzup}")

    # Emoji
    emojis = set(EMOJI_RE.findall(html))
    if emojis:
        errors.append(f"znaleziono emoji: {' '.join(sorted(emojis))}")

    # Spis treści w tekście (pandoc umieszcza go w nav.xhtml, nie w treści)
    if src and re.search(r"^#+\s*(spis treści|table of contents)\s*$", src, re.I | re.M):
        warnings.append("źródło zawiera ręczny spis treści; czytnik ma własny w menu")

    for line in ok:
        print(f"[OK]    {line}")
    for line in warnings:
        print(f"[UWAGA] {line}")
    for line in errors:
        print(f"[BŁĄD]  {line}")
    print("\nPamiętaj: ręcznie porównaj liczby w tabelach z aktualną wersją PDF/TeX.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
