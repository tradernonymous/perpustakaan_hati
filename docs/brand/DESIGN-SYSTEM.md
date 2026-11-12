# Design System 3.3 "Daylight Grove"

**Status: current version as of 2026-11-11 (Daylight Grove 3.3: Astryx bridge + opt-in nightlight + AJE branch).** This is the look for Perpustakaan Hati. Green still leads; the storefront now lives on warm ivory and gold carries the luxury detail. The cinematic forest stage is kept for covers, seals and posters.
Version token: `--ph-system-version: '3.3.0'` in `design-tokens.css`.

Share per storefront frame: **green 55 / gold 30 / cream + ruby 15**. On the dark stage (covers, posters) the share stays green 50 / gold 40 / ruby + cream 10. Charts are locked (see `visual-identity.md` and `design-tokens.css` `--chart-1` through `--chart-5`). Teman Hati companion chat is a first-class surface: `--companion-*`, `--glass-*`, `--chart-*`, `.ph-glass`, `.ph-companion`, `.ph-tilt` live in `design-tokens.css` and `ui-kit.md`.

## Two branches — pick one per surface

| Branch | Who | Palette | Where |
|---|---|---|---|
| **Perpustakaan Hati** | Rahimam's personal, editorial brand | ivory / sage / emerald / gilt | the storefront, eBooks, Threads, counselling |
| **AJE** | Armazas Jaya Enterprise, Rahimam's company | black / gold only | AJE signage, posters, shop material, stationery |

The branch is decided by **who the work is for**, never by taste. If a layout needs both, split it into separate bands — never put AJE gold on a Perpustakaan Hati green card, or the AJE turtle on a healing surface. AJE's full rules, facts and files: [`aje.md`](./aje.md).

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
   itself, not by dashes.

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
