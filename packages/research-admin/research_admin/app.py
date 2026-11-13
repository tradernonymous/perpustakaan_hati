"""Password-protected local admin app for Threads research."""

import csv
import hashlib
import hmac
import html as html_module
import io
import json
import secrets
import time
from urllib.parse import parse_qs, quote, urlsplit

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from .audiences import build_audiences
from .config import Settings
from .content import DRAFT_KINDS, DRAFT_LANGUAGES, DRAFT_TONES, generate_drafts
from .dashboard import DashboardData, render_dashboard
from .jobs import JobCancelled
from .research import ResearchError, mine_pain_points
from .store import Store, StoreError, build_vault
from .threads_client import SampleLimits, ThreadsClient, ThreadsError

SESSION_COOKIE = "research_session"
CSRF_COOKIE = "research_csrf"
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
    store.recover_interrupted_jobs()
    app.state.store = store

    def sealed(response: Response) -> Response:
        for key, value in SAFE_RESPONSE_HEADERS.items():
            response.headers[key] = value
        return response

    def error(status: int, message: str, **extra) -> Response:
        return sealed(JSONResponse({"error": message, **extra}, status_code=status))

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

    async def csrf_token_ok(request: Request) -> bool:
        """Double-submit token for browsers/webviews that omit Origin on a same-site form POST.

        Reads the body (not the form) so the downstream handler still gets it.
        """
        content_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/x-www-form-urlencoded":
            return False
        cookie_token = request.cookies.get(CSRF_COOKIE, "")
        if not cookie_token:
            return False
        body = (await request.body()).decode("utf-8", "replace")
        submitted = (parse_qs(body).get("csrf") or [""])[0]
        return bool(submitted) and hmac.compare_digest(submitted, cookie_token)

    @app.middleware("http")
    async def security(request: Request, call_next):
        if request.url.path == "/healthz":
            return await call_next(request)
        if _hostname(request.headers.get("host", "")) not in settings.allowed_hosts:
            return error(400, "Unexpected host header.")
        # /login validates its own CSRF (double-submit cookie or same-origin
        # Origin), so browsers and webviews that omit both headers can still
        # sign in. Every other mutation keeps the strict origin check.
        if request.method == "POST" and request.url.path != "/login" and not (safe_origin(request) or await csrf_token_ok(request)):
            return error(403, "Cross-origin or missing-origin requests are blocked.")
        if request.url.path not in ("/login", "/auth/callback"):
            if not settings.admin_password:
                return error(503, "RESEARCH_ADMIN_PASSWORD is not set. Set it and restart the server.")
            if not signed_in(request):
                # A browser that opens the service root should land on the sign-in
                # form, not on a raw JSON 401 (the issue reported on Railway).
                denied: Response = error(401, "Sign in first.")
                if request.method == "GET" and _wants_html(request):
                    denied = sealed(RedirectResponse(f"/login?next={quote(request.url.path, safe='')}", status_code=303))
                return denied
        return sealed(await call_next(request))

    @app.exception_handler(httpx.HTTPError)
    async def unreachable(request, exc):
        return error(502, "Threads or OpenRouter unreachable; check your connection and retry.")

    def _clean_focus(value) -> str:
        return " ".join(str(value or "").split())[:500]

    def _cancel_check(job_id: int | None) -> None:
        if job_id is not None and store.job_cancel_requested(job_id):
            raise JobCancelled("Job cancelled.")

    def _perform_research(params: dict, job_id: int | None = None) -> dict:
        limits = SampleLimits(
            params.get("post_limit", 50), params.get("top_posts", 5), params.get("replies_per_post", 50)
        ).normalized()
        token = store.get_token()
        if not token or token.expires_at <= time.time():
            raise ThreadsError("Threads token expired or revoked; reconnect your account.")
        if not settings.openrouter_api_key:
            raise ResearchError("OPENROUTER_API_KEY is not set. Add it to the server secret store to analyze collected Threads text.")
        _cancel_check(job_id)
        research = ThreadsClient(settings, app.state.http).collect_research(
            token.access_token, post_limit=limits.post_limit, top_posts=limits.top_posts, replies_per_post=limits.replies_per_post)
        _cancel_check(job_id)
        insights = mine_pain_points(research["sources"], settings, app.state.http, focus=params.get("focus", ""))
        _cancel_check(job_id)
        store.save_insights(insights)
        run_id = store.save_research_run(
            posts_sampled=research["posts_sampled"], selected_posts=research.get("selected_posts", 0),
            insights=insights, limitations=research["limitations"], posts=research.get("selected_posts_data", []),
            post_limit=limits.post_limit, top_posts=limits.top_posts, replies_per_post=limits.replies_per_post,
            focus=params.get("focus", ""),
        )
        return {"run_id": run_id, "insights": insights, "limitations": research["limitations"], "posts_sampled": research["posts_sampled"], "limits": limits.as_dict(), "focus": params.get("focus", "")}

    def _perform_drafts(params: dict, job_id: int | None = None) -> dict:
        ids = list(dict.fromkeys(int(value) for value in params.get("insight_ids", [])))[:20]
        if not ids:
            raise ResearchError("Select between 1 and 20 valid saved insights.")
        selected = store.get_insights_by_ids(ids)
        if len(selected) != len(ids):
            raise ResearchError("One or more selected insights are no longer available.")
        _cancel_check(job_id)
        saved = store.save_drafts(
            generate_drafts(
                selected, settings, app.state.http,
                kinds=params.get("kinds"), tone=params.get("tone", "empathetic"), language=params.get("language", "match evidence"),
            ),
            ids,
        )
        return {"drafts": saved}

    def run_job(job: dict) -> bool:
        job_id = int(job["id"])
        try:
            if job["kind"] == "research":
                result = _perform_research(job["params"], job_id)
            elif job["kind"] == "drafts":
                result = _perform_drafts(job["params"], job_id)
            else:
                raise StoreError("Unknown job kind.")
        except JobCancelled:
            store.mark_job_cancelled(job_id)
            return False
        except (ThreadsError, ResearchError, StoreError) as exc:
            store.fail_job(job_id, str(exc))
            return False
        except Exception:  # noqa: BLE001 - a crash must surface as a failed job, not kill the worker
            store.fail_job(job_id, "Unexpected job failure; retry, and check the service log if it repeats.")
            return False
        store.finish_job(job_id, result)
        return True

    def process_next_job() -> bool:
        job = store.claim_job()
        if not job:
            return False
        run_job(job)
        return True

    app.state.process_next_job = process_next_job

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
            data = parse_form(dict(await request.form()))
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
            return sealed(HTMLResponse(login_html(next_path, cookie_token or secrets.token_urlsafe(24), "Kata laluan salah. Cuba lagi."), status_code=401))
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
        view = request.query_params.get("view", "overview")
        search = request.query_params.get("q", "") if view == "research" else ""
        selection = request.query_params.get("select", "") if view in ("research", "studio") else ""
        status = request.query_params.get("status", "") if view == "library" else ""
        token = app.state.store.get_token()
        connected = token is not None and token.expires_at > time.time()
        expiry = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(token.expires_at)) if connected else ""
        connection = f"Connected · expires {expiry}" if connected else "Not connected"
        insights = app.state.store.list_insights(query=search)
        audiences = build_audiences(app.state.store.list_insights())
        runs = app.state.store.list_research_runs()
        drafts = app.state.store.list_drafts(status=status)
        csrf = request.cookies.get(CSRF_COOKIE) or secrets.token_urlsafe(24)
        limits = SampleLimits.from_row(runs[0] if runs else None)
        focus = runs[0].get("focus", "") if runs else ""
        page = render_dashboard(DashboardData(
            view=view, connection=connection, expiry=expiry, insights=insights, runs=runs,
            audiences=audiences, drafts=drafts, query=search,
            selection=selection, status_filter=status, csrf=csrf, limits=limits,
            jobs=store.list_jobs(),
            focus=focus,
            model=settings.openrouter_model,
            error=request.query_params.get("notice", ""), configured=bool(settings.openrouter_api_key), threads_configured=not settings.missing_threads(),
        ), logout_action=f'<form method=post action=/logout><input type=hidden name=csrf value="{html_module.escape(csrf, quote=True)}"><button class=signout>Sign out</button></form>')
        response = HTMLResponse(page)
        if not request.cookies.get(CSRF_COOKIE):
            response.set_cookie(CSRF_COOKIE, csrf, httponly=True, secure=settings.secure_cookies, samesite="lax", max_age=SESSION_TTL)
        return response

    @app.get("/auth/start")
    def auth_start(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        missing = settings.missing_threads()
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
        if not settings.openrouter_api_key:
            return error(503, "OPENROUTER_API_KEY is not set. Add it to the server secret store to analyze collected Threads text.")
        limits = SampleLimits.from_form(data)
        params = {**limits.as_dict(), "focus": _clean_focus(data.get("focus"))}
        if "text/html" in request.headers.get("accept", ""):
            job = app.state.store.create_job("research", params)
            return RedirectResponse(f"/?view=research&notice=Research+queued+(job+%23{job['id']})", status_code=303)
        try:
            result = _perform_research(params)
        except (ThreadsError, ResearchError, StoreError) as exc:
            return error(502, str(exc))
        return result

    @app.get("/research/runs")
    def research_runs(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        return {"runs": app.state.store.list_research_runs()}

    @app.get("/research/insights")
    def research_insights(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        return {"insights": app.state.store.list_insights()}

    @app.get("/audiences")
    def audiences(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        return {"audiences": build_audiences(app.state.store.list_insights())}

    @app.get("/audiences/export.csv")
    def audiences_export(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(("audience_segment", "evidence_count", "themes", "quote", "source_url", "ebook_idea"))
        for audience in build_audiences(app.state.store.list_insights()):
            for item in audience["evidence"]:
                cells = [audience["name"], audience["evidence_count"], ", ".join(audience["themes"]), item["quote"], item["source_url"], item["ebook_idea"]]
                writer.writerow([("'" + str(value)) if str(value).startswith(("=", "+", "-", "@", "\t", "\r")) else value for value in cells])
        return Response(output.getvalue(), media_type="text/csv; charset=utf-8", headers={"Content-Disposition": "attachment; filename=threads-audience-evidence.csv"})

    @app.post("/content/generate")
    async def content_generate(request: Request):
        is_html = "text/html" in request.headers.get("accept", "")
        try:
            form = await request.form()
            raw_ids = form.getlist("insight_ids")
            consent = form.get("consent", "")
            kinds_raw = form.getlist("kinds")
            tone = form.get("tone", "empathetic")
            language = form.get("language", "match evidence")
        except Exception:
            try:
                body = await request.json()
            except Exception:
                body = {}
            raw_ids = body.get("insight_ids", []) if isinstance(body, dict) else []
            consent = body.get("consent", "") if isinstance(body, dict) else ""
            kinds_raw = body.get("kinds", []) if isinstance(body, dict) else []
            tone = body.get("tone", "empathetic") if isinstance(body, dict) else "empathetic"
            language = body.get("language", "match evidence") if isinstance(body, dict) else "match evidence"
        if str(consent) != "on":
            return error(400, "Tick the content-generation consent box before continuing.")
        if not isinstance(raw_ids, (list, tuple)):
            raw_ids = [raw_ids]
        if not isinstance(kinds_raw, (list, tuple)):
            kinds_raw = [kinds_raw]
        try:
            ids = list(dict.fromkeys(int(value) for value in raw_ids))
        except (TypeError, ValueError):
            ids = []
        if not ids or len(ids) > 20:
            return error(400, "Select between 1 and 20 valid saved insights.")
        selected = app.state.store.get_insights_by_ids(ids)
        if len(selected) != len(ids):
            return error(400, "One or more selected insights are no longer available.")
        params = {
            "insight_ids": ids,
            "kinds": [kind for kind in DRAFT_KINDS if kind in kinds_raw] or list(DRAFT_KINDS),
            "tone": tone if tone in DRAFT_TONES else DRAFT_TONES[0],
            "language": language if language in DRAFT_LANGUAGES else DRAFT_LANGUAGES[0],
        }
        if is_html:
            job = app.state.store.create_job("drafts", params)
            return RedirectResponse(f"/?view=studio&notice=Drafts+queued+(job+%23{job['id']})", status_code=303)
        try:
            result = _perform_drafts(params)
        except (ResearchError, StoreError) as exc:
            return error(502, str(exc))
        return result

    @app.post("/content/drafts/{draft_id}/status")
    async def content_draft_status(request: Request, draft_id: int):
        try:
            form = await request.form()
            status = str(form.get("status", ""))
        except Exception:
            try:
                body = await request.json()
                status = str(body.get("status", "")) if isinstance(body, dict) else ""
            except Exception:
                status = ""
        if status not in ("draft", "approved", "archived"):
            return error(400, "Status must be draft, approved, or archived.")
        if not app.state.store.update_draft_status(draft_id, status):
            return error(404, "Draft not found.")
        if "text/html" in request.headers.get("accept", ""):
            return RedirectResponse("/?view=library&notice=Draft+status+updated", status_code=303)
        return {"id": draft_id, "status": status}

    @app.get("/content/drafts")
    def content_drafts(request: Request, status: str = ""):
        if not signed_in(request):
            return error(401, "Sign in first.")
        return {"drafts": app.state.store.list_drafts(status=status)}

    @app.get("/queue")
    def queue_status(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        return {"jobs": app.state.store.list_jobs()}

    @app.post("/queue/clear")
    def queue_clear(request: Request):
        cleared = app.state.store.clear_queued_jobs()
        return RedirectResponse(f"/?view=research&notice=Cleared+{cleared}+queued+job{'' if cleared == 1 else 's'}", status_code=303)

    @app.post("/queue/{job_id}/cancel")
    def queue_cancel(request: Request, job_id: int):
        app.state.store.cancel_job(job_id)
        return RedirectResponse("/?view=research&notice=Cancel+requested", status_code=303)

    @app.post("/queue/{job_id}/retry")
    def queue_retry(request: Request, job_id: int):
        job = app.state.store.retry_job(job_id)
        if not job:
            return error(400, "Only failed or cancelled jobs can be retried.")
        return RedirectResponse(f"/?view=research&notice=Job+%23{job['id']}+queued", status_code=303)

    @app.get("/healthz")
    def healthz():
        return {"ok": True}

    return app
