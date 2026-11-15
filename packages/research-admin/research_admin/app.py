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
from .followers import (
    AUDIENCE_LIST_LABELS,
    AUDIENCE_LISTS,
    FOLLOW_SORTS,
    FOLLOW_VIEW_LISTS,
    GRAPH_COMMUNITY_LABELS,
    GRAPH_COMMUNITY_LISTS,
    MAX_ENTRIES,
    UNFOLLOW_FILTERS,
    AudienceError,
    analyze_audience,
    analyze_graph_community,
    extract_engagers,
    filter_graph_people,
    filter_people,
    parse_export,
    since_date,
)
from .jobs import JobCancelled
from .research import ResearchError, mine_pain_points
from .store import Store, StoreError, build_vault
from .threads_client import POST_TEXT_MAX, SampleLimits, ThreadsClient, ThreadsError

SESSION_COOKIE = "research_session"
CSRF_COOKIE = "research_csrf"
STATE_TTL = 600
SESSION_TTL = 8 * 3600
LOGIN_MAX_FAILURES = 5
LOGIN_WINDOW = 300
MAX_IMPORT_BYTES = 20 * 1024 * 1024  # both export files combined
SAFE_RESPONSE_HEADERS = {"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer", "X-Frame-Options": "deny"}


def parse_form(data: dict) -> dict:
    return {k: v for k, v in data.items() if isinstance(v, str)}


class UploadRejected(AudienceError):
    """Import rejected before parsing, with the HTTP status to answer with."""

    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status


