# Research Admin — Threads pain-point mining

Local admin backend that connects to Threads (Meta Graph API) with OAuth, samples your own posts and their public replies, ranks them by engagement, and uses the configured OpenRouter model to mine audience pain points for the Phase 2 eBooks. Insights land in a local SQLite database; the Threads access token is stored only in the OS keyring (Secret Service), never in a file.

## What it collects (be honest with your audience)

- Sample sizes are set per run on the Research page — owned posts to fetch, posts to prioritize, and replies per post — with server-side ceilings of **150 posts**, **25 prioritized posts**, and **100 replies per post**. Defaults are 50 / 5 / 50.
- Engagement metrics per post (views, likes, replies, reposts, quotes) — the highest-scoring posts are selected and their metrics are kept in each bounded research-run history entry, together with the limits that run used.
- The run form shows these limits; a status board on the same page shows the Threads connection and expiry, the active AI model, the last run, and library totals.
- This is a **sample, not all-time virality**. Threads' API cannot see other users' reply-level engagement, so a wildly viral *comment on someone else's post* will not appear. Every research run labels these limits.
- The sampled material is sent to the AI provider (OpenRouter) **only after you tick the consent box** on the run form. The Threads collection/analyze run requires the server-side `OPENROUTER_API_KEY` to be configured; generating a content set requires its own separate consent.

## One-time setup (Jack only)

1. **Meta app** — <https://developers.facebook.com/apps> → Create app → *Threads* use case. Note the **Threads App ID** (= client id) and **App secret**. Request `threads_basic`, `threads_read_replies`, `threads_manage_insights`. Add Rahimam as an app tester and accept the invitation while the app is in development mode. The server defaults to `http://127.0.0.1:8787/auth/callback`; the URI registered with Meta must match `THREADS_REDIRECT_URI` exactly. **Meta may require an HTTPS redirect**: if HTTP loopback is rejected, set up a loopback-only HTTPS reverse proxy and set `THREADS_REDIRECT_URI` to that local HTTPS callback. This live OAuth setup has not yet been verified; do not expose the admin publicly or weaken TLS checks.
2. **OpenRouter key** — <https://openrouter.ai/keys> → create key. The default model is `openai/gpt-6-luna`, a cheap paid model that answers JSON directly: thinking models used to spend the whole token budget on reasoning and return no JSON. Reasoning is switched off in the request, OpenAI-prefixed models send `max_completion_tokens` instead of `max_tokens`, every OpenRouter call carries `HTTP-Referer`/`X-Title` attribution headers, and free models (`openrouter/free` or any `...:free`) still get `provider.max_price` 0 enforced. Any other paid model is rejected before a network call unless you add it to `PAID_MODELS` in `research_admin/research.py`.
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

Open <http://127.0.0.1:8787/login>, sign in with the admin password, click **connect Threads**, authorise in the same browser tab, then open **Research** and use **Run consented research**. The admin is an evidence-to-content workspace:

1. **Overview** — recent research, source-linked evidence, current sample’s own-post performance, audience signals, drafts needing review, and a four-step workflow.
2. **Research** — status board (connection and expiry, active AI model, last run, library totals), per-run sample-limit controls, an optional **Research focus** field (up to 500 characters; it steers only the next run, is appended to the analysis prompt, is stored on the run, and is never published), run history (which shows the focus used), searchable saved insights, original Threads source links, and checkboxes to select evidence for content generation. Running research and generating content have separate explicit AI-consent checkboxes.
3. **Followers** — automatic live follower telemetry (`followers_count`, growth delta, `follower_demographics` by country, city, age, and gender for profiles with ≥100 followers) and an automatic **Active Community Roster** (repliers and insight contributors discovered from your Threads replies via the Graph API, with no manual JSON download required), plus optional follow-back diffing from Rahimam's Threads data export (`followers.json` + `following.json`).
4. **Audiences** — qualitative working segments inferred only from evidence themes/quotes (trust & boundaries, healing after a breakup, self-worth, communication, unhealthy patterns, or “needs further research”), synchronized with the Draft Library (showing draft counts and an `Underserved · 0 drafts` badge when a segment has no drafts yet) and active community voices (`@username` links). **Export evidence CSV** at `/audiences/export.csv` for offline planning.
5. **Content studio** — select up to 20 evidence items (or click a 1-click Audience Segment shortcut pill), choose which **draft kinds** to generate (Threads post, ebook chapter outline, design brief — any subset), a **tone** (empathetic, direct, reflective, practical) and a **language** (match the evidence, Bahasa Melayu, English). Every draft must cite supplied saved insight IDs. The outline and design brief also carry a **Reference posts** line with the original Threads permalink(s), added from the saved evidence rather than from model output, so a copied draft still points back to its source. The Threads post draft omits it by design.
6. **Draft library** — edit drafts inline (`POST /content/drafts/{id}/edit`), inspect the 500-character counter on Threads post drafts, copy to clipboard, mark ready for use (`approved`), archive, or publish approved Threads post drafts directly via the Threads Graph API (`POST /content/drafts/{id}/publish`).
7. **Connections & settings** — Threads token status/expiry, 1-click 60-day token renewal (`POST /auth/refresh`), opt-in `threads_content_publish` OAuth connection (`/auth/start?scope=publish`), what the API sample covers, OpenRouter configuration and privacy boundaries.

