# Perpustakaan Hati — Design System 3.2 "Daylight Grove"

Brand: Perpustakaan Hati by @rahimam. Malay-language healing eBooks. Tagline: "Karya untuk jiwa yang pernah terluka".
Mood: a sunlit reading room with a lantern still lit in the corner. Editorial, foil-stamped, calm. **GREEN LEADS.**
Colour share per frame: **green 55 / gold 30 / cream + ruby 15** on light surfaces; green 50 / gold 40 / ruby + cream 10 on the dark stage (covers, seals, posters). Never invent a new colour. Never use neutral black as a ground outside the AJE branch.

**Surface rule (3.2).** The storefront runs on warm ivory (`--daylight`), alternating with sage (`--sage`). The cinematic forest stage is now reserved for objects: book covers, seals, posters and the 3D book. On light, gold is *detail* (`--gold-ink` for text, `--gold-ink-soft` for hairlines); green carries headings and CTAs. Never put `--gold-light` text on ivory. When a design needs the wordmark on light, typeset it — gilt small caps above a deep-green Fraunces word — instead of using the dark lockup SVG.
Charts (locked): `--chart-1` green-500, `--chart-2` gold, `--chart-3` burgundy-light, `--chart-4` lantern, `--chart-5` mint-glass. Pair with label/shape. Teman Hati companion surface uses `--companion-*`, `.ph-glass`, `.ph-tilt`.

## Fonts
Use Fraunces for display, Inter for UI and labels, and Source Serif 4 for long reading. Shipped templates load the self-hosted files in `packages/brand-tools/fonts/`; never add Google Fonts runtime links. In Doop, use these family names with `Georgia`/`system-ui` fallbacks when local font files are unavailable.

Weights per role: display caps 560, hero word 660, titles 520, italic script 400, Inter labels 600, bylines 500. Never use 800/900. Fraunces = display, Source Serif 4 = long reading, Inter = UI and labels.