async def read_import(request: Request) -> dict:
    """Read both upload files from the request, or raise UploadRejected."""
    try:
        declared = int(request.headers.get("content-length") or 0)
    except ValueError:
        declared = 0
    if declared > MAX_IMPORT_BYTES:
        raise UploadRejected("Export files are too large; 20 MB combined limit.", 413)
    try:
        form = await request.form()
    except Exception as exc:  # noqa: BLE001 - a malformed multipart body must answer with a message
        raise UploadRejected("The upload could not be read; try again with the two JSON files.") from exc
    uploads = {}
    for field_name, label in (("followers", "followers.json"), ("following", "following.json")):
        item = form.get(field_name)
        if item is None or isinstance(item, str) or not getattr(item, "filename", ""):
            raise UploadRejected(f"Upload both files: {label} is missing.")
        raw = await item.read()
        if len(raw) > MAX_IMPORT_BYTES:
            raise UploadRejected("Export files are too large; 20 MB combined limit.", 413)
        uploads[field_name] = (label, raw)
    if uploads["followers"][1] == uploads["following"][1]:
        raise UploadRejected("Both files are identical. Upload followers.json and following.json, not the same file twice.")
    try:
        return {
            key: parse_export(json.loads(raw.decode("utf-8-sig", "replace")), label=label)
            for key, (label, raw) in uploads.items()
        }
    except json.JSONDecodeError as exc:
        raise UploadRejected("One of the files is not valid JSON. Upload followers.json and following.json as they come from the export.") from exc


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

    def graph_audience_analysis() -> dict | None:
        stored = store.get_graph_audience()
        if not stored:
            return None
        return analyze_graph_community(stored, store.list_insights())

    def audience_analysis() -> dict | None:
        stored = store.get_audience()
        if not stored:
            return None
        graph = graph_audience_analysis()
        analysis = analyze_audience(
            stored["followers"],
            stored["following"],
            unfollow_map=store.get_unfollow_map(),
            engagers=graph["engagers"] if graph else None,
        )
        analysis["imported_at"] = stored["imported_at"]
        return analysis

    app.state.audience_analysis = audience_analysis
    app.state.graph_audience_analysis = graph_audience_analysis

    def _cancel_check(job_id: int | None) -> None:
        if job_id is not None and store.job_cancel_requested(job_id):
            raise JobCancelled("Job cancelled.")

    def _perform_graph_sync(params: dict, job_id: int | None = None) -> dict:
        token = store.get_token()
        if not token or token.expires_at <= time.time():
            raise ThreadsError("Threads token expired or revoked; reconnect your account.")
        _cancel_check(job_id)
        synced = ThreadsClient(settings, app.state.http).sync_graph_audience(
            token.access_token,
            post_limit=params.get("post_limit", 25),
            replies_per_post=params.get("replies_per_post", 50),
        )
        _cancel_check(job_id)
        existing_graph = store.get_graph_audience() or {}
        engagers = extract_engagers(
            synced.get("replies", []),
            store.list_insights(),
            owner_username=synced["profile"].get("username", ""),
            existing=existing_graph.get("engagers", []),
        )
        synced_at = store.save_graph_audience(
            profile=synced["profile"],
            followers_count=synced["followers_count"],
            metrics=synced["metrics"],
            demographics=synced["demographics"],
            engagers=engagers,
        )
        analysis = graph_audience_analysis()
        return {
            "synced_at": synced_at,
            "followers_count": synced["followers_count"],
            "followers_delta": analysis["counts"]["followers_delta"] if analysis else None,
            "profile": synced["profile"],
            "metrics": synced["metrics"],
            "demographics": synced["demographics"],
            "active_repliers": len(engagers),
        }

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
        client = ThreadsClient(settings, app.state.http)
        research = client.collect_research(
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
        # Synchronize discovered community repliers from the sampled Graph posts/replies into Followers
        existing_graph = store.get_graph_audience() or {}
        owner = str((existing_graph.get("profile") or {}).get("username", ""))
        engagers = extract_engagers(
            research.get("sources", []),
            store.list_insights(),
            owner_username=owner,
            existing=existing_graph.get("engagers", []),
        )
        profile_data = None
        followers_count = None
        user_metrics = None
        demographics = None
        if str(params.get("sync_graph", "")).lower() in ("on", "true", "1"):
            try:
                profile_data = client.fetch_profile(token.access_token)
                u_insights = client.fetch_user_insights(token.access_token)
                followers_count = u_insights["followers_count"]
                user_metrics = u_insights["metrics"]
                demographics = u_insights["demographics"]
                if profile_data.get("username"):
                    engagers = extract_engagers(
                        research.get("sources", []),
                        store.list_insights(),
                        owner_username=profile_data["username"],
                        existing=existing_graph.get("engagers", []),
                    )
            except Exception:  # noqa: BLE001
                pass
        if engagers or existing_graph or followers_count is not None:
            store.save_graph_audience(
                profile=profile_data,
                followers_count=followers_count,
                metrics=user_metrics,
                demographics=demographics,
                engagers=engagers,
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
            elif job["kind"] == "graph_sync":
                result = _perform_graph_sync(job["params"], job_id)
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
        follow_list = request.query_params.get("list", "") if view == "followers" else ""
        graph_list = request.query_params.get("glist", "") if view == "followers" else ""
        follow_query = request.query_params.get("q", "") if view == "followers" else ""
        follow_uf = request.query_params.get("uf", "") if view == "followers" else ""
        follow_sort = request.query_params.get("sort", "newest") if view == "followers" else "newest"
        token = app.state.store.get_token()
        connected = token is not None and token.expires_at > time.time()
        expiry = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(token.expires_at)) if connected else ""
        connection = f"Connected · expires {expiry}" if connected else "Not connected"
        insights = app.state.store.list_insights(query=search)
        all_drafts = app.state.store.list_drafts()
        audiences = build_audiences(app.state.store.list_insights(), all_drafts)
        runs = app.state.store.list_research_runs()
        drafts = app.state.store.list_drafts(status=status) if status else all_drafts
        audience = audience_analysis()
        graph_audience = graph_audience_analysis()
        csrf = request.cookies.get(CSRF_COOKIE) or secrets.token_urlsafe(24)
        limits = SampleLimits.from_row(runs[0] if runs else None)
        focus = runs[0].get("focus", "") if runs else ""
        page = render_dashboard(DashboardData(
            view=view, connection=connection, expiry=expiry, insights=insights, runs=runs,
            audiences=audiences, drafts=drafts, query=search,
            selection=selection, status_filter=status, csrf=csrf, limits=limits,
            jobs=store.list_jobs(),
            focus=focus,
            audience=audience, graph_audience=graph_audience,
            unfollow_queue=store.list_unfollow_queue(),
            follow_list=follow_list, graph_list=graph_list, follow_query=follow_query,
            follow_uf=follow_uf, follow_sort=follow_sort,
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
        include_publish = request.query_params.get("scope") == "publish"
        response = RedirectResponse(
            ThreadsClient(settings, app.state.http).authorize_url(state, include_publish=include_publish),
            status_code=307,
        )
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

    @app.post("/auth/refresh")
    def auth_refresh(request: Request):
        is_html = "text/html" in request.headers.get("accept", "")
        token = app.state.store.get_token()
        if not token or token.expires_at <= time.time():
            if is_html:
                return RedirectResponse("/?view=settings&notice=Threads+token+expired;+reconnect+Threads", status_code=303)
            return error(401, "reconnect")
        now = int(time.time())
        try:
            refreshed = ThreadsClient(settings, app.state.http).refresh_token(token.access_token)
            expires_at = now + refreshed.expires_in
            app.state.store.save_token(refreshed.access_token, expires_at)
        except (ThreadsError, StoreError) as exc:
            if is_html:
                return RedirectResponse(f"/?view=settings&notice={quote(str(exc))}", status_code=303)
            return error(502, str(exc))
        if is_html:
            return RedirectResponse("/?view=settings&notice=Threads+token+refreshed+for+60+days", status_code=303)
        return {"connected": True, "expires_at": expires_at}

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
        if str(data.get("sync_graph", "")).lower() in ("on", "true", "1"):
            params["sync_graph"] = "on"
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
        return {"audiences": build_audiences(app.state.store.list_insights(), app.state.store.list_drafts())}

    @app.get("/audiences/export.csv")
    def audiences_export(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(("audience_segment", "evidence_count", "themes", "quote", "source_url", "ebook_idea"))
        for audience in build_audiences(app.state.store.list_insights(), app.state.store.list_drafts()):
            for item in audience["evidence"]:
                cells = [audience["name"], audience["evidence_count"], ", ".join(audience["themes"]), item["quote"], item["source_url"], item["ebook_idea"]]
                writer.writerow([("'" + str(value)) if str(value).startswith(("=", "+", "-", "@", "\t", "\r")) else value for value in cells])
        return Response(output.getvalue(), media_type="text/csv; charset=utf-8", headers={"Content-Disposition": "attachment; filename=threads-audience-evidence.csv"})

    def follow_redirect(notice: str) -> RedirectResponse:
        return RedirectResponse(f"/?view=followers&notice={quote(notice)}", status_code=303)

    @app.get("/followers")
    def followers_index(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        analysis = audience_analysis()
        graph = graph_audience_analysis()
        if not analysis and not graph:
            return {"audience": None}
        query = request.query_params.get("q", "")
        uf = request.query_params.get("uf", "")
        sort = request.query_params.get("sort", "newest")
        audience_payload = None
        if analysis:
            audience_payload = {
                "counts": analysis["counts"],
                "insights": analysis["insights"],
                "imported_at": analysis["imported_at"],
                "query": query,
                "uf": uf if uf in UNFOLLOW_FILTERS else "all",
                "sort": sort if sort in FOLLOW_SORTS else "newest",
                "lists": {
                    key: {
                        "label": AUDIENCE_LIST_LABELS[key],
                        "total": len(analysis[key]),
                        "people": filter_people(analysis, key, query, uf=uf, sort=sort, limit=500)[0],
                    }
                    for key in FOLLOW_VIEW_LISTS
                },
            }
        if not graph:
            return {"audience": audience_payload}
        graph_payload = {
            "counts": graph["counts"],
            "profile": graph["profile"],
            "metrics": graph["metrics"],
            "demographics": graph["demographics"],
            "synced_at": graph["synced_at"],
            "query": query,
            "lists": {
                key: {
                    "label": GRAPH_COMMUNITY_LABELS[key],
                    "total": len(graph[key]),
                    "people": filter_graph_people(graph, key, query, limit=500)[0],
                }
                for key in GRAPH_COMMUNITY_LISTS
            },
        }
        return {"audience": audience_payload, "graph": graph_payload}

    @app.post("/followers/unfollow")
    async def followers_unfollow(request: Request):
        is_html = "text/html" in request.headers.get("accept", "")
        ctype = request.headers.get("content-type", "").lower()
        ret_list, ret_uf, ret_sort, ret_q = "not_following_back", "", "newest", ""
        if "application/json" in ctype:
            try:
                body = await request.json()
            except Exception:
                body = {}
            raw_names = body.get("usernames", []) if isinstance(body, dict) else []
            action = str(body.get("action", "later")).strip() if isinstance(body, dict) else "later"
        else:
            try:
                form = await request.form()
                raw_names = form.getlist("usernames")
                action = str(form.get("action", "later")).strip()
                ret_list = str(form.get("return_list", "not_following_back")).strip()
                ret_uf = str(form.get("return_uf", "")).strip()
                ret_sort = str(form.get("return_sort", "newest")).strip()
                ret_q = str(form.get("return_q", "")).strip()
            except Exception:
                raw_names = []
                action = "later"
        if isinstance(raw_names, str):
            raw_names = [part.strip() for part in raw_names.split(",") if part.strip()]
        elif isinstance(raw_names, (list, tuple)):
            expanded = []
            for item in raw_names:
                expanded.extend(part.strip() for part in str(item).split(",") if part.strip())
            raw_names = expanded
        else:
            raw_names = []
        if action not in ("later", "unfollowed", "keep"):
            return follow_redirect("Invalid unfollow action.") if is_html else error(400, "Invalid unfollow action.")
        if not raw_names:
            return follow_redirect("Select at least one account first.") if is_html else error(400, "Select at least one account first.")
        updated = app.state.store.set_unfollow_status(raw_names, action)
        if is_html:
            labels = {
                "later": f"Saved {updated} account{'' if updated == 1 else 's'} to Unfollow Later",
                "unfollowed": f"Marked {updated} account{'' if updated == 1 else 's'} as unfollowed",
                "keep": f"Removed {updated} account{'' if updated == 1 else 's'} from Unfollow Later",
            }
            target_list = ret_list if ret_list in FOLLOW_VIEW_LISTS else "not_following_back"
            qs = f"/?view=followers&list={quote(target_list)}"
            if ret_uf in UNFOLLOW_FILTERS and ret_uf != "all":
                qs += f"&uf={quote(ret_uf)}"
            if ret_sort in FOLLOW_SORTS and ret_sort != "newest":
                qs += f"&sort={quote(ret_sort)}"
            if ret_q:
                qs += f"&q={quote(ret_q)}"
            qs += f"&notice={quote(labels[action])}"
            return RedirectResponse(qs, status_code=303)
        return {"updated": updated, "action": action}

    @app.post("/followers/sync")
    async def followers_sync(request: Request):
        is_html = "text/html" in request.headers.get("accept", "")
        token = app.state.store.get_token()
        if not token or token.expires_at <= time.time():
            return follow_redirect("Connect Threads first before syncing from the Graph API.") if is_html else error(401, "reconnect")
        try:
            data = dict(await request.form())
        except Exception:
            try:
                body = await request.body()
                data = json.loads(body) if body else {}
            except Exception:
                data = {}
        params = {
            "post_limit": min(max(int(data.get("post_limit", 25) or 25), 1), 50),
            "replies_per_post": min(max(int(data.get("replies_per_post", 50) or 50), 1), 100),
        }
        if str(data.get("queue", "")).lower() in ("on", "true", "1"):
            job = app.state.store.create_job("graph_sync", params)
            return follow_redirect(f"Graph sync queued (job #{job['id']})")
        try:
            result = _perform_graph_sync(params)
        except (ThreadsError, StoreError) as exc:
            return follow_redirect(str(exc)) if is_html else error(502, str(exc))
        if is_html:
            return follow_redirect(
                f"Synced {result['followers_count']:,} followers and {result['active_repliers']} active community repliers from Threads Graph"
            )
        return result

    @app.get("/followers/graph.csv")
    def followers_graph_export(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        graph = graph_audience_analysis()
        if not graph:
            return error(404, "No Threads Graph audience synced yet. Run research or click Sync from Threads Graph first.")
        wanted = request.query_params.get("glist", "")
        keys = [wanted] if wanted in GRAPH_COMMUNITY_LISTS else ["all_engagers"]
        query = request.query_params.get("q", "")
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(("username", "profile_url", "replies_count", "insights_count", "themes", "last_seen", "sample_quote"))
        for key in keys:
            people, _total = filter_graph_people(graph, key, query, limit=MAX_ENTRIES)
            for person in people:
                cells = (
                    person["username"],
                    person["href"],
                    person["replies_count"],
                    len(person.get("insight_ids", [])),
                    ", ".join(person.get("themes", [])),
                    person.get("last_seen", ""),
                    person.get("sample_quote", ""),
                )
                writer.writerow([("'" + str(value)) if str(value).startswith(("=", "+", "-", "@", "\t", "\r")) else value for value in cells])
        return Response(output.getvalue(), media_type="text/csv; charset=utf-8", headers={"Content-Disposition": "attachment; filename=threads-graph-community.csv"})

    @app.get("/followers/export.csv")
    def followers_export(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        analysis = audience_analysis()
        if not analysis:
            return error(404, "No follower import yet. Upload followers.json and following.json first.")
        wanted = request.query_params.get("list", "")
        keys = [wanted] if wanted in FOLLOW_VIEW_LISTS else list(AUDIENCE_LISTS)
        query = request.query_params.get("q", "")
        uf = request.query_params.get("uf", "")
        sort = request.query_params.get("sort", "newest")
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(("list", "username", "profile_url", "since"))
        for key in keys:
            people, _total = filter_people(analysis, key, query, uf=uf, sort=sort, limit=MAX_ENTRIES)
            for person in people:
                cells = (AUDIENCE_LIST_LABELS[key], person["username"], person["href"], since_date(person["since"]))
                writer.writerow([("'" + str(value)) if str(value).startswith(("=", "+", "-", "@", "\t", "\r")) else value for value in cells])
        return Response(output.getvalue(), media_type="text/csv; charset=utf-8", headers={"Content-Disposition": "attachment; filename=threads-followers.csv"})

    @app.post("/followers/import")
    async def followers_import(request: Request):
        is_html = "text/html" in request.headers.get("accept", "")

        def fail(message: str, status: int = 400) -> Response:
            # The browser form gets its error back as a dashboard notice, not a dead-end JSON page.
            return follow_redirect(message) if is_html else error(status, message)

        try:
            parsed = await read_import(request)
        except UploadRejected as exc:
            return fail(str(exc), exc.status)
        except AudienceError as exc:
            return fail(str(exc))
        imported_at = app.state.store.save_audience(parsed["followers"], parsed["following"])
        if is_html:
            return follow_redirect(
                f"Imported {len(parsed['followers']):,} followers and {len(parsed['following']):,} following · {imported_at[:10]}"
            )
        return {"imported_at": imported_at, "followers": len(parsed["followers"]), "following": len(parsed["following"])}

    @app.post("/followers/clear")
    async def followers_clear(request: Request):
        cleared_import = app.state.store.clear_audience()
        cleared_graph = app.state.store.clear_graph_audience()
        cleared = bool(cleared_import or cleared_graph)
        if "text/html" in request.headers.get("accept", ""):
            return follow_redirect("Follower import cleared" if cleared else "No follower import to clear")
        return {"cleared": cleared}

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

    @app.post("/content/drafts/{draft_id}/edit")
    async def content_draft_edit(request: Request, draft_id: int):
        is_html = "text/html" in request.headers.get("accept", "")
        draft = app.state.store.get_draft(draft_id)
        if not draft:
            return error(404, "Draft not found.")
        try:
            data = dict(await request.form())
        except Exception:
            try:
                body = await request.json()
                data = body if isinstance(body, dict) else {}
            except Exception:
                data = {}
        title = " ".join(str(data.get("title", draft["title"])).split())[:160]
        if not title:
            return error(400, "Draft title cannot be empty.")
        content = dict(draft["content"])
        if draft["kind"] == "threads_post":
            post_text = str(data.get("post", content.get("post", ""))).strip()
            if not post_text:
                return error(400, "Post text cannot be empty.")
            if len(post_text) > POST_TEXT_MAX:
                return error(400, f"Threads posts are limited to {POST_TEXT_MAX} characters.")
            content["post"] = post_text
        elif draft["kind"] == "ebook_outline":
            if "premise" in data:
                content["premise"] = str(data.get("premise", "")).strip()[:1000]
            if "intended_reader_need" in data:
                content["intended_reader_need"] = str(data.get("intended_reader_need", "")).strip()[:1000]
        elif draft["kind"] == "design_brief":
            for field_name in ("concept", "format", "visual_direction", "copy"):
                if field_name in data:
                    content[field_name] = str(data.get(field_name, "")).strip()[:2000]
        app.state.store.update_draft_content(draft_id, title=title, content=content)
        if is_html:
            return RedirectResponse("/?view=library&notice=Draft+updated", status_code=303)
        return {"id": draft_id, "title": title, "content": content}

    @app.post("/content/drafts/{draft_id}/publish")
    async def content_draft_publish(request: Request, draft_id: int):
        is_html = "text/html" in request.headers.get("accept", "")
        draft = app.state.store.get_draft(draft_id)
        if not draft:
            return error(404, "Draft not found.")
        content = dict(draft["content"])
        err_msg = (
            "Only Threads post drafts can be published to Threads." if draft["kind"] != "threads_post"
            else "Approve the draft before publishing to Threads." if draft["status"] != "approved"
            else "This draft has already been published to Threads." if content.get("published")
            else ""
        )
        if err_msg:
            return error(400, err_msg)
        token = app.state.store.get_token()
        if not token or token.expires_at <= time.time():
            return RedirectResponse("/?view=library&notice=Connect+Threads+before+publishing", status_code=303) if is_html else error(401, "reconnect")
        post_text = str(content.get("post", "")).strip()
        try:
            published = ThreadsClient(settings, app.state.http).publish_post(token.access_token, post_text)
        except ThreadsError as exc:
            return RedirectResponse(f"/?view=library&notice={quote(str(exc))}", status_code=303) if is_html else error(502, str(exc))
        pub_meta = {
            "id": published["id"],
            "url": published.get("permalink", ""),
            "published_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        content["published"] = pub_meta
        app.state.store.update_draft_content(draft_id, title=draft["title"], content=content)
        return RedirectResponse("/?view=library&notice=Published+to+Threads", status_code=303) if is_html else {"id": draft_id, "published": pub_meta}

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
