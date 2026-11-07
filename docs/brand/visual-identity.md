# Visual Identity — Color, Type & Logo

> **Current: Design System 3.1 "Gilded Grove".** The system is not locked — it can
> change. Working rules are in [`DESIGN-SYSTEM.md`](./DESIGN-SYSTEM.md). Sections
> below on the 2.0 ink-and-gold look are history; v3 sections are the law today.

Palette derived from the 6 brand reference images (pixel-sampled, not guessed).
Dominant reality in the artwork: **ink black + antique gold + sepia brown**, with
burgundy and terracotta accents. Green is a deliberate brand addition, not sampled.

All contrast ratios below were computed from the hex values in this file
(WCAG 2.1 relative-luminance formula), not estimated.

## Palette (hex)

| token | hex | role | source |
|---|---|---|---|
| `ink` | `#0a0a0c` | primary ground, hero, cover base | photo 1/2/4 dominant |
| `ink-soft` | `#17171a` | panel, card surface on dark | sampled |
| `gold` | `#c9a86a` | primary accent, wordmark, rules | `#b6956a`/`#af8f6b` |
| `gold-light` | `#e9cea2` | headings on dark, soft text | sampled |
| `gold-deep` | `#a07b45` | hover / tertiary gold | sampled |
| `sepia` | `#573a2f` | warm mid-tone panel | sampled |
| `sepia-deep` | `#3a2a21` | deep warm shadow | `#483324` |
| `burgundy` | `#5c1e17` | emotional accent, premium tier fill | `#3f1711` |
| `burgundy-deep` | `#3f1711` | burgundy shadow | sampled |
| `burgundy-light` | `#c25a58` | premium tier **badge text on ink** | brand addition |
| `terracotta` | `#da725b` | CTA / urgency accent | photo 5/6 tiles |
| `terracotta-soft` | `#e69677` | CTA hover, highlight | sampled |
| `cream` | `#fdfee6` | light ground, calendar body | sampled |
| `paper` | `#f4efe6` | eBook interior ground | brand addition |

### The Living Green ramp

Green is the brand's healing signal and the primary accent alongside gold.
It is a **ramp, not a single colour** — each token is tuned for the ground it
sits on, because one flat green cannot pass contrast on both dark and light.

The ramp was designed for Design System 2.0 ("Living Sanctuary"). It keeps
`#5b9b7d` as the main green — it is mature rather than fluorescent, passes
AA on ink, and is already embedded throughout the templates — and adds
deeper steps for dimensional work plus two lighter steps for surfaces.

| token | hex | role | on `ink` | on `cream` |
|---|---|---|---|---|
| `green-950` | `#0b2418` | deepest gradient endpoint, 3D back plane | 1.21:1 — dark ground only | **16.02:1** AAA |
| `green-900` | `#123d2a` | 3D extrusion, dark brand panels | 1.63:1 — dark ground only | **11.87:1** AAA |
| `green-800` | `#1d5a3d` | deep accent surfaces, body copy on light | 2.43:1 — dark ground only | **7.94:1** AAA |
| `green-700` | `#2d7954` | strong brand accent, headings on light | 3.74:1 AA-large | **5.16:1** AA |
| `green-600` | `#3f9167` | CTA gradient start, active state | 5.14:1 AA | 3.76:1 — AA-large only |
| `green-500` | `#5b9b7d` | **THE main green** — healing marker, tier badge, accents | **6.06:1** AA | 3.19:1 AA-large only |
| `green-400` | `#7db895` | hover, icons, green text on ink | **8.63:1** AAA | 2.24:1 — dark ground only |
| `green-300` | `#a7d3b6` | soft highlights, green text on ink | **11.90:1** AAA | 1.62:1 — dark ground only |
| `green-200` | `#cbe8d5` | light surfaces and dividers | 15.11:1 AAA | 1.28:1 — dark ground only |
| `green-100` | `#e4f4e9` | pale green background | 17.35:1 AAA | 1.11:1 — dark ground only |
| `lime-glow` | `#c8e986` | 3D rim light, energy accents — never body text | **14.56:1** AAA | 1.33:1 — dark ground only |
| `mint-glass` | `#9de1c1` | translucent botanical highlight | **13.16:1** AAA | 1.47:1 — dark ground only |

