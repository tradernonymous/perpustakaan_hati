# Asset register · November 2026

Paths are relative to the repository root. This register covers assets used in the refreshed catalog, edition exports, and launch film. The edition proofs and launch film were approved for release. The repository carries the approved free PDF, cover images, and delivery encodes. The two paid masters belong on the private delivery volume. No image generation service was used for this refresh.

## Editorial reference

The local [Perkara Kecil, Hati Kenyang PDF](../../preview/ebook-edisi-poket-perkara-kecil-hati-kenyang.pdf) supplies the forest-green page treatment, fine gilt rules, chapter numerals and reflection-panel structure. Its project README identifies the 14-page edition as the PKK sequence on the Doop canvas. The refinement reuses the project logo and tier seals with its own geometry and type. The two linked live frames were unavailable during review.

## Edition covers

Each cover reproduces page 1 of its own edition. The artwork combines the manuscript's title and subtitle, the tier layout, the book-heart emblem, and a project-drawn seal. The images contain the full page, centered, with no crop. The credited author in the edition layout is @rahimam. The project brief authorizes use on the bookstore and in the launch film. A separate grant for redistribution of the books or brand marks is not on file here.

| Edition and catalog alt text | Source manuscript in `content/ebooks/` | Seal in `docs/brand/assets/` | Output filename in both galleries |
|---|---|---|---|
| Kulit Edisi Poket | `tier-1-free/manuscript/edisi-poket.md` | `seal-edisi-poket.svg` | `cover-poket.png` |
| Kulit Edisi Membangun | `tier-2-standard/manuscript/edisi-membangun.md` | `seal-edisi-membangun.svg` | `cover-membangun.png` |
| Kulit Teman Hidup | `tier-3-premium/manuscript/teman-hidup.md` | `seal-teman-hidup.svg` | `cover-teman-hidup.png` |

The 1197 × 1804 px gallery is `docs/brand/preview/`. The 599 × 902 px PNGs in `apps/web/public/ebooks/` retain the established catalog URLs. Rebuild both sets with the command documented in `packages/brand-tools/build-tier-covers.py`. It typesets fresh, buyer-neutral PDFs from the three named manuscripts and rasterizes only page 1 with Poppler at 200 and 100 dpi. Older cover designs are recoverable from commit `e3bbc76` under the same filenames.

## Poket topic covers in the catalog

These existing previews are sourced from page 1 of the named PDFs in `docs/brand/preview/`. The cover derivatives are centered, fully contained on a 560 × 792 px canvas, with WebP for modern clients and a JPEG fallback. For each row, both files are in `apps/web/public/ebooks/`. Their shared builder is `apps/web/scripts/build-ebook-covers.mjs`.

| Catalog alt text | Source PDF | WebP and JPEG basenames |
|---|---|---|
| Kulit A4 ebook Ruang atau Hukuman | `ebook-edisi-poket-ruang-atau-hukuman.pdf` | `ruang-atau-hukuman-a4` |
| Kulit A4 ebook Perkara Kecil, Hati Kenyang | `ebook-edisi-poket-perkara-kecil-hati-kenyang.pdf` | `perkara-kecil-hati-kenyang-a4` |
| Kulit A4 ebook Pulang kepada Suara Sendiri | `ebook-edisi-poket-pulang-kepada-suara-sendiri.pdf` | `pulang-kepada-suara-sendiri-a4` |
| Kulit A4 ebook Cuma Kawan Pejabat | `ebook-edisi-poket-cuma-kawan-pejabat.pdf` | `cuma-kawan-pejabat-a4` |
| Kulit A4 ebook Tips Psikologi Suami Isteri | `ebook-edisi-poket-tips-psikologi-suami-isteri.pdf` | `tips-psikologi-suami-isteri-a4` |

The first four editions have source manuscripts and editorial acknowledgments in their respective `content/ebooks/edisi-poket-*/` directories. The fifth has a reference PDF in this checkout. The PDFs establish the page used for each derivative. The individual creators, original licensing of embedded illustrations, generation models, prompts, seeds, and approval records are unverified. Their scope here is the existing first-page catalog preview.

## Marks, ornaments, and type

