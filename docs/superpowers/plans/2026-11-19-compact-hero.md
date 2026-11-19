# Compact Hero Implementation Plan

> Execute natively with test-driven-development and verification-before-completion.

**Goal:** Replace the tall homepage hero with the approved text-led introduction.
**Architecture:** Keep Hero as a server component. Return the compact introduction and a separate #percuma section containing the unchanged OptInForm.
**Tech Stack:** Next.js, React, Tailwind, Vitest.
**Spec:** docs/superpowers/specs/2026-11-19-compact-hero-design.md

## Constraints
Keep other agent's working tree intact; use isolated checkout from main. No dependency or shared style changes.

## Review focus
Mobile wrapping, keyboard links, #percuma target, one h1, subscription form preserved.

## Task
- [ ] Add tests for approved heading, CTA targets, separate form section and absent hero media; run and observe failure.
- [ ] Replace apps/web/components/Hero.tsx; update obsolete hero assertions only.
- [ ] Run complete web test suite, TypeScript and production build; review diff.
- [ ] Commit feature branch, push, create PR, check CI and squash merge. Billing-only CI failures may be excepted per Jack; report actual status.

## Verification record
- New tests first failed (3/3), then passed after implementation.
- Full suite: 56 files, 389 tests passed. TypeScript check passed.
- Independent read-only review: no blocking findings.
- Removed obsolete assertions requiring the retired art, beam, book and wordmark; component tests remain.
- Browser preview blocked by sandbox listen EPERM. Production build could not complete here: Turbopack stalled; webpack reported TypeScript --showConfig parsing failure although direct tsc --showConfig succeeds. No claim of successful production build.
