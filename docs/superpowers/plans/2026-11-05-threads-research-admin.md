# Threads Research Admin — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A local admin backend that connects to Threads via OAuth, pulls Rahimam's own posts and replies, and uses OpenRouter AI to mine audience pain points for the Phase 2 eBooks.

**Architecture:** One Python package `packages/research-admin` (FastAPI + SQLite). Three layers: Threads OAuth client (Meta Graph API), token/insight store (SQLite), research service (fetch posts → send to OpenRouter → store structured insights). Minimal server-rendered admin page for status + "run research". Secrets come only from environment variables; never committed.

**Tech Stack:** Python 3.12, FastAPI, httpx, pytest (with respx for HTTP mocking), uv.

**Spec:** This plan (agreed in chat 2026-11-05: "create a placeholder or an admin access that have the backend to connect threads by oauth to do proper research with ai integration, use openrouter as provider").

## Global Constraints

- Secrets (`THREADS_CLIENT_ID`, `THREADS_CLIENT_SECRET`, `OPENROUTER_API_KEY`) read from env only; no secret ever written to a repo file or log.
- All external HTTP (Meta graph, OpenRouter) must be mockable in tests — no live network in test suite.
- Package must run with `uv run --project packages/research-admin python -m research_admin` on Python 3.12.
- Follow repo commit style: `feat(research): ...` / `test(research): ...`, never commit stray dotfiles.
- UI copy and code comments in English; insight output schema field names in English.

## Review Focus

- Expired/short-lived Threads access token (long-lived tokens still expire ~60 days): `/auth/status` must show expiry, `/research/run` must fail with a clear "reconnect" message, not a raw 4xx dump.
- OpenRouter returns non-200 or malformed JSON: research run must surface the provider error message, not crash.
- Posts fetch paginated beyond one page (`next` cursor present): the client must follow cursors up to a hard cap.
- Missing env secrets: server must start and `/auth/start` must return a clear "not configured" error instead of redirecting to a broken URL.
- Empty research result (profile has no posts yet): `/research/run` must succeed with zero insights, not error.

---

### Task 1: Package scaffold + config

**Files:**
- Create: `packages/research-admin/pyproject.toml`
- Create: `packages/research-admin/research_admin/__init__.py`
- Create: `packages/research-admin/research_admin/config.py`
- Test: `packages/research-admin/tests/test_config.py`

**Interfaces:**
- Produces: `Settings` dataclass in `config.py` with fields `threads_client_id: str`, `threads_client_secret: str`, `openrouter_api_key: str`, `redirect_uri: str`, `db_path: str` (default `~/.local/state/perpustakaan-hati/research.db`), `database_url: str | None`; classmethod `Settings.from_env(environ: dict) -> Settings` that raises `MissingSecretError` naming the missing keys.

- [ ] **Step 1: Write failing test**

```python
from research_admin.config import Settings, MissingSecretError

def test_from_env_reads_all_secrets():
    s = Settings.from_env({"THREADS_CLIENT_ID": "id", "THREADS_CLIENT_SECRET": "sec",
                           "OPENROUTER_API_KEY": "key"})
    assert s.threads_client_id == "id"
    assert s.openrouter_api_key == "key"

def test_from_env_missing_secret_raises_with_key_names():
    try:
        Settings.from_env({})
        assert False, "should raise"
    except MissingSecretError as e:
        assert "THREADS_CLIENT_ID" in str(e)
```

- [ ] **Step 2: Run test, verify FAIL** — `uv run --project packages/research-admin pytest tests/test_config.py -v` (module not found)
- [ ] **Step 3: Implement `config.py`** (dataclass + `from_env`; missing keys collected and raised together). `pyproject.toml`: project `research-admin`, deps `fastapi`, `uvicorn`, `httpx`; dev deps `pytest`, `respx`.
- [ ] **Step 4: Run test, verify PASS**
- [ ] **Step 5: Commit** `feat(research): scaffold research-admin package with env settings`

### Task 2: SQLite token + insight store

**Files:**
- Create: `packages/research-admin/research_admin/store.py`
- Test: `packages/research-admin/tests/test_store.py`

**Interfaces:**
- Consumes: `Settings.db_path`
- Produces: `Store(db_path: str)` with `init_schema()`, `save_token(access_token: str, expires_at: int) -> None`, `get_token() -> StoredToken | None` (dataclass `access_token: str, expires_at: int`), `save_insights(items: list[dict]) -> None`, `list_insights() -> list[dict]`. Uses stdlib `sqlite3`, table `token` (single row) and table `insights` (id, theme, quote, source_url, created_at).

- [ ] **Step 1: Write failing tests** — save/get token roundtrip; `get_token()` returns `None` when empty; insights roundtrip preserves theme/quote/source_url; re-saving token replaces old row.
- [ ] **Step 2: Run, verify FAIL**
- [ ] **Step 3: Implement `store.py`** (sqlite3 with `check_same_thread=False` and a `threading.Lock`; parameterised SQL only)
- [ ] **Step 4: Run, verify PASS**
- [ ] **Step 5: Commit** `feat(research): add SQLite token and insight store`

### Task 3: Threads OAuth client (Meta Graph API)

**Files:**
- Create: `packages/research-admin/research_admin/threads_client.py`
- Test: `packages/research-admin/tests/test_threads_client.py`

