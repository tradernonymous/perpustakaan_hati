# Phase 0 — current-system inventory and baseline

Date: 2026-11-19. Branch: `feat/storefront-research-ebook-video-upgrade` (created from `main` at `1dd6d5d`).
Companion plan: `docs/superpowers/plans/2026-11-19-brand-storefront-research-ebook-video-upgrade.md`.

Everything below was read or executed on this date. Nothing is claimed from memory.

## 1. Repo shape

| Area | Path | Stack |
|---|---|---|
| Storefront | `apps/web` | Next.js 16 (App Router), React 19, Tailwind 3.4, Vitest 5, TypeScript |
| Research admin | `packages/research-admin` | FastAPI + uvicorn, server-rendered HTML strings (`research_admin/dashboard.py`), SQLite, pytest/ruff |
| Ebook builder | `packages/ebook-builder` | Python CLI → WeasyPrint (`ebook-builder build`) and a headless-Chrome A4 composer (`ebook_builder.pocket_cli`), pytest |
| Brand tools | `packages/brand-tools` | Python asset builders + `check-lock.py` / `check-contrast.py`, pytest |
| Shared UI tokens | `packages/ui` | spec copies of `tailwind.config.js`, `fonts.css`, `shadcn-theme.css` |
| Content | `content/ebooks` | `tier-1-free`, `tier-2-standard`, `tier-3-premium`, plus `edisi-poket-<slug>/` A4 books |
| Video | `videos/edisi-poket-launch` (v1), `videos/edisi-poket-launch-v2` (current) | HyperFrames 0.9.54, 1920×1080, 24 s, 30 fps |
| Brand docs | `docs/brand` | `DESIGN-SYSTEM.md` (3.8 Void Grove), `design-tokens.css`, `design-tokens.json`, `ui-kit.md`, previews |

`videos/` and `dist/` are git-ignored. No root `package.json`; `apps/web/package.json` is the only npm manifest.

## 2. Design System 3.8 sources and token generation

- Canonical CSS: `docs/brand/design-tokens.css`; runtime copy `apps/web/styles/design-tokens.css`.
  `diff -q` on 2026-11-19: **byte-identical**. Sync is enforced by
  `packages/brand-tools/tests/test_handle_badge.py::test_web_copy_matches_docs_copy`, not by a generator.
- `docs/brand/design-tokens.json` is a hand-mirrored export and still declares **3.6.0** in `$meta`
  while `--ph-system-version` in the CSS is `3.8.0`. **No generator script exists** (repo grep finds only readers).
  This is the "canonical and generated files out of sync" gap the plan calls out.
- Drift check: `uv run --no-project python packages/brand-tools/check-lock.py` → `DESIGN SYSTEM CHECK: ok — no drift detected`.
  It tracks `docs/brand/design-tokens.css` but **not** `apps/web/styles/design-tokens.css`.
- Contrast check: `packages/brand-tools/check-contrast.py` (advisory).
- Version bump assertions live in `apps/web/tests/nightlight.test.ts`.

## 3. Storefront inventory (apps/web)

- Pages: `/`, `/surat-hati`, `/terima-kasih`, `/demo-bayar`, `/kad-jujur-hati`, `/hadiah-hati`, `/admin`,
  `/cermin-pasangan`, `/teman-hati`, `/booking`, `/kelab`, `/beli/[id]`, `/pustaka`, `/cabaran-7-hari`,
  `/astryx-scratch` (unlinked scratch), `/healthz`, `/muat-turun/[token]`.
- API: `checkout`, `subscribe`, `surat`, `booking`, `pustaka`, `edisi-poket/pdf`, `webhooks/billplz`,
  `webhooks/stripe`, `demo/pay`, `orders/[id]/status`, `auth/threads/*`, `auth/facebook/*`, `admin/subscribers`.
- Homepage order today (`app/page.tsx`): SiteHeader → **Hero (with `components/HeroBeam.tsx`)** → StatsStrip →
  Ticker → HowItWorks → EcosystemHub → TierLadder/EbookDeck/TierCompare (`#edisi`) → ChapterPreview →
  PlateGallery → Testimonials → Faq → ClosingCta → SafetyFooter → StickyCta → LuxCursor.
- Hero: `components/Hero.tsx` renders `HeroBeam` (`.ph-hero-beam` top-edge beam + `.ph-hero-spot` pointer
  spotlight) before the grid. This is the decoration Phase 2 replaces.
