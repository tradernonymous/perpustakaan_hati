"""Password-protected local admin app for Threads research."""

import hmac
import html as html_module
import json
import secrets
import time
from urllib.parse import urlsplit

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


def create_app(settings: Settings, *, vault_factory=None) -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.state.settings = settings
    app.state.http = httpx.Client(timeout=60)
    app.state.session_key = secrets.token_bytes(32)
    pending_states: dict[str, float] = {}
    sessions: dict[str, float] = {}
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
        expiry = sessions.get(request.cookies.get(SESSION_COOKIE, ""))
        return bool(settings.admin_password and expiry and expiry > time.time())

    @app.middleware("http")
    async def security(request: Request, call_next):
        if request.url.path == "/healthz":
            return await call_next(request)
        if _hostname(request.headers.get("host", "")) not in settings.allowed_hosts:
            return error(400, "Unexpected host header.")
        if request.method == "POST" and not safe_origin(request):
            return error(403, "Cross-origin or missing-origin requests are blocked.")
        if request.url.path not in ("/login", "/auth/callback"):
            if not settings.admin_password:
                return error(503, "RESEARCH_ADMIN_PASSWORD is not set. Set it and restart the server.")
            if not signed_in(request):
                return error(401, "Sign in first.")
        response = await call_next(request)
        for key, value in SAFE_RESPONSE_HEADERS.items():
            response.headers[key] = value
        return response

    @app.exception_handler(httpx.HTTPError)
    async def unreachable(request, exc):
        return error(502, "Threads or OpenRouter unreachable; check your connection and retry.")

    @app.get("/login", response_class=HTMLResponse)
    def login_page():
        if not settings.admin_password:
            return error(503, "RESEARCH_ADMIN_PASSWORD is not set. Set it and restart the server.")
        return HTMLResponse("<!doctype html><html lang=en><head><meta charset=utf-8><title>Threads research admin</title></head><body><form method=post action=/login><p><input type=password name=password placeholder='Admin password' autocomplete=current-password></p><p><button>Sign in</button></p></form></body></html>")

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
            data = dict(await request.form())
        except Exception:
            data = {}
        if not hmac.compare_digest(str(data.get("password", "")).encode("utf-8"), settings.admin_password.encode("utf-8")):
            recent.append(now)
            return error(401, "Wrong admin password.")
        login_failures.pop(client, None)
        for key, expiry in list(sessions.items()):
            if expiry < now:
                del sessions[key]
        token = secrets.token_urlsafe(32)
        sessions[token] = time.time() + SESSION_TTL
        response = RedirectResponse("/", status_code=303)
        response.set_cookie(SESSION_COOKIE, token, httponly=True, secure=settings.secure_cookies, samesite="lax", max_age=SESSION_TTL)
        return response

    @app.post("/logout")
    def logout(request: Request):
        sessions.pop(request.cookies.get(SESSION_COOKIE, ""), None)
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
