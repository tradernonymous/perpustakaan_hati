# Edisi Poket: Pulang kepada Suara Sendiri

A pocket edition built from Rahimam's Threads post
[`DfmG-LrkQrM`](https://www.threads.com/@rahimam/post/DfmG-LrkQrM).

## What it is

A free tier-1 booklet, A4 portrait, fourteen pages, in the Perpustakaan Hati
dark stage (Gilded Grove). It is a gentle guide to naming the experience of
not being heard in a relationship, and to giving your own voice room again
after a breakup, without turning the blame inward.

Each chapter runs across two pages: the thinking, then the practice. That is
what lets the edition hold one type scale: a page that carried its prose, its
chart, its steps and its closing line together had to shrink its type to fit,
which made the same element a different size on every page.

| Page | Content |
|---|---|
| 1 | Cover: "Pulang kepada Suara Sendiri", foil wordmark, Edisi Poket seal |
| 2 | The post, quoted verbatim, with the "X" = "tak" gloss |
| 3 | 01 Apabila Kita Berhenti Bercerita |
| 4 | 01 practice: Mengenali Apa yang Kamu Tahan, three steps |
| 5 | 02 Menamakan Apa yang Terasa |
| 6 | 02 practice: Dua Senarai yang Dipisahkan, three steps |
| 7 | 03 Mendengar Semula Diri Sendiri |
| 8 | 03 practice: Lima Minit, Tiga Soalan, three steps |
| 9 | 04 Menyuarakan Keperluan dengan Lembut dan Jelas |
| 10 | 04 practice: Empat Ayat untuk Mula, four tip cards |
| 11 | 05 Membina Kepercayaan terhadap Suara Sendiri |
| 12 | 05 practice: Langkah Kecil Minggu Ini, three steps |
| 13 | 06 Kad Refleksi: printable worksheet |
| 14 | Sudut Keselamatan: HEAL 15555, Befrienders KL, 999. No pitch |

## Source files

| File | Role |
|---|---|
| `content/ebooks/edisi-poket-pulang-kepada-suara-sendiri/manuscript.md` | The copy. Single source of truth. |
| `content/ebooks/edisi-poket-pulang-kepada-suara-sendiri/assets/` | Seven art panels, five step icons, one ornament divider |
| `packages/ebook-builder/ebook_builder/pocket.py` | Parser, typesetter, layout audit, renderer |
| `packages/ebook-builder/ebook_builder/pocket_cli.py` | Command line entry point |
| `packages/ebook-builder/tests/test_pocket.py` | Tests |
| `docs/brand/preview/ebook-edisi-poket-pulang-kepada-suara-sendiri.pdf` | Built artefact |

Build:

```
cd packages/ebook-builder
uv run --project . python -m ebook_builder.pocket_cli \
  ../../content/ebooks/edisi-poket-pulang-kepada-suara-sendiri/manuscript.md \
  --out ../../docs/brand/preview/ebook-edisi-poket-pulang-kepada-suara-sendiri.pdf
```

## Editorial rules

- **"X" stays on the post, "tak" everywhere else.** The post is Rahimam's
  own words and is quoted as sent. The book's prose spells it out.
- **No numbers, so nothing to cite.** This edition carries no charts: every
  claim in it is qualitative and belongs to the reader's own experience. The
  only source is the reference post itself, quoted verbatim on page 2.
- **No pitch.** The closing page carries the helplines and nothing else.
- **Malay sentence case** in body copy, Title Case for headings, tier names
  exactly as `docs/brand/tier-naming.md` fixes them.
- **No em dash.** The brand copy rule forbids it in reader-facing text.

## Art

Seven panels in `assets/` (telephone, two chairs, brass tags, journal and
pen, half-open door, lanterns, hanging lantern), supplied as full-resolution
square renders and prepared in two steps:

1. **Trimmed to the band that prints.** The panel is a 56 mm strip with a
   feathered mask, so each square was cropped to its centre band and resized
   to 1760 px wide, matching the pixel density of the sibling editions.
2. **Graded to the stage.** The renders arrive on warm brown or cream
   grounds, which print as bright rectangles on the forest-night page. Each
   panel has its highlights normalised to roughly 0.62 luminance, then
   blended 32% toward `--forest-night` (`#07140d`) with a small contrast
   lift, so the gold survives and the field dissolves into the sheet.

Unmodified copies of the renders are kept outside the repo in
`/tmp/opencode/art-originals/`. Regrading is idempotent only on the trimmed
files: re-copy the originals before running a new grade.

## Toolchain notes

- **Chrome, not WeasyPrint.** WeasyPrint does not implement
  `-webkit-background-clip: text`, so the cover's foil wordmark prints as a
  flat band. The wordmark is rasterised in the screenshot path and embedded.
- **The layout audit is part of the build.** Chrome measures each page's
  fill, every text block's last line, and the computed size of each text
  role. A page that overflows or sits too thin, a block whose last line holds
  one word, a clipped quote, or a role that renders at a different size on
  another page fails the build.
- **One type scale, one rhythm.** Every page is set from the same `--base`
  (21px) and the same `--rhythm` (1.3em) gap between blocks. A page that
  cannot hold its copy gets less copy, not smaller type.
- **Pull quotes are one line.** They are set `nowrap` and the audit fails the
  build when one clips, so closing lines stay under about 78 characters.

## Citations

- Rahimam, Threads post `DfmG-LrkQrM`, quoted verbatim on page 2
- Talian HEAL 15555; Befrienders KL: 03-7627 2929; talian kecemasan 999
