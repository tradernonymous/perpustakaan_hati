# Multi-Format Design System

Phase 1 deliverable covering three output surfaces from one token source
(`docs/brand/design-tokens.css`).

## 1. Web UI Kit (Next.js + Tailwind + shadcn/ui)

### Layout
- Mobile-first, single column, max content width `--content-reading: 640px` for reading, `--content-grid: 1200px` for landing grids, `--content-chat: 760px` for Teman Hati.
- Warmer share: green 50 / gold 40 / ruby + cream 10. Green still leads; gold warmth rises.
- The web shell uses `ph-nightlight ph-void ph-storefront`. Raised bands and cards use `--surface-raised`. Covers, seals and posters use their edition-specific treatments.
- Sticky bottom CTA on mobile (checkout, tier selection) — 56px tall, green gradient fill, `forest-night` label.

### 3.6 utilities (web)
| Utility | What it does |
|---|---|
| `:focus-visible` | global 2px ring, offset 2px, `--focus-color` (green-300 dark / green-800 light) |
| `::selection` | green selection fill with a measured label colour |
| `.ph-balance` / `.ph-pretty` | `text-wrap: balance` / `pretty` (already applied to headings and paragraphs) |
| `.ph-nums` | tabular numerals for stats, prices and tables |
| `.ph-elev-1..4` / `shadow-elev-1..4` | the elevation ladder; the theme scope decides the material |
| `.ph-cv` | opt-in `content-visibility: auto` for very long sections |

### Components
| Component | Spec |
|---|---|
| Button primary | `.ph-cta` uses the green gradient, pill radius, Geist Sans 600, and a raised edge that compresses on press |
| Button secondary | 1px `gold` border, text `gold-light`, bg transparent |
| Button tier-select | 1px tier-colour border, tier-colour label, `gold` fill on selected |
| Card | bg `daylight-raised`, 1px `daylight-edge`, radius 8px, `shadow-depth-1` on hover → `shadow-depth-2` (dark-stage cards keep `forest-raised` + gold hairline) |
| Featured card | bg `forest-soft`, `shadow-depth-2`, top 1px `green-700` highlight rule |
| Tier card | Tier rim, Instrument Serif title and price, and a tier shape (circle / hexagon / arch) beside the badge |
| Catalog cover | Pair `.ph-book-stage` and `.ph-book-object` around the cover artwork. The object projects from a paper edge with the edition’s bevel. Fine pointers get a hover tilt. |
| Chapter preview | bg `cream`, text `ink`, serif body for the reading sample |
| Trust badge | 1px `gold-deep` border, `gold` text, 11px uppercase |
| Input | bg `daylight-soft`, 1px `daylight-edge`, focus 2px `green-700` ring, error 1px `burgundy-light` |
| Healing progress | green-to-gold gradient track, travelling glow, text percentage always visible |
| Footer | bg `sage`, top 1px `gold-ink-soft` rule, `muted-grove` text |

### Typography in web
- Hero `Instrument Serif` regular, 44–120px fluid, line-height 0.98, tracking −0.02em
- Headings and pull quotes use `Instrument Serif`. Pull quotes use the italic face.
- Section titles tighten to −0.012em tracking, line-height 1.05
- Body `Geist Sans` 17px, `text-on-dark`, line-height 1.55, optical sizing auto
- Labels `Geist Sans` 12–14px, weight 500–600
- Reading sample body `Source Serif 4` 17px, line-height 1.7

### Brand fonts
The storefront loads `apps/web/styles/fonts.css` before Tailwind in
`apps/web/app/globals.css`. Font files and notices live in `apps/web/public/fonts/`.

```css
@import "../styles/fonts.css";
```

| role | family | where |
|---|---|---|
| Display | Instrument Serif | Storefront headings, pull quotes and tier names |
| Body / UI | Geist Sans (variable) | Storefront copy, buttons, labels and form fields |
| Reading | Source Serif 4 (variable) | Long-form eBook body and chapter previews |
| Publishing display and UI | Fraunces and Inter (variable) | Cover titles, publishing templates and folios |

