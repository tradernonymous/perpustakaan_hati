# Dark Premium Rebuild Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the storefront (`apps/web`) and research admin UI (`packages/research-admin`) as dark, premium, Raycast-style surfaces on Design System 3.7, with a storefront flow that converts better.

**Architecture:** Make the existing `nightlight` scope the default surface through tokens and `layout.tsx`, then rebuild the home page as a conversion funnel from existing components and assets. Port the same tokens into the research dashboard's inline CSS. Two PRs: storefront, then research UI.

**Tech Stack:** Next.js 16, React 19, Tailwind 3, vitest, plain CSS tokens; Python (research admin, pytest).

**Spec:** `docs/superpowers/specs/2026-11-18-dark-premium-rebuild-design.md`

## Global Constraints

- No new runtime dependencies, no new fonts.
- Keep brand palette: green leads, gold is the luxury detail. Do not copy Raycast red.
- Keep all existing assets (plates, seals, covers, lockup, monogram, OG image).
- Do not touch payment, auth, database, API routes, or Python research logic.
- No invented testimonials or numbers; reuse existing Malay copy.
- No `backdrop-filter` on anything that scrolls below 768px; motion honours `prefers-reduced-motion`.
- Editing `docs/brand/design-tokens.css` requires `python3 packages/brand-tools/check-lock.py --update`.
- Never `cd` into `docs/brand/assets` (creates `.claude/.cc-writes`, breaks `test_lock`).
- Run git network commands with the sandbox bypass.

## Review Focus

- Text on dark below 4.5:1 (muted copy, gold on forest): `check-contrast.py` must cover the new pairs.
- Focus ring invisible on dark: ring colour must be 3:1+ against `--forest-night`.
- Hydration/`themeColor` mismatch: `viewport.themeColor` must match the dark ground.
- Mobile jank: no scrolling blur; hero glow must be static on phones.
- Form still submits: opt-in form moved into the hero must keep labels, error text, and `/api/subscribe` behaviour.
- Sub-pages that hard-code ivory classes (`bg-daylight`, `text-green-900`) become unreadable on dark.

---

### Task 1: Dark default tokens and shell

**Files:**
- Modify: `apps/web/app/layout.tsx` (body class `ph-nightlight`, `themeColor: "#07140d"`)
- Modify: `apps/web/app/globals.css` (body bg/text from surface tokens, focus colour from `--focus-color`)
- Modify: `apps/web/styles/design-tokens.css` (`--ph-system-version: '3.7.0'`, add dark page-level tokens: `--ph-glow-green`, `--ph-glow-gold`, `--ph-hairline-dark`)
- Modify: `docs/brand/design-tokens.css`, `docs/brand/DESIGN-SYSTEM.md`, `docs/brand/design-tokens.json` (mirror and document 3.7)
- Test: `apps/web/tests/dark-default.test.tsx` (create); update `precise-grove.test.ts`, `daylight-a11y.test.ts` where they pin ivory body

**Interfaces:**
- Produces: body has class `ph-nightlight`; CSS vars `--ph-glow-green`, `--ph-glow-gold`, `--ph-hairline-dark`; `.ph-dark-section` (forest-night ground) and `.ph-dark-section-raised` (forest-raised ground) classes used by Tasks 2-5.

- [ ] **Step 1: Write failing test** `dark-default.test.tsx`: read `layout.tsx` source and assert it contains `ph-nightlight` and `#07140d`; read `design-tokens.css` and assert `--ph-system-version: '3.7.0'` and the three new vars exist.
- [ ] **Step 2: Run** `cd apps/web && npx vitest run tests/dark-default.test.tsx` — expect FAIL.
- [ ] **Step 3: Implement** the edits above; keep `.ph-daylight` scope intact for PDF/print.
- [ ] **Step 4: Fix any structural tests** pinning ivory body; do not delete assertions, update them to the dark values.
- [ ] **Step 5: Re-measure contrast** — add the new pairs (gold-light on forest-night, text-muted-on-dark on forest-raised) to `check-contrast.py`, run `python3 packages/brand-tools/check-contrast.py`; expect all pairs >= 4.5:1 (3:1 for graphics).
- [ ] **Step 6: Refresh brand baseline** `python3 packages/brand-tools/check-lock.py --update`, then `python3 packages/brand-tools/check-lock.py` expects pass.
- [ ] **Step 7: Run** `cd apps/web && npm run lint && npx vitest run` — expect pass.
- [ ] **Step 8: Commit** `feat(design): Design System 3.7 dark default surface`.