**The rule that prevents most mistakes:** never set `green-500`, `green-400`
or `green-300` as body text on `cream`/`paper`. Use `green-700`, `green-800`
or `green-900` there. Never set `green-900` or `green-950` on `ink`.

### Usage rules
- Dark-first. `ink` is the default page ground; `cream`/`paper` are the alternative (print / eBook interiors / calendar pages).
- Gold never fills large areas. It draws rules, the wordmark, and small caps labels.
- Green appears as: healing-tier marker, quiet CTA on dark, divider accents in eBook. Never as a large flat background next to gold.
- Burgundy only on the Premium/Teman Hidup tier and heartbreak-tone content.
- Terracotta only for conversion actions (buttons, price tags, badges).
- Text on dark: `gold-light` for headings, `#e6e2da` for body. Never pure white.

## Contrast check (WCAG AA on `ink` ground)

Measured, not estimated. Every ratio below is produced by
`packages/brand-tools/check-contrast.py` — re-run it after any colour change:

```bash
uv run --no-project python packages/brand-tools/check-contrast.py
```

| pair | ratio | grade |
|---|---|---|
| `cream #fdfee6` on `#0a0a0c` | 19.31:1 | AAA |
| `gold-light #e9cea2` on `#0a0a0c` | 13.01:1 | AAA |
| `lime-glow #c8e986` on `#0a0a0c` | 14.56:1 | AAA |
| `green-300 #a7d3b6` on `#0a0a0c` | 11.90:1 | AAA |
| `mint-glass #9de1c1` on `#0a0a0c` | 13.16:1 | AAA |
| `green-400 #7db895` on `#0a0a0c` | 8.63:1 | AAA |
| `gold #c9a86a` on `#0a0a0c` | 8.75:1 | AAA |
| `terracotta #da725b` on `#0a0a0c` | 6.16:1 | AA |
| `green #5b9b7d` on `#0a0a0c` | 6.06:1 | AA |
| `green-600 #3f9167` on `#0a0a0c` | 5.14:1 | AA |
| `gold-deep #a07b45` on `#0a0a0c` | 5.10:1 | AA |
| `burgundy-light #c25a58` on `#0a0a0c` | 4.61:1 | AA |

On `cream` ground:

| pair | ratio | grade |
|---|---|---|
| `ink #0a0a0c` on `#fdfee6` | 19.31:1 | AAA |
| `green-900 #123d2a` on `#fdfee6` | 11.87:1 | AAA |
| `burgundy #5c1e17` on `#fdfee6` | 12.40:1 | AAA |
| `sepia #573a2f` on `#fdfee6` | 9.99:1 | AAA |
| `green-800 #1d5a3d` on `#fdfee6` | 7.94:1 | AAA |
| `green-700 #2d7954` on `#fdfee6` | 5.16:1 | AA |


| `ink #0a0a0c` on `#gold #c9a86a` | 8.75:1 | AAA (dark-on-gold buttons) |

> **Do not use `sepia`, `burgundy` or `green-900` as text on `ink`** — they
> measure 1.93, 1.56 and 1.62:1 respectively. Use them as fills only.

### Colour-blindness safety

The three tier colours must stay tellable apart for colour-blind readers,
since they are the navigation of the whole product ladder. Simulated with
Brettel/Viénot matrices for protanopia, deuteranopia and tritanopia,
measuring CIE76 ΔE between the simulated colours:

| pair | normal ΔE | worst CVD ΔE |
|---|---|---|
| green ~ gold | 43.2 | **21.2** (protanopia) |
| gold ~ burgundy | 44.8 | **36.7** (protanopia) |
| green ~ burgundy | 70.6 | **19.8** (protanopia) |

All pairs stay well above the ΔE ≈ 10 threshold where tiers would become
confusable. This is why the green is a *saturated* emerald rather than the
earlier desaturated olive — desaturated greens sit too close to gold once
red is removed from the vision.

Because colour alone must never carry the tier, each tier also has a
distinct **shape**: Edisi Poket = circle, Edisi Membangun = hexagon,
Teman Hidup = arch/shield. Always render the tier name alongside the badge.