- Search / quick-jump: `components/CommandPalette.tsx` (`PALETTE_ITEMS`, Ctrl/Cmd+K, ARIA combobox),
  triggered from `components/SiteHeader.tsx`.
- **No filter UI and no URL filter state anywhere** (`useSearchParams`/`pushState` absent). Phase 2's
  "preserve URL filter state" is therefore new behaviour, not preservation.
- Data: `src/catalog.ts` (products/prices), `src/content.ts` (TIERS, CHAPTERS, TESTIMONIALS, NAV, STEPS, FAQS).
- Tests: 56 files in `apps/web/tests/`, several JSdoc-relevant here:
  `void-hero.test.tsx` (3.8 hero), `editorial-grove.test.tsx`, `home-funnel.test.tsx`, `content.test.tsx`,
  `tier-ladder.test.ts`, `dark-default.test.ts`, `precise-grove.test.ts`, `nightlight.test.ts`,
  `command-palette.test.tsx`, `checkout/fulfil/webhooks/payments` (purchase path), `forms-a11y.test.tsx`.
- Commands: `npm run lint` (= `tsc --noEmit`), `npm test` (= `vitest run`), `npm run build`.
  No ESLint config and no separate typecheck script.
- Next.js note: `apps/web/AGENTS.md` requires reading `apps/web/node_modules/next/dist/docs/`
  (`01-app`, `02-pages`, `03-architecture`, `04-community`) before writing Next code.

## 4. Research admin inventory (packages/research-admin)

- Single view function `GET /?view=…`; views: `overview, research, followers, audiences, studio, library,
  calendar, inbox, knowledge, settings` plus `/mini`. UI is Python f-string HTML + one `<style>` blob in
  `dashboard.py` with **hard-coded dark tokens** (`--bg:#07140d …`), not imported from `docs/brand/design-tokens.css`.
- Auth: session HMAC cookie (`research_session`), double-submit CSRF, Origin/Host allow-list middleware,
  per-route `signed_in()` checks, HMAC-signed internal endpoints (`X-Research-Signature`).
- Feature classification (private / publishable):
  - **Private only**: research runs, followers/graph, audiences, inbox, ops/watchlist/backups, mini app.
  - **Publishable today**: Studio drafts → `GET /content/drafts/{id}/ebook.md` and
    `GET /content/export/publish-pack?format=md|ics` (`research_admin/cards.py`), which feed
    `content/ebooks/**/manuscript*.md` → ebook-builder. This is the existing human-mediated publication path.
  - **No JSON manifest / storefront publication contract exists.** Phase 3 builds it.
- Storefront links: `_relay_token_to_web()` POSTs to `${WEB_INTERNAL_URL}/api/internal/threads-token`,
  but **no such route exists in `apps/web`** (dead contract on one side). Reverse `/internal/ingest/web-signals`
  likewise unimplemented in the storefront.
- Tests: 19 files, 179 tests, all green (session/CSRF/OAuth/research/studio/followers/dashboard/app).
- Commands: `uv sync --locked --all-extras --dev`, `uvx ruff check .`, `uv run pytest -q`.

## 5. Ebook builder inventory

- `ebook-builder build <dir> --tier {poket|membangun|teman-hidup} --out <dir>` → WeasyPrint, one PDF per `*.md`.
- `python -m ebook_builder.pocket_cli <manuscript.md>` → headless Chrome A4 composed pages + layout audit.
- Templates: only `packages/ebook-builder/templates/ebook-interior.html` (shared, 6×9 in, tier differences are
  cover-only `:root` ramps at lines 123-139) and `templates/cover.html` (rendered only by
  `packages/brand-tools/build-tier-covers.py`). The Edisi Poket A4 design lives as a CSS string inside
  `ebook_builder/pocket.py::_page_css()`.
- **There are no per-tier interior templates today.** Phase 4 introduces scoped tier templates.
- Fonts shared from `packages/brand-tools/fonts/` (Fraunces Display, Source Serif 4, Inter).
- Tier naming map (`cli.py:20-24`): `tier-1-free → poket`, `tier-2-standard → membangun`, `tier-3-premium → teman-hidup`.
- Tests: 4 files, 98 tests, green (manuscript parser, typesetter, watermark, pocket Chrome render assertions).

## 6. Video inventory

