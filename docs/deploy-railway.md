# Deploy the research admin to Railway

The admin was written as a loopback-only tool. Running it on Railway is supported through a
small set of configuration switches; no source changes are needed per deployment.

Railway gives the app a public HTTPS URL, which also removes Meta's HTTPS-redirect problem.

## What changes on Railway

| Local | Railway |
|---|---|
| binds `127.0.0.1:8787` | binds `0.0.0.0` on `$PORT` |
| token in the OS keyring (`secret-tool`) | token encrypted in SQLite, key from `RESEARCH_TOKEN_KEY` |
| SQLite under `$XDG_STATE_HOME` | SQLite on the mounted volume at `/data` |
| `http://127.0.0.1:8787/auth/callback` | `https://<domain>/auth/callback` |
| host allowlist `127.0.0.1`/`localhost` | host allowlist = your Railway domain |

`RAILWAY_ENVIRONMENT` (set automatically) turns on public mode: HTTPS-only redirect URI,
`Secure` cookies, and a minimum 12-character admin password. The app refuses to boot if any of
those are missing.

## Steps

1. Create a Railway account and a new project from the GitHub repository
   `tradernonymous/perpustakaan_hati`.

2. Open the service settings and set **Root Directory** to `packages/research-admin`. Railway then
   finds `Dockerfile` and `railway.json` in that folder.

3. Add a **Volume** and mount it at `/data`. Without it, the SQLite file and the encrypted Threads
   token are wiped on every redeploy.

4. Generate a token-encryption key. Copy the output and keep it out of git:

```bash
openssl rand -base64 32
```

5. Add these variables in **Variables** (raw editor is fastest):

| Variable | Value |
|---|---|
| `THREADS_CLIENT_ID` | Threads App ID from the Meta app |
| `THREADS_CLIENT_SECRET` | Threads App secret |
| `OPENROUTER_API_KEY` | OpenRouter key |
| `OPENROUTER_MODEL` | `qwen/qwen3.7-flash` (the default; a few hundredths of a cent per run) |
| `RESEARCH_ADMIN_PASSWORD` | at least 12 characters |
| `RESEARCH_VAULT` | `sqlite` |
| `RESEARCH_TOKEN_KEY` | the value generated in step 4 |
| `RESEARCH_DB_PATH` | `/data/research.db` |
| `RESEARCH_PUBLIC` | `1` |

`THREADS_REDIRECT_URI` and `RESEARCH_ALLOWED_HOSTS` are derived automatically from
`RAILWAY_PUBLIC_DOMAIN`, which Railway sets as soon as the service has a domain. Set them yourself
only if you use a custom domain or a proxy in front of Railway.

6. Deploy. Wait for the healthcheck at `/healthz` to pass, then copy the public domain from
   **Settings → Networking → Public Networking**.

7. If the domain was assigned after the first deploy, redeploy so `RAILWAY_PUBLIC_DOMAIN` is picked
   up. The derived callback is `https://<domain>/auth/callback`.

8. In the Meta app, add `https://<domain>/auth/callback` to **Valid OAuth Redirect URIs** and keep
   Rahimam added as an app tester while the app is in development mode.

9. Open `https://<domain>/login`, sign in, click **connect Threads**, authorise, then run research.

## Verify

```bash
curl -fsS https://<domain>/healthz
```

Expected: `{"ok":true}`. Then open `https://<domain>/` in a browser: it must redirect (303) to `/login`, the sign-in form must render, and a correct password must return the dashboard. A JSON `{"error":"Sign in first."}` at `/` means the old build is still running.

## Security notes

- The app is now reachable from the internet. Use a long, unique admin password; sign-in is rate
  limited to 5 failures per 5 minutes per IP.
- The Threads token is encrypted at rest with a key that exists only in Railway's variables. Rotate
  `RESEARCH_TOKEN_KEY` only together with reconnecting Threads, because the old ciphertext cannot be
  decrypted with a new key.
- `RESEARCH_ALLOWED_HOSTS` must match the public domain exactly, or every request returns 400. It is
  filled in from `RAILWAY_PUBLIC_DOMAIN` when unset.
- Do not set `RESEARCH_PUBLIC=0` on Railway: the app would bind loopback and the healthcheck would
  fail.
- Responses are `no-store`; cookies are `HttpOnly`, `Secure`, `SameSite=Lax`.
- The signed-in session is a stateless HMAC cookie derived from `RESEARCH_ADMIN_PASSWORD`, so a deploy no longer signs you out. Changing the password invalidates every existing session — that is the intended way to force sign-out everywhere. Changing `RESEARCH_TOKEN_KEY` is unrelated to sign-in.
- Sign-in accepts either a same-origin `Origin` header or the double-submit `csrf` token from the form, so Safari/webviews that omit `Origin` can still sign in. Cross-site POSTs remain blocked.

## Troubleshooting

| Symptom | Cause |
|---|---|
| `400 Unexpected host header` | `RESEARCH_ALLOWED_HOSTS` does not match the Railway domain |
| `503 RESEARCH_ADMIN_PASSWORD is not set` | password missing or shorter than 12 characters in public mode |
| `400 Threads connection failed; reconnect` | redirect URI mismatch between Meta, `THREADS_REDIRECT_URI`, and the browser URL |
| `OS keyring unavailable` | `RESEARCH_VAULT=sqlite` was not set |
| Research history disappears after deploy | volume not mounted at `/data`, or `RESEARCH_DB_PATH` points elsewhere |
| Opening `/` shows raw `{"error":"Sign in first."}` JSON | build predates the 303-to-`/login` redirect; redeploy |
| Signed out after every deploy | build predates the stateless signed session cookie; redeploy (sessions then last 8 hours and survive restarts) |
| `403 Cross-origin or missing-origin requests are blocked` on sign-in | build predates the CSRF double-submit token; redeploy, then submit the form rather than posting manually |
| App exits on boot with `public mode is misconfigured` | the message lists every missing item: a 12+ character password and/or an HTTPS redirect (generate a domain, or set `THREADS_REDIRECT_URI`) |

## Local use is unchanged

Without `RAILWAY_ENVIRONMENT`, the app still binds `127.0.0.1`, uses the keyring, and defaults to
the loopback redirect URI. See `docs/research-admin.md`.
