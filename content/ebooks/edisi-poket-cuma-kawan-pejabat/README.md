# Edisi Poket: Cuma Kawan Pejabat

The pocket edition built from Rahimam's Threads post
[`DnK_N67Oz`](https://www.threads.com/share/DnK_N67Oz).

## What it is

A free tier-1 booklet, A4 portrait, thirteen pages, in the Perpustakaan Hati
dark stage (Gilded Grove). It is not a flowing book: every page is composed,
because it was written to be read on a phone while waiting for the bus.

Each chapter runs across two pages: the thinking, then the evidence. That is
what lets the edition hold one type scale: a page that carried its prose, its
chart, its steps and its closing line together had to shrink its type to fit,
which made the same element a different size on every page.

| Page | Content |
|---|---|
| 1 | Cover: "Cuma Kawan Pejabat", foil wordmark, Edisi Poket seal |
| 2 | The thread, quoted verbatim, with the "X" = "tak" gloss |
| 3 | 01 Separuh yang Benar: what a half-truth is |
| 4 | 01 evidence: chart, IFS 2024 · three steps |
| 5 | 02 Dua Sisi, Satu Meja: both sides |
| 6 | 02 evidence: chart, Shirley Glass · three steps |
| 7 | 03 Yang Dikatakan, Yang Diam: half-truth vs honesty |
| 8 | 03 evidence: chart, MPFS-5 · three steps |
| 9 | 04 Amalan: Yang Menyimpan: three steps |
| 10 | 05 Amalan: Yang Tertinggal: three steps |
| 11 | 06 Ayat Penuntun: three sourced Islamic quotes |
| 12 | 07 Kad Refleksi: printable worksheet |
| 13 | Sudut Keselamatan: HEAL 15555, Befrienders KL, 999. No pitch |

## Source files

| File | Role |
|---|---|
| `content/ebooks/edisi-poket-cuma-kawan-pejabat/manuscript.md` | The copy. Single source of truth. |
| `packages/ebook-builder/ebook_builder/pocket.py` | Parser, typesetter, layout audit, renderer |
| `packages/ebook-builder/ebook_builder/pocket_cli.py` | Command line entry point |
| `packages/ebook-builder/tests/test_pocket.py` | Tests |
| `docs/brand/preview/ebook-edisi-poket-cuma-kawan-pejabat.pdf` | Built artefact |

Build:

```
cd packages/ebook-builder
uv run --project . python -m ebook_builder.pocket_cli \
  ../../content/ebooks/edisi-poket-cuma-kawan-pejabat/manuscript.md \
  --out ../../docs/brand/preview/ebook-edisi-poket-cuma-kawan-pejabat.pdf
```

## Editorial rules

- **"X" stays on the thread, "tak" everywhere else.** The post is Rahimam's
  own words and is quoted as sent. The book's prose spells it out.
- **Every number is cited on the page.** A chart without a source line is
  rejected by the parser.
- **No pitch.** The closing page carries the helplines and nothing else.
- **Malay sentence case** in body copy, Title Case for headings, tier names
  exactly as `docs/brand/tier-naming.md` fixes them.

## Toolchain notes

- **Chrome, not WeasyPrint.** WeasyPrint does not implement
  `-webkit-background-clip: text`, so the cover's foil wordmark prints as a
  flat band. Chrome's print path drops it too, so the wordmark is rasterised
  in the screenshot path, where the gradient does clip to the glyphs, and the
  PNG is embedded on the cover.
- **The layout audit is part of the build.** Chrome measures each page's fill,
  every text block's last line, and the computed size of each text role. A
  page that overflows or sits too thin, a block whose last line holds one word,
  a clipped quote, or a role that renders at a different size on another page
  fails the build.
- **One type scale, one rhythm.** Every page is set from the same `--base`
  (21px) and the same `--rhythm` (1.3em) gap between blocks. Nothing scales a
  page to fill its sheet: a page that cannot hold its copy gets less copy, not
  smaller type. That is what keeps a body paragraph the same size on page 3 as
  on page 11.
- **Closing quotes sit in the flow.** Each page's pull quote is one line at
  0.78em, set under a hairline rule, so it reads as a closing beat rather than
  another paragraph.

## Citations

- Institute for Family Studies, tinjauan iFidelity (n=2,000 dewasa AS, Julai 2024)
- Shirley Glass, *Not "Just Friends"* (1997)
- Tinjuan Penduduk dan Keluarga Malaysia ke-5, MPFS-5 (2014)
- Tinjauan NORC, University of Chicago (1990–2002)
- Sahih al-Bukhari 6018; Sahih al-Bukhari 33; Sahih Muslim 58; Al-Quran, An-Nisa 4:58
