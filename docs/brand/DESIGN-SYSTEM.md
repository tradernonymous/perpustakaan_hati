# Design System 3.1 "Gilded Grove"

**Status: current version as of 2026-11-08 (Warmer Grove extension).** This is the look for Perpustakaan Hati. Green still leads; warmth rises.
Version token: `--ph-system-version: '3.1.0'` in `design-tokens.css`.

Warmer share: green 50 / gold 40 / ruby + cream 10. Charts are locked (see `visual-identity.md` and `design-tokens.css` `--chart-1` through `--chart-5`). Teman Hati companion chat is a first-class surface: `--companion-*`, `--glass-*`, `--chart-*`, `.ph-glass`, `.ph-companion`, `.ph-tilt` live in `design-tokens.css` and `ui-kit.md`.

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

## Sanctioned assets (`docs/brand/assets/`)
| File | Use |
|---|---|
| `emblem-book-heart.svg` | the brand mark |
| `lockup-cinematic.svg` | hero lockup, headers, posters |
| `monogram-stamp.svg` | below 48px, favicon, avatar |
| `seal-edisi-poket.svg` / `seal-edisi-membangun.svg` / `seal-teman-hidup.svg` | tier seals |
| `cop-stamp.svg` | buyer watermark on paid pages |

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