## Tokens (paste in <style>)
```css
:root{
 --forest-night:#07140d;--forest-raised:#0d2117;--forest-soft:#142c20;--forest-edge:rgb(157 225 193/.14);
 --green-950:#0b2418;--green-900:#123d2a;--green-800:#1d5a3d;--green-700:#2d7954;--green-600:#3f9167;--green-500:#5b9b7d;--green-400:#7db895;--green-300:#a7d3b6;--green-200:#cbe8d5;--green-100:#e4f4e9;
 --lime-glow:#c8e986;--gold:#c9a86a;--gold-light:#e9cea2;--gold-deep:#a07b45;
 --burgundy:#5c1e17;--burgundy-light:#c25a58;--heart-ruby:#c8343c;--lantern:#f2b85c;
 --cream:#fdfee6;--paper:#f4efe6;--linen:#eae2d4;--ink:#0a0a0c;
 --text-on-dark:#e6e2da;--text-muted-on-dark:#a49c8d;
 --foil-emerald:linear-gradient(178deg,#d9f3df 0%,#8fd0a6 22%,#3f9167 46%,#2d7954 58%,#a7d3b6 76%,#3f9167 100%);
 --foil-gold:linear-gradient(178deg,#fff1c9 0%,#ecc983 24%,#b8904a 48%,#9a7638 58%,#f1d79b 78%,#b8904a 100%);
 --depth-emerald:drop-shadow(0 -1px 0 rgb(227 247 232/.55)) drop-shadow(0 1px 0 #1d5a3d) drop-shadow(0 1px 0 #19503a) drop-shadow(0 1px 0 #164733) drop-shadow(0 1px 0 #123d2a) drop-shadow(0 1px 0 #0f3324) drop-shadow(0 1px 0 #0b2418) drop-shadow(0 2px 1.5px rgb(0 0 0/.55)) drop-shadow(0 16px 22px rgb(0 0 0/.5));
 --depth-gold:drop-shadow(0 -1px 0 rgb(255 244 214/.6)) drop-shadow(0 1px 0 #7a5a28) drop-shadow(0 1px 0 #5e4520) drop-shadow(0 1px 0 #3a2a14) drop-shadow(0 2px 1.5px rgb(0 0 0/.5)) drop-shadow(0 10px 16px rgb(0 0 0/.45));
 --glow-emerald:radial-gradient(70% 60% at 50% 40%,rgb(63 145 103/.42),transparent 72%);
 --glow-lantern:radial-gradient(60% 50% at 50% 38%,rgb(242 184 92/.30),transparent 70%);
 --vignette:radial-gradient(120% 90% at 50% 45%,transparent 48%,rgb(0 0 0/.72) 100%);
 --rule-flank:linear-gradient(90deg,transparent,var(--gold) 30%,var(--gold) 70%,transparent);
 --font-display:'Fraunces',Georgia,serif;--font-body:'Inter',system-ui,sans-serif;--font-reading:'Source Serif 4',Georgia,serif;
 --daylight:#f7f4ea;--daylight-raised:#fffdf6;--daylight-soft:#eef2e8;--sage:#e9f0e6;--daylight-edge:#d2c4a8;--ink-grove:#12251b;--muted-grove:#4f5f53;--gold-ink:#7a5a22;--gold-ink-soft:#96742f;
 --aje-black:#0a0a0a;--aje-black-raised:#151515;--aje-gold:#c9a86a;--aje-gold-light:#e9cea2;--aje-gold-deep:#8a6224;--aje-cream:#fdfee6;
}
.ph-daylight{background:var(--daylight);color:var(--ink-grove)}
.ph-daylight .ph-card{background:var(--daylight-raised);border:1px solid var(--daylight-edge);color:var(--ink-grove);box-shadow:0 1px 0 rgb(255 255 255/.9) inset,0 1px 3px rgb(60 45 20/.08),0 18px 40px -24px rgb(60 45 20/.35)}
.ph-daylight .ph-kicker{color:var(--gold-ink)}
.ph-aje{background:var(--aje-black);color:var(--aje-cream)}
.ph-aje .ph-kicker{color:var(--aje-gold-light)}
*{margin:0;box-sizing:border-box}
.ph-stage{position:relative;background-color:var(--forest-night);background-image:var(--vignette),var(--glow-emerald),var(--glow-lantern)}
.ph-foil-emerald,.ph-foil-gold{-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;font-family:var(--font-display)}
.ph-foil-emerald{background-image:var(--foil-emerald);filter:var(--depth-emerald);font-weight:660;letter-spacing:.06em}
.ph-foil-gold{background-image:var(--foil-gold);filter:var(--depth-gold);font-weight:560;letter-spacing:.2em;text-transform:uppercase}
.ph-kicker{display:flex;align-items:center;gap:.9em;font:500 13px var(--font-body);letter-spacing:.32em;text-transform:uppercase;color:var(--gold-light)}
.ph-kicker::before,.ph-kicker::after{content:'';flex:1 1 3em;height:1px;background:var(--rule-flank)}
.ph-card{background:linear-gradient(180deg,var(--forest-raised),var(--forest-night));border:1px solid var(--forest-edge);border-radius:8px;color:var(--text-on-dark);box-shadow:inset 0 1px 0 rgb(167 211 182/.1),inset 0 -1px 0 rgb(0 0 0/.35),0 0 0 1px rgb(201 168 106/.1),0 1px 1px rgb(0 0 0/.35),0 6px 12px -2px rgb(0 0 0/.3),0 28px 60px -12px rgb(0 0 0/.55)}
.ph-cta{display:inline-flex;gap:.5em;padding:.85em 1.6em;border:0;border-radius:999px;font:600 16px/1 var(--font-body);color:var(--forest-night);background:linear-gradient(180deg,var(--green-400),var(--green-500) 50%,var(--green-600));box-shadow:inset 0 1px 0 rgb(255 255 255/.45),inset 0 -2px 0 rgb(18 61 42/.35),0 3px 0 var(--green-800),0 4px 2px rgb(0 0 0/.35),0 12px 28px rgb(63 145 103/.4)}
.ph-ribbon{display:inline-block;padding:.5em 1.6em;background:linear-gradient(180deg,#3a8a62,var(--green-700) 18%,var(--green-800) 60%,var(--green-900));color:var(--gold-light);font:italic 400 22px var(--font-display);border-block:1.5px solid var(--gold)}
```

## Logo assets (hotlink these, never redraw or re-type the brand)
- Cinematic lockup (hero, 1600x1000, has its own ground): https://doop.design/a/NsN8xlPEn0.svg
- Book-heart emblem (transparent, 600x420, put on forest-night): https://doop.design/a/7-XyLuNdUs.svg
- Monogram PH (square, use below 48px, favicon, avatar): https://doop.design/a/CW_YgN_i4C.svg
- Seal Edisi Poket (FREE, green): https://doop.design/a/bh-Gs4mcn6.svg
- Seal Edisi Membangun (STANDARD, gold): https://doop.design/a/DS6LWqMaav.svg
- Seal Teman Hidup (PREMIUM, burgundy): https://doop.design/a/ZwAepEEo6Q.svg
Seals: 96px minimum, rotate -8deg on covers, `filter:drop-shadow(0 18px 30px rgb(0 0 0/.55))`. Emblem minimum 48px wide.

## AJE branch — Armazas Jaya Enterprise (black + gold)
A separate design-system branch for Rahimam's company: **black and gold only**, no green, no ivory ground, no Perpustakaan Hati emblem. Use it when the work is for AJE (shop signage, price cards, stationery, the ONE STOP CENTRE seal). Full facts and files: `docs/brand/aje.md`.

