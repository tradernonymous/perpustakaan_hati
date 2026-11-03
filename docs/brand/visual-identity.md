# Visual Identity — Color, Type & Logo

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

### The green ramp

Green is the brand's healing signal and the primary accent alongside gold.
It is a **ramp, not a single colour** — each token is tuned for the ground it
sits on, because one flat green cannot pass contrast on both dark and light.

| token | hex | role | on `ink` | on `cream` |
|---|---|---|---|---|
| `green` | `#5b9b7d` | **primary green** — healing marker, tier badge, accents | **6.06:1** AA | 3.19:1 AA-large only |
| `green-light` | `#8fc9a8` | highlights, rules, hover states | **10.44:1** AAA | 1.85:1 — dark ground only |
| `green-mid` | `#3f7d5e` | body copy on light grounds | 4.06:1 AA-large | **4.76:1** AA |
| `green-deep` | `#255740` | headings on light grounds | 2.37:1 — dark ground only | **8.15:1** AAA |
| `green-ink` | `#173c2c` | body text on light grounds | 1.62:1 — dark ground only | **11.92:1** AAA |
| `green-wash` | `#d9efe1` | soft panel fill (always with `ink` text) | 16.37:1 AAA | 1.18:1 — dark ground only |

**The rule that prevents most mistakes:** never set `green` or `green-light`
as body text on `cream`/`paper`. Use `green-mid`, `green-deep` or `green-ink`
there. Never set `green-deep` or `green-ink` on `ink`.

### Usage rules
- Dark-first. `ink` is the default page ground; `cream`/`paper` are the alternative (print / eBook interiors / calendar pages).
- Gold never fills large areas. It draws rules, the wordmark, and small caps labels.
- Green appears as: healing-tier marker, quiet CTA on dark, divider accents in eBook. Never as a large flat background next to gold.
- Burgundy only on the Premium/Teman Hidup tier and heartbreak-tone content.
- Terracotta only for conversion actions (buttons, price tags, badges).
- Text on dark: `gold-light` for headings, `#e6e2da` for body. Never pure white.

## Contrast check (WCAG AA on `ink` ground)

Measured, not estimated:

| pair | ratio | grade |
|---|---|---|
| `cream #fdfee6` on `#0a0a0c` | 19.31:1 | AAA |
| `gold-light #e9cea2` on `#0a0a0c` | 13.01:1 | AAA |
| `green-light #8fc9a8` on `#0a0a0c` | 10.44:1 | AAA |
| `gold #c9a86a` on `#0a0a0c` | 8.75:1 | AAA |
| `terracotta #da725b` on `#0a0a0c` | 6.16:1 | AA |
| `green #5b9b7d` on `#0a0a0c` | 6.06:1 | AA |
| `burgundy-light #c25a58` on `#0a0a0c` | 4.61:1 | AA |
| `gold-deep #a07b45` on `#0a0a0c` | 5.10:1 | AA |

On `cream` ground:

| pair | ratio | grade |
|---|---|---|
| `ink #0a0a0c` on `#fdfee6` | 19.31:1 | AAA |
| `green-ink #173c2c` on `#fdfee6` | 11.92:1 | AAA |
| `burgundy #5c1e17` on `#fdfee6` | 12.40:1 | AAA |
| `sepia #573a2f` on `#fdfee6` | 9.99:1 | AAA |
| `green-deep #255740` on `#fdfee6` | 8.15:1 | AAA |
| `green-mid #3f7d5e` on `#fdfee6` | 4.76:1 | AA |
| `ink #0a0a0c` on `gold #c9a86a` | 8.75:1 | AAA (dark-on-gold buttons) |

> **Do not use `sepia`, `burgundy` or `green-deep` as text on `ink`** — they
> measure 1.93, 1.56 and 2.37:1 respectively. Use them as fills only.

### Colour-blindness safety

The three tier colours must stay tellable apart for colour-blind readers,
since they are the navigation of the whole product ladder. Simulated with
Brettel/Viénot matrices for protanopia, deuteranopia and tritanopia,
measuring CIE76 ΔE between the simulated colours:

| pair | normal ΔE | worst CVD ΔE |
|---|---|---|
| green ~ gold | 43.2 | **24.4** |
| gold ~ burgundy | 44.8 | **20.6** |
| green ~ burgundy | 68.2 | **37.8** |

All pairs stay well above the ΔE ≈ 10 threshold where tiers would become
confusable. This is why the green is a *saturated* emerald rather than the
earlier desaturated olive — desaturated greens sit too close to gold once
red is removed from the vision.

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
`packages/brand-tools/fonts/` (~260 KB for all four files). Load with
`font-display: swap`. Never rely on Google Fonts CDN at runtime — the
brand must render identically offline, in the PDF build, and on a
malay reader's slow phone connection.

## Logo & watermark stamp
- Wordmark: `PERPUSTAKAAN HATI` — Fraunces, uppercase, `letter-spacing: 0.18em`, gold `#c9a86a` on ink. Second line `— by @rahimam —` in Inter uppercase 0.25em tracking, `gold-light`.
- Sub-brand rule: `— by @rahimam —` in gold, 1px `gold-deep` rules above and below.
- `Cop Perpustakaan Hati` watermark stamp: diagonal, 10–12% opacity, `gold-light`, bottom-right of every paid page, plus buyer name/email in 7pt (Phase 2 watermarking engine).
- Safe area: wordmark padding ≥ 1.5× cap-height. Minimum width 120px digital / 18mm print.
- Avatar/photography guideline: Rahimam photography warm-graded, cream/gold wardrobe tones, avoid cool/blue cast.

### Logo files are outlined, not font-dependent

All three SVGs in `docs/brand/assets/` are generated by
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

## Tailwind usage
Wire into `tailwind.config.ts` under `extend`. Copy `docs/brand/design-tokens.css` into the app root.

### CSS vars
```css
:root {
  --ink: #0a0a0c;
  --ink-soft: #17171a;
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
  --green: #5b9b7d;
  --green-light: #8fc9a8;
  --green-mid: #3f7d5e;
  --green-deep: #255740;
  --green-ink: #173c2c;
  --green-wash: #d9efe1;
}
```

### Tailwind snippet
```ts
extend: {
  colors: {
    ink: { DEFAULT: '#0a0a0c', soft: '#17171a' },
    gold: { DEFAULT: '#c9a86a', light: '#e9cea2', deep: '#a07b45' },
    sepia: { DEFAULT: '#573a2f', deep: '#3a2a21' },
    burgundy: { DEFAULT: '#5c1e17', deep: '#3f1711', light: '#c25a58' },
    terracotta: { DEFAULT: '#da725b', soft: '#e69677' },
    cream: '#fdfee6',
    paper: '#f4efe6',
    green: {
      DEFAULT: '#5b9b7d',
      light: '#8fc9a8',
      mid: '#3f7d5e',
      deep: '#255740',
      ink: '#173c2c',
      wash: '#d9efe1',
    },
  },
  fontFamily: {
    display: ['Fraunces', 'Georgia', 'serif'],
    body: ['Inter', 'system-ui', 'sans-serif'],
    reading: ['Source Serif 4', 'Georgia', 'serif'],
  },
}
```
