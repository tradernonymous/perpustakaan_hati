"""Password-protected local admin app for Threads research."""

import hashlib
import hmac
import html as html_module
import json
import secrets
import time
from urllib.parse import quote, urlsplit

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from .config import Settings
from .research import ResearchError, mine_pain_points
from .store import Store, StoreError, build_vault
from .threads_client import ThreadsClient, ThreadsError

SESSION_COOKIE = "research_session"
STATE_TTL = 600
SESSION_TTL = 8 * 3600
LOGIN_MAX_FAILURES = 5
LOGIN_WINDOW = 300
SAFE_RESPONSE_HEADERS = {"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer", "X-Frame-Options": "deny"}


def parse_form(data: dict) -> dict:
    return {k: v for k, v in data.items() if isinstance(v, str)}


def _hostname(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("["):
        return value[1:].split("]", 1)[0]
    return value.rsplit(":", 1)[0] if value.count(":") == 1 else value


def _signed(value: str, key: bytes) -> str:
    return hmac.new(key, value.encode(), "sha256").hexdigest()


def _session_key(settings: Settings) -> bytes:
    """Stable signing key: a signed-in browser survives a redeploy or restart.

    The previous implementation kept sessions in a process dict, so every
    Railway deploy signed the admin out; the cookie was also unverifiable
    after a restart. Deriving the key from the admin password keeps the
    session stateless and rotates it whenever the password changes.
    """
    return hashlib.sha256(b"research-admin-session|" + settings.admin_password.encode()).digest()


def _issue_session(settings: Settings) -> str:
    expiry = int(time.time()) + SESSION_TTL
    nonce = secrets.token_urlsafe(16)
    payload = f"{expiry}.{nonce}"
    return f"{payload}.{_signed(payload, _session_key(settings))}"


def _valid_session(cookie: str, settings: Settings) -> bool:
    if not settings.admin_password or not cookie:
        return False
    parts = cookie.split(".")
    if len(parts) != 3:
        return False
    expiry, nonce, signature = parts
    if not expiry.isdigit() or int(expiry) < time.time():
        return False
    return hmac.compare_digest(signature, _signed(f"{expiry}.{nonce}", _session_key(settings)))


def _wants_html(request: Request) -> bool:
    return "text/html" in request.headers.get("accept", "").lower()


def _safe_next(value: str) -> str:
    """Only same-site absolute paths, so ?next= cannot become an open redirect."""
    value = (value or "").strip()
    if not value.startswith("/") or value.startswith("//") or "\\" in value:
        return "/"
    return value

def create_app(settings: Settings, *, vault_factory=None) -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.state.settings = settings
    app.state.http = httpx.Client(timeout=60)
    app.state.session_key = secrets.token_bytes(32)
    pending_states: dict[str, float] = {}
    login_failures: dict[str, list[float]] = {}
    store = Store(settings.db_path, vault=vault_factory() if vault_factory else build_vault(settings))
    store.init_schema()
    app.state.store = store

    def error(status: int, message: str, **extra) -> JSONResponse:
        response = JSONResponse({"error": message, **extra}, status_code=status)
        for key, value in SAFE_RESPONSE_HEADERS.items():
            response.headers[key] = value
        return response

    def safe_origin(request: Request, *, mutation: bool = True) -> bool:
        host = _hostname(request.headers.get("host", ""))
        if host not in settings.allowed_hosts:
            return False
        if not mutation:
            return True
        origin = request.headers.get("origin")
        if not origin:
            return False
        try:
            parsed = urlsplit(origin)
        except ValueError:
            return False
        return parsed.scheme in ("http", "https") and _hostname(parsed.netloc) == host

    def signed_in(request: Request) -> bool:
        return _valid_session(request.cookies.get(SESSION_COOKIE, ""), settings)

    @app.middleware("http")
    async def security(request: Request, call_next):
        if request.url.path == "/healthz":
            return await call_next(request)
        if _hostname(request.headers.get("host", "")) not in settings.allowed_hosts:
            return error(400, "Unexpected host header.")
        # /login validates its own CSRF (double-submit cookie or same-origin
        # Origin), so browsers and webviews that omit both headers can still
        # sign in. Every other mutation keeps the strict origin check.
        if request.method == "POST" and request.url.path != "/login" and not safe_origin(request):
            return error(403, "Cross-origin or missing-origin requests are blocked.")
        if request.url.path not in ("/login", "/auth/callback"):
            if not settings.admin_password:
                return error(503, "RESEARCH_ADMIN_PASSWORD is not set. Set it and restart the server.")
            if not signed_in(request):
                # A browser that opens the service root should land on the sign-in
                # form, not on a raw JSON 401 (the issue reported on Railway).
                if request.method == "GET" and _wants_html(request):
                    denied = RedirectResponse(f"/login?next={quote(request.url.path, safe='')}", status_code=303)
                    for key, value in SAFE_RESPONSE_HEADERS.items():
                        denied.headers[key] = value
                else:
                    denied = error(401, "Sign in first.")
                return denied
        response = await call_next(request)
        for key, value in SAFE_RESPONSE_HEADERS.items():
            response.headers[key] = value
        return response

    @app.exception_handler(httpx.HTTPError)
    async def unreachable(request, exc):
        return error(502, "Threads or OpenRouter unreachable; check your connection and retry.")

    def login_html(next_path: str, csrf: str, message: str = "") -> str:
        note = f"<p class=err role=alert>{html_module.escape(message)}</p>" if message else ""
        return f"""<!doctype html><html lang=ms><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Masuk — Threads research admin</title>
<style>
:root{{--ink:#12251b;--muted:#4f5f53;--line:#d2c4a8;--gold:#7a5a22;--green:#2d7954;--bg:#f7f4ea;--card:#fffdf6}}
*{{box-sizing:border-box}}body{{margin:0;min-height:100vh;display:grid;place-items:center;background:var(--bg);color:var(--ink);font:16px/1.5 Inter,system-ui,sans-serif;padding:24px}}
main{{width:100%;max-width:380px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:28px;box-shadow:0 18px 40px -24px rgb(60 45 20/.35)}}
.kicker{{display:flex;align-items:center;gap:.7em;margin:0 0 6px;font-size:12px;letter-spacing:.28em;text-transform:uppercase;color:var(--gold)}}
.kicker::before,.kicker::after{{content:'';flex:1 1 2em;height:1px;background:var(--line)}}
h1{{font-family:Georgia,serif;font-weight:600;font-size:24px;margin:6px 0 4px}}p.sub{{margin:0 0 18px;color:var(--muted);font-size:14px}}
label{{display:block;font-size:13px;font-weight:600;margin:0 0 6px}}input{{width:100%;min-height:44px;border:1px solid var(--line);border-radius:8px;background:#eef2e8;color:var(--ink);padding:0 12px;font-size:16px}}
input:focus-visible{{outline:2px solid var(--green);outline-offset:2px}}button{{width:100%;min-height:48px;margin-top:14px;border:0;border-radius:999px;background:linear-gradient(180deg,#7db895,#5b9b7d 50%,#3f9167);color:#07140d;font:600 16px/1 Inter,system-ui,sans-serif;cursor:pointer;box-shadow:0 3px 0 #1d5a3d}}
.err{{margin:12px 0 0;color:#8a2f2f;font-size:14px}}footer{{margin-top:16px;font-size:12px;color:var(--muted)}}
</style></head><body><main>
<p class=kicker>Threads research</p>
<h1>Masuk ke admin</h1>
<p class=sub>Masukkan kata laluan admin untuk membuka research dan sambungan Threads.</p>
<form method=post action=/login>
<input type=hidden name=csrf value="{html_module.escape(csrf, quote=True)}">
<input type=hidden name=next value="{html_module.escape(next_path, quote=True)}">
<label for=pw>Kata laluan admin</label>
<input id=pw type=password name=password placeholder="Admin password" autocomplete=current-password required autofocus>
<button>Masuk</button>
{note}
</form>
<footer>Perpustakaan Hati · satu-satunya admin.</footer>
</main></body></html>"""

    @app.get("/login", response_class=HTMLResponse)
    def login_page(request: Request, next: str = "/"):
        if not settings.admin_password:
            return error(503, "RESEARCH_ADMIN_PASSWORD is not set. Set it and restart the server.")
        if signed_in(request):
            return RedirectResponse(_safe_next(next), status_code=303)
        csrf = secrets.token_urlsafe(24)
        response = HTMLResponse(login_html(_safe_next(next), csrf))
        response.set_cookie("login_csrf", csrf, httponly=True, secure=settings.secure_cookies, samesite="lax", max_age=STATE_TTL)
        return response

    @app.post("/login")
    async def login(request: Request):
        if not settings.admin_password:
            return error(503, "RESEARCH_ADMIN_PASSWORD is not set. Set it and restart the server.")
        now = time.time()
        client = request.client.host if request.client else "unknown"
        recent = [stamp for stamp in login_failures.get(client, []) if stamp > now - LOGIN_WINDOW]
        login_failures[client] = recent
        if len(recent) >= LOGIN_MAX_FAILURES:
            return error(429, "Too many failed sign-ins. Wait a few minutes and retry.")
        try:
            data = {k: v for k, v in (await request.form()).items() if isinstance(v, str)}
        except Exception:
            data = {}
        # CSRF: the double-submit token covers browsers/webviews that omit both
        # Origin and Referer on a same-site form POST; a same-origin Origin is
        # still accepted for clients that send it.
        submitted = str(data.get("csrf", ""))
        cookie_token = request.cookies.get("login_csrf", "")
        token_ok = bool(submitted and cookie_token and hmac.compare_digest(submitted, cookie_token))
        if not (token_ok or safe_origin(request)):
            return error(403, "Cross-origin or missing-origin requests are blocked.")
        next_path = _safe_next(str(data.get("next", "/")))
        if not hmac.compare_digest(str(data.get("password", "")).encode("utf-8"), settings.admin_password.encode("utf-8")):
            recent.append(now)
            response = HTMLResponse(login_html(next_path, cookie_token or secrets.token_urlsafe(24), "Kata laluan salah. Cuba lagi."), status_code=401)
            for key, value in SAFE_RESPONSE_HEADERS.items():
                response.headers[key] = value
            return response
        login_failures.pop(client, None)
        response = RedirectResponse(next_path, status_code=303)
        response.set_cookie(SESSION_COOKIE, _issue_session(settings), httponly=True, secure=settings.secure_cookies, samesite="lax", max_age=SESSION_TTL)
        response.delete_cookie("login_csrf")
        return response

    @app.post("/logout")
    def logout(request: Request):
        response = RedirectResponse("/login", status_code=303)
        response.delete_cookie(SESSION_COOKIE)
        return response

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        token = app.state.store.get_token()
        insights = app.state.store.list_insights()
        connected = token is not None and token.expires_at > time.time()
        expiry = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(token.expires_at)) if connected else ""
        connection = f"connected until {expiry}" if connected else "not connected — <a href=/auth/start>connect Threads</a>"
        def link(item):
            escaped = html_module.escape(item["source_url"], quote=True)
            if item["source_url"].startswith(("http://", "https://")):
                return f"<a href='{escaped}' rel='noreferrer' target='_blank'>source</a>"
            return f"<span title='unsafe link blocked'>{escaped}</span>"

        rows = "".join(
            f"<tr><td>{html_module.escape(i['theme'])}</td><td>{html_module.escape(i['quote'])}</td>"
            f"<td>{link(i)}</td>"
            f"<td>{html_module.escape(i['ebook_idea'])}</td></tr>"
            for i in insights)
        table = f"<table><tr><th>Theme</th><th>Quote</th><th>Source</th><th>Ebook idea</th></tr>{rows}</table>" if rows else ""
        return HTMLResponse(f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Threads research admin</title></head><body><h1>Threads research</h1>
<p>Connection: {connection}</p><p>Stored insights: {len(insights)}</p>
<form method=post action=/research/run><p><label><input type=checkbox name=consent required> I understand sampled posts and public replies are sent to the configured AI provider for analysis.</label></p><p><button>Run research</button></p></form>
<p>Sample limits: at most 50 recent owned posts (3 pages), top 5 by engagement, up to 50 visible direct replies each. This is a sample, not all-time virality.</p>
{table}
<form method=post action=/logout><button>Sign out</button></form></body></html>""")

    @app.get("/auth/start")
    def auth_start(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        missing = settings.missing_threads() + ([] if settings.openrouter_api_key else ["OPENROUTER_API_KEY"])
        if missing:
            return error(503, "not configured", missing=missing)
        state = secrets.token_urlsafe(24)
        pending_states[state] = time.time() + STATE_TTL
        response = RedirectResponse(ThreadsClient(settings, app.state.http).authorize_url(state), status_code=307)
        response.set_cookie("oauth_browser", _signed(state + request.cookies.get(SESSION_COOKIE, ""), app.state.session_key), httponly=True, secure=settings.secure_cookies, samesite="lax", max_age=STATE_TTL)
        return response

    @app.get("/auth/callback")
    def auth_callback(request: Request, code: str = "", state: str = ""):
        now = time.time()
        for key, expiry in list(pending_states.items()):
            if expiry < now:
                del pending_states[key]
        browser = request.cookies.get("oauth_browser", "")
        expected = _signed(state + request.cookies.get(SESSION_COOKIE, ""), app.state.session_key)
        if not state or pending_states.pop(state, None) is None or not browser or not hmac.compare_digest(browser, expected):
            return error(400, "Invalid or expired authorization state; reconnect.")
        if not code:
            return error(400, "Threads denied the connection; reconnect.")
        try:
            token = ThreadsClient(settings, app.state.http).exchange_code(code)
            app.state.store.save_token(token.access_token, int(now + token.expires_in))
        except (ThreadsError, StoreError):
            return error(400, "Threads connection failed; reconnect.")
        response = RedirectResponse("/", status_code=303)
        response.delete_cookie("oauth_browser")
        return response

    @app.get("/auth/status")
    def auth_status(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        token = app.state.store.get_token()
        connected = token is not None and token.expires_at > time.time()
        return {"connected": connected, "expires_at": token.expires_at if connected else None}

    @app.post("/research/run")
    async def research_run(request: Request):
        try:
            data = dict(await request.form())
        except Exception:
            try:
                body = await request.body()
                data = json.loads(body) if body else {}
            except Exception:
                data = {}
        if str(data.get("consent", "")) != "on":
            return error(400, "Tick the AI-sharing consent box before running research.")
        token = app.state.store.get_token()
        if not token or token.expires_at <= time.time():
            return error(401, "reconnect")
        try:
            research = ThreadsClient(settings, app.state.http).collect_research(token.access_token)
            insights = mine_pain_points(research["sources"], settings, app.state.http)
            app.state.store.save_insights(insights)
        except (ThreadsError, ResearchError, StoreError) as exc:
            return error(502, str(exc))
        return {"insights": insights, "limitations": research["limitations"], "posts_sampled": research["posts_sampled"]}

    @app.get("/research/insights")
    def research_insights(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        return {"insights": app.state.store.list_insights()}

    @app.get("/healthz")
    def healthz():
        return {"ok": True}

    return app