## Typography

Three faces, each with a distinct job:

| role | family | use |
|---|---|---|
| **Display** | **Fraunces** (variable: `opsz`, `wght`, `SOFT`, `WONK`) | headings, wordmark, pull quotes, cover titles |
| **Body / UI** | **Inter** (variable) | body copy, buttons, kickers, labels, folios |
| **Reading** | **Source Serif 4** (variable) | long-form eBook body text, chapter previews |

- Fraunces replaces Playfair Display. It keeps the high-contrast editorial
  serif character but adds a `SOFT` axis (softer terminals = warmer, less
  severe) and a `WONK` axis for the slightly quirky letterforms that suit a
  personal, human brand. The wordmark uses `WONK 1` for character.
- Source Serif 4 handles long-form reading. Playfair Display was set at
  11.5pt in the eBook interiors; it is high-contrast and tiring over a full
  chapter. Source Serif 4 is designed for sustained reading.
- Scale: 1.25 modular. Line height 1.15 headings, 1.65 body, 1.6 long-form eBook.
- eBook interiors: 11.5pt/1.6 Source Serif 4, measure 62–68 characters, justified off.
- Kicker/label: Inter, uppercase, `letter-spacing: 0.18em`, 12px, gold.

### Self-hosting

Brand fonts are subset to the brand glyph set and stored as woff2 in
`packages/brand-tools/fonts/` (~340 KB for all four files). Load with
`font-display: swap`. Never rely on Google Fonts CDN at runtime — the
brand must render identically offline, in the PDF build, and on a
malay reader's slow phone connection.

The subsets are built from the upstream variable fonts by
`packages/brand-tools/build-fonts.py`:

```bash
uv run --no-project --with fonttools --with brotli \
  python packages/brand-tools/build-fonts.py
```

Two rules the build enforces, both learned from real fallbacks:

1. **`wght` stays a range** (400–700 / 400–600). A pinned weight makes any
   other weight request fall back to a system font.
2. **Each face is subset to the characters it actually contains.** Fraunces
   has no arrows and no Greek; Source Serif 4 has no double-headed arrows.
   Subsetting to a character the source lacks drops it silently, and the
   renderer then falls back — which is exactly how `Δ` in the accessibility
   notes ended up rendering as Cantarell.

After any font change, audit every template for fallbacks:

```bash
pdffonts /tmp/design-system-3-sheet.pdf | grep -ci "noto\|cantarell\|dejavu"
```

Every template must report `0`.

## The 3D design language

### What "3D type" means here

**Not** a novelty 3D font. That would weaken the editorial character of the
brand and reintroduce a runtime font dependency.

**Instead:** a vector *treatment* applied to the existing Fraunces outlines —
the glyph is extruded in vector, given a lit edge, and cast a soft shadow.
This scales to a poster without blurring and stays portable.

The reference build is `docs/brand/assets/lockup-cinematic.svg`, generated
by `build_lockup_cinematic()` in `packages/brand-tools/build-logos.py`.

### Three levels of depth

| level | name | use | token |
|---|---|---|---|
| 1 | Soft emboss | ordinary cards, controls | `--depth-1` |
| 2 | Dimensional surface | featured cards, marketing panels | `--depth-2` |
| 3 | Dimensional brand object | 3D wordmark, campaign artwork | `--depth-extrude` |

```css
--depth-1:
  inset 0 1px 0 rgb(255 255 255 / 0.05),
  0 8px 24px rgb(0 0 0 / 0.24);
--depth-2:
  inset 0 1px 0 rgb(255 255 255 / 0.06),
  0 18px 50px rgb(0 0 0 / 0.34);
--depth-3:
  inset 0 1px 0 rgb(255 255 255 / 0.08),
  0 32px 80px rgb(0 0 0 / 0.42);
--depth-extrude:
  0 3px 0 rgb(18 61 42 / 0.8),
  0 32px 80px rgb(0 0 0 / 0.42);
```

Shadows carry a **green undertone**, so raised surfaces feel lit by foliage
rather than by cold studio light.

### The 3D material recipe

The canonical four-part recipe for extruded brand type:

