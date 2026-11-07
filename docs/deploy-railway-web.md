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

## Privacy

E-mails and WhatsApp numbers are personal data under PDPA. The form records explicit consent, the
list is not shared, and nothing is emailed yet. Delete rows on request.

## Notes

- Security headers (CSP, HSTS, nosniff, referrer policy, permissions policy) live in
  `src/server/security.ts` and are tested. The CSP allows inline scripts because Next.js needs them;
  a nonce setup is the next hardening step.
- The container runs as root so it can write to the Railway volume, the same as the admin app.
