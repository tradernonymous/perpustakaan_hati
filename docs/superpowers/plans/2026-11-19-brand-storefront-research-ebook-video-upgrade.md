# Perpustakaan Hati — storefront, research, ebook and motion upgrade plan

Date: 2026-11-19
Status: Draft for review. Planning only; no implementation or deployment authorized by this document.

## 1. Brief and scope

Upgrade the existing product rather than scaffold a replacement. Preserve Malay editorial voice, green brand recognition, current purchases, downloads, authentication and research workflows. Make the storefront minimal, mobile-first and impactful; make the research application visually consistent without exposing private research. Give each ebook tier a genuinely different editorial identity. Refresh videos using those same approved assets.

Required skills for execution:
- `/ui-ux-pro-max:ui-ux-pro-max`: visual direction, responsive behavior, accessibility and component states.
- `/ecc:orch-build-mvp`: staged delivery of an existing-system vertical slice, not a new application scaffold. Approve its slice plan before execution.
- `/hyperframes:hyperframes-animation`: deterministic video choreography and reusable motion treatments.

This document is a proposed implementation brief for those workflows, not a claim that any build, render or visual audit has passed.

## 2. Baseline and decisions

The supplied repository baseline is Design System 3.8 Void Grove, following 3.6 Precise Grove and 3.7 Dark Grove. Do not revert to the older 3.6 target in `docs/superpowers/specs/2026-11-18-dark-premium-rebuild-design.md`.

Known design sources include `docs/brand/design-tokens.json`, `docs/brand/design-tokens.css` and `apps/web/styles/design-tokens.css`. The storefront is `apps/web`; the existing design brief identifies the research application as `packages/research-admin`. Verify current entry points and commands before implementation.

### Approaches considered
1. Cosmetic refresh only: smallest change, but does not solve synchronization or ebook differentiation.
2. **Recommended: shared foundations with separate surface compositions.** Reuse current applications, introduce tier-scoped editorial tokens, replace the hero, and add a narrow publication contract. This balances distinctiveness with maintainability.
3. Full framework rewrite: unnecessary migration risk and slower delivery; no evidence currently justifies it.

### Locked requirements from the request
- Dark website backgrounds, mobile-first interaction and restrained animation.
- Replace or remove the current hero design.
- Edisi Poket: green and gold.
- Edisi Membangun: white primary, green and gold supporting.
- Teman Hidup: black primary, green and gold supporting, premium editorial details.
- Upgrade design assets and video together.

### Proposed defaults, not approved product decisions
- Keep existing licensed fonts unless a specimen demonstrates a clear improvement.
- No autoplay video in the mobile hero.
- Research-to-storefront synchronization means an explicit approved publication step, not live mirroring of private research.
- Preserve prices and product promises; invent no testimonials, usage counts, counseling services or premium entitlements.

## 3. Reference research and applicability

Research method: public GitHub repository metadata and README excerpts retrieved on 2026-11-19. This is reference triage, not a source-code audit, live UI review, security review or proof that a project uses the newest techniques. Verify exact source files and licenses before reusing implementation or assets. Repository popularity is not a suitability criterion.