### Followers, Active Community & Follow-back

The Followers page now operates in two complementary modes:

1. **Automatic Threads Graph API Sync (no manual file download needed):**
   - Clicking **Sync from Threads Graph ↻** (`POST /followers/sync`) or running a Research job (with **Also sync live follower count & demographics from Threads Graph** ticked) pulls:
     - Profile metadata (`/v1.0/me`: `id`, `username`, `name`, `threads_profile_picture_url`, `threads_biography`).
     - Account-level insights (`/v1.0/me/threads_insights`: `followers_count` with growth delta vs. the previous sync, plus `views`, `likes`, `replies`, `reposts`, `quotes`).
     - Follower demographics (`/v1.0/me/threads_insights?metric=follower_demographics&breakdown=country|city|age|gender`, automatically skipped when a profile has `<100` followers).
     - **Active Community Roster**: every non-owner account that replies to your sampled Threads posts or is cited in your saved research insights is indexed automatically with their reply count, cited insight IDs, themes, latest quote, and direct shortcuts to filter their evidence in Research or draft from their insights in Studio.
   - Three filterable community views (**All active community**, **Insight contributors**, **Frequent repliers (2+)**) and a formula-safe CSV export at `GET /followers/graph.csv`.
   - Every insight card across Overview, Research, and Studio automatically displays community engagement badges (`N replies` or `Active replier`) alongside any follow-back badge.