| part | colour | token |
|---|---|---|
| Face | `#f4efe6` or `#e9cea2` | `--material-face` / `--material-face-warm` |
| Extrusion (side wall) | `#123d2a` | `--material-extrude` |
| Rim light | `#c8e986` | `--material-rim` |
| Ambient shadow | `rgb(0 0 0 / 0.45)` | `--material-shadow` |

For a gold 3D wordmark specifically: face `gold #c9a86a`, extrusion
`gold-deep #a07b45`, rim `green-400 #7db895`.

### Reference assets

| asset | what it is |
|---|---|
| `docs/brand/assets/lockup-cinematic.svg` | the extruded 3D lockup (campaign use) |
| `docs/brand/preview/design-system-3-1.png` | the full design-system showcase sheet |
| `docs/brand/templates/design-system-3-sheet.html` | the source of the showcase sheet |

Regenerate the PNG with any headless Chromium:

```bash
chrome-headless-shell --allow-file-access-from-files --window-size=1600,1200 \
  --screenshot=docs/brand/preview/design-system-3-1.png \
  file://$PWD/docs/brand/templates/design-system-3-sheet.html
```

### Where 3D is allowed

| Surface | 3D allowed? |
|---|---|
| Social headers, event posters, video openers | **Yes** — full treatment |
| Tier badges, large CTAs, stat numerals | **Yes** — light bevel only |
| Site header, eBook cover, PDF master | **No** — use the flat wordmark |
| Body copy, long-form reading, form fields | **No** |

The flat outlined wordmark remains the primary mark. 3D is a campaign asset.

### Performance and motion

- 3D is a **marketing-layer material system**, not a default UI style.
- Every 3D surface needs a **static fallback** — a low-end Malaysian phone
  should never be forced to over-paint.
- Healing-progress animation is a travelling glow, 200–400 ms, never a
  spinner. It must respect `prefers-reduced-motion`.
- Progress always carries a text percentage or label — never colour alone.

## Logo & watermark stamp
- Wordmark: `PERPUSTAKAAN HATI` — Fraunces, uppercase, `letter-spacing: 0.18em`, gold `#c9a86a` on ink. Second line `— by @rahimam —` in Inter uppercase 0.25em tracking, `gold-light`.
- Sub-brand rule: `— by @rahimam —` in gold, 1px `gold-deep` rules above and below.
- `Cop Perpustakaan Hati` watermark stamp: diagonal, 10–12% opacity, `gold-light`, bottom-right of every paid page, plus buyer name/email in 7pt (Phase 2 watermarking engine).
- Safe area: wordmark padding ≥ 1.5× cap-height. Minimum width 120px digital / 18mm print.
- Avatar/photography guideline: Rahimam photography warm-graded, cream/gold wardrobe tones, avoid cool/blue cast.

### Logo files are outlined, not font-dependent

All four SVGs in `docs/brand/assets/` are generated by
`packages/brand-tools/build-logos.py`, which converts the type to real
vector outlines. **They do not reference a font by name.** This matters
because a `<text>` element with `font-family="Fraunces"` silently falls
back to Georgia on any machine without the font installed — the logo would
render differently on a phone, in a PDF, or on a designer's laptop.

Regenerate with:

```bash
uv run --no-project --with fonttools --with brotli \
  python packages/brand-tools/build-logos.py
```

The build is reproducible — regenerating produces byte-identical files.

Verify there is no font dependency at any time with:

```bash
grep -c 'font-family=' docs/brand/assets/*.svg
```

Every file must report `0`.

## Tailwind usage
Wire into `tailwind.config.ts` under `extend`. Copy `docs/brand/design-tokens.css` into the app root.

### CSS vars
```css
:root {
  --ink: #0a0a0c;
  --ink-raised: #121416;
  --ink-soft: #17171a;
  --ink-elevated: #202226;
  --gold: #c9a86a;
  --gold-light: #e9cea2;
  --gold-deep: #a07b45;
  --sepia: #573a2f;
  --sepia-deep: #3a2a21;
  --burgundy: #5c1e17;
  --burgundy-deep: #3f1711;
  --burgundy-light: #c25a58;
  --terracotta: #da725b;
  --terracotta-soft: #e69677;
  --cream: #fdfee6;
  --paper: #f4efe6;
  --linen: #eae2d4;
  --green-950: #0b2418;
  --green-900: #123d2a;
  --green-800: #1d5a3d;
  --green-700: #2d7954;
  --green-600: #3f9167;
  --green-500: #5b9b7d;
  --green-400: #7db895;
  --green-300: #a7d3b6;
  --green-200: #cbe8d5;
  --green-100: #e4f4e9;
  --lime-glow: #c8e986;
  --mint-glass: #9de1c1;
}
```

