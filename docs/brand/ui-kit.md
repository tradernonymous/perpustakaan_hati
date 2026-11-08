# Multi-Format Design System

Phase 1 deliverable covering three output surfaces from one token source
(`docs/brand/design-tokens.css`).

## 1. Web UI Kit (Next.js + Tailwind + shadcn/ui)

### Layout
- Mobile-first, single column, max content width `--content-reading: 640px` for reading, `--content-grid: 1200px` for landing grids, `--content-chat: 760px` for Teman Hati.
- Warmer share: green 50 / gold 40 / ruby + cream 10. Green still leads; gold warmth rises.
- Base ground: `daylight` (`<body class="ph-daylight">`). Section alternation: `daylight` → `sage` → `daylight`; the final CTA band closes on `sage`. Book covers, seals and posters stay on `.ph-stage` (`forest-night`) because they are objects, not page grounds. AJE surfaces use `.aje-surface` (black + gold) and never mix with the green system in one band.
- Sticky bottom CTA on mobile (checkout, tier selection) — 56px tall, green gradient fill, `forest-night` label.

### Components
| Component | Spec |
|---|---|
| Button primary | bg `green-cta` gradient `#3f9167→#5b9b7d`, text `ink`, radius 2px, `shadow-depth-1`, uppercase Inter 12px tracking 0.14em |
| Button secondary | 1px `gold` border, text `gold-light`, bg transparent |
| Button tier-select | 1px tier-colour border, tier-colour label, `gold` fill on selected |
| Card | bg `daylight-raised`, 1px `daylight-edge`, radius 8px, `shadow-depth-1` on hover → `shadow-depth-2` (dark-stage cards keep `forest-raised` + gold hairline) |
| Featured card | bg `forest-soft`, `shadow-depth-2`, top 1px `green-700` highlight rule |
| Tier card | left 3px tier-colour rule, title `gold-light` Fraunces, price `cream`, tier shape (circle / hexagon / arch) beside the badge |
| Chapter preview | bg `cream`, text `ink`, serif body for the reading sample |
| Trust badge | 1px `gold-deep` border, `gold` text, 11px uppercase |
| Input | bg `daylight-soft`, 1px `daylight-edge`, focus 2px `green-700` ring, error 1px `burgundy-light` |
| Healing progress | green-to-gold gradient track, travelling glow, text percentage always visible |
| Footer | bg `sage`, top 1px `gold-ink-soft` rule, `muted-grove` text |

### Typography in web
- H1 `Fraunces` 32–40px, `gold-light`, line-height 1.15
- H2 `Fraunces` 24–28px, `gold-light`
- Body `Inter` 16px, `text-on-dark`, line-height 1.65
- Kicker `Inter` 12px uppercase 0.18em, `gold`
- Pull quote `Fraunces` italic 20px, `gold-light`, 1px `gold-deep` left rule
- Reading sample body `Source Serif 4` 17px, line-height 1.7

### Brand fonts
Load `packages/ui/fonts.css` before Tailwind's base layer in
`apps/web/app/globals.css` (Phase 3):

```css
@import '@perpustakaan-hati/ui/fonts.css';
```

Self-hosted woff2 in `packages/brand-tools/fonts/` — never a Google Fonts CDN
link. Three faces, three jobs:

| role | family | where |
|---|---|---|
| Display | Fraunces (variable) | H1–H3, wordmark, pull quotes, cover titles, tier names |
| Body / UI | Inter (variable) | body copy, buttons, kickers, labels, folios, form fields |
| Reading | Source Serif 4 (variable) | long-form eBook body, chapter previews |

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
- Trim 6×9 in (152×229mm). Margins: inner 20mm, outer 15mm, top 18mm, bottom 20mm.
- Baseline grid 12pt; body 11.5pt Source Serif 4 (serif reading) / 10.5pt Inter for exercises.
- Display type (titles, chapter openers, pull quotes) Fraunces.
- Folio: outer bottom corner, 9pt Inter, `gold-deep` on ink pages, `sepia-deep` on cream pages.

### Master layouts
| Layout | Description |
|---|---|
| `cover` | Full-bleed `ink`, gold wordmark, tier-colour bar, `— by @rahimam —`, title Fraunces 28pt `gold-light` |
| `title-page` | Cream, centered wordmark, tagline, tier badge |
| `chapter-opener` | Ink page, oversized chapter numeral in `gold` outline, chapter title Fraunces 24pt, one-line epigraph in `gold-light` italic |
| `body` | Cream page, serif body, drop cap in `sepia`, first-line indent 5mm, no hyphenation |
| `pull-quote` | Ink page, centered Fraunces italic 22pt `gold-light`, thin `gold-deep` rules above/below |
| `worksheet` | Cream page, dotted 4mm write-on rules in `sepia-deep` 30% opacity, checkbox column 6mm |
| `reflection-card` | Ink card, 90×50mm, gold border, `green` healing-tier marker, rounded 4mm, quote + prompt |
| `script-page` | Cream page, two columns: left "Saya mahu kata" (terracotta), right "Cara aku kata" (sepia), for *Skrip Bincang Hati ke Hati* |
| `back-matter` | Helpline page, `cream`, Talian HEAL 15555 / Befrienders in `sepia`, PDPA note 8pt |

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
- Kicker: `by @rahimam` flanked by gold rules via `.ph-kicker`.
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