### shadcn/ui mapping
shadcn default tokens are neutral-light. Override in `globals.css`:
```
--background: var(--forest-night)
--foreground: var(--text-on-dark)
--primary: var(--green-500)
--primary-foreground: var(--forest-night)
--secondary: var(--forest-soft)
--accent: var(--gold)
--accent-foreground: var(--forest-night)
--border: var(--forest-edge)
--ring: var(--green-400)
--radius: 0.25rem
```

> **Change from Phase 1:** `--primary` was `terracotta`; it is now the
> healing green. Terracotta is reserved for conversion accents only —
> price tags, urgency badges, the final CTA block on a cream band.

### Charts (locked 2026-11-08)
- `--chart-1` green-500, `--chart-2` gold, `--chart-3` burgundy-light, `--chart-4` lantern, `--chart-5` mint-glass. Never rename.
- Pair every series with a direct label or shape. Color never carries meaning alone.

### Teman Hati companion chat
- Surface: `--companion-bg`, bubbles `--companion-bubble-assistant` (forest-raised + gold hairline) and `--companion-bubble-user` (green gradient, forest label). Input: `--companion-input-bg`, focus `--focus-ring`.
- Glass sheet: `.ph-glass` (`--glass-bg`, `--glass-blur: 18px`). Tilt card: `.ph-tilt` (`--tilt-perspective: 1200px`, `--tilt-max: 6deg`). Particles: `--particle-count: 42`, `--companion-particle: mint-glass`.
- WebGL loads only on companion and games. Reading and checkout never use WebGL. Static fallback and `prefers-reduced-motion: reduce` zero-motion required.

## 2. eBook Layout Templates

### Page geometry

The edition masters use a 152 × 229 mm trim with 16 mm side margins, a 19 mm top margin, and an 18 mm bottom margin. Source Serif 4 sets the body at 11.25 pt. Fraunces sets the display text, and Inter sets the running header, folios and labels.

| Edition | Ground and cover | Reading and writing elements |
|---|---|---|
| Edisi Poket | Forest-green wash, double gilt arch, book-heart emblem and circular seal | Cream type, sage numerals, gold rules, checkbox list, seven-day sequence, reflection and note panels |
| Edisi Membangun | White paper, green binding stripe, emblem and hexagonal seal | Green headings, warm writing panels, one question per worksheet page |
| Teman Hidup | Near-black ground, double gold frame, emblem and arched seal | Roman chapter dividers, green journal and reflection fields, bordered scripts that stay together |

All three use linked contents with folios, a running edition label and recurring page-number placement. Each cover is rendered directly from its manuscript and master template. See the [provenance manifest](assets/refresh-2026-11/manifest.md) for derivative paths.

The next PDF review proofs add botanical linework and a three-step reading panel to Poket. Membangun uses a linked exercise index and lined, fillable worksheets. Teman Hidup uses orbital vector artwork, a linked 30-day map, a day-position strip and separate journal and next-step fields. Form fields are standard AcroForm text widgets. Their writing lines are printed as page artwork, so the pages work on paper as well as in PDF readers that support forms.

### Watermark
- Every paid page: `Cop Perpustakaan Hati` diagonal at −20°, 10% opacity, `gold-deep`, bottom-right.
- Buyer line: `<Nama Pembeli> · <email>` 7pt, 14% opacity, bottom-center, on pages 2–6 only (so spread reads clean).

## 3. Threads Visual Kit

### Sizes
- Quote card 1080×1350 (4:5), carousel panel 1080×1080, story 1080×1920.
- Template as 3×4 grid at 270×338px each.

### Quote card layout
Three templates ship in `content/threads/templates/`, all 1080×1350 (4:5) and
all built on Design System 3.1 "Gilded Grove":

| Template | File | Composition |
|---|---|---|
| A — left aligned | `quote-card.html` | emblem top-left, quote block left, wordmark + tier seal along the bottom |
| B — centred | `quote-card-b.html` | emblem centred, quote centred, foil wordmark + tier pill centred below |
| C — gilded ribbon | `quote-card-c.html` | the cover's double gilt frame, left-aligned editorial quote, foil wordmark left + green `.ph-ribbon` tier band and seal right |

