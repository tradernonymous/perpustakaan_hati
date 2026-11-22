# Perpustakaan Hati — project memory

## Git ops and GitHub accounts

- This repo is `tradernonymous/perpustakaan_hati` (private). Use the **github-work** MCP for all PR/CI/merge operations.
- `printezy247` resources (e.g. private `website_sam` reference repo) use the **github** MCP or the `gh` CLI — different account.
- Account routing for builds: `tradernonymous/*` repos → **github-work** MCP only. `printezy247/*` repos → **github** MCP or `gh` CLI. The `gh` CLI is logged in as `printezy247`, so never use it for PR/CI/merge on this repo. If github-work MCP is unavailable, stop and ask instead of falling back to `gh` or switching credentials.
- Flow that works with Railway auto-deploy: feature branch → push → MCP `create_pull_request` → `pull_request_read get_check_runs` until green → `merge_pull_request` → sync local `main` → delete merged branch. Merging to `main` triggers Railway deploys for both `web` and `perpustakaan_hati` (research-admin) services.
- Railway occasionally parks deploys as `NEEDS_APPROVAL`; approve via `railway api 'mutation { deploymentApprove(id:"...") }'` or the dashboard.
- CI failing only because of a GitHub billing issue (jobs blocked by payment or spending limit, not by test or build errors): squash merge anyway, as Jack said. Check the check-run output first to confirm the failure is billing-only, and say so in the PR and the report. Any other CI failure still blocks the merge.

## Private content — never commit

- `content/ebooks/tier-2-standard/`, `content/ebooks/tier-3-premium/` (paid masters), `apps/web/private/` are gitignored. They exist only on local disk and the Railway `/data` volume.
- The free Edisi Poket tier stays tracked. Paid files still exist in old git history — do not rewrite history or make the repo public without a `filter-repo` cleanup first.
- Before any branch switch/reset, copy ignored paid dirs aside — git removes untracked files on checkout and uncommitted edits will be lost.

## Licensing status (as of 2026-11-21)

- Launch score (`videos/edisi-poket-launch-v2/src/score.rb`): owner-declared original, recorded in `docs/brand/assets/refresh-2026-11/manifest.md`.
- Brand marks/seals/layout: owner-declared project grant recorded in the same manifest.
- **PENDING:** @rahimam signature on `docs/brand/assets/refresh-2026-11/poket-author-permission.md` (Poket PDF redistribution + artwork reuse). Until countersigned, the grant is pending — remind Jack to chase it.

## Design system

- `docs/brand/design-tokens.css` and `apps/web/styles/design-tokens.css` must stay byte-identical — tests enforce it.
- Sanctioned asset/token changes need `python3 packages/brand-tools/check-lock.py --update` to refresh `design-system.baseline.json`, then `--strict` must pass.
- New top-level files in `docs/brand/assets/` must be added to `ASSETS` in `check-lock.py` or placed inside an allowed subdir (e.g. `refresh-2026-11/`).
- Motion work: follow `prefers-reduced-motion` fallbacks; Sam-inspired hero layers live in `HeroAtmosphere.module.css`, `design-tokens.css` (`.ph-glyphs`, `.ph-cta::after` sheen) and `TipsFlipbook.module.css`.

## Verification

- Web: `cd apps/web && npm run lint && npx vitest run` (62 files / 412 tests).
- Brand tools: `uv run --no-project --with pytest --with fonttools --with brotli pytest packages/brand-tools/tests -q` and `check-lock.py --strict`.
- Browser checks/screenshots: Lightpanda CLI only (`/home/jack/.local/bin/lightpanda fetch <url> --dump html|png`) — PNGs are text-layout approximations, not pixel-accurate.
- Live site: https://perpustakaanhati.biz · Railway project "Perpustakaan Hati" · services `web` and `perpustakaan_hati`.