- Turtle mark (transparent, 3D): `https://web-production-0cfb9.up.railway.app/brand/aje/aje-turtle-emerald.svg` (green) and `.../aje-turtle-noir.svg` (gold on black). PNG exports sit beside them (`-1024`, `-512`, `-256`).
- Ground `--aje-black`, gold `--aje-gold` for rules and marks, `--aje-gold-light` for headings, `--aje-cream` for body copy. Minimum mark width 48px; never recolour, skew or add a third colour; never place the turtle inside the PH green system or on ivory.
- Seal lockup: double gold ring, "ONE STOP CENTRE" arced on top, "AJE" centred, "BELI DISINI, PASTI PUAS HATI !" arced below at 62% size.
- Do not invent AJE claims, prices or hours. The fixed facts: (PG0543717-U), since 2016, Sat–Thu 8.30 PG–11.45 MLM, Fri 2.15 PTG–11.45 MLM, daily break 6.30–8.20 PTG.

## Tiers (fixed colours, never rename)
| Tier | Name | Price | Colour | Subcopy |
|---|---|---|---|---|
| Free | Edisi Poket | Free | green-400 text, green-700 seal | Ringkas, menyentuh, mudah dibawa. |
| Standard | Edisi Membangun | RM 29-49 | gold | Panduan yang paling jujur dan paling mudah diikuti. |
| Premium | Teman Hidup | RM 79-149 | burgundy-light text, burgundy seal | Untuk jiwa yang ingin pulih. |
Do not use "Edisi Dompet" or "Edisi Pulih" publicly. Colour never carries the tier alone: always add the seal shape and the text label.

## Layout recipes
- **Hero / header:** `.ph-stage` ground; emblem 340px centred; PERPUSTAKAAN as `.ph-foil-gold` (62px), HATI as `.ph-foil-emerald` (150px); `.ph-kicker` "by @rahimam"; italic Fraunces tagline in green-300. Or use the cinematic lockup image directly.
- **eBook cover 1200x1800:** `.ph-stage` + double gilt frame (inset 56px 2px gold-deep, inset 16px 1px gold 35%); emblem, foil wordmark, `.ph-kicker` "Koleksi Ebook", title Fraunces 520 88px cream with `text-wrap:balance`, `.ph-ribbon` tier name, subtitle Source Serif italic green-300, tier seal bottom-right, kicker "by @rahimam" bottom centre.
- **Threads quote card 1080x1350:** `.ph-stage`, emblem 180px top-left, `— @rahimam —` kicker, quote Fraunces gold-light, footer PERPUSTAKAAN HATI foil-gold + tier badge outline in tier colour.
- **Cards / CTA:** `.ph-card` on forest-night; one green `.ph-cta` per view; a pressed CTA sinks 3px.

## Rules (brand guidance — the system is not locked, so these can evolve)
1. Ground is `--forest-night`. `--ink` only for print. Never `#000`, never pure grey.
2. One key glow per frame (emerald OR lantern strength dominant). Never two glows of the same hue.
3. Foil only for display words >= 32px. Body copy flat: text-on-dark on forest = 14.58:1; muted text-muted-on-dark = 6.92:1.
4. Green text on dark: green-400 (8.22:1) or green-300. Green text on cream/paper: green-700+ only (never green-500/400).
5. Ruby lives inside the heart emblem only. Never for text, buttons, or backgrounds.
6. Gold = frame, rules, bylines, ribbons' edges. Never a full-bleed fill larger than a seal.
7. Bylines are always flanked: `— by @rahimam —` via `.ph-kicker`.
8. Icons: simple line icons in gold-light or green-400. No emoji, no stock photos of people. Imagery: warm lantern, books, desk, dawn mountains; graded warm, no cool or blue cast.
9. Motion: one foil sheen on enter, never looped; none under reduced-motion.
10. Language: Bahasa Malaysia first. Tone: gentle, honest, never clinical, never shaming ("jiwa yang pernah terluka", not "rosak").
11. AVOID: purple or blue gradients, neon, glassmorphism, 800/900 weights, pure-black grounds, red CTAs, the silver "R" monogram, Edisi Dompet.

## Changing the system
The system is not locked — a new Doop canvas or a new frame may extend it.
- Edit `docs/brand/design-tokens.css` and the `.ph-*` classes there, then rebuild assets with `packages/brand-tools/build-logos.py`.
- Re-run `check-contrast.py` (all required pairs must pass) and the pytest suite.
- Bump `--ph-system-version` in `design-tokens.css`, then re-save this guide to the Doop canvas with `set_guidelines`.
- Tier names, prices and seal shapes stay fixed — colour never carries a tier alone.

## Source of truth
Repo `tradernonymous/perpustakaan_hati`: `docs/brand/design-tokens.css` is the value authority; `docs/brand/DESIGN-SYSTEM.md` is the current-version and navigation authority; `docs/brand/visual-identity.md` holds rationale; preview `docs/brand/preview/design-system-3-1.png`. This guideline is `docs/brand/doop-guideline.md`; its copied token snapshot must stay aligned with `design-tokens.css`.