Shared rules for all three:
- Ground `forest-night`, one key glow (lantern-dominant on B, emerald-dominant on C), vignette.
- Kicker: `by @rahimam` flanked by gold rules via `.ph-kicker`. The handle is lowercase with the `@` in a rainbow-ring badge: `.ph-handle` + `.ph-at`.
- Quote: Fraunces 72–76px, `gold-light`, line-height ~1.23, `cream` for the emphasised phrase.
- Tagline: Source Serif 4 italic 28–30px, `green-300`.
- Wordmark: `PERPUSTAKAAN` foil-gold above `HATI` foil-emerald (38/76px on B, 34/72px on C, 104px single line on A).
- Tier: seal 96px minimum, rotated -8deg, tier name + price + one line of tier copy.
- Fonts self-hosted in `packages/brand-tools/fonts/` — never a Google Fonts CDN link.
- Copy is filled at render time: `{{QUOTE_LEAD}}`, `{{QUOTE_EMPH}}`, `{{QUOTE_TAIL}}`.
- Tier class on `.card`: `tier-poket`, `tier-membangun`, `teman-hidup`.

- Grid overlay guide only in the template file, never in the exported PNG.

### Design system showcase sheet

`docs/brand/templates/design-system-3-sheet.html` shows the
Gilded Grove system: the cinematic lockup, foils, the green-led colour share,
the ribbon, seals, card, CTA and the `.ph-stage` atmosphere layers. Preview:
`docs/brand/preview/design-system-3-1.png`. Render it with any headless
Chromium (`--allow-file-access-from-files --window-size=1600,1200`).

### Four fixed social templates

| Template | Ground | Type treatment | Where |
|---|---|---|---|
| Quote card | `forest-night` | Fraunces flat, `gold-light` | 4:5 posts |
| Tutorial carousel | `paper` / `cream` | Fraunces heading, green numeral, gold folio | 1:1 threads |
| Tier comparison | `forest-night` | three `shadow-depth-2` cards, colour + shape | 1:1 threads |
| Event poster | `forest-night` | **3D extruded** Fraunces, gold frame | 4:5 / 9:16 story |

The event poster is the only social template that uses the 3D treatment.
Use `docs/brand/assets/lockup-cinematic.svg` — never a re-typed approximation,
because the extrusion is real vector geometry.

### Image generation direction

Brand imagery should read as *a contemporary library at dusk where deep-green
botanical shadows grow between books and warm gold light enters a window*.

Include: ink-black interiors, deep emerald foliage, antique-gold light,
modern bookbinding, paper grain, human details (hands, letters, turning
pages), restrained dew or glass for contemporary texture.

Avoid: generic smiling stock portraits, fake parchment and scroll clichés,
floating leaves on a green gradient, neon sci-fi effects, large areas of
glossy chrome, decorative leaves around the logo.

```text
A quiet contemporary sanctuary library at dusk, deep forest-green
botanical shadows, warm antique-gold window light, a single open book on
an ink-black table, subtle paper grain, tactile natural materials,
cinematic depth, calm editorial photography, healing atmosphere,
no text, no logo, no excessive ornament
```

### Carousel panel (10 slides)
1. Cover — wordmark, "Karya untuk jiwa yang pernah terluka"
2–7. Six quote panels, one idea per slide
8. Tier ladder — three panels side-by-side showing green / gold / burgundy tiers with prices
9. Problem slide — "Pernah rasa begini?" (teaser of the pain point)
10. CTA — "Mula dengan Edisi Poket — percuma", green button block, handle

### Teaser graphic
- Never a fake screenshot. Use a real book render or typographic card.
- Calendar tile template (from the reference artwork): cream ground, `sepia` text, `terracotta` prayer-time accents, Hijri date in Fraunces italic, one hadith quote per month.

### Export
- sRGB, PNG for photos, JPEG q85 for photos, PDF for print assets.
- Filename: `ph-{tier}-{type}-{n}-{w}x{h}.{ext}` e.g. `ph-pocket-quote-03-1080x1350.png`.