### Tailwind snippet
```ts
extend: {
  colors: {
    ink: {
      DEFAULT: '#0a0a0c',
      raised: '#121416',
      soft: '#17171a',
      elevated: '#202226',
    },
    gold: { DEFAULT: '#c9a86a', light: '#e9cea2', deep: '#a07b45' },
    sepia: { DEFAULT: '#573a2f', deep: '#3a2a21' },
    burgundy: { DEFAULT: '#5c1e17', deep: '#3f1711', light: '#c25a58' },
    terracotta: { DEFAULT: '#da725b', soft: '#e69677' },
    cream: '#fdfee6',
    paper: '#f4efe6',
    linen: '#eae2d4',
    green: {
      950: '#0b2418',
      900: '#123d2a',
      800: '#1d5a3d',
      700: '#2d7954',
      600: '#3f9167',
      500: '#5b9b7d',
      400: '#7db895',
      300: '#a7d3b6',
      200: '#cbe8d5',
      100: '#e4f4e9',
      DEFAULT: '#5b9b7d',
    },
    lime: { glow: '#c8e986' },
    mint: { glass: '#9de1c1' },
  },
  fontFamily: {
    display: ['Fraunces', 'Georgia', 'serif'],
    body: ['Inter', 'system-ui', 'sans-serif'],
    reading: ['Source Serif 4', 'Georgia', 'serif'],
  },
  boxShadow: {
    'depth-1': 'inset 0 1px 0 rgb(255 255 255 / 0.05), 0 8px 24px rgb(0 0 0 / 0.24)',
    'depth-2': 'inset 0 1px 0 rgb(255 255 255 / 0.06), 0 18px 50px rgb(0 0 0 / 0.34)',
    'depth-3': 'inset 0 1px 0 rgb(255 255 255 / 0.08), 0 32px 80px rgb(0 0 0 / 0.42)',
    extrude: '0 3px 0 rgb(18 61 42 / 0.8), 0 32px 80px rgb(0 0 0 / 0.42)',
  },
  backgroundImage: {
    'green-cta': 'linear-gradient(135deg, #3f9167, #5b9b7d)',
    'green-cta-hover': 'linear-gradient(135deg, #2d7954, #4d9573)',
    'green-deep': 'linear-gradient(160deg, #123d2a, #0b2418)',
  },
}
```

## Design System 3.1 — "Gilded Grove"

v3 takes its cues from the 2026 reference boards: cinematic, lantern-lit
scenes, metallic serif type, an open book with a heart rising from it,
flanked `— by @rahimam —` bylines, ribbon banners and scalloped seals.
The boards are black-and-gold with a red heart. **v3 keeps green as the
main colour** in three ways:

1. **The ground is green.** `forest-night` `#07140d` is a green-black. It
   replaces neutral `ink` as the default dark ground, so even empty space
   reads green. `ink` stays for print and for backward compatibility.
2. **The hero word is emerald.** In every lockup the biggest word (`HATI`)
   is emerald foil. Gold foil is used for the frame line (`PERPUSTAKAAN`),
   the rules and the byline.
3. **The heart is emerald, edged in ruby.** The reference heart is red. Ours
   is an emerald-foil heart with a thin `heart-ruby` inner line. Ruby is
   never used for text or CTAs.

Colour share per layout: **green 50 / gold 40 / ruby + cream 10** (Warmer Grove, 2026-11-08). Green still leads: the ground stays `forest-night` green-black and thread renders stay green-led (mean G > R and G > B). Gold warmth rises through gilt hairlines, rules, and the lantern key glow.

### New tokens (all in `design-tokens.css`)