### Task 2: Header and footer

**Files:**
- Modify: `apps/web/components/SiteHeader.tsx`, `SafetyFooter.tsx`, `StickyCta.tsx`, `BrandMark.tsx` (dark variants only)
- Modify: `apps/web/styles/design-tokens.css` (`.ph-header`, `.ph-sticky-cta` dark rules)
- Test: `apps/web/tests/dark-shell.test.tsx` (create); update `nav-chat-a11y.test.tsx`

**Interfaces:**
- Consumes: Task 1 tokens.
- Produces: `SiteHeader({ base })` signature unchanged; header gets one primary pill link "Dapatkan percuma" to `#percuma` (or `/#percuma` when `base` set).

- [ ] **Step 1: Failing test:** render `SiteHeader`, assert a link named `Dapatkan percuma` with `href="#percuma"`, skip link still first tab stop, header has no `backdrop-filter` class below 768px (class `ph-header` rule check via CSS text).
- [ ] **Step 2: Run, expect FAIL. Step 3: Implement** hairline border, translucent dark ground, pill CTA. **Step 4: Run, expect PASS.**
- [ ] **Step 5: Commit** `feat(web): dark header, footer and sticky CTA`.

### Task 3: Home hero and funnel flow

**Files:**
- Modify: `apps/web/app/page.tsx` (new section order and `Section` dark recipe)
- Modify: `apps/web/components/Hero.tsx` (dark hero, inline free opt-in via `OptInForm`, glow backdrop)
- Modify: `apps/web/components/StatsStrip.tsx`, `Ticker.tsx`, `HowItWorks.tsx`, `Testimonials.tsx`, `Faq.tsx`
- Create: `apps/web/components/ClosingCta.tsx`
- Test: `apps/web/tests/home-funnel.test.tsx` (create); update `redesign.test.tsx`, `redesign-animated.test.tsx`, `hero-heading-order.test.tsx`, `editorial-grove.test.tsx`, `premium-experience.test.tsx`, `ui-ux-upgrades.test.tsx`

**Interfaces:**
- Produces: `ClosingCta(): JSX.Element` with heading and link to `#percuma`.
- Section order in `page.tsx`: Hero (with opt-in, `id="percuma"` anchor kept) → StatsStrip → HowItWorks `#cara` → Bento features `#interaktif` → Tiers `#edisi` → ChapterPreview `#bab` → PlateGallery `#plat` → Testimonials `#pembaca` → Faq `#soalan` → ClosingCta.

- [ ] **Step 1: Failing test:** render `Home`; assert exactly one `h1`; assert order of section ids above via `compareDocumentPosition`; assert `#percuma` exists inside the hero and the opt-in email field has a visible label; assert a `ClosingCta` link to `#percuma`.
- [ ] **Step 2: Run, expect FAIL. Step 3: Implement.** Hero: one primary CTA, one text link to `#edisi`; static glow on phones (no animation under 768px).
- [ ] **Step 4: Run** full vitest; fix structural tests to the new order. **Step 5: Commit** `feat(web): dark home funnel with inline opt-in`.

### Task 4: Cards, tiers, bento, galleries

**Files:**
- Modify: `apps/web/components/TierLadder.tsx`, `TierCompare.tsx`, `EbookDeck.tsx`, `ChapterPreview.tsx`, `PlateGallery.tsx`, `EcosystemHub.tsx`, `ProductCover.tsx`, `Illustration.tsx`
- Modify: `apps/web/styles/design-tokens.css` (`.ph-card`, `.ph-bento*`, `.ph-chapter-card`, `.ph-gallery` dark materials: hairline border, raised ground, soft glow on hover via transform/opacity only)
- Test: `apps/web/tests/dark-cards.test.tsx` (create)

