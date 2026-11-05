#!/usr/bin/env python3
"""Buduje EPUB3 z pliku Markdown przy użyciu pandoc i stylu ze skilla.

Użycie:
    python build_epub.py tekst.md -o NAZWA.epub [--css inny.css] [--resource-path DIR]
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CSS = SKILL_DIR / "assets" / "style.css"


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="Markdown -> EPUB3 (pandoc, MathML, CSS).")
    p.add_argument("source", type=Path, help="plik Markdown z metadanymi YAML")
    p.add_argument("-o", "--output", type=Path, help="plik wynikowy .epub (domyślnie nazwa źródła)")
    p.add_argument("--css", type=Path, default=DEFAULT_CSS, help="arkusz stylów (domyślnie assets/style.css)")
    p.add_argument("--resource-path", help="katalog z obrazkami (domyślnie katalog źródła)")
    args = p.parse_args()

    if shutil.which("pandoc") is None:
        print("BŁĄD: nie znaleziono pandoc. Zainstaluj: https://pandoc.org/installing.html", file=sys.stderr)
        return 2
    if not args.source.is_file():
        print(f"BŁĄD: brak pliku {args.source}", file=sys.stderr)
        return 2
    if not args.css.is_file():
        print(f"BŁĄD: brak pliku CSS {args.css}", file=sys.stderr)
        return 2

    output = args.output or args.source.with_suffix(".epub")
    resource_path = args.resource_path or str(args.source.resolve().parent)

    cmd = [
        "pandoc", str(args.source), "-o", str(output),
        "--to", "epub3", "--mathml", "--css", str(args.css),
        "--toc", "--toc-depth=2", "--split-level=1",
        "--resource-path", resource_path,
    ]
    print("$ " + " ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        return result.returncode
    print(f"OK: zapisano {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
