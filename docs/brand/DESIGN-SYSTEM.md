# Design System 3.9 "Void Grove"

**Current storefront release, 2026-11-21.** Version token `--ph-system-version: '3.9.0'` in `design-tokens.css`.

| Role | Recipe |
|---|---|
| Display | Instrument Serif regular for headlines and italic for editorial emphasis. The hero uses a 46–96px fluid scale, 0.96 leading, and −0.015em tracking. |
| Interface | Variable Geist Sans for navigation, labels, controls, and body copy. |
| Reading and publishing | Source Serif 4 for reading text. The publishing templates use their established Fraunces and Inter roles for covers and labels. |
| Dimensional covers | `.ph-book-stage` sets perspective and reserves space for the edges. Its `.ph-book-object` child uses a right paper edge, a bottom edge, a tier-tinted bevel, and a cast shadow. Hover on a fine pointer tilts and lifts the cover. |
| Hero and reader | The hero layers light above a projected spread of ruled pages. Its atmosphere pauses offscreen and has a visible pause control on wider screens. The reader uses the shared perspective and page-stack shadow with a page-turn entrance. |
| Interaction | Use the feedback duration for disclosure and the entrance duration for turning and lifting. Touch shows the resting book pose. Reduced motion shows flat covers and disables the hero, hover, and reader transitions. |

The 3D reference is the local Ezymap design system, particularly its perspective staging and beveled objects. Void Grove applies those ideas to paper, binding, and gilt instead of using trading imagery.

