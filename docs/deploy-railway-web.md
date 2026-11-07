# Deploy the storefront (`apps/web`) to Railway

The storefront is a second Railway service in the same project as the research admin. It is a
public website: any browser can open it, including the Threads and Instagram in-app browsers.

## What it needs

| Item | Value |
|---|---|
| Root Directory | `apps/web` (Railway finds `Dockerfile` and `railway.json` there) |
| Volume | mounted at `/data` (signups are stored in `/data/subscribers.db`) |
| Variable | `DATA_DIR=/data` |
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

## Reading the signup list (for now)

There is no admin page for subscribers yet. Until one exists, open the Railway shell for the
storefront service and run:

```bash
node -e "const D=require('better-sqlite3');console.table(new D('/data/subscribers.db',{readonly:true}).prepare('select * from subscribers').all())"
```

## Privacy

E-mails and WhatsApp numbers are personal data under PDPA. The form records explicit consent, the
list is not shared, and nothing is emailed yet. Delete rows on request.

## Notes

- Security headers (nosniff, referrer policy, permissions policy) are set in `next.config.ts`.
  A Content-Security-Policy is a later hardening step.
- The container runs as root so it can write to the Railway volume, the same as the admin app.
