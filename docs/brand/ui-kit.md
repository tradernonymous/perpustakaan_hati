# Multi-Format Design System

Phase 1 deliverable covering three output surfaces from one token source
(`docs/brand/design-tokens.css`).

## 1. Web UI Kit (Next.js + Tailwind + shadcn/ui)

### Layout
- Mobile-first, single column, max content width 640px for reading, 1200px for landing grids.
- Base ground: `ink`. Section alternation: `ink` → `ink-soft` → `cream` (final CTA band on cream for contrast break).
- Sticky bottom CTA on mobile (checkout, tier selection) — 56px tall, `terracotta` fill, `ink` label.

### Components
| Component | Spec |
|---|---|
| Button primary | bg `terracotta`, text `ink`, radius 2px, no shadow, uppercase Inter 12px tracking 0.14em |
| Button secondary | 1px `gold` border, text `gold-light`, bg transparent |
| Button tier-select | 1px tier-colour border, tier-colour label, `gold` fill on selected |
| Card | bg `ink-soft`, 1px `border-dark`, radius 4px, `shadow-card` on hover → `shadow-lift` |
| Tier card | left 3px tier-colour rule, title `gold-light` Playfair, price `cream` |
| Chapter preview | bg `cream`, text `ink`, serif body for the reading sample |
| Trust badge | 1px `gold-deep` border, `gold` text, 11px uppercase |
| Input | bg `ink-soft`, 1px `border-dark`, focus 1px `gold`, error 1px `terracotta` |
| Footer | bg `ink-soft`, top 1px `gold-deep` rule, `text-muted-on-dark` |

### Typography in web
- H1 `Playfair Display` 32–40px, `gold-light`, line-height 1.15
- H2 `Playfair Display` 24–28px, `gold-light`
- Body `Inter` 16px, `text-on-dark`, line-height 1.65
- Kicker `Inter` 12px uppercase 0.18em, `gold`
- Pull quote `Playfair Display` italic 20px, `gold-light`, 1px `gold-deep` left rule

### shadcn/ui mapping
shadcn default tokens are neutral-light. Override in `globals.css`:
```
--background: var(--ink)
--foreground: var(--text-on-dark)
--primary: var(--terracotta)
--primary-foreground: var(--ink)
--secondary: var(--ink-soft)
--accent: var(--gold)
--accent-foreground: var(--ink)
--border: var(--border-dark)
--ring: var(--gold)
--radius: 0.25rem
```

## 2. eBook Layout Templates

### Page geometry
- Trim 6×9 in (152×229mm). Margins: inner 20mm, outer 15mm, top 18mm, bottom 20mm.
- Baseline grid 12pt; body 11.5pt Playfair Display (serif reading) / 10.5pt Inter for exercises.
- Folio: outer bottom corner, 9pt Inter, `gold-deep` on ink pages, `sepia-deep` on cream pages.

### Master layouts
| Layout | Description |
|---|---|
| `cover` | Full-bleed `ink`, gold wordmark, tier-colour bar, `— by @rahimam —`, title Playfair 28pt `gold-light` |
| `title-page` | Cream, centered wordmark, tagline, tier badge |
| `chapter-opener` | Ink page, oversized chapter numeral in `gold` outline, chapter title Playfair 24pt, one-line epigraph in `gold-light` italic |
| `body` | Cream page, serif body, drop cap in `sepia`, first-line indent 5mm, no hyphenation |
| `pull-quote` | Ink page, centered Playfair italic 22pt `gold-light`, thin `gold-deep` rules above/below |
| `worksheet` | Cream page, dotted 4mm write-on rules in `sepia-deep` 30% opacity, checkbox column 6mm |
| `reflection-card` | Ink card, 90×50mm, gold border, `olive` healing-tier marker, rounded 4mm, quote + prompt |
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
- Ground `ink`, 1px `gold-deep` inner border, 24px padding.
- Kicker: `— @rahimam —` `gold`, Inter 24px uppercase 0.2em.
- Quote: Playfair Display 60–72px, `gold-light`, line-height 1.2, max 4 lines.
- Footer: `PERPUSTAKAAN HATI` Playfair 28px `gold`, tracking 0.22em, bottom-left; `tier badge` bottom-right.
- Grid overlay guide only in the template file, never in the exported PNG.

### Carousel panel (10 slides)
1. Cover — wordmark, "Karya untuk jiwa yang pernah terluka"
2–7. Six quote panels, one idea per slide
8. Tier ladder — three panels side-by-side showing olive / gold / burgundy tiers with prices
9. Problem slide — "Kennt kamu rasa ini?" (teaser of the pain point)
10. CTA — "Mula dengan Edisi Poket — percuma", terracotta button block, handle

### Teaser graphic
- Never a fake screenshot. Use a real book render or typographic card.
- Calendar tile template (from the reference artwork): cream ground, `sepia` text, `terracotta` prayer-time accents, Hijri date in Playfair italic, one hadith quote per month.

### Export
- sRGB, PNG for photos, JPEG q85 for photos, PDF for print assets.
- Filename: `ph-{tier}-{type}-{n}-{w}x{h}.{ext}` e.g. `ph-pocket-quote-03-1080x1350.png`.
