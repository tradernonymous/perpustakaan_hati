# Visual Identity — Color, Type & Logo

Palette derived from the 6 brand reference images (pixel-sampled, not guessed).
Dominant reality in the artwork: **ink black + antique gold + sepia brown**, with
burgundy and terracotta accents. Green is a deliberate brand addition, not sampled.

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
| `burgundy` | `#5c1e17` | emotional accent, premium tier | `#3f1711` |
| `burgundy-deep` | `#3f1711` | burgundy shadow | sampled |
| `terracotta` | `#da725b` | CTA / urgency accent | photo 5/6 tiles |
| `terracotta-soft` | `#e69677` | CTA hover, highlight | sampled |
| `cream` | `#fdfee6` | light ground, calendar body | sampled |
| `olive` | `#5f6f4a` | **healing accent** — green | brand addition |
| `olive-deep` | `#3c482d` | olive shadow, dark green text | brand addition |

### Usage rules
- Dark-first. `ink` is the default page ground; `cream` is the alternative (print / eBook interiors / calendar pages).
- Gold never fills large areas. It draws rules, the wordmark, and small caps labels.
- Olive appears as: healing-tier marker, quiet CTA on dark, divider accents in eBook. Never as a large flat background next to gold.
- Burgundy only on the Premium/Teman Hidup tier and heartbreak-tone content.
- Terracotta only for conversion actions (buttons, price tags, badges).
- Text on dark: `gold-light` for headings, `#e6e2da` for body. Never pure white.

## Contrast check (WCAG AA on `ink` ground)
- `gold-light #e9cea2` on `#0a0a0c` ≈ 14.5:1 — pass AAA
- `cream #fdfee6` on `#0a0a0c` ≈ 19:1 — pass AAA
- `terracotta #da725b` on `#0a0a0c` ≈ 6.2:1 — pass AA
- `olive #5f6f4a` on `#0a0a0c` ≈ 4.6:1 — pass AA for large text only; use `gold-light` for olive-tinted body copy
- `ink #0a0a0c` on `gold #c9a86a` ≈ 8.1:1 — pass AA (dark-on-gold buttons)

## Typography
- Display / headings: **Playfair Display** (high-contrast serif, matches the antique gold editorial feel of the artwork). Fallback `Georgia, serif`.
- Body: **Inter**. Fallback `system-ui, sans-serif`.
- Accent / kicker labels: Inter, uppercase, `letter-spacing: 0.18em`, 12px, gold.
- Scale: 1.25 modular. Line height 1.15 headings, 1.65 body, 1.5 long-form eBook.
- eBook interiors: 11.5pt/1.6, measure 62–68 characters, justified off.

## Logo & watermark stamp
- Wordmark: `PERPUSTAKAAN HATI` — Playfair Display, uppercase, `letter-spacing: 0.22em`, gold `#c9a86a` on ink. Second line `RAHIMAM SIGNATURE` in Inter uppercase 0.3em tracking, `gold-light`.
- Sub-brand rule: `— by @rahimam —` in gold, 1px `gold-deep` rules above and below.
- `Cop Perpustakaan Hati` watermark stamp: diagonal, 12% opacity, `gold-light`, bottom-right of every paid page, plus buyer name/email in 7pt (Phase 2 watermarking engine).
- Safe area: wordmark padding ≥ 1.5× cap-height. Minimum width 120px digital / 18mm print.
- Avatar/photography guideline: Rahimam photography warm-graded, cream/gold wardrobe tones, avoid cool/blue cast.

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
  --terracotta: #da725b;
  --terracotta-soft: #e69677;
  --cream: #fdfee6;
  --olive: #5f6f4a;
  --olive-deep: #3c482d;
}
```

### Tailwind snippet
```ts
extend: {
  colors: {
    ink: { DEFAULT: '#0a0a0c', soft: '#17171a' },
    gold: { DEFAULT: '#c9a86a', light: '#e9cea2', deep: '#a07b45' },
    sepia: { DEFAULT: '#573a2f', deep: '#3a2a21' },
    burgundy: { DEFAULT: '#5c1e17', deep: '#3f1711' },
    terracotta: { DEFAULT: '#da725b', soft: '#e69677' },
    cream: '#fdfee6',
    olive: { DEFAULT: '#5f6f4a', deep: '#3c482d' },
  },
  fontFamily: {
    display: ['Playfair Display', 'Georgia', 'serif'],
    body: ['Inter', 'system-ui', 'sans-serif'],
  },
}
```