**Interfaces:**
- Consumes: Task 1 classes. Component props unchanged.

- [ ] **Step 1: Failing test:** every `img` in these components keeps `width` and `height`; no source file in these components contains `bg-daylight` or `text-green-900`; hover rules use `transform`/`opacity` only (CSS text check).
- [ ] **Step 2-4:** run FAIL, implement, run PASS. **Step 5: Commit** `feat(web): dark cards, tiers, bento and galleries`.

### Task 5: Sub-pages and forms

**Files:**
- Modify: pages under `apps/web/app/` (`pustaka`, `teman-hati`, `kelab`, `booking`, `beli/[id]`, `hadiah-hati`, `cermin-pasangan`, `kad-jujur-hati`, `surat-hati`, `cabaran-7-hari`, `terima-kasih`, `demo-bayar`) and components `PageShell.tsx`, `OptInForm.tsx`, `CheckoutForm.tsx`, `BookingForm.tsx`, `SuratHatiForm.tsx`, `LibraryLogin.tsx`, `TemanHatiChat.tsx`, `OrderStatus.tsx` (replace ivory-only classes with surface tokens)
- Test: `apps/web/tests/dark-pages.test.tsx` (create); keep `forms-a11y.test.tsx`, `optin-a11y.test.tsx` passing

- [ ] **Step 1: Failing test:** scan those files for `bg-daylight`, `bg-sage`, `text-green-900`, `text-ink-grove` and assert none remain outside `.ph-daylight`-scoped print routes.
- [ ] **Step 2-4:** FAIL, implement, PASS. Form labels and error text stay visible and >= 4.5:1.
- [ ] **Step 5: Build and smoke** `cd apps/web && npm run build`; start with `npm start`, fetch `/` and each route with `lightpanda fetch <url> --dump markdown`; each returns 200 with its h1. Note: text layout only, not pixel-accurate.
- [ ] **Step 6: Commit** `feat(web): dark sub-pages and forms`. Open PR 1 (storefront), wait for CI, squash merge (also when CI fails only for billing; say so in the PR).

### Task 6: Research admin dark UI

**Files:**
- Modify: `packages/research-admin/research_admin/dashboard.py` (CSS blob at the `<style>` block, lines ~1076-1102: swap `:root` vars to dark tokens, cards, tables, forms, status chips, mobile bar)
- Test: `packages/research-admin/tests/test_dashboard.py` (add `test_dashboard_uses_dark_tokens`)

**Interfaces:**
- Produces: `:root` defines `--bg:#07140d`, `--paper`, `--line`, `--ink`, `--muted`, `--gold`, `--green`; HTML structure and class names unchanged.

- [ ] **Step 1: Failing test:** render the dashboard HTML; assert `--bg:#07140d` in the CSS and that no `background:#FBF7F0` remains.
- [ ] **Step 2:** `cd packages/research-admin && uv run pytest tests/test_dashboard.py -k dark_tokens -v` expect FAIL.
- [ ] **Step 3: Implement** dark palette from design tokens; inputs get dark ground and visible 2px focus outline (`#9de1c1`); status chips re-checked at 4.5:1.
- [ ] **Step 4:** full `uv run pytest` expect pass. **Step 5: Commit** `feat(research): dark premium admin UI`. Open PR 2, CI, squash merge.

### Task 7: Report and memory

- [ ] Report what shipped, then Jack's steps (reconnect GitHub if needed; redeploy on Railway). Offer the Front-End Checklist audit. Save a project memory note.

## Self-review

- Spec coverage: dark default (T1), header/CTA flow (T2), funnel + opt-in (T3), assets kept (T4), sub-pages (T5), research UI (T6), contrast/lock/docs (T1), two PRs (T5, T6).
- Types: `SiteHeader({ base })` and `ClosingCta()` named consistently.
- Known limit: Chrome render tests (18) cannot run in the sandbox.
