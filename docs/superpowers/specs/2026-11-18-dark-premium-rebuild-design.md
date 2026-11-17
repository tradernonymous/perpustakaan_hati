# Dark premium rebuild (storefront + research site) — design

Date: 2026-11-18. Status: awaiting approval.

## Intent
Rebuild the storefront (`apps/web`) and the research admin UI (`packages/research-admin`) on Design System 3.6 Precise Grove, in a dark, clean, premium look with Raycast (raycast.com) as the layout reference. The storefront must also convert better: more visitors reach the free Edisi Poket opt-in and then a paid tier.

## Goals
- Dark ground by default on both sites, using the existing `nightlight` scope and `--forest-night` tokens.
- Storefront home rebuilt around one primary action per screen, in this order: hero + inline free opt-in, social proof, how it works, bento feature grid (edisi, plates, Teman Hati, club), tier ladder, testimonials, FAQ, closing call to action. Mobile sticky call to action stays.
- Keep every existing asset: illustration plates, seals, covers, lockup, monogram, OG image.
- Keep Malay copy, brand voice, payment/checkout/booking behaviour, and all API routes untouched.
- Research UI: same tokens, sidebar, cards, tables, forms on dark, same behaviour.
- Accessibility holds: contrast pairs re-measured in `check-contrast.py`, focus ring, reduced motion, no backdrop-filter on scrolling elements on phones.

## Non-goals
- No new runtime dependencies, no new fonts.
- No changes to payment, auth, database, or the Python research logic.
- No copy a reader has not seen (no invented testimonials or numbers).
- Sub-pages (`/pustaka`, `/teman-hati`, `/kelab`, `/booking`, etc.) get the dark shell and tokens, not new layouts.

## Anti-goals
- A dark page that is only ivory repainted.
- Copying Raycast's red, keyboard artwork or text.
- Breaking the brand rule: green leads, gold is the luxury detail; AJE black-and-gold stays separate.

## Constraints
- Next.js 16, Tailwind 3, plain CSS tokens in `apps/web/styles/design-tokens.css`.
- 50 vitest files pin current structure; tests are updated first (TDD), not deleted to pass.
- Brand lock: editing `docs/brand/design-tokens.css` needs `check-lock.py --update`.
- Chrome render tests (18) cannot run in the sandbox.
- Research UI CSS is one inline blob in `dashboard.py`.

## Approaches
1. Token flip only: fast, but reads as dark paint on an ivory layout.
2. Dark re-skin plus new home flow: lower risk, keeps component structure.
3. Full rebuild of layout (picked by Jack): new page and component structure for the home page, headers, cards and research shell. Highest risk and longest PR; mitigated by TDD, two separate PRs, and keeping data/behaviour modules untouched.

## Decisions (Jack's)
- Approach 3, full rebuild.
- Raycast is the reference for layout and polish; palette stays brand green and gold.

## My calls (builder may adjust)
- Dark becomes the default storefront surface; ivory stays for PDFs and print. DESIGN-SYSTEM.md is updated to say so and version bumps to 3.7.
- Two PRs: storefront first, research UI second.
- Build in this order per surface: tokens and shell, then sections, then sub-pages.
- Verification: `tsc`, vitest, `check-contrast.py`, `check-lock.py`, Python tests, plus Lightpanda text-layout checks (not pixel-accurate).
- CI failing only for billing: squash merge anyway, as Jack said, and say so in the report.

## Left to the builder
Exact spacing, glow gradients, card layouts, and component names within the structure above.

## Risks
- Large diff; many structural tests to rewrite.
- GitHub connector must be connected to open and merge PRs.
- Cannot pixel-check renders in the sandbox.