| Token | Value | Role | Measured |
|---|---|---|---|
| `forest-night` | `#07140d` | default dark ground | text-on-dark 14.58:1 |
| `forest-raised` | `#0d2117` | cards | 13.04:1 |
| `forest-soft` | `#142c20` | overlays, inputs | 11.52:1 |
| `foil-emerald` | 6-stop gradient | display type ≥ 32px | darkest stop 3.56:1 |
| `foil-gold` | 6-stop gradient | display type ≥ 32px | darkest stop 4.50:1 |
| `foil-pearl` | 4-stop gradient | rare third foil | — |
| `heart-ruby` | `#c8343c` | emblem heart only (graphic) | 3.60:1 (WCAG 1.4.11) |
| `lantern` | `#f2b85c` | glow cores only | 10.57:1 |
| `glow-emerald`, `glow-lantern`, `glow-dawn` | radial/linear gradients | the key light | — |
| `vignette`, `grain` | gradient, SVG noise | cinematic finish | — |
| `ribbon-*`, `seal-*`, `card-v3-*`, `cta-v3-*` | component tokens | see below | 5.16–12.40:1 |

Every pair is in `packages/brand-tools/check-contrast.py` and must pass.

### The cinematic recipe

One class does it: `.ph-stage` = `forest-night` + `glow-emerald` +
`glow-lantern` + `vignette` + `grain`. Rules:

- One key glow per layout. Never stack two glows of the same hue.
- Foil is for display words only (≥ 32px). Body copy stays flat and AA.
- Foil type gets `--foil-shadow`: a 1px top highlight, a 3px green-900
  emboss and a soft cast shadow. Under `forced-colors` it falls back to
  flat text.
- Motion: one foil sheen on enter (`--dur-glint`, 2.4s), never looped.
  Zero under `prefers-reduced-motion`.

### v3 components (CSS classes in `design-tokens.css`)

| Class | What it is | Reference |
|---|---|---|
| `.ph-foil-emerald` / `.ph-foil-gold` / `.ph-foil-pearl` | metallic display text | the gold serif titles |
| `.ph-stage` | cinematic ground | the lantern-lit library scenes |
| `.ph-kicker` | flanked label `——— by @rahimam ———` | every reference byline |
| `.ph-ribbon` | emerald ribbon, gold edges, notched ends | "Handbag Edition" banner |
| `.ph-seal` (+ `.is-standard`, `.is-premium`) | round tier medallion | "Edisi Mini Portable" seal |
| `.ph-card` | forest card with gold hairline | — |
| `.ph-cta` | green pill CTA, forest label 5.77:1 | — |

### v3 assets (generated by `build-logos.py`)

| File | Use |
|---|---|
| `assets/emblem-book-heart.svg` | the new brand mark: emerald-bound open book, emerald-foil heart |
| `assets/lockup-cinematic.svg` | hero lockup: emblem + gold `PERPUSTAKAAN` + extruded emerald `HATI` + byline + tagline |
| `assets/seal-edisi-poket.svg` | tier seal, green fill, gold rim |
| `assets/seal-edisi-membangun.svg` | tier seal, gold fill, emerald rim |
| `assets/seal-teman-hidup.svg` | tier seal, burgundy fill, gold rim |
| `templates/design-system-3-sheet.html` | v3.1 showcase sheet; PNG at `preview/design-system-3-1.png` |
| `preview/cover-v3-sample.png` | sample render of the v3 eBook cover |

All are outlined vector (no font dependency). `monogram-stamp.svg` (v3
emerald-foil PH) is for anything below 48px, because the emblem's detail
does not survive at that size. `cop-stamp.svg` is the buyer watermark.
The 2.0 `wordmark-primary`, `wordmark-3d` and v2 sheet were **removed**
when the system was locked (see `DESIGN-SYSTEM.md`).

What we did **not** take from the boards: photographic scenes baked into
the logo, the silver/chrome "R" monogram, and the red heart as a solid
fill. Those would push green out of the lead role.

### v3.1 refinement — real font weights + lit 3D

