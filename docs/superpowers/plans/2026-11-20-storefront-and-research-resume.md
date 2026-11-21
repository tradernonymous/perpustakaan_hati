# Perpustakaan Hati implementation checkpoint

The approved master plan is ready for implementation. The workspace is reachable again. The prior implementation attempt stopped during inspection, before any changes, tests, or release operations for this plan.

## Baseline

- Local branch: `feat/storefront-research-ebook-video-upgrade`. The working tree already contains 67 changed or untracked paths from the earlier upgrade. Preserve and inspect those changes before editing.
- Production was last verified on commit `fa0cd4e` from PR #54, which deployed the compact animated hero. Recheck production before relying on that baseline.
- The earlier combined upload was rejected by automated review over potential exposure of research and publication material in a public repository. Keep private records and paid ebook masters out of public releases.
- Prior release bundle: `dist/release/perpustakaan-hati-upgrade-motion.bundle`. It is a baseline, and predates this approved plan.

## Approved scope and gates

1. **Storefront and social entry.** Publish the distinct Poket, Membangun, and Teman Hidup covers. Remove placeholder testimonials and hide Teman Hati AI across navigation, discovery, direct routes, and any backend entry points. Retain the Teman Hidup ebook. Place the public *Tips Psikologi Suami Isteri* flipbook after the hero and link directly to titles from TikTok and Threads. Guests can read the entire flipbook. All other current and future Poket PDFs are free with sign-in. Check old URLs and server-side access.
2. **Signup and Pustaka.** Launch Google and email first. Preserve the book and page through signup and any handoff from a social in-app browser. Add TikTok and Facebook as provider setup clears. Evaluate Apple and X against observed demand. Keep one reader identity with linked login methods, purchase recovery, a shelf, progress, bookmarks, downloads, and account controls. Record acquisition independently from login provider. Test returning buyers and the reader flow in TikTok and Threads on iOS and Android.
3. **Edition comparison.** Replace the blurred carousel with readable cards and build an accurate desktop comparison. On mobile, show a two-edition comparison with adjustable selections and an option to show differences. Pull current prices from checkout and verify actual inclusions. Check at 320, 375, and 390 pixels, with keyboard access and zoom.
4. **Suara Pembaca.** Shortlist genuine first-person book feedback in a private consent queue, identify the writer to contact, record permission for the exact quote and attribution, and support withdrawal. Publish only approved excerpts. The screenshots do not identify a verified testimonial author.
5. **Research.** Fix the duplicate account label and page alignment. Add Malaysia-time day, week, and month Calendar views, an unscheduled queue, and preserve exports. Improve Studio with searchable evidence, editable briefs, version history, review, preview, and scheduling. Keep evidence and approval records private.
6. **Paid usage and release.** Recheck the previously created daily paid-usage watch before changing it. Add first-billable-use telemetry for storefront, Pustaka, and any Studio background work that serves the storefront. Test notification with a simulated event. Report tests, CI, PR and deployment status, production smoke checks, and any unresolved provider or consent dependencies.

## First implementation slice

Read `apps/web/AGENTS.md` and the applicable local Next.js documentation. Start with the existing cover and catalog work, the comparison layout, Teman Hati AI visibility, and placeholder testimonials. Inspect `packages/research-admin/research_admin/dashboard.py` for the shared header and layout fixes. Use focused changes and verify the slice before moving into authentication and book access.

## Implementation progress

- PR #55 merged as `c0dd2ad` after GitHub CI passed. It hides Teman Hati AI by default and removes the public sample testimonials and their navigation links.
- Local storefront work includes checkout-linked prices, the two-edition mobile comparison, the public ten-page Tips reader, protected Poket download routes, email login, Google login for verified Gmail accounts with an email fallback, a Pustaka shelf, and a saved Tips bookmark.
- Local Research work includes the header and page alignment fixes, Malaysia-time day/week/month views with a ready-to-schedule queue, and the searchable Studio evidence picker.
- Local checks passed for 416 storefront tests, TypeScript, and four Research dashboard tests. The local production build and broader Research integration runs reached their timeouts.
- The protected-download release needs a working email sender and Google OAuth for the storefront. Railway has `DOWNLOAD_SECRET` configured. Set `SITE_URL=https://perpustakaanhati.biz`, `RESEND_API_KEY`, `EMAIL_FROM`, `GOOGLE_READER_CLIENT_ID`, and `GOOGLE_READER_CLIENT_SECRET` on the web service. Register `https://perpustakaanhati.biz/api/pustaka/google/callback` with the Google Web application. Confirm the approved supplemental Poket files exist in the private assets directory.
- Remaining work includes additional identity providers and account linking, social attribution, broader reading controls, the testimonial consent workflow and approved quotes, Studio versioning and review, and the first-billable-event integration. The daily paid-usage watch is active.
