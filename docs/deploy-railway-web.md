# Deploy the storefront (`apps/web`) to Railway

The storefront is a second Railway service in the same project as the research admin. It is a
public website: any browser can open it, including the Threads and Instagram in-app browsers.

## What it needs

| Item | Value |
|---|---|
| Root Directory | `apps/web` (Railway finds `Dockerfile` and `railway.json` there) |
| Volume | mounted at `/data` (signups are stored in `/data/subscribers.db`) |
| Variable | `DATA_DIR=/data` |
| Variable | `SITE_URL=https://<your domain>` (canonical URL, sitemap) |
| Variable | `ADMIN_TOKEN=<long random string>` (password for the subscriber export) |
| Healthcheck | `/healthz` (already in `railway.json`) |

Without the volume, every redeploy wipes the signup list.

## Steps

1. In the existing Railway project, click **New → GitHub Repo** and pick
   `tradernonymous/perpustakaan_hati` again. This creates a second service next to the admin.
2. In the new service, open **Settings** and set **Root Directory** to `apps/web`.
3. Add a **Volume** and mount it at `/data`.
4. In **Variables**, add `DATA_DIR` with the value `/data`.
5. Open **Settings → Networking → Generate Domain**. Later, add your own domain here.
6. Deploy and wait for the `/healthz` check to pass.
7. Leave the admin service untouched. Its Root Directory stays `packages/research-admin`.

## Verify

```bash
curl -fsS https://<domain>/healthz
```

Expected: `{"status":"ok"}`. Then open `https://<domain>/` on your phone and submit a test signup
with your own e-mail.

## Reading the signup list

Open `https://<domain>/admin/subscribers` in a browser. It asks for a login: type any user name and
use `ADMIN_TOKEN` as the password. You get `subscribers.csv`. Without `ADMIN_TOKEN` set, the page
always refuses.

## Admin sign-in with Facebook

`/admin` is the site's admin door. It opens with either credential:

1. **Facebook Login**, for the accounts listed in `ADMIN_FACEBOOK_IDS`. A successful
   Facebook login is not enough on its own: an id that is not on the list is refused
   with a 403 and no session is opened.
2. **The `ADMIN_TOKEN` password**, kept as the fallback so the door can never lock you out.

Add these **Variables** to the web service:

| Variable | Value |
|---|---|
| `FACEBOOK_APP_ID` | App ID from **Meta dashboard → App settings → Basic** |
| `FACEBOOK_APP_SECRET` | App secret from the same panel (mark it secret in Railway) |
| `ADMIN_FACEBOOK_IDS` | Comma-separated numeric Facebook user ids allowed to sign in |
| `FACEBOOK_REDIRECT_URI` | optional; defaults to `${SITE_URL}/api/auth/facebook/callback` |

In the Meta dashboard, under **Facebook Login → Settings → Valid OAuth Redirect URIs**, add
exactly `https://web-production-0cfb9.up.railway.app/api/auth/facebook/callback`. Keep the
app in **Development** mode and list the account under **App roles** — Facebook then refuses
anyone who is not on that list before our allowlist is even consulted.

To find your numeric id: open <https://developers.facebook.com/tools/explorer>, run
`GET /me?fields=id,name`, and copy `id` (not the name).

The session is a signed cookie (`<expires>.<hmac>` keyed on `ADMIN_TOKEN`), HttpOnly,
SameSite=Lax, Secure on https, valid for 8 hours. There is no session table: rotating
`ADMIN_TOKEN` signs everyone out.

## Connect Rahimam's Threads

The site has a small admin-only Threads OAuth flow. It stores one long-lived token
(60 days, refreshable) in `/data/threads.db` and never exposes it to the browser.
Facebook Login is **not** what grants Threads access: a Facebook session cannot read or
post to Threads. Threads has its own authorization window (`threads.com/oauth/authorize`)
and its own Threads App ID and secret, found in the same Meta app under
**App settings → Basic**. Facebook Login is used only to prove *who is signing in* to
`/admin` (see the section above).

Add these **Variables** to the web service:

| Variable | Value |
|---|---|
| `THREADS_APP_ID` | Threads App ID from **App Dashboard → App settings → Basic** |
| `THREADS_APP_SECRET` | Threads App secret from the same panel (mark it secret in Railway) |
| `THREADS_REDIRECT_URI` | `https://web-production-0cfb9.up.railway.app/api/auth/threads/callback` — must be the **web** service, not the Python admin service |
| `THREADS_SCOPES` | optional, defaults to `threads_basic`; add `threads_content_publish` only after Meta approves that permission |

In the Meta app, add **Threads API** as a product, then paste the exact
`THREADS_REDIRECT_URI` under **Threads API → Settings → Valid OAuth Redirect URIs**.
While the app is in development mode, add Rahimam's Threads account as an app tester
and accept the invite from that account.

Then, in a browser:

1. Open `https://<domain>/api/auth/threads/start`. Log in with any user name and
   `ADMIN_TOKEN` as the password. Approve the Threads window as @rahimam.
2. `https://<domain>/api/auth/threads/status` (same login) reports
   `{ connected, username, expiresAt, daysLeft }`.
3. Refresh before the 60 days run out: send `POST` to
   `/api/auth/threads/refresh` with `Authorization: Bearer $ADMIN_TOKEN`.
   Meta rejects a refresh within 24 hours of issue, so refresh monthly.

Notes:

- The token is stored unencrypted in SQLite on the Railway volume. That is the same
  trust boundary as the order and subscriber databases; anyone with volume access
  already owns the service.
- If the app stays in development mode, only accounts listed as testers can
  authorize, and tokens can expire when testing access is revoked.
- Reconnecting overwrites the stored token, so one account is connected at a time.

## Privacy

E-mails and WhatsApp numbers are personal data under PDPA. The form records explicit consent, the
list is not shared, and nothing is emailed yet. Delete rows on request.

## Offer the Edisi Poket PDF ("Cuma Kawan Pejabat")

The pocket edition built from Rahimam's Threads post lives at
`docs/brand/preview/ebook-edisi-poket-cuma-kawan-pejabat.pdf` in the repo. It is a
free tier-1 product: no checkout, no order, no watermark.

Rebuild it after any copy change:

```
cd packages/ebook-builder
uv run --project . python -m ebook_builder.pocket_cli \
  ../../content/ebooks/edisi-poket-cuma-kawan-pejabat/manuscript.md \
  --out ../../docs/brand/preview/ebook-edisi-poket-cuma-kawan-pejabat.pdf
```

The build measures every page in headless Chrome, scales each page's type so the
sheet reads as composed, and fails if any text block ends on a single word. Chrome
is required, because WeasyPrint does not clip the cover's foil gradient to the
glyphs.

To offer it for download:

1. Copy the PDF into the web service's assets directory on the Railway volume
   (`ASSETS_DIR`, alongside `edisi-membangun.pdf` and `teman-hidup.pdf`). The
   free tier has no `ProductId` today, so it needs a free download route that
   serves this file directly rather than through `/muat-turun/[token]`, which
   requires a paid order.
2. Point the "Edisi Poket, percuma" block on the landing page at that route.
3. Keep the tier seal and the "Edisi Poket" name on the cover, as
   `docs/brand/tier-naming.md` fixes them.

## Notes

- Security headers (CSP, HSTS, nosniff, referrer policy, permissions policy) live in
  `src/server/security.ts` and are tested. The CSP allows inline scripts because Next.js needs them;
  a nonce setup is the next hardening step.
- The container runs as root so it can write to the Railway volume, the same as the admin app.
