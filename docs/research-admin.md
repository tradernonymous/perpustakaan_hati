# Research Admin — Threads pain-point mining

Local admin backend that connects to Threads (Meta Graph API) with OAuth, samples your own posts and their public replies, ranks them by engagement, and uses a **free** OpenRouter model to mine audience pain points for the Phase 2 eBooks. Insights land in a local SQLite database; the Threads access token is stored only in the OS keyring (Secret Service), never in a file.

## What it collects (be honest with your audience)

- Up to **50 recent owned posts** (3 API pages), fields: id, text, permalink, timestamp.
- Engagement metrics per post (views, likes, replies, reposts, quotes) — top **5 posts by engagement** are selected.
- Up to **50 visible direct replies** per selected post.
- This is a **sample, not all-time virality**. Threads' API cannot see other users' reply-level engagement, so a wildly viral *comment on someone else's post* will not appear. Every research run labels these limits.
- The sampled material is sent to the AI provider (OpenRouter) **only after you tick the consent box** on the run form.

## One-time setup (Jack only)

1. **Meta app** — <https://developers.facebook.com/apps> → Create app → *Threads* use case. Note the **Threads App ID** (= client id) and **App secret**. Request `threads_basic`, `threads_read_replies`, `threads_manage_insights`. Add Rahimam as an app tester and accept the invitation while the app is in development mode. The server defaults to `http://127.0.0.1:8787/auth/callback`; the URI registered with Meta must match `THREADS_REDIRECT_URI` exactly. **Meta may require an HTTPS redirect**: if HTTP loopback is rejected, set up a loopback-only HTTPS reverse proxy and set `THREADS_REDIRECT_URI` to that local HTTPS callback. This live OAuth setup has not yet been verified; do not expose the admin publicly or weaken TLS checks.
2. **OpenRouter key** — <https://openrouter.ai/keys> → create key. The app only ever uses free models (`openrouter/free` router or any `...:free` model); paid models are rejected before any network call, and `provider.max_price` 0 is enforced in the request.
3. **Store the four configuration values in the keyring** (never paste their values into commands or chat). Each command prompts for its value; the values themselves do not go into shell history.

```bash
secret-tool store --label='Threads client id' service perpustakaan-hati-research account THREADS_CLIENT_ID
```

```bash
secret-tool store --label='Threads client secret' service perpustakaan-hati-research account THREADS_CLIENT_SECRET
```

```bash
secret-tool store --label='OpenRouter API key' service perpustakaan-hati-research account OPENROUTER_API_KEY
```

```bash
secret-tool store --label='Research admin password' service perpustakaan-hati-research account RESEARCH_ADMIN_PASSWORD
```

4. **Run it** (exports read from the keyring; nothing is written to disk):

```bash
export THREADS_CLIENT_ID="$(secret-tool lookup service perpustakaan-hati-research account THREADS_CLIENT_ID)"
```

```bash
export THREADS_CLIENT_SECRET="$(secret-tool lookup service perpustakaan-hati-research account THREADS_CLIENT_SECRET)"
```

```bash
export OPENROUTER_API_KEY="$(secret-tool lookup service perpustakaan-hati-research account OPENROUTER_API_KEY)"
```

```bash
export RESEARCH_ADMIN_PASSWORD="$(secret-tool lookup service perpustakaan-hati-research account RESEARCH_ADMIN_PASSWORD)"
```

```bash
uv run --project packages/research-admin python -m research_admin
```

Open <http://127.0.0.1:8787/login>, sign in with the admin password, click **connect Threads**, authorise in the same browser tab, then return and use **Run research**. A successful run displays JSON; return to `/` to view the saved insights table. Run commands from the repository root. `secret-tool` and an unlocked Secret Service keyring are required before connecting Threads.

## Security model

- Binds to `127.0.0.1` only. Nothing on the LAN (house rule).
- Password login, session cookie (8 h), no external exposure.
- OAuth `state` is single-use, 10-minute, browser- and session-bound (signed cookie) — a stolen state from another browser fails.
- All `POST`s require same-origin; foreign or missing `Origin` and unexpected `Host` headers are rejected.
- Access token: OS keyring only; SQLite keeps just the expiry. Database file is `0600` in `~/.local/state/perpustakaan-hati/research.db`.
- AI answers are validated: quotes must appear verbatim in the sampled material and source URLs must be sampled permalinks, or the run fails loudly instead of storing invented evidence.
- Errors returned to the browser never contain tokens or keys.

## API

| Route | What |
|---|---|
| `GET /` | Status page + insights table |
| `GET /login` / `POST /login` / `POST /logout` | Password session |
| `GET /auth/start` | Begin Threads OAuth (307) |
| `GET /auth/callback` | Finish OAuth, store token |
| `GET /auth/status` | `{"connected", "expires_at"}` |
| `POST /research/run` | Consent-protected research run |
| `GET /research/insights` | Stored insights JSON |

Token refresh: long-lived Threads tokens last ~60 days. When `/auth/status` says disconnected, click **connect Threads** again.

## Tests

```bash
uv run --project packages/research-admin pytest packages/research-admin/tests -q
```