| Asset | Creator or source | Derivative, size, and placement | Permission or evidence |
|---|---|---|---|
| Three edition seals | Perpustakaan Hati geometry in `packages/brand-tools/build-logos.py` | SVG masters in `docs/brand/assets/`, each with a 600 × 600 viewBox. Circle, hexagon, and arch respectively; preserve the full outline. Decorative next to the edition name. | Embedded SVG notes identify ebook covers and store cards as intended uses. |
| Book-heart emblem | `docs/brand/assets/emblem-book-heart.svg` (600 × 420 viewBox) | Embedded in all three PDFs. The catalog displays the exported Poket cover and the site header uses the animated emblem. | Existing project mark. |
| Edition rules, frames, and writing lines | Perpustakaan Hati layout in `packages/ebook-builder/templates/ebook-interior.html` | Vector and CSS geometry in the edition pages. Decorative, with dimensions set by the page layout. | Built with the edition; no separately sourced texture. |
| Fraunces display and italic | The Fraunces Project Authors. Source files `Fraunces.ttf` and `Fraunces-Italic.ttf` | `FrauncesDisplay.woff2` and `FrauncesDisplayItalic.woff2` | SIL Open Font License 1.1, recorded in the source fonts' name tables. |
| Inter UI | The Inter Project Authors, Rasmus Andersson. Source `Inter.ttf` | `InterUI.woff2` | SIL Open Font License 1.1, source name table. |
| Source Serif 4 body | Adobe Systems Incorporated, Frank Grießhammer. Source `SourceSerif4.ttf` | `SourceSerifText.woff2` | SIL Open Font License 1.1, reserved name “Source,” source name table. |

The source TTFs live in `packages/brand-tools/fonts/source/`. The subsetter `packages/brand-tools/build-fonts.py` produces the self-hosted WOFF2 files in the parent directory. Font and vector assets have no generation prompt or seed. The repository carries an MIT notice for its software and associated documentation. Embedded publications and fonts have their own provenance.

## Interior samples

Each 599 × 902 px PNG uses one complete page of the final 152 × 229 mm PDF at 100 dpi. The samples share the manuscripts, attribution, and type sources of their respective covers. The Membangun and Teman Hidup samples live with the local review outputs.

| Edition | Source in `dist/editions/` | Sample and intended surface | Alt text |
|---|---|---|---|
| Poket | `edisi-poket.pdf`, p. 4 | `docs/brand/specimens/edisi-poket-sample.png` · free design specimen | Kad Refleksi pada halaman hijau dengan ruang menulis. |
| Membangun | `edisi-membangun.pdf`, p. 20 | `dist/editions/specimens/edisi-membangun-sample.png` · internal proof | Halaman Soalan 1 dengan ruang menulis. |
| Teman Hidup | `teman-hidup.pdf`, p. 40 | `dist/editions/specimens/teman-hidup-sample.png` · internal proof | Kad refleksi hijau pada halaman hitam. |

## Rights declarations — 21 November 2026

Declared by the project owner:

- **Score.** `videos/edisi-poket-launch-v2/src/score.rb` is an original composition owned by the project. No third-party composer or music license is required for the launch film or its delivery encodes.
- **Brand marks.** The three edition seals, book-heart emblem, monogram and copy stamps, lockup, edition rules/frames, and layout geometry are project-owned design. Grant recorded for use on the storefront, inside the edition PDFs, and in the launch film, including free redistribution of the Edisi Poket edition. Paid edition masters remain private delivery assets and are not redistributed.
- **Poket authorship.** The credited author is @rahimam. A short redistribution-and-artwork permission note is drafted at `docs/brand/assets/refresh-2026-11/poket-author-permission.md` and awaits signature; until countersigned, treat the Poket redistribution grant as pending rather than on file.

## Launch film, end cards, and posters

The film source is `videos/edisi-poket-launch-v2/src/build_editions.py`. It composes five scenes from the three catalog cover PNGs, the project fonts listed above, and original editorial lettering. The Poket prompt comes from its free manuscript. Its accompanying detail is a crop of the reflection field on page 4 of `content/ebooks/tier-1-free/edisi-poket.pdf`. The Membangun and Teman Hidup cards are original editorial treatments for this film. Highlighted covers retain the full page, with text and art positioned independently for each ratio.

The instrumental score is labeled original in `src/score.rb` within the video project. The production uses its project recording `src/score_render.wav` with a 25-second trim and fades. The launch project supplies the score for this use. No voiceover or external recording was added. Owner declaration, 21 November 2026: the score is an original composition written for this project (`score.rb`, Sonic Pi) and is owned by the project; no third-party composer or music license applies.

| Surface | Frame and composition | Outputs in `videos/edisi-poket-launch-v2/renders/` |
|---|---|---|
| Vertical | 1080 × 1920, text above tier covers | `editions-9x16.mp4`, `editions-9x16.jpg` |
| Feed portrait | 1080 × 1350, shorter stacked layout | `editions-4x5.mp4`, `editions-4x5.jpg` |
| Landscape | 1920 × 1080, type left and books right | `editions-16x9.mp4`, `editions-16x9.jpg` |

Each poster samples its own end card at 21 seconds. Poster alt text for all three is “Tiga kulit buku Perpustakaan Hati dengan pelawaan untuk bermula dengan Edisi Poket.” Full-resolution exports remain in the video project. The storefront uses the H.264/AAC delivery encodes in `apps/web/public/launch/` and its landscape `poster.jpg`. The player keeps video loading on demand and links to both portrait formats.
