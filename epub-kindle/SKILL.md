---
name: epub-kindle
description: Przygotowuje plik EPUB3 do czytania na czytniku (Kindle) z Markdownu lub LaTeX-a przy użyciu pandoc, MathML i własnego CSS, w polskiej typografii. Użyj, gdy użytkownik prosi o EPUB, ebook, wersję na Kindle/czytnik albo o konwersję dokumentu (Markdown, .tex, PDF) do formatu e-book. Triggers: "epub", "ebook", "e-book", "Kindle", "czytnik", "convert to epub".
---

# EPUB na czytnik (Kindle)

Instrukcja przygotowania pliku EPUB do czytania na czytniku. Źródłem jest Markdown z metadanymi YAML,
budowanie robi pandoc, a gotowy plik sprawdza skrypt kontrolny.

Pliki skilla:

- `assets/style.css`: arkusz stylów dla EPUB (ramki, tabele, czerwone wyróżnienia).
- `assets/szablon.md`: szablon pliku źródłowego z wszystkimi konwencjami.
- `scripts/build_epub.py`: buduje EPUB3 z właściwymi opcjami pandoc.
- `scripts/check_epub.py`: kontrola gotowego pliku przed wysłaniem.

---

## 1. Ogólna zasada

- Źródłem jest **Markdown** z metadanymi YAML. Nie konwertujemy bezpośrednio z `.tex`, bo pandoc gubi
  własne makra i środowiska (np. `tcolorbox`, `\newcommand`).
- Jeśli dokument istnieje już w LaTeX-u, przepisz jego treść 1:1 do Markdown. Nie skracaj i nie zmieniaj
  liczb. Tekst ma być identyczny z aktualną wersją PDF.
- Budujemy **EPUB3** pandoc-iem, ze wzorami w **MathML** i plikiem `assets/style.css`.
- Język polski, styl przyjazny dla oka: krótkie akapity, pogrubione hasła na początku punktów,
  wzory zebrane w dodatku na końcu, a nie w środku tekstu.
- Autora (`author`) bierz od użytkownika lub z dokumentu źródłowego. Nie zgaduj.

---

## 2. Struktura pliku Markdown

Zacznij od kopii `assets/szablon.md`. Skrócony wzór:

```markdown
---
title: Tytuł dokumentu
author: Imię Nazwisko
date: Październik 2026
lang: pl-PL
---

# Rozdział 1          ← każdy rozdział (#) zaczyna się w EPUB na nowej stronie

## Podrozdział         ← poziom 2 widoczny w spisie treści czytnika

Zwykły akapit z **pogrubieniem**, *kursywą* i `kodem`.

::: wazne
**Najważniejsza myśl sekcji** w niebieskiej ramce.
:::

| kolumna | kolumna |
|:---|:-:|
| tekst | [czerwony]{.zle} |

# Dodatek: wzory

$$\text{F1} = \frac{2 \cdot P \cdot R}{P + R}$$
```

Konwencje:

- **Ramki z najważniejszą myślą:** blok `::: wazne ... :::`. Używaj oszczędnie, 1–2 na rozdział
  (np. zasada rankingu, wniosek z przykładu, najbliższe kroki).
- **Wyróżnienie błędu / ważnej wartości na czerwono:** `[tekst]{.zle}`.
- **Brakujące wartości do uzupełnienia:** `[?]{.uzup}` (czerwone). Nie zostawiaj ich w wersji końcowej.
- **Tabele:** zwykłe tabele Markdown; czytnik dostaje obramowanie i nagłówek z tłem z CSS.
- **Wzory:** `$...$` w tekście, `$$...$$` jako osobny wiersz. Polski przecinek dziesiętny we wzorach
  pisz jako `0{,}3`.
- **Kreski:** zakresy liczbowe z półpauzą (`11 185–90 651`, `1–4`). W tekście nie używaj myślników
  jako wtrąceń; zamiast tego przecinek, średnik albo dwukropek.
- **Bez spisu treści w tekście.** Spis treści jest w menu czytnika (generuje go pandoc).
- **Bez emoji.**

---

## 3. Plik CSS

Używaj `assets/style.css` bez zmian, chyba że użytkownik prosi inaczej.

Kindle jest czarno-biały: kolory i tła są dodatkiem. Każde wyróżnienie musi być też pogrubione
albo w ramce, żeby było widoczne bez koloru.

---

## 4. Budowanie

Wymagany jest `pandoc` (2.19+, ze względu na `--split-level`). Najprościej skryptem:

```bash
python scripts/build_epub.py tekst.md -o NAZWA.epub
```

Skrypt sam podaje ścieżkę do `assets/style.css`. Równoważne wywołanie ręczne:

```bash
pandoc tekst.md -o NAZWA.epub \
  --to epub3 --mathml --css <skill>/assets/style.css \
  --toc --toc-depth=2 --split-level=1
```

- `--split-level=1`: każdy rozdział `#` w osobnym pliku, czyli od nowej strony.
- `--toc --toc-depth=2`: spis treści w menu czytnika (rozdziały i podrozdziały).
- `--mathml`: wzory jako MathML, a nie obrazki.
- Nazwa pliku: bez spacji i polskich znaków, np. `MTAH_2027_wprowadzenie.epub`.

---

## 5. Kontrola przed wysłaniem

1. Uruchom kontrolę:

   ```bash
   python scripts/check_epub.py NAZWA.epub --source tekst.md
   ```

   Skrypt sprawdza: język `pl-PL`, obecność wzorów w `<math>` (jeśli źródło ma wzory),
   ramki `class="wazne"` i wyróżnienia `class="zle"` (jeśli źródło ich używa),
   brak pozostawionych `[?]{.uzup}`, brak emoji i nazwę pliku bez spacji i polskich znaków.
   Kod wyjścia różny od 0 oznacza błąd do poprawienia.
2. Ręcznie porównaj liczby w tabelach z aktualną wersją PDF/TeX. Tego skrypt nie zrobi.

---

## 6. Wzory a Kindle (ważne)

- Kindle (i konwersja Amazonu) **może źle wyświetlić MathML**: ułamki, sumy, indeksy.
- Dlatego wzory trzymamy **w dodatku na końcu**, a główny tekst ma być zrozumiały bez nich.
- Jeśli użytkownik zgłosi, że wzory się rozjeżdżają: wyrenderuj każdy wzór do PNG
  (np. LaTeX → `dvipng` albo matplotlib mathtext, ok. 300 dpi, białe tło) i wstaw jako obrazek
  `![wzór](wzor1.png)` z czytelnym tekstem alternatywnym.
