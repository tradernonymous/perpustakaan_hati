# Edisi Poket: Ruang atau Hukuman

A pocket edition built from Rahimam's Threads post on silence: the
difference between a silence that settles a pair and a silence that punishes
one.

## What it is

A free tier-1 booklet, A4 portrait, nine pages, in the Perpustakaan Hati
dark stage (Gilded Grove). It names two kinds of quiet in the same house,
then gives the reader one thing to try the next night.

The edition is shorter than its siblings because its argument is one
distinction, not a course: "Saya perlukan masa, nanti kita bincang" is a
room when it comes with a time, and a punishment when it does not.

| Page | Content |
|---|---|
| 1 | Cover: "Ruang atau Hukuman", foil wordmark, Edisi Poket seal |
| 2 | The post, quoted verbatim, with the "Tp" and "yg" shorthand kept |
| 3 | 01 Dua Diam, Satu Rumah: the two silences named |
| 4 | 02 Ruang yang Diam Buka: three sayings on when to stay quiet |
| 5 | 03 Amalan: Ruang yang Sihat, three steps |
| 6 | 04 Kad Refleksi: three prompts to write before bed |
| 7 | 05 Dua Laluan, Dua Hujung: the model chart, marked illustrative |
| 8 | 06 Lima Tips Ruang yang Sihat: five tip cards |
| 9 | Pulang Bersama, Bukan Sempurna: closing page with the safety lines |

## Source files

| File | Role |
|---|---|
| `content/ebooks/edisi-poket-ruang-atau-hukuman/manuscript.md` | The copy. Single source of truth. |
| `content/ebooks/edisi-poket-ruang-atau-hukuman/assets/` | Three art panels, three step icons, one ornament divider |
| `packages/ebook-builder/ebook_builder/pocket.py` | Parser, typesetter, layout audit, renderer |
| `packages/ebook-builder/ebook_builder/pocket_cli.py` | Command line entry point |
| `packages/ebook-builder/tests/test_pocket.py` | Tests |
| `docs/brand/preview/ebook-edisi-poket-ruang-atau-hukuman.pdf` | Built artefact |

Build:

```
cd packages/ebook-builder
uv run --project . python -m ebook_builder.pocket_cli \
  ../../content/ebooks/edisi-poket-ruang-atau-hukuman/manuscript.md \
  --out ../../docs/brand/preview/ebook-edisi-poket-ruang-atau-hukuman.pdf
```

## Editorial rules

- **The post is quoted as sent.** "Tp" and "yg" stay on page 2, because
  that is how it was written. The book's own prose spells them out.
- **The one chart says it is a model.** Its numbers are illustrative, and
  the note on the chart says so, so no reader mistakes it for a statistic.
- **No pitch in the closing page.** The safety lines are the last thing on
  the sheet, and nothing follows them.
- **Malay sentence case** in body copy, Title Case for headings, tier names
  exactly as `docs/brand/tier-naming.md` fixes them.
- **No em dash.** The brand copy rule forbids it in reader-facing text.

## Artwork

Eight files in `assets/`, in the same gold line-art on a forest field as the
other pocket editions. Each page's art is named in the manuscript and
resolved from this folder, so a replacement is one file swap.

| File | Used on |
|---|---|
| `art-diam-thread.png` | The post as sent |
| `art-dua-diam.png` | 01 Dua Diam |
| `art-ruang.png` | 03 Amalan |
| `art-selamat.png` | reserved for the closing page |
| `icon-*.png`, `ornament-divider.png` | steps and openers |

## Toolchain notes

- **Chrome, not WeasyPrint.** WeasyPrint does not implement
  `-webkit-background-clip: text`, so the cover's foil wordmark prints as a
  flat band. The wordmark is rasterised in the screenshot path and the PNG
  is embedded on the cover.
- **The layout audit is part of the build.** Chrome measures each page's
  fill, every text block's last line, and the computed size of each text
  role. A page that overflows or sits too thin, a block whose last line holds
  one word, a clipped quote, or a role that renders at a different size on
  another page fails the build.
- **One type scale, one rhythm.** Every page is set from the same `--base`
  (21px) and the same `--rhythm` (1.3em) gap between blocks. Nothing scales a
  page to fill its sheet: a page that cannot hold its copy gets less copy, not
  smaller type.
- **Tip cards are disclosures.** `<details open>` means the print path shows
  every tip and the browser path lets a reader fold one away, with no script.

## Citations

- Rahimam, Threads post on silence, quoted verbatim on page 2
- Sahih al-Bukhari 6018; HR Abu Dawud dan at-Tirmidhi; Al-Quran, Al-Muzzammil 73:10
- Talian HEAL 15555; Befrienders KL: 03-7627 2929; talian kecemasan 999