2. **Optional Follow-back Diff & Unfollow Planner (`followers.json` + `following.json` export):**
   - Because Meta's Graph API does not expose passive follower usernames who have never replied, you can still optionally upload `followers.json` and `following.json` from **Accounts Center → Your information and permissions → Download your information → Threads (JSON)** (comparison approach credited to [Threads-Follower](https://github.com/Xiang511/Threads-Follower)).
   - **Follow-Back & Unfollow Insights Board**: computes reciprocity rate (`mutuals / following`), follower-to-following ratio, one-way fan share, **Ghost non-followers** (`0` Graph replies + doesn't follow back) vs. **Engaged non-followers** (replied to your posts despite not following back), follow tenure buckets (`≥90d`, `≥30d`, `<30d`, median wait days, oldest non-follower), and top non-reciprocated follow cohorts (`YYYY-MM`).
   - **Filter `Following` to Unfollow Later**: five list tabs (**Not following back**, **Following**, **Unfollow later**, **Fans**, **Mutuals**), 8 unfollow sub-filters (`?uf=all|not_following_back|ghosts|older_90d|older_30d|recent_30d|engaged|unfollow_later`), and 3 sort orders (`?sort=newest|oldest|az`).
   - **Unfollow Queue (`POST /followers/unfollow`)**: select accounts in **Following** or **Not following back** to **Save to Unfollow Later** (`action=later`), copy `@usernames`, export a filtered CSV at `GET /followers/export.csv`, open their Threads profile (`Open to unfollow ↗`), and click **Mark selected as Unfollowed ✓** (`action=unfollowed`) to remove them from your active `following` list without re-downloading `following.json`.

### Background job queue

Browser form submissions (**Run consented research**, **Create grounded drafts**, **Generate selected drafts**) enqueue a job instead of blocking the page; a worker thread inside the app runs jobs one at a time. The **Job queue** panel lists recent jobs with their status and a one-line summary, refreshes itself while anything is queued or running, and offers:

- **Cancel** — a queued job stops immediately; a running job is asked to stop and exits between collection, analysis, and save stages, so no partial insights are stored.
- **Retry** — re-queues a failed or cancelled job with the same parameters.
- **Clear queue** — cancels every queued job at once (running jobs are untouched).

Failed jobs keep their reason (provider errors are shown as-is; unexpected crashes are reported as "Unexpected job failure; retry, and check the service log if it repeats." so internal details never reach the page). If the service restarts while a job is running, startup marks that job failed with "Interrupted by a restart. Retry the job." — jobs are never resumed mid-run. JSON API callers are unaffected: `POST /research/run` and `POST /content/generate` with a non-HTML `Accept` header still run synchronously and return the result directly.

A successful browser form run redirects back to the workspace; API clients can continue using JSON. Run commands from the repository root. `secret-tool` and an unlocked Secret Service keyring are required before connecting Threads.

## Security model

- Binds to `127.0.0.1` only. Nothing on the LAN (house rule).
- Password login, session cookie (8 h), no external exposure.
- OAuth `state` is single-use, 10-minute, browser- and session-bound (signed cookie) — a stolen state from another browser fails.
- All `POST`s require same-origin; foreign or missing `Origin` and unexpected `Host` headers are rejected.
- Access token: OS keyring only; SQLite keeps just the expiry. Database file is `0600` in `~/.local/state/perpustakaan-hati/research.db`.
- AI answers are validated: quotes must appear verbatim in the sampled material and source URLs must be sampled permalinks, or the run fails loudly instead of storing invented evidence. Generated draft IDs must refer to selected saved evidence; unknown citations are discarded and drafts without citations are rejected.
- Research history retains bounded own-post metrics and only top-level run summaries; audience segments are qualitative keyword groupings of saved themes/quotes, not verified demographics.
- CSV export neutralizes spreadsheet formula-leading characters. Source URLs and saved text are escaped when rendered.
- Uploaded follower exports are parsed server-side, stored in the local database only, and never forwarded to the AI provider.
- Research and content creation are separate explicit-consent actions. No scheduler or Threads publishing route is implemented; approved drafts must be copied and published manually.
- Errors returned to the browser never contain tokens or keys.

## API

| Route | What |
|---|---|
| `GET /` | Status page + insights table |
| `GET /login` / `POST /login` / `POST /logout` | Password session |
| `GET /auth/start` | Begin Threads OAuth (307); pass `?scope=publish` to include `threads_content_publish` |
| `GET /auth/callback` | Finish OAuth, store token |
| `POST /auth/refresh` | Refresh the stored 60-day Threads access token via `/refresh_access_token` |
| `GET /auth/status` | `{"connected", "expires_at"}` |
| `POST /research/run` | Consent-protected research run; accepts optional `focus` (≤500 chars) and `sync_graph=on` to refresh Graph follower telemetry. Automatically synchronizes active community repliers into the Followers view |
| `GET /research/insights` | Stored insights JSON |
| `GET /research/runs` | Saved sample history: limits used, themes, focus used, and the prioritized owned-post metrics |
| `GET /audiences` | Evidence-backed qualitative segments synchronized with draft coverage (`draft_count`, `needs_drafts`) and community `voices` |
| `GET /audiences/export.csv` | Source-linked audience evidence CSV (spreadsheet formula-safe) |
| `POST /followers/sync` | Pull live `followers_count`, `follower_demographics`, profile metadata, and active community repliers directly from the Threads Graph API (pass `queue=on` to run in background queue) |
| `GET /followers/graph.csv` | Formula-safe CSV export of the Graph active community (`?glist=all_engagers\|insight_contributors\|frequent_engagers&q=`) |
| `POST /followers/import` | Multipart upload of `followers.json` + `following.json` from the Threads data export; rejects identical files, bad JSON, >20 MB combined, and >50,000 accounts per file. HTML submissions redirect back with a notice, JSON returns counts |
| `GET /followers` | Returns `{"audience": ..., "graph": ...}` combining imported follow-back lists, unfollow insights, and live Graph follower/community data (`?uf=&sort=&q=`) |
| `POST /followers/unfollow` | Queue accounts in **Unfollow Later** (`action=later`), mark them **Unfollowed** (`action=unfollowed`), or restore (`action=keep`) |
| `GET /followers/export.csv` | Follow-back CSV, formula-safe; optional `?list=not_following_back\|following\|unfollow_later\|fans\|mutuals`, `?uf=`, `?sort=`, and `?q=` filters |
| `POST /followers/clear` | Remove the stored follower import and Graph audience snapshot |
| `POST /content/generate` | Consent-protected drafts from 1–20 selected insight IDs, optional `kinds` (subset), `tone`, `language`; non-post drafts include `content.references` with the source permalink. HTML submissions are queued, JSON stays synchronous |
| `GET /content/drafts` | Saved draft library (`?status=draft|approved|archived`), including `content.references` on non-post drafts |
| `POST /content/drafts/{id}/status` | Mark a draft `draft`, `approved`, or `archived` |
| `POST /content/drafts/{id}/edit` | Edit a saved draft's title and content fields inline |
| `POST /content/drafts/{id}/publish` | Publish an `approved` Threads post draft directly to Threads via `/v1.0/me/threads` + `/v1.0/me/threads_publish` and record the live permalink |
| `GET /queue` | Recent background jobs: kind, status, params, result, error |
| `POST /queue/clear` | Cancel every queued job |
| `POST /queue/{id}/cancel` | Cancel a queued job, or request a running job to stop |
| `POST /queue/{id}/retry` | Re-queue a failed or cancelled job (400 otherwise) |

Token refresh: long-lived Threads tokens last ~60 days. When `/auth/status` says disconnected, click **connect Threads** again.

## Tests

```bash
uv run --project packages/research-admin pytest packages/research-admin/tests -q
```