Visit the [live design system](https://perpustakaanhati.biz/design-system) to try the storefront components. Open [the foundations specimen](specimens/foundations.html) to review the current type, cover depth, motion, and component states. [Instrument Serif](https://github.com/Instrument/instrument-serif) and [Geist](https://github.com/vercel/geist-font) are self-hosted under `apps/web/public/fonts/` with their SIL Open Font License notices. The legacy static brand board is [archived here](preview/design-system-3-1.png).

## Hero marks and cover motion

- The hero and the public specimen use the same three treatments of Perpustakaan Hati’s marks. The foil heart uses a warm gold rim, the original book-and-heart sits on an emerald medallion, and the fintech treatment uses a mint grid and a rounded-square edge.
- On wide screens the medallions turn in perspective at different tempos. Light sweeps across each face and traces the orbit. These loops run only while the hero is in view and share the hero pause control. Narrow screens play a short entrance and keep the resting pose. Reduced motion displays the resting pose immediately.
- Chapter and catalog covers with a picture face get one gold sweep on fine-pointer hover. The movement is decorative and adds no control or new tab stop.

## Shared foundations layer (added 2026-11-19, still 3.8)

The shared foundations provide ebook palettes, motion roles, and a specimen sheet.

| Piece | Token / class | Why |
|---|---|---|
| Scoped ebook-tier tokens | `.ph-ebook-poket`, `.ph-ebook-membangun`, `.ph-ebook-teman-hidup` → `--ebook-<tier>-{page,ink,heading,rule,ornament,field,field-ink,wash}` | Each edition gets its own page ground and ink. Declared **only** inside the scoped class, never in `:root`, so a white Edisi Membangun PDF cannot turn the storefront white. The renderer opts in by putting the class on its page root. |
| Motion roles | `--motion-feedback-dur/ease`, `--motion-entrance-dur/ease`, `--motion-scene-dur/ease`, `--motion-reduced-dur` | A component names the role it plays (feedback / entrance / scene) instead of picking a curve. Values reference `--dur-*`/`--ease-*`, and the `prefers-reduced-motion` block zeroes the durations explicitly. |
| Specimen sheet | `docs/brand/specimens/foundations.html` | Review sheet: buttons, forms, navigation, cards, dialogs, loading/empty/success/error states and the three tier specimens. Uses `design-tokens.css` only — the test suite fails the sheet if a raw hex colour appears. |

Pinned by `packages/brand-tools/tests/test_phase1_foundations.py`: token presence, scoping (not in `:root`), reduced-motion zeroing, byte-identical CSS copies, `design-tokens.json` ↔ CSS version and value sync, WCAG contrast on the new tier pairs (text ≥4.5:1, graphics ≥3:1), and the specimen sections.

## Earlier: Design System 3.8 "Void Grove"

| Piece | Token / class | Why |
|---|---|---|
| Void ground | `body.ph-void`, `--ph-void #030604`, `--ph-void-raised #08120c`, `--ph-void-soft #0e1b13`, `themeColor #030604` | The page is near-black; raised bands and cards are only a breath lighter. Roles (`bg-surface*`) re-point, components do not change |
| Band hairline | `.ph-dark-section::before` + `--ph-hairline-dark` | A glowing line opens every band |
| Hero light | `HeroBeam`, `.ph-hero-beam`, `.ph-hero-spot` | One beam falls from the top edge and breathes by opacity; a soft spotlight follows a real pointer. Opacity and transform only; still on phones after the entrance; off under reduced motion |
| Headline rise | `.ph-rise` | The three headline words rise in sequence once |
| Gradient headings | `.ph-void .ph-title` | White fading to muted, with a forced-colours fallback |
| Lit card ring | `.ph-void .ph-lux:not(.ph-beam)::before` | A cursor-lit 1px border ring on spotlight cards; chapter cards and the edition card now join the spotlight |
| Eyebrow link | `.ph-hero-eyebrow` as `<a href="#edisi">` | The pill is a link with an arrow, as on the reference |

## Earlier: Dark Grove (3.7), built on Design System 3.6 "Precise Grove"

Introduced the dark forest-night stage for the storefront and the research admin (`<body class="ph-nightlight">`). Ivory (`.ph-daylight`) is used for print and light eBook templates. Green leads the palette and gold carries the detail.
Version token: `--ph-system-version: '3.7.0'` in `design-tokens.css`.

## Dark Grove (3.7)

| Piece | Token / class | Why |
|---|---|---|
| Dark default | `body.ph-nightlight`, `themeColor #07140d` | One ground for every storefront and admin page |
| Semantic colours | Tailwind `bg-surface`, `bg-surface-raised`, `bg-surface-soft`, `text-fg`, `text-fg-muted`, `text-fg-accent`, `text-fg-healing`, `border-line` | Components name a role, the theme scope decides the colour. Never hard-code `bg-daylight` or `text-green-900` on a page |
| Hero glow | `--ph-glow-green`, `--ph-glow-gold` | The single soft light behind the hero |
| Hairline | `--ph-hairline-dark` | Dividers on dark |
| Section grounds | `.ph-dark-section`, `.ph-dark-section-raised` | Sections alternate night / raised for rhythm |

Earlier layers below (3.6 and older) still apply. Where they say "ivory", read "the active theme scope".

The 3.4 layer changes how the storefront **composes**, not what it is built of. Everything
under it still uses the same tokens, the same fonts and the same assets; what changed is
that the page now reads like an illustrated book (a plate behind the hero, a gallery of
the edition's art, chapter cards that carry a picture) rather than a stack of centred card
rows, and that the three most expensive effects on a phone were turned off.

Share per storefront frame: **green 55 / gold 30 / cream + ruby 15**. On the dark stage (covers, posters) the share stays green 50 / gold 40 / ruby + cream 10. Charts are locked (see `visual-identity.md` and `design-tokens.css` `--chart-1` through `--chart-5`). Teman Hati companion chat is a first-class surface: `--companion-*`, `--glass-*`, `--chart-*`, `.ph-glass`, `.ph-companion`, `.ph-tilt` live in `design-tokens.css` and `ui-kit.md`.

## Two branches — pick one per surface

| Branch | Who | Palette | Where |
|---|---|---|---|
| **Perpustakaan Hati** | Rahimam's personal, editorial brand | ivory / sage / emerald / gilt | the storefront, eBooks, Threads, counselling |
| **AJE** | Armazas Jaya Enterprise, Rahimam's company | black / gold only | AJE signage, posters, shop material, stationery |

The branch is decided by **who the work is for**, never by taste. If a layout needs both, split it into separate bands — never put AJE gold on a Perpustakaan Hati green card, or the AJE turtle on a healing surface. AJE's full rules, facts and files: [`aje.md`](./aje.md).

## Editorial Grove (3.4)

The storefront's composition layer. Pure CSS plus the six Edisi Poket plates.

| Piece | Class | What it does |
|---|---|---|
| Bento hero | `.ph-hero-grid`, `.ph-art`, `.ph-book-overlap` | the hero is an illustrated plate with the 3D book overlapping its lower edge |
| Plate gallery | `.ph-gallery` | the six illustrations: a scroll-snap scroller on a phone, a three-column grid on a wide screen |
| Chapter cards | `.ph-chapter-grid`, `.ph-chapter-card` | the chapter preview becomes a card grid, each card carrying its own art |
| Bento ecosystem | `.ph-bento`, `.ph-bento-feature` | the interactive space is an asymmetric grid with one dark feature card |
| Section numbers | `.ph-sec-index` | each band is numbered like a chapter of the book |

**The plates.** `apps/web/public/illustrations/` holds WebP at 480 / 768 / 1200 px plus one
JPEG fallback, rendered from `docs/brand/illustrations/edisi-poket-kehilangan/` by
`apps/web/scripts/build-illustrations.mjs`. They are pre-rendered on purpose: the next/image
optimizer needs sharp at runtime and sharp is a devDependency here, so a production deploy
would fail to serve optimized images. `apps/web/src/illustrations.ts` is the typed manifest.

**Phone rules.** These are the rules the 3.4 layer holds itself to, and they are checked by
`apps/web/tests/editorial-grove.test.tsx`:

1. No `backdrop-filter` on anything that scrolls. The sticky header loses its blur below
   768px; the blur is a class, not a Tailwind utility, so the guard can turn it off.
2. No continuously repainting gradient on a phone. The gold beam (`.ph-beam`) stops
   spinning below 768px and under `prefers-reduced-motion`.
3. No animation that triggers layout. The hero glyphs float by transforming, never by
   animating `margin-top`.
4. Every image carries explicit width and height, so nothing shifts as it loads.


## Precise Grove (3.6)

A refinement layer, not a new look: same palette, same fonts, same assets, same
layout recipes. 3.6 is the machinery a mature system needs so that a later surface
does not invent its own value. Each item is a published practice, and each one is
either a base rule or a token with a named consumer.

| Piece | Token / class | Why |
|---|---|---|
| Focus recipe | `--focus-width`, `--focus-offset`, `--focus-color` (`:focus-visible`) | WCAG 2.2 SC 2.4.11: a 2px perimeter at 3:1+ against the ground. `outline` is used so it never fights a component's box-shadow. |
| Wide focus offset | `--focus-offset-wide` | A filled control (`.ph-cta`) steps the ring out to the page ground, where it is actually measured. |
| Selection, caret, native controls | `--selection-bg`, `--selection-fg`, `--caret-color`, `--accent-color` | The browser's default blue was the one foreign colour left in the brand. |
| Text wrapping | `h1-h3`, `.ph-title` balance; `p`, `li` pretty | A two-line Malay title never leaves one orphaned word. |
| Tabular numerals | `.ph-nums`, `.ph-stat-num` | Digits do not change width while a count-up runs. |
| Motion roles | `--ease-standard`, `--ease-decelerate`, `--ease-accelerate` | A component picks the role it plays, not a curve. `.ph-card` uses standard; `.ph-sticky-cta` decelerates in and accelerates out. |
| Elevation ladder | `--elevation-1..4`, `.ph-elev-1..4`, Tailwind `shadow-elev-1..4` | One ladder, two materials: the theme scope decides the shadow. |
| High contrast | `prefers-contrast: more` | Raises muted copy, hairlines and the glass scrim. No hue changes. |
| Forced colours | `@media (forced-colors: active)` | The focus ring survives Windows High Contrast. |
| Off-screen work | `.ph-cv` | Opt-in `content-visibility` for very long sections. |
| Scrollbar | `--scrollbar-thumb`, `--scrollbar-thumb-light` | Slim, brand-tinted, stable gutter: no layout jump between a short and a long view. |

Measured pairs for the new indicators live in `check-contrast.py` (the 3.6 block):
green-300 on forest-night 11.33:1, green-800 on daylight 7.39:1, cream on
green-800 7.94:1, ink-grove on green-200 12.28:1.

## The Daylight layer (3.2)

| Token | Value | Role |
|---|---|---|
| `daylight` | `#f7f4ea` | default light page ground (warm ivory) |
| `daylight-raised` | `#fffdf6` | light cards and inputs |
| `sage` | `#e9f0e6` | alternating light section |
| `daylight-edge` | `#d2c4a8` | warm hairline on light |
| `ink-grove` | `#12251b` | primary text on light |
| `muted-grove` | `#4f5f53` | muted text on light |
| `gold-ink` | `#7a5a22` | gold **text / small caps** on light (AA) |
| `gold-ink-soft` | `#96742f` | gold hairline / ornament on light |

The theme is applied with `<body class="ph-daylight">`. That scope remaps
semantic and component tokens only (`--surface-*`, `--text-*`, `--card-v3-*`,
`--glass-*`), so `.ph-card`, `.ph-glass` and `.ph-kicker` adapt without
per-component hacks, while `--forest-night` stays intact for the book covers
and `.ph-stage` posters inside the same page.

**Rules on light**
1. Green leads: headings and CTAs are green (`green-900` / `green-800` / the `.ph-cta` gradient). Gold is a detail, never the main fill.
2. Never set `gold-light` or `gold` as text on ivory. Use `gold-ink`; `gold-light` is for the dark stage only.
3. The cinematic lockup (`lockup-hero.svg`) is for dark grounds. On light, typeset the wordmark: gilt small caps `PERPUSTAKAAN` over a deep-green Fraunces `HATI` — see `components/Hero.tsx`.
4. Book covers, seals and the 3D book stay dark: they are objects, not backgrounds.
5. One green CTA per view; gold hairlines and the `.ph-ornament` mark section breaks.

## Astryx — where it is allowed (3.3)

Astryx (`@astryxdesign/core` 0.7.12 + `@astryxdesign/theme-stone`, pinned exact) is an
**accessibility component layer**, never a second design system. It consumes our tokens;
it never replaces them.

| Rule | Why |
|---|---|
| Astryx CSS enters through `src/astryx/AstryxScope.tsx` only | One import point, so the 271 kB chunk can be route-scoped |
| Never mount the provider in `app/layout.tsx` | That would put Astryx CSS on every storefront page; Next keeps it on the routes that import it |
| `src/astryx/astryx-brand.css` maps Astryx variables to brand tokens, unlayered | Astryx ships its variables in `@layer astryx-theme`; unlayered rules win regardless of import order |
| No new hex in the bridge | Every value is `var(--brand-token)` or `color-mix()` of two brand tokens |
| Adopted: `/admin` only (Banner, Button, Card) | Admin is `noindex`, low-traffic, off the storefront path |

**Deliberately not adopted**, with the reason recorded so a later session does not
re-litigate it:

- **Forms (`Field`, `TextInput`)** — `TextInput` is controlled and would replace the
  approved brand styling. The real gap was the ARIA contract, now fixed directly in
  `OptInForm`, `CheckoutForm` and `LibraryLogin`: `noValidate`, `aria-invalid`,
  `aria-describedby`, one `role="alert"` per field, focus moved to the first invalid control.
- **`Chat`** — it is a composer/drawer toolkit, not a bubble renderer; adopting it would
  replace the Teman Hati bubble styling. The gap (no `role="log"`, no label, no form
  semantics) is fixed in `TemanHatiChat` instead.
- **`Collapsible` for the mobile nav** — `SiteHeader` already ships `aria-expanded` +
  `aria-controls` + Escape-to-close. Swapping it buys nothing and risks the nav. The
  missing piece was a **skip link**, now added as the first tab stop.
- **`Accordion`** — Astryx has no such export; `Faq` uses native `<details>`, which is
  correct and needs no JavaScript.
- **`ProgressBar`** — `ReadingProgress` already emits `role="progressbar"` with
  `aria-valuenow`/`aria-valuemax`.

The CLI is available for component contracts: `npm run astryx -- component --list`.

## Nightlight — opt-in dark scope (3.3)

`.ph-nightlight` / `[data-theme="nightlight"]` remaps the semantic layer onto the existing
dark primitives (`--forest-night`, `--forest-raised`, `--text-on-dark`, `--gold-light`).
It is **never** applied by `prefers-color-scheme` alone: the storefront ships daylight, and
flipping the ground for every dark-OS visitor is a brand decision, not a preference default.
A test enforces both halves of that rule.

## What "current" means
- The system is **not locked**. You can change the palette, type, assets, layout
  recipes or copy whenever the brand needs it.
- `uv run --no-project python packages/brand-tools/check-lock.py` is an **advisory
  reviewer**: it lists drift (a new asset in `docs/brand/assets/`, a missing token,
  a reference to a retired 2.0 asset, a tracked file changed since the last
  baseline) and always exits 0. It never blocks a build.
- Run it with `--strict` if you want warnings to fail a CI job:
  `uv run --no-project python packages/brand-tools/check-lock.py --strict`.
- The sanctioned-asset list, the required-token list and the retired-asset names
  below are **guidance for humans and agents**, not a gate.

## Copy rules
These rules govern every piece of copy the brand publishes: eBooks, Threads
cards, the storefront, emails and page titles.

1. **Never use the em dash (—) in copy.** Not in a heading, a sentence, a
   label, a chart row or a page title. Set a clause apart with a colon, a
   comma, a full stop, or a second line. Em dashes read as imported English
   punctuation, and the Malay copy in this brand does not use them.

   ```
   Wrong:  "Bacaan, kerja, dan skrip — teman hidup."
   Right:  "Bacaan, kerja, dan skrip, teman hidup."
   Wrong:  "KAD REFLEKSI — tiga soalan untuk malam ini"
   Right:  "KAD REFLEKSI: tiga soalan untuk malam ini"
   ```

   A hyphen is fine for a compound ("paling-penting", "sebab-kerja"). The
   byline reads `by @rahimam`, flanked by the rule that `.ph-kicker` draws
   itself, not by dashes. The handle is lowercase, and its `@` is set as the
   rainbow-ring badge (`.ph-handle` + `.ph-at`). Every other kicker label
   stays uppercase gold.

   This rule covers reader-facing text only. Code comments, CSS comments and
   SVG source comments are not copy and are not affected.

2. **Malay sentence case for body copy.** Capitalise the first word of a
   sentence, the first word of a title, and proper nouns (`Perpustakaan
   Hati`, `Threads`, `Edisi Poket`). Do not capitalise every word of a title.

3. **Tier names are fixed.** `Edisi Poket`, `Edisi Membangun`, `Teman Hidup`.
   Their subcopy is locked in `docs/brand/tier-naming.md`.

4. **No invented numbers.** Every figure carries its source on the page.
   A chart without a source line does not ship.

5. **No pitch in the free tier.** The closing page of a pocket edition carries
   the helplines and nothing else.

`packages/brand-tools/tests/test_copy_rules.py` fails the build when the em
dash reappears in published copy.

## Sanctioned assets (`docs/brand/assets/`)
| File | Use |
|---|---|
| `emblem-book-heart.svg` | the brand mark |
| `lockup-cinematic.svg` | hero lockup, headers, posters |
| `monogram-stamp.svg` | below 48px, favicon, avatar |
| `seal-edisi-poket.svg` / `seal-edisi-membangun.svg` / `seal-teman-hidup.svg` | tier seals |
| `cop-stamp.svg` | buyer watermark on paid pages |
| `aje/aje-turtle-emerald.svg` | AJE branch: turtle mark, green colourway |
| `aje/aje-turtle-noir.svg` | AJE branch: turtle mark, gold-on-black colourway |
| `aje/*.png` | matching transparent PNG exports (1024 / 512 / 256) |

Retired 2.0 ink-and-gold assets (do not bring them back): `wordmark-primary.svg`,
`wordmark-3d.svg`, `design-system-sheet.html`, `design-system-2-1.png`.

## Where the rules live
| What | File |
|---|---|
| Tokens and `.ph-*` classes | `docs/brand/design-tokens.css` |
| Full rationale, contrast numbers, 3D recipes | `docs/brand/visual-identity.md` |
| Web / eBook / Threads kits | `docs/brand/ui-kit.md` |
| Threads quote card templates | `content/threads/templates/quote-card.html` (A), `quote-card-b.html` (B, centred), `quote-card-c.html` (C, gilded ribbon) |
| Tier names (fixed) | `docs/brand/tier-naming.md` |
| Doop / AI-designer guideline | `docs/brand/doop-guideline.md` |
| AJE branch (facts, assets, rules) | `docs/brand/aje.md` |
| Showcase sheet | `docs/brand/templates/design-system-3-sheet.html` and `preview/design-system-3-1.png` |

## Using it in Doop (via the MCP)
The guideline `perpustakaan-hati-design-system` is saved on the Doop canvas
`Gr9TixlKwm` ("Perpustakaan Hati — Design System 3.1"). To use it on any other canvas:
1. `get_guidelines(canvas_id="Gr9TixlKwm", name="perpustakaan-hati-design-system")`
2. `set_guidelines(canvas_id=<your canvas>, name="perpustakaan-hati-design-system", markdown=<that text>, agent_name="Claude")`
3. Design with the pasted tokens and the hotlinked logo URLs inside it.
Claude Code also keeps this in `~/.claude/doop-design-systems.md` (entry 5), so just ask:
"make a Doop frame with the Perpustakaan Hati design system".

## Changing the system
1. Edit tokens or build scripts. Rebuild: `build-fonts.py`, `build-logos.py`, then `build-web-lockup.py` (derives the website hero lockup `apps/web/public/brand/lockup-hero.svg` from `lockup-cinematic.svg`), then `build-animated-logos.py` (animated copies of the emblem, hero lockup and three seals in `apps/web/public/brand/animated/`: the heart draws on, the ruby line traces, HATI lifts out of its extrusion, seal rings turn; CSS inside the SVG, ends on the original artwork, off under reduced motion). `test_animated_logos.py` fails if these are stale. Copy `docs/brand/design-tokens.css` to `apps/web/styles/design-tokens.css` unchanged (a web test checks they match).
2. Run `check-contrast.py` and the pytest suite. Everything must pass.
3. Bump the version here and in `design-tokens.css`.
4. Re-save the Doop guideline from `doop-guideline.md`.
5. Run `check-lock.py --update` to refresh the baseline, and commit.

## Checks to run before any release
```bash
uv run --no-project python packages/brand-tools/check-contrast.py
uv run --no-project --with fonttools --with brotli --with pytest pytest packages/brand-tools/tests -q
uv run --no-project python packages/brand-tools/check-lock.py
```

## Motion layer v2 (2026-11-08)
Logo motion and page motion, all CSS (no animation library). Classes live in
`design-tokens.css`; every one has a static fallback and stops under
`prefers-reduced-motion`.

| Class / file | What it does | Origin |
|---|---|---|
| `public/brand/animated/*.svg` | heart draws on, ruby traces, glint twinkles; lockup HATI lifts out of its 14px slab + one sheen; seal rings turn | brand (stroke paths in `build-logos.py`) |
| `.ph-logo-stage` | pointer 3D tilt + counter-shadow + lantern spotlight for the hero lockup | brand |
| `.ph-coin` | tier seals sway as 3D coins (seals stay >= 96px) | brand |
| `.ph-beam` | gold light circling a card edge (`@property` angle) | website_sam `.holo-btn` |
| `.ph-lux` + `LuxCursor` | one page-wide cursor spotlight + light sweep on cards | website_sam `.lux` |
| `.ph-spine` | gilt spine on coverflow covers; side covers blur | website_sam `.deck-spine` |
| `.ph-ticker` | masked marquee, pauses on hover/focus | website_sam `.ticker` |
| `StatsStrip` | count-up numerals (server renders the final number) | website_sam `AnimatedNumber` |
| `.ph-sticky-cta` | mobile CTA steps aside while the opt-in form is visible | website_sam `StickyBuyBar` |
| `.ph-page-in` | chapters tip up like pages on scroll | website_sam `reader-page-in` |
| `.ph-ink-in` | Fraunces `wght` 400 -> 520 "ink in" on scroll (variable axis; subsets keep `wght` live, `SOFT 40 / WONK 1` pinned) | brand fonts |