**Font fix.** `build-fonts.py` used to only *relabel* the weight axis as
400–700. It never moved the outlines. Fraunces ships with a default weight
of 900, so every "regular" glyph was really Black, and `font-weight: 700`
also rendered as 900 (Inter 700 and Source Serif 600 too). The subsetter
now limits `wght` through the instancer, which re-solves the outlines with
400 as the true default.
`packages/brand-tools/tests/test_fonts.py` measures glyph ink against the
upstream font at every boundary weight (12 tests, ±1.5%). The subsets also
got 51 KB smaller.

**Weight roles** (same in CSS, Tailwind and the SVG outlines):

| Role | Weight | Token / class | Used for |
|---|---|---|---|
| display caps | 560 | `--weight-display`, `.ph-caps`, `font-display` | PERPUSTAKAAN, wordmarks |
| hero | 660 | `--weight-hero`, `.ph-hero`, `font-hero` | HATI, seal main word, foil words |
| title | 520 | `--weight-title`, `.ph-title`, `font-title` | eBook / page titles |
| script | 400 italic | `--weight-script`, `.ph-script` | taglines, ribbons |
| label | 600 | `--weight-label`, `font-label` | Inter caps on seals |
| byline | 500 | `--weight-byline`, `font-byline` | kickers, bylines |

**3D in SVG** (`build-logos.py`):
- `bevel_filter()` is a chiselled-metal bevel made from real lighting.
  The glyph alpha is blurred into a height map, diffuse light shades the
  slopes, and specular light adds a hot rim on the lit edge. The key light
  sits top-left (azimuth 235°). The result is clipped back to the glyph,
  so outlines never grow.
- `extrude()` builds a solid side wall from 1px `<use>` copies graded from
  near to far colour. HATI is 14px deep, PERPUSTAKAAN 4px, the book cover
  6px, the heart tube 6px and the seal rims 8px.
- Shadows come in two layers: a tight *contact* shadow (3px blur) plus a
  soft *ambient* one (14px blur).
- `deboss_filter()` stamps the seal labels into the medallion: shade above,
  a light catch below.
- The emblem gains a gilt page block, a spine shadow and one glint. Glints
  never touch type, because there they read as a diacritic.

**3D in CSS** (`design-tokens.css`): a lighting filter can't run on text,
so `--depth-emerald`, `--depth-gold` and `--depth-pearl` chain 1px
drop-shadows (N steps give an N-px solid) after a 1px top bevel catch.
They end with a contact and an ambient shadow. `.ph-sheen` sweeps one
specular band across a foil word on enter. The other elements:
- **Ribbon:** a lit front band, with notched tails tucked behind and dark
  fold triangles.
- **CTA:** a glossy top lip and a 3px green-800 "thickness". On
  `:active` it sinks into that edge.
- **Card:** a six-layer bevel, contact and ambient stack, with a hover lift.
- **Seal:** a rim bevel, a recessed medallion and a debossed label.

### Warmer Grove extension (2026-11-08)

Share moves to green 50 / gold 40 / ruby + cream 10 for a warmer storefront feel. Green stays the lead: `forest-night` remains the ground and the Threads renders stay green-led (mean G > R and G > B). Gold warmth rises via gilt hairlines, rules, and the lantern key glow.

**Charts (locked).** `--chart-1` green-500, `--chart-2` gold, `--chart-3` burgundy-light, `--chart-4` lantern, `--chart-5` mint-glass. Locked 2026-11-08 for quiz, assessment, and progress dashboards. Never rename. Pair every series with a direct label or shape; color never carries meaning alone.

**Teman Hati companion.** First-class surface. Uses WebGL particles (42 particles, `--particle-count`), tilt (`--tilt-perspective: 1200px`, `--tilt-max: 6deg`), glass (`--glass-bg`, `--glass-blur: 18px`), and lantern glow. Assistant bubbles use `--companion-bubble-assistant` with a gold hairline; user bubbles use the green gradient. Reading and checkout never use WebGL. Every WebGL surface needs a static-image fallback and zero motion under `prefers-reduced-motion: reduce`.

**Layout and state.** `--content-reading: 640px`, `--content-grid: 1200px`, `--content-chat: 760px`, `--tap-min: 44px`, `--tap-cta-mobile: 56px`, `--z-sticky: 30` through `--z-toast: 70`, `--focus-ring` and `--focus-ring-light`.
