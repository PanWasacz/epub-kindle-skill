# epub-kindle: skill dla Claude

Skill dla [Claude Code](https://claude.com/claude-code) i Claude.ai, który przygotowuje pliki **EPUB3**
do czytania na czytniku (Kindle): Markdown → pandoc → EPUB ze wzorami w MathML, własnym CSS
i polską typografią, plus automatyczna kontrola gotowego pliku.

*A Claude skill that turns Markdown (or LaTeX rewritten to Markdown) into a Kindle-friendly EPUB3
with pandoc, MathML and a custom stylesheet. Instructions are in Polish.*

## Zawartość

```
epub-kindle/
├── SKILL.md               instrukcje dla Claude (zasady, konwencje, budowanie, kontrola)
├── assets/
│   ├── style.css          styl EPUB: ramki .wazne, czerwone .zle / .uzup, tabele
│   └── szablon.md         szablon źródła z wszystkimi konwencjami
└── scripts/
    ├── build_epub.py      pandoc z właściwymi opcjami
    └── check_epub.py      kontrola EPUB przed wysłaniem
```

## Instalacja

### Claude Code

Skopiuj katalog `epub-kindle` do katalogu skilli:

```bash
git clone https://github.com/PanWasacz/epub-kindle-skill.git

# dla wszystkich projektów
cp -r epub-kindle-skill/epub-kindle ~/.claude/skills/

# albo tylko dla jednego projektu
cp -r epub-kindle-skill/epub-kindle <projekt>/.claude/skills/
```

### Claude.ai

Spakuj katalog `epub-kindle` do ZIP i wgraj w **Settings → Capabilities → Skills**.

## Wymagania

- [pandoc](https://pandoc.org/installing.html) 2.19 lub nowszy
- Python 3.8+ (tylko biblioteka standardowa)

## Użycie

Wystarczy poprosić Claude, np. *„zrób z tego EPUB na Kindle”*. Skrypty można też uruchomić ręcznie:

```bash
python epub-kindle/scripts/build_epub.py tekst.md -o Moj_dokument.epub
python epub-kindle/scripts/check_epub.py Moj_dokument.epub --source tekst.md
```

## Licencja

MIT, zobacz [LICENSE](LICENSE).