**Interfaces:**
- Consumes: `Settings`
- Produces: `ThreadsClient(settings: Settings, http: httpx.Client)`, methods:
  - `authorize_url(state: str) -> str` (Threads OAuth dialog URL, scopes `threads_basic,threads_content_read`)
  - `exchange_code(code: str) -> TokenResponse` (dataclass `access_token: str, expires_in: int`)
  - `fetch_my_posts(limit: int = 50) -> list[dict]` (follows `paging.next` cursors up to 3 pages; each item `{"id": str, "text": str, "permalink": str, "timestamp": str}`; media fields `id,text,permalink,timestamp`)

- [ ] **Step 1: Write failing tests with respx** — `authorize_url` contains client id, redirect uri, state, both scopes; `exchange_code` posts to token endpoint and parses token; `fetch_my_posts` returns items and follows one `paging.next` cursor; second page also fetched; hard cap: 4 pages of cursors still stops after 3 requests.
- [ ] **Step 2: Run, verify FAIL**
- [ ] **Step 3: Implement `threads_client.py`** (base `https://graph.threads.net/v1.0`; token exchange at `/oauth/access_token`)
- [ ] **Step 4: Run, verify PASS**
- [ ] **Step 5: Commit** `feat(research): add Threads OAuth client with pagination`

### Task 4: OpenRouter research service

**Files:**
- Create: `packages/research-admin/research_admin/research.py`
- Test: `packages/research-admin/tests/test_research.py`

**Interfaces:**
- Consumes: `ThreadsClient.fetch_my_posts`, `Settings.openrouter_api_key`
- Produces: `mine_pain_points(posts: list[dict], settings: Settings, http: httpx.Client) -> list[dict]` — POSTs to `https://openrouter.ai/api/v1/chat/completions`, model `anthropic/claude-sonnet-4.5` (configurable via env `OPENROUTER_MODEL`), prompt asks for JSON array of `{"theme", "quote", "source_url"}`; parses and returns the list. Raises `ResearchError` with the provider message on non-200 or unparsable body. Empty `posts` returns `[]` without calling OpenRouter.

- [ ] **Step 1: Write failing tests with respx** — happy path returns parsed insights; non-200 raises `ResearchError` containing provider message; malformed JSON raises `ResearchError`; empty posts returns `[]` with zero HTTP calls (assert via respx call count).
- [ ] **Step 2: Run, verify FAIL**
- [ ] **Step 3: Implement `research.py`** (system prompt fixed in module as `PAIN_POINT_PROMPT`; request `response_format={"type": "json_object"}`, tolerate JSON fenced in markdown)
- [ ] **Step 4: Run, verify PASS**
- [ ] **Step 5: Commit** `feat(research): add OpenRouter pain-point mining service`

### Task 5: FastAPI admin app + status/run/research routes

**Files:**
- Create: `packages/research-admin/research_admin/app.py`
- Create: `packages/research-admin/research_admin/__main__.py`
- Test: `packages/research-admin/tests/test_app.py`

**Interfaces:**
- Consumes: all earlier tasks.
- Produces: `create_app(settings: Settings) -> FastAPI` with routes:
  - `GET /` — HTML status page: connection state, token expiry, insight count, "Run research" form
  - `GET /auth/start` — 302 to Threads authorize URL (or 503 JSON `{"error": "not configured", "missing": [...]}` when secrets absent)
  - `GET /auth/callback?code&state` — exchanges code, saves token, redirects to `/`
  - `GET /auth/status` — JSON `{"connected": bool, "expires_at": int | null}`
  - `POST /research/run` — 401 JSON `{"error": "reconnect"}` when no token or token expired; otherwise fetches posts, mines insights, saves them, returns `{"insights": [...]}`
  - `GET /research/insights` — JSON list
- `__main__.py`: `uvicorn.run(create_app(Settings.from_env(dict(os.environ))))` on `127.0.0.1:8787`.

- [ ] **Step 1: Write failing tests with FastAPI TestClient + respx** — `/auth/status` unconnected; `/auth/start` not-configured 503 with missing keys listed; `/auth/callback` stores token (mock exchange); `/research/run` without token gives 401 reconnect; with valid token and mocked Threads+OpenRouter saves and returns insights; expired token gives 401; empty posts gives `{"insights": []}` 200.
- [ ] **Step 2: Run, verify FAIL**
- [ ] **Step 3: Implement `app.py`** (app factory builds `Store`, `ThreadsClient` per request with `httpx.Client` dependency; HTML page is a single f-string template, no template engine)
- [ ] **Step 4: Run, verify PASS; then full suite** `uv run --project packages/research-admin pytest -v` all green
- [ ] **Step 5: Commit** `feat(research): add FastAPI admin app with OAuth and research routes`

### Task 6: Docs + README wiring

**Files:**
- Modify: `README.md` (Phase 2 section: mark "Audience Pain-Point Mining" tooling as started, link new doc)
- Create: `docs/research-admin.md`

**Interfaces:** none.

- [ ] **Step 1: Write `docs/research-admin.md`** — how to create the Meta Threads app (Jack-only steps), which env vars to set (`secret-tool` storage + export), how to run (`uv run --project packages/research-admin python -m research_admin`), OAuth flow walkthrough, where insights land.
- [ ] **Step 2: README Phase 2 bullet update** — add pointer line to `docs/research-admin.md`.
- [ ] **Step 3: Run full test suite once more; commit** `docs(research): document research admin setup and wiring`