| Reference | Verified scope | Proposed inspiration | Boundary |
|---|---|---|---|
| [Ant Design Landing](https://github.com/ant-design/ant-design-landing) | Landing templates built with Ant Motion; modular and responsive sections | Section rhythm, one-action hero, reusable reveal choreography | MIT metadata; do not import its whole template stack or assume dependencies are current |
| [china-dictatorship](https://github.com/cirosantilli/china-dictatorship) | Political information/archive repository | At most, evaluate navigation of long-form source material | Not a design-system reference; exclude political copy and imagery from this brand |
| [awesome-architecture](https://github.com/study8677/awesome-architecture) | Architecture tutorials, templates and end-to-end cases | Document publication boundaries, trade-offs and failure recovery | MIT metadata; no justification for microservices or additional infrastructure |
| [Carbon Design Kit](https://github.com/carbon-design-system/carbon-design-kit) | Versioned components, icons, styles and grid templates; accessibility guidance | Token roles, component states, grid discipline and accessible controls | Apache-2.0 metadata; asset/trademark terms still need inspection; do not copy IBM branding |
| [React](https://github.com/react/react) | UI library repository | Component boundaries and progressive interaction, where current stack supports them | MIT metadata; not a visual template or reason to rewrite the Python research UI |
| [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) | Image-generation interface | Reproducible asset production with prompts, seeds and review records | AGPL-3.0 code; model and generated-asset rights are separate. No installation or GPU workload in this task |
| [Open WebUI](https://github.com/open-webui/open-webui) | AI-oriented application interface | Investigate workspace navigation, searchable history and progressive disclosure | GitHub license metadata is `Other/NOASSERTION`; inspect current license and branding terms before reuse |
| [React Hook Form](https://github.com/react-hook-form/react-hook-form) | Form state and validation library | Accessible validation, submission feedback and draft preservation | MIT metadata; add only if current forms need it, not for simple forms already working |
| [IT Tools](https://github.com/CorentinTh/it-tools) | Developer utilities collection with Vue-oriented tooling | Investigate searchable tools, favorites and clear tool entry points for research | GPL-3.0 metadata; independently implement relevant patterns rather than copying components |
| [Wand Enhancer](https://github.com/k1tbyte/Wand-Enhancer) | UX/interoperability extension for Wand/WeMod | Investigate optional controls and settings organization | Apache-2.0 metadata; desktop extension behavior is not a storefront dependency |

The UI/UX skill search suggested storytelling and liquid-glass treatments. Adopt only the readable narrative structure and accessible interaction guidance. Reject blanket glass effects, its generic light palette and its font recommendations: they conflict with this brief and add mobile cost. The recommendations below are project-specific proposals, not features verified in each reference.

## 4. Visual system: quiet editorial, not decorative overload

Retain the near-black web foundation and green identity. Use gold sparingly for hierarchy, fine rules and premium edition details. Favor generous spacing, strong type, real cover artwork and one focal point over glow stacks, floating particles, glass cards or generic bento layouts.

### Token architecture
- Primitive layer: existing colors, font families, spacing and radius values.
- Semantic layer: web canvas, raised surface, readable text, muted text, border, action, focus, success and error.
- Tier layer: page ground, page ink, heading, rule, ornament, reflection field and cover treatment.
- Motion layer: feedback, entrance and scene-change duration/easing, plus reduced-motion equivalents.
- Scope ebook themes to their renderer; a white Membangun PDF must not turn the storefront white.
- Keep canonical and generated token files synchronized through the existing generation workflow. Do not maintain divergent hand-edited palettes.

Build a review sheet covering buttons, inputs, validation, cards, navigation, dialogs, empty/loading/error states and all three tier specimens. Check contrast on actual combinations, not individual swatches.

## 5. Storefront: replace the hero

### Recommended composition

```text
Compact wordmark                       Menu

A short Malay promise
that fits on a phone.
One sentence describing the reader benefit.

[Start with Edisi Poket]  [Browse editions]

One authentic cover + a readable interior excerpt
(no rotating carousel, no large decorative beam)

Choose your next step
Poket / Membangun / Teman Hidup
```

Desktop may use a balanced text-and-art split. Mobile uses copy, primary action, then one static artwork. The current hero beam and competing decorative elements are replaced, not layered underneath a new hero.

Page sequence: hero → real sample → tier comparison → relevant catalog → how access works → factual FAQ → closing action. Only include social proof with verified source and permission.

### Functional scope
- Search and filter editions using existing catalog fields; keep filters in the URL.
- Clear tier comparison, sample preview and price/access explanation.
- Preserve opt-in, checkout, booking and download paths.
- Evaluate saved editions as a later slice; do not silently introduce account requirements or cross-device synchronization.
- Reuse the existing quick-jump pattern where useful; do not duplicate search interfaces.
- Mobile primary action must not hide content, keyboard focus or consent controls.

## 6. Research application and publication synchronization

First inventory existing research features and mark each as: private-only, public-ready, or missing. Visual consistency does not mean porting every admin control to the storefront.

### Proposed publication flow

```text
Research draft → editorial review → approved version
                                      ↓
                         validated public manifest
                                      ↓
                         storefront/catalog/preview
```

Start with the simplest mechanism supported by the existing repository: a versioned manifest/export and explicit import is preferable to introducing a service. Use an authenticated server-side API only if existing architecture and freshness requirements justify it.

Proposed contract fields: stable item ID, slug, title, tier, approved summary, artwork reference, sample reference, publication status, schema version and content revision. Prices, entitlements and paid file locations remain under their existing authoritative systems, not editable via public research payloads.

Required behavior:
- Drafts and private notes never appear in public exports.
- Explicit permission checks for preview and publication.
- Validate allowed fields, URLs, assets and revisions before publication.
- Idempotent publication; reject stale revisions instead of silent overwrites.
- Preserve last known good published version if export/import fails.
- Record publication outcome and offer a controlled rollback.
- Show pending, synchronized and failed states with retry guidance.
- Never place privileged credentials or private download URLs in client bundles.

Research UI proposals: dark navigation shell, searchable work list, clearly separated reading/editing/review states, mobile cards instead of unusably wide tables, draft preservation and visible validation. Prioritize existing workflows over adding an AI chat interface merely because Open WebUI was referenced.

## 7. Ebook tier identities

Differentiate layout, pacing and material treatment—not just background color.

| Tier | Identity | Layout and typography | Signature assets |
|---|---|---|---|
| Edisi Poket | Intimate green-and-gold reading companion | Compact chapters, one idea per spread, friendly reflection cards, restrained serif emphasis | Botanical line work, small gold rules, soft illustration vignettes |
| Edisi Membangun | White editorial workbook | White reading pages, structured exercises, wider writing space, green chapter navigation, gold separators | Paper texture used lightly, diagrams where useful, practical worksheet markers |
| Teman Hidup | Black collector-style edition | Spacious opening spreads, large chapter numerals, carefully paced imagery, premium typographic hierarchy | Subtle foil-like gold detail, black material texture, green accents, bespoke chapter artwork |

Digital foil is a visual simulation, not a print-production guarantee. Premium must remain readable: no low-contrast gold body copy or ornaments behind paragraphs. Offer a print-friendly treatment for ink-heavy pages if included in the approved scope.

### Ebook acceptance
- Approve cover, chapter, exercise and closing-page specimens for each tier before batch conversion.
- Text remains selectable/searchable; fonts embed correctly; links work.
- No missing glyphs, duplicated body/document markup, inconsistent numbering, orphan headings or truncated writing fields.
- Verify both image containment and subject framing. `object-fit: cover` may crop artwork; use a deliberate focal point or `contain` when the whole illustration matters.
- Fixed image panels in flex layouts must not silently shrink or displace the footer.
- Check every exported page, not only HTML. Previous absolute-positioning changes are not evidence that all ebook overflow is resolved.
- Preserve source attribution and distinguish quotations from adaptations.
- Remove unsupported pricing, service promises and testimonials.

## 8. Asset production plan

Proposed new locations, to confirm against current asset conventions:
- `docs/brand/assets/refresh-2026-11/`: approved shared design assets and provenance manifest.
- `docs/brand/illustrations/<topic>/`: topic illustrations, retaining existing originals.
- `docs/brand/specimens/`: three tier specimen sets and a component/motion sheet.
- Existing video project directory: refreshed compositions, not a second unrelated video framework.

Asset list: one hero focal image or cover composition, three tier covers, three interior samples, restrained tier ornaments/textures, video poster images and aspect-ratio-specific end cards.

Each asset record should include source, creator, license/permission, intended surface, original filename, optimized derivative, dimensions, focal point and alt text. Generated assets additionally record model/license, prompt, seed when available and human approval. Do not invent a generated image URL or run Stable Diffusion merely because it is listed as inspiration.

Use SVG for appropriate vectors, AVIF/WebP for web illustrations and high-quality print assets for PDFs. Preserve originals; never indiscriminately overwrite unrelated illustrations. Lazy-load below-fold images, not the hero LCP asset.

## 9. Video and motion direction

Refresh the existing launch concept after tier artwork is approved. Proposed master: 24 seconds, with 9:16 primary and independently reframed 4:5 and 16:9 exports.

### Storyboard
- 0–3s: concise emotional hook, fully readable text.
- 3–8s: Poket green/gold cover and one usable interior detail.
- 8–13s: Membangun white workbook and reflection/exercise detail.
- 13–19s: Teman Hidup black edition, slower premium reveal and readable spread.
- 19–24s: the three-tier ladder and one truthful action/end card.

Use two to four motion patterns: opacity/vertical entrance, restrained cover transform, rule wipe and match-cut transition. No obligatory 3D, particles, strobing or blur-heavy text. Keep holds long enough to read Malay copy; audio never carries the only meaning.

Hyperframes requirements: one paused, registered root timeline; finite duration; deterministic seeking; no random/time-dependent layout; transforms rather than width/height animation; no asynchronous timeline construction. Use tier tokens in scenes and keep captions inside platform-safe regions.

Acceptance: lint/check the composition using the installed CLI's verified commands; inspect snapshots at scene boundaries and mid-motion; inspect the rendered first/last frame, audio sync, text clipping and all aspect ratios. Produce MP4 outputs and static posters. Check audio rights before including music. A browser text-layout approximation is not a video quality check.

Web motion is separate: short feedback transitions and small entrances, reduced-motion fallback, no scroll hijacking, no continuous background animation on mobile, pause decorative motion offscreen. Do not load the video timeline runtime into the storefront just for hover effects.

## 10. Ordered execution slices

Each slice requires a small diff, relevant tests, review and explicit evidence before completion. Use `/ecc:orch-build-mvp` against this document only after approving scope; reuse the existing scaffold.

### Slice 0 — Baseline and scope gate
- [ ] Confirm current entry points, scripts, route inventory, research capabilities, video sources and ebook generation paths.
- [ ] Capture current functional tests and representative screenshots/exports.
- [ ] Agree the public/private publication boundary and initial feature-parity list.
- [ ] Review reference licenses for any actual reuse.
- Exit: approved scope, artifact list and reliable verification commands; no product edits yet.

### Slice 1 — Foundations and one end-to-end specimen
- [ ] Define scoped semantic/tier/motion tokens and update brand documentation.
- [ ] Create one Poket specimen and its storefront card using the same approved asset.
- [ ] Carry one approved research item through the chosen publication contract into that card.
- [ ] Test draft exclusion, invalid payload rejection and preservation of the last published version.
- Exit: one functional publication-to-catalog path, not a full visual rebuild.

### Slice 2 — Storefront hero and catalog
- [ ] Replace current hero with the proposed mobile-first composition.
- [ ] Add or refine catalog search, filters, tier comparison and preview using existing data.
- [ ] Preserve opt-in, checkout, booking and download regression coverage.
- Exit: complete mobile discovery-to-existing-purchase/access journey.

### Slice 3 — Research workspace
- [ ] Apply shared tokens to navigation, reading/editing and mobile layouts.
- [ ] Add publication status, validation, retry and rollback UI supported by Slice 1.
- [ ] Test permission checks, stale revisions and failure handling.
- Exit: complete private draft-to-approved-publication workflow.

### Slice 4 — Three ebook editions
- [ ] Approve all three specimen sets.
- [ ] Implement tier-scoped renderer templates without changing editorial content silently.
- [ ] Export representative PDFs, inspect every page, then convert the remaining selected content.
- Exit: genuinely distinct, readable, correctly numbered exports with no cropping/overflow defects.

### Slice 5 — Video and assets
- [ ] Reuse approved tier artwork and tokens in the existing composition.
- [ ] Implement storyboard and inspect deterministic snapshots.
- [ ] Render/review each aspect ratio and produce optimized poster images.
- Exit: actual playable exports with asset provenance, not just composition source.

### Slice 6 — Integrated release gate
- [ ] Run functional, accessibility, performance and visual/export checks below.
- [ ] Review changed code, security-sensitive publication logic and React/TypeScript changes with the appropriate reviewers.
- [ ] Confirm no unrelated files or generated junk enter the change.
- [ ] Follow authorized repository release workflow; never bypass failed checks or permission denials.
- Exit: shipped report with changed surfaces, commit/PR if authorized, real artifact paths, evidence and remaining limitations.

## 11. Quality gates

Proposed performance targets, to measure rather than claim in advance: mobile LCP ≤2.5s, CLS ≤0.1 and field INP ≤200ms where field data exists. Lab interaction measurements are proxies, not field INP. Establish a representative route/device/network baseline before setting bundle and asset budgets.

Accessibility: WCAG 2.2 AA target; normal text contrast ≥4.5:1, large text ≥3:1, visible focus, keyboard access, semantic headings, labeled forms, useful errors, reduced-motion support and at least 44×44px intended touch targets. Test 320/375/390/768/1024/1440px layouts and 200% zoom. No hover-only functionality.

Verification inventory:
- Run the current storefront typecheck, lint, test and production-build scripts discovered from `apps/web/package.json`.
- Run existing research and ebook tests using their documented environments.
- Run brand contrast and lock checks; regenerate lock baseline intentionally when canonical tokens change.
- Add failing behavioral tests before new code; do not delete existing assertions merely to make a redesign pass.
- Publication tests: unauthorized access, draft leakage, malformed input, retry, idempotency, stale revisions and rollback.
- PDF checks: page count, text extraction, embedded fonts, links, layout and image framing.
- Video checks: composition validation, seek determinism, scene snapshots and final playback.
- Use permitted browser tooling. Lightpanda PNGs are text-layout approximations; explicitly report pixel-accurate visual verification as blocked if no permitted renderer is available.
- Audit against the [Front-End Checklist](https://frontendchecklist.io): HTML, CSS, JS, accessibility, performance, SEO, security and images.

## 12. Risks and approval boundary

Primary risks: broad scope; unintended ebook/theme coupling; private research leakage; publication conflicts; licensed asset reuse; expensive mobile effects; export-only layout failures; treating old plans or memories as current verification.

Mitigation: one vertical slice first, scoped themes, explicit publishing, deterministic assets, representative specimens and real output inspection. Keep existing exported deliverables available until their replacements pass review. Publish selected revisions explicitly and retain a known-good rollback artifact; never mutate public assets in place without a versioning decision.

Approval needed before implementation: proposed hero direction, specimen identities, publication scope and slice order. Exact typography spacing and implementation details remain builder decisions within these constraints. No dependency installation, cloud resource creation, paid image generation, production migration or deployment is part of this planning task.
