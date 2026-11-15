# Edisi Poket: Perkara Kecil, Hati Kenyang

A pocket edition built from Rahimam's Threads post
[`DfhY2C_j1cC`](https://www.threads.com/@rahimam/post/DfhY2C_j1cC).

## What it is

A free tier-1 booklet, A4 portrait, fourteen pages, in the Perpustakaan Hati
dark stage (Gilded Grove). It is a practical guide to showing attention
through ordinary daily gestures, without waiting for a special occasion.

Each chapter runs across two pages: the thinking, then the practice. That is
what lets the edition hold one type scale: a page that carried its prose, its
chart, its steps and its closing line together had to shrink its type to fit,
which made the same element a different size on every page.

| Page | Content |
|---|---|
| 1 | Cover: "Perkara Kecil, Hati Kenyang", foil wordmark, Edisi Poket seal |
| 2 | The post, quoted verbatim, with the "X" = "tak" gloss |
| 3 | 01 Kenali Apa yang Membuat Pasangan Rasa Dihargai |
| 4 | 01 practice: five ways people feel appreciated, three steps |
| 5 | 02 Gestur Kecil yang Boleh Dimulakan Hari Ini |
| 6 | 02 practice: small gestures, three steps |
| 7 | 03 Tunjukkan Perhatian dalam Rutin Harian |
| 8 | 03 practice: three openings in the daily routine, three steps |
| 9 | 04 Ucapkan Penghargaan dengan Ikhlas |
| 10 | 04 practice: general thanks vs specific thanks, three steps |
| 11 | 05 Kekal Konsisten tanpa Mengejar Kesempurnaan |
| 12 | 05 practice: small and often vs large and rare, three steps |
| 13 | 06 Kad Refleksi: printable worksheet |
| 14 | Sudut Keselamatan: HEAL 15555, Befrienders KL, 999. No pitch |

## Source files

| File | Role |
|---|---|
| `content/ebooks/edisi-poket-perkara-kecil-hati-kenyang/manuscript.md` | The copy. Single source of truth. |
| `packages/ebook-builder/ebook_builder/pocket.py` | Parser, typesetter, layout audit, renderer |
| `packages/ebook-builder/ebook_builder/pocket_cli.py` | Command line entry point |
| `packages/ebook-builder/tests/test_pocket.py` | Tests |
| `docs/brand/preview/ebook-edisi-poket-perkara-kecil-hati-kenyang.pdf` | Built artefact |

Build:

```
cd packages/ebook-builder
uv run --project . python -m ebook_builder.pocket_cli \
  ../../content/ebooks/edisi-poket-perkara-kecil-hati-kenyang/manuscript.md \
  --out ../../docs/brand/preview/ebook-edisi-poket-perkara-kecil-hati-kenyang.pdf
```

## Editorial rules

- **"X" stays on the post, "tak" everywhere else.** The post is Rahimam's own
  words and is quoted as sent. The book's prose spells it out.
- **Every number is cited on the page.** A chart without a source line is
  rejected by the parser.
- **A model says it is a model.** The five charts in this edition are
  illustrative: each carries a note naming it a model and a source line naming
  the writing framework it comes from, so no reader mistakes it for a survey.
- **No pitch.** The closing page carries the helplines and nothing else.
- **Malay sentence case** in body copy, Title Case for headings, tier names
  exactly as `docs/brand/tier-naming.md` fixes them.

## Artwork

The illustrations are shared with the two earlier pocket editions: gold
line-art on a forest field, reused rather than regenerated. Each page's art is
named in the manuscript and resolved from this folder, so a replacement is one
file swap.

| File | Used on |
|---|---|
| `art-thread.png` | Post Asal |
| `art-perhatian.png` | 01 Kenali |
| `art-gestur.png` | 02 Gestur |
| `art-rutin.png` | 03 Rutin |
| `art-penghargaan.png` | 04 Penghargaan |
| `art-konsisten.png` | 05 Konsisten |
| `art-selamat.png` | reserved for the closing page |
| `icon-*.png`, `ornament-divider.png` | steps and openers |

## Toolchain notes

- **Chrome, not WeasyPrint.** WeasyPrint does not implement
  `-webkit-background-clip: text`, so the cover's foil wordmark prints as a
  flat band. Chrome's print path drops it too, so the wordmark is rasterised
  in the screenshot path and the PNG is embedded on the cover.
- **The layout audit is part of the build.** Chrome measures each page's fill,
  every text block's last line, and the computed size of each text role. A
  page that overflows or sits too thin, a block whose last line holds one word,
  a clipped quote, or a role that renders at a different size on another page
  fails the build.
- **One type scale, one rhythm.** Every page is set from the same `--base`
  (21px) and the same `--rhythm` (1.3em) gap between blocks. Nothing scales a
  page to fill its sheet: a page that cannot hold its copy gets less copy, not
  smaller type.
- **Closing quotes sit in the flow.** Each page's pull quote is one line at
  0.78em, set under a hairline rule, so it reads as a closing beat rather than
  another paragraph.

## Design reference on Doop

Canvas `https://doop.design/c/yZvMtpvIa0` carries this edition as
`PKK p01` through `PKK p14` (794 × 1123), in their own column at x = 12520 so
they sit clear of the earlier PDF / PDF2 / PDF3 runs.
