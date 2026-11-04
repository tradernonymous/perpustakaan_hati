# Design System 3.1 "Gilded Grove"

**Status: current version as of 2026-11-04.** This is the look for Perpustakaan Hati.
Version token: `--ph-system-version: '3.1.0'` in `design-tokens.css`.

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
1. Edit tokens or build scripts. Rebuild: `build-fonts.py`, `build-logos.py`.
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