- Current project: `videos/edisi-poket-launch-v2` (HyperFrames 0.9.54, `hyperframes.json`,
  `index.html` root `data-width=1920 data-height=1080 data-duration=24`, 7 scene files
  `compositions/frames/01-hook…07-end.html`, audio `assets/audio/score.wav`).
- v1 (`videos/edisi-poket-launch`, 0.9.29) is older and has the Python HTML generator; v2 is hand-authored.
- Commands: `npm run check`, `npx hyperframes lint`, `npx hyperframes snapshot --at …`, `npm run render`, `npm run dev`.
- Baseline check on v2: **passed**, 0 errors, 1 craft warning
  (`line_unread`: "Skrip Bincang Hati ke Hati" on screen 1.46 s vs 1.50 s floor, `06-claim.html` t=19.539s).

## 7. Feature map: research ↔ storefront

| Feature | State |
|---|---|
| Free Edisi Poket PDF | Shared: `content/ebooks/tier-1-free/edisi-poket.pdf` → `GET /api/edisi-poket/pdf` |
| Draft → manuscript → PDF | Shared, human-mediated, file-based (Studio `ebook.md` → `content/ebooks`) |
| Publish pack (md/ics) | Research-only export |
| Research JSON manifest → storefront catalog | **Missing** (Phase 3) |
| Threads token relay `api/internal/threads-token` | **Missing in storefront** (dead contract) |
| Followers/audiences/inbox/knowledge/ops | Private-only, must never export |
| Prices, entitlements, download links | Storefront-authoritative (`src/catalog.ts`, `src/server/*`) — out of research scope |
| Tier specimen templates per edition | **Missing** (Phase 4) |
| Asset provenance manifest | **Missing** (Phase 5) |

## 8. Baseline verification results (all executed 2026-11-19)

| Check | Command | Result |
|---|---|---|
| Storefront typecheck | `npm run lint` (apps/web) | **pass**, exit 0 |
| Storefront tests | `npm test` (apps/web) | **pass** — 55 files, 401 tests |
| Storefront production build | `npm run build` | **pass**, exit 0, all routes generated |
| Brand tests | `uv run --no-project --with pytest --with fonttools --with brotli pytest packages/brand-tools/tests -q` | **pass** — 145 passed, 1 skipped |
| Design lock | `uv run --no-project python packages/brand-tools/check-lock.py` | **pass** — no drift |
| Research lint | `uvx ruff check .` | **pass** |
| Research tests | `uv run pytest -q` | **pass** — 179 passed |
| Ebook lint | `uvx ruff check .` | **pass** |
| Ebook tests | `uv run pytest -q` | **pass** — 98 passed |
| Ebook end-to-end build | `uv run ebook-builder build ../../content/ebooks/tier-1-free/manuscript --tier poket --out /tmp/ph-baseline-dist` | **pass** — `edisi-poket-poket.pdf` (71 274 B) |
| HyperFrames check (v2) | `npm run check` | **pass** — 0 errors, 1 craft warning (hold 1.46 s < 1.50 s floor) |

## 9. Baseline artifacts

- PDFs: `dist/edisi-poket-poket.pdf`, `dist/edisi-membangun-ruang-atau-hukuman/`,
  `docs/brand/preview/ebook-edisi-poket-*.pdf` (6 files), `content/ebooks/tier-1-free/edisi-poket.pdf`.
- Covers: `docs/brand/preview/cover-{poket,membangun,teman-hidup}.png`, `cover-v3-sample.png`.
- Design sheet: `docs/brand/preview/design-system-3-1.png` (check-lock showcase reference).
- Videos: `videos/edisi-poket-launch/renders/edisi-poket-launch_2026-11-10_20-11-04.mp4`,
  `videos/edisi-poket-launch-v2/renders/edisi-poket-launch-v2_2026-11-16_13-21-19.mp4`.
- Illustrations: `docs/brand/illustrations/edisi-poket-kehilangan/*.png` + derived WebP in
  `apps/web/public/illustrations/` via `apps/web/scripts/build-illustrations.mjs`.

## 10. Baseline limitations (stated honestly)

- No pixel-accurate screenshot was taken during baseline. Lightpanda PNGs are text-layout approximations only,
  so visual verification of the current pages is **not** claimed.
- Performance targets (LCP/CLS/INP) were **not** measured at baseline; no field data is available locally.
- Video baseline used HyperFrames `check` only; no frame snapshots or re-render were run in Phase 0.
- The 10 reference repositories were not source-audited; only metadata/README triage exists (plan §3).
