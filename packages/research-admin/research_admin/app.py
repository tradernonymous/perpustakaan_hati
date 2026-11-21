"""Password-protected admin app for Perpustakaan Hati Threads research, community & content studio."""

import asyncio
import csv
import hashlib
import hmac
import html as html_module
import io
import json
import re
import secrets
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import parse_qs, quote, urlsplit

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse

from .audiences import build_audiences
from .avatars import AVATAR_PATH, ThreadsAvatar
from .cards import build_publish_pack, draft_to_ebook_markdown, render_quote_card_html
from .config import Settings
from .content import (
    DRAFT_KINDS,
    DRAFT_LANGUAGES,
    DRAFT_TONES,
    adjust_draft_variant,
    draft_reply,
    generate_drafts,
    generate_variants,
)
from .dashboard import DashboardData, render_dashboard
from .discovery import expand_google_autocomplete
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
    diff_snapshots,
    extract_engagers,
    filter_graph_people,
    filter_people,
    parse_export,
    since_date,
)
from .jobs import JobCancelled
from .knowledge import compile_fact_sheet, ensure_default_knowledge, extract_wiki_links
from .publications import PublicationError, Publications
from .research import ResearchError, mine_keyword_sources, mine_pain_points
from .store import Store, StoreError, build_vault
from .telegram_ops import build_draft_keyboard, format_digest_html, send_telegram_alert
from .theme import RAISED, SOFT, VOID
from .threads_client import (
    EXPANDED_SCOPES,
    POST_TEXT_MAX,
    PUBLISH_SCOPES,
    READ_SCOPES,
    SampleLimits,
    ThreadsClient,
    ThreadsError,
    verify_webhook_signature,
)

STATIC_FONTS_DIR = Path(__file__).resolve().parent / "static" / "fonts"
ALLOWED_FONTS = {
    "FrauncesDisplay.woff2",
    "FrauncesDisplayItalic.woff2",
    "InterUI.woff2",
    "SourceSerifText.woff2",
}
SVG_FAVICON = (
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>"
    "<rect width='64' height='64' rx='16' fill='#1C2D23'/>"
    "<text x='50%' y='54%' dominant-baseline='middle' text-anchor='middle' "
    "font-family='Georgia,serif' font-weight='bold' font-size='28' fill='#C99B6B'>PH</text></svg>"
)

SESSION_COOKIE = "research_session"
CSRF_COOKIE = "research_csrf"
STATE_TTL = 600
SESSION_TTL = 8 * 3600
LOGIN_MAX_FAILURES = 5
LOGIN_WINDOW = 300
MAX_IMPORT_BYTES = 20 * 1024 * 1024  # both export files combined
SAFE_RESPONSE_HEADERS = {
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "X-Frame-Options": "deny",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}


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
    store = Store(settings.db_path, vault=vault_factory() if vault_factory else build_vault(settings))
    store.init_schema()
    store.recover_interrupted_jobs()
    app.state.store = store
    publications = Publications(store._connect)
    avatar = ThreadsAvatar()

    def sealed(response: Response, *, csp_nonce: str = "") -> Response:
        for key, value in SAFE_RESPONSE_HEADERS.items():
            response.headers[key] = value
        ctype = response.headers.get("content-type", "")
        if ctype.startswith("text/html"):
            nonce_src = f"'nonce-{csp_nonce}' " if csp_nonce else ""
            response.headers["Content-Security-Policy"] = (
                f"default-src 'self'; font-src 'self'; img-src 'self' https: data:; "
                f"style-src 'self' 'unsafe-inline'; script-src 'self' {nonce_src}; "
                f"connect-src 'self'; form-action 'self'; frame-ancestors 'none'"
            )
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
        """Double-submit token for browsers/webviews that omit Origin on same-site form POSTs."""
        content_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
        cookie_token = request.cookies.get(CSRF_COOKIE, "")
        if not cookie_token:
            return False
        if content_type == "application/x-www-form-urlencoded":
            body = (await request.body()).decode("utf-8", "replace")
            submitted = (parse_qs(body).get("csrf") or [""])[0]
            return bool(submitted) and hmac.compare_digest(submitted, cookie_token)
        if content_type == "multipart/form-data":
            try:
                declared = int(request.headers.get("content-length") or 0)
            except ValueError:
                declared = 0
            if declared > MAX_IMPORT_BYTES:
                return False
            try:
                form = await request.form()
                submitted = str(form.get("csrf") or "")
            except Exception:
                return False
            return bool(submitted) and hmac.compare_digest(submitted, cookie_token)
        return False

    @app.middleware("http")
    async def security(request: Request, call_next):
        path = request.url.path
        if path == "/healthz":
            return await call_next(request)
        if _hostname(request.headers.get("host", "")) not in settings.allowed_hosts:
            return error(400, "Unexpected host header.")
        is_public_signed_or_asset = (
            path in ("/webhooks/threads", "/internal/ingest/web-signals", "/internal/status")
            or (request.method == "GET" and (path.startswith("/assets/fonts/") or path == "/favicon.ico"))
        )
        blocked: Response | None = None
        if not is_public_signed_or_asset:
            if request.method == "POST" and path != "/login" and not (safe_origin(request) or await csrf_token_ok(request)):
                blocked = error(403, "Cross-origin or missing-origin requests are blocked.")
            elif path not in ("/login", "/auth/callback"):
                if not settings.admin_password:
                    blocked = error(503, "RESEARCH_ADMIN_PASSWORD is not set. Set it and restart the server.")
                elif not signed_in(request):
                    if request.method == "GET" and _wants_html(request):
                        blocked = sealed(RedirectResponse(f"/login?next={quote(path, safe='')}", status_code=303))
                    else:
                        blocked = error(401, "Sign in first.")
        if blocked is not None:
            return blocked
        return sealed(await call_next(request), csp_nonce=getattr(request.state, "csp_nonce", ""))

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

    def _sync_inbox_from_replies(replies: list[dict], owner_username: str = "") -> int:
        owner_cf = owner_username.strip().lstrip("@").casefold()
        inbox_rows = []
        for item in replies or []:
            if not isinstance(item, dict) or item.get("source_type") == "post":
                continue
            rid = str(item.get("id") or "").strip()
            uname = str(item.get("username") or "").strip().lstrip("@")
            text = str(item.get("text") or "").strip()
            if not rid or not text or (owner_cf and uname.casefold() == owner_cf):
                continue
            inbox_rows.append({
                "reply_id": rid,
                "post_id": str(item.get("parent_id", "")),
                "post_permalink": str(item.get("parent_permalink") or item.get("permalink") or ""),
                "username": uname,
                "text": text,
                "created_at": str(item.get("timestamp") or ""),
            })
        return store.upsert_inbox_items(inbox_rows) if inbox_rows else 0

    def _relay_token_to_web(token_value: str, expires_at: int) -> None:
        if not (settings.web_internal_url and settings.sync_secret):
            return
        body = json.dumps({"access_token": token_value, "expires_at": expires_at}).encode("utf-8")
        sig = hmac.new(settings.sync_secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
        try:
            app.state.http.post(
                f"{settings.web_internal_url}/api/internal/threads-token",
                content=body,
                headers={"Content-Type": "application/json", "X-Research-Signature": f"sha256={sig}"},
                timeout=8.0,
            )
        except httpx.HTTPError:
            pass

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
        owner_username = str(synced["profile"].get("username", ""))
        engagers = extract_engagers(
            synced.get("replies", []),
            store.list_insights(),
            owner_username=owner_username,
            existing=existing_graph.get("engagers", []),
        )
        _sync_inbox_from_replies(synced.get("replies", []), owner_username)
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
            token.access_token, post_limit=limits.post_limit, top_posts=limits.top_posts, replies_per_post=limits.replies_per_post
        )
        _cancel_check(job_id)
        fact_sheet = compile_fact_sheet(store)
        insights = mine_pain_points(
            research["sources"],
            settings,
            app.state.http,
            focus=params.get("focus", ""),
            options={"fact_sheet": fact_sheet, "store": store},
        )
        _cancel_check(job_id)
        store.save_insights(insights)
        run_id = store.save_research_run(
            posts_sampled=research["posts_sampled"], selected_posts=research.get("selected_posts", 0),
            insights=insights, limitations=research["limitations"], posts=research.get("selected_posts_data", []),
            post_limit=limits.post_limit, top_posts=limits.top_posts, replies_per_post=limits.replies_per_post,
            focus=params.get("focus", ""),
        )
        existing_graph = store.get_graph_audience() or {}
        owner = str((existing_graph.get("profile") or {}).get("username", ""))
        engagers = extract_engagers(
            research.get("sources", []),
            store.list_insights(),
            owner_username=owner,
            existing=existing_graph.get("engagers", []),
        )
        _sync_inbox_from_replies(research.get("sources", []), owner)
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
        if settings.telegram_bot_token and settings.telegram_chat_id and insights:
            lines = [f"- [{item['theme']}] {item['quote'][:90]}" for item in insights[:4]]
            msg = format_digest_html(title=f"Research run #{run_id}: {len(insights)} new insights", lines=lines)
            send_telegram_alert(settings, store, app.state.http, msg, {"dedupe_key": f"research-run-{run_id}"})
        return {"run_id": run_id, "insights": insights, "limitations": research["limitations"], "posts_sampled": research["posts_sampled"], "limits": limits.as_dict(), "focus": params.get("focus", "")}

    def _perform_drafts(params: dict, job_id: int | None = None) -> dict:
        ids = list(dict.fromkeys(int(value) for value in params.get("insight_ids", [])))[:20]
        if not ids:
            raise ResearchError("Select between 1 and 20 valid saved insights.")
        selected = store.get_insights_by_ids(ids)
        if len(selected) != len(ids):
            raise ResearchError("One or more selected insights are no longer available.")
        _cancel_check(job_id)
        fact_sheet = compile_fact_sheet(store)
        saved = store.save_drafts(
            generate_drafts(
                selected,
                settings,
                app.state.http,
                kinds=params.get("kinds"),
                tone=params.get("tone", "empathetic"),
                language=params.get("language", "match evidence"),
                options={"fact_sheet": fact_sheet, "store": store},
            ),
            ids,
        )
        return {"drafts": saved}

    def _perform_keyword_search(params: dict, job_id: int | None = None) -> dict:
        token = store.get_token()
        if not token or token.expires_at <= time.time():
            raise ThreadsError("Threads token expired or revoked; reconnect your account.")
        query = " ".join(str(params.get("query") or params.get("keyword") or "").split())[:100]
        if not query:
            raise ResearchError("Provide a keyword to search Threads.")
        _cancel_check(job_id)
        client = ThreadsClient(settings, app.state.http)
        items = client.keyword_search(token.access_token, query, search_mode=str(params.get("mode", "KEYWORD")))
        _cancel_check(job_id)
        insights = mine_keyword_sources(query, items, settings, app.state.http, {"store": store}) if items else []
        if insights:
            store.save_insights(insights)
        return {"query": query, "sampled": len(items), "insights_count": len(insights)}

    def _perform_watchlist(params: dict, job_id: int | None = None) -> dict:
        token = store.get_token()
        if not token or token.expires_at <= time.time():
            raise ThreadsError("Threads token expired or revoked; reconnect your account.")
        res = _perform_research({"post_limit": 25, "top_posts": 3, "replies_per_post": 30, "focus": params.get("focus", ""), "sync_graph": "on"}, job_id)
        client = ThreadsClient(settings, app.state.http)
        kw_insights = 0
        for kw in (params.get("keywords") or [])[:5]:
            _cancel_check(job_id)
            try:
                items = client.keyword_search(token.access_token, kw)
                mined = mine_keyword_sources(kw, items, settings, app.state.http, {"store": store}) if items else []
                if mined:
                    store.save_insights(mined)
                    kw_insights += len(mined)
            except (ThreadsError, ResearchError):
                continue
        store.touch_watchlist_run()
        return {**res, "watchlist_keyword_insights": kw_insights}

    def _perform_scheduled_publish(params: dict, job_id: int | None = None) -> dict:
        draft_id = int(params.get("draft_id", 0) or 0)
        draft = store.get_draft(draft_id)
        if not draft:
            raise StoreError("Scheduled draft not found.")
        if draft.get("status") == "published" or (isinstance(draft.get("content"), dict) and draft["content"].get("published")):
            return {"draft_id": draft_id, "already_published": True}
        token = store.get_token()
        if not token or token.expires_at <= time.time():
            raise ThreadsError("Threads token expired or revoked; reconnect your account.")
        post_text = str((draft.get("content") or {}).get("post", "")).strip()
        published = ThreadsClient(settings, app.state.http).publish_post(token.access_token, post_text)
        pub_meta = {
            "id": published["id"],
            "url": published.get("permalink", ""),
            "published_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        content = dict(draft["content"])
        content["published"] = pub_meta
        store.update_draft_content(draft_id, title=draft["title"], content=content)
        store.mark_draft_published(draft_id, post_id=published["id"], permalink=published.get("permalink", ""))
        return {"draft_id": draft_id, "published": pub_meta}

    def run_job(job: dict) -> bool:
        job_id = int(job["id"])
        try:
            kind = job["kind"]
            if kind == "research":
                result = _perform_research(job["params"], job_id)
            elif kind == "drafts":
                result = _perform_drafts(job["params"], job_id)
            elif kind == "graph_sync":
                result = _perform_graph_sync(job["params"], job_id)
            elif kind == "keyword_search":
                result = _perform_keyword_search(job["params"], job_id)
            elif kind == "watchlist":
                result = _perform_watchlist(job["params"], job_id)
            elif kind == "scheduled_publish":
                result = _perform_scheduled_publish(job["params"], job_id)
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

    def run_maintenance_tick() -> None:
        token = store.get_token()
        if not token or token.expires_at <= time.time():
            return
        queued_or_running = [j for j in store.list_jobs(limit=25) if j["status"] in ("queued", "running")]
        scheduled_ids = {int(j["params"].get("draft_id", 0) or 0) for j in queued_or_running if j["kind"] == "scheduled_publish"}
        for draft in store.list_due_scheduled_drafts():
            if int(draft["id"]) not in scheduled_ids:
                store.create_job("scheduled_publish", {"draft_id": int(draft["id"])})
        wl = store.get_watchlist_config()
        if wl.get("enabled") and not any(j["kind"] == "watchlist" for j in queued_or_running):
            last_raw = wl.get("last_run_at") or ""
            due = not last_raw
            if last_raw:
                try:
                    last_dt = datetime.fromisoformat(last_raw.replace("Z", "+00:00"))
                    due = (datetime.now(UTC) - last_dt) >= timedelta(hours=int(wl.get("interval_hours", 24)))
                except ValueError:
                    due = True
            if due:
                store.create_job("watchlist", {"keywords": wl.get("keywords", []), "focus": wl.get("focus", "")})

    app.state.process_next_job = process_next_job
    app.state.run_maintenance_tick = run_maintenance_tick

    def login_html(next_path: str, csrf: str, message: str = "") -> str:
        note = f"<p class=err role=alert>{html_module.escape(message)}</p>" if message else ""
        return f"""<!doctype html><html lang=ms><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Masuk — Threads research admin</title>
<style>
:root{{--ink:#e6e2da;--muted:#a49c8d;--line:#24402f;--gold:#e9cea2;--green:#9de1c1;--bg:{VOID};--card:{RAISED};color-scheme:dark}}
*{{box-sizing:border-box}}body{{margin:0;min-height:100vh;display:grid;place-items:center;background:var(--bg);color:var(--ink);font:16px/1.5 Inter,system-ui,sans-serif;padding:24px}}
main{{width:100%;max-width:380px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:28px;box-shadow:0 18px 40px -24px rgb(0 0 0/.7)}}
.kicker{{display:flex;align-items:center;gap:.7em;margin:0 0 6px;font-size:12px;letter-spacing:.28em;text-transform:uppercase;color:var(--gold)}}
.kicker::before,.kicker::after{{content:'';flex:1 1 2em;height:1px;background:var(--line)}}
h1{{font-family:Georgia,serif;font-weight:600;font-size:24px;margin:6px 0 4px}}p.sub{{margin:0 0 18px;color:var(--muted);font-size:14px}}
label{{display:block;font-size:13px;font-weight:600;margin:0 0 6px}}input{{width:100%;min-height:44px;border:1px solid var(--line);border-radius:8px;background:{SOFT};color:var(--ink);padding:0 12px;font-size:16px}}
input:focus-visible{{outline:2px solid var(--green);outline-offset:2px}}button{{width:100%;min-height:48px;margin-top:14px;border:0;border-radius:999px;background:linear-gradient(180deg,#7db895,#5b9b7d 50%,#3f9167);color:#07140d;font:600 16px/1 Inter,system-ui,sans-serif;cursor:pointer;box-shadow:0 3px 0 #1d5a3d}}
.err{{margin:12px 0 0;color:#f0a3a0;font-size:14px}}footer{{margin-top:16px;font-size:12px;color:var(--muted)}}
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
        if store.check_auth_locked(client, now_ts=now):
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
            store.record_auth_failure(
                client,
                window_seconds=LOGIN_WINDOW,
                limit=LOGIN_MAX_FAILURES,
                lockout_seconds=LOGIN_WINDOW,
                now_ts=now,
            )
            return sealed(HTMLResponse(login_html(next_path, cookie_token or secrets.token_urlsafe(24), "Kata laluan salah. Cuba lagi."), status_code=401))
        store.clear_auth_failures(client)
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
        inbox_status = request.query_params.get("status", "open") if view == "inbox" else "open"
        follow_list = request.query_params.get("list", "") if view == "followers" else ""
        graph_list = request.query_params.get("glist", "") if view == "followers" else ""
        follow_query = request.query_params.get("q", "") if view == "followers" else ""
        graph_query = request.query_params.get("graph_q", follow_query if graph_list else "") if view == "followers" else ""
        follow_uf = request.query_params.get("uf", "") if view == "followers" else ""
        follow_sort = request.query_params.get("sort", "newest") if view == "followers" else "newest"
        ac_seed = request.query_params.get("ac", "").strip() if view == "research" else ""
        if view in ("knowledge", "research", "studio", "audiences"):
            ensure_default_knowledge(store)
        token = store.get_token()
        connected = token is not None and token.expires_at > time.time()
        expiry = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(token.expires_at)) if connected else ""
        connection = f"Connected · expires {expiry}" if connected else "Not connected"
        all_insights = store.list_insights()
        insights = store.list_insights(query=search) if search else all_insights
        all_drafts = store.list_drafts()
        custom_segments = store.list_audience_segments()
        audiences = build_audiences(all_insights, all_drafts, custom_segments=custom_segments)
        runs = store.list_research_runs()
        drafts = store.list_drafts(status=status) if status else all_drafts
        stored_aud = store.get_audience()
        audience = audience_analysis()
        snapshot_diff = diff_snapshots(store.get_previous_audience_snapshot(), stored_aud["followers"], stored_aud["following"]) if stored_aud else None
        graph_audience = graph_audience_analysis()
        csrf = request.cookies.get(CSRF_COOKIE) or secrets.token_urlsafe(24)
        csp_nonce = secrets.token_urlsafe(16)
        request.state.csp_nonce = csp_nonce
        limits = SampleLimits.from_row(runs[0] if runs else None)
        focus = runs[0].get("focus", "") if runs else ""
        ai_configured = bool(
            settings.openrouter_api_key
            or settings.groq_api_key
            or settings.nim_api_key
            or (settings.openai_compat_base_url and settings.openai_compat_api_key)
        )
        ac_results = expand_google_autocomplete(ac_seed, app.state.http) if ac_seed else []
        token_meta = store.get_token_meta() or {}
        notice_param = request.query_params.get("notice", "")
        err_param = request.query_params.get("err", "")
        page = render_dashboard(DashboardData(
            view=view, connection=connection, expiry=expiry, insights=insights, runs=runs,
            calendar_mode=request.query_params.get("mode", "week"),
            calendar_date=request.query_params.get("date", ""),
            audiences=audiences, drafts=drafts, query=search,
            selection=selection, status_filter=status, csrf=csrf, limits=limits,
            jobs=store.list_jobs(),
            focus=focus,
            audience=audience, graph_audience=graph_audience,
            unfollow_queue=store.list_unfollow_queue(),
            follow_list=follow_list, graph_list=graph_list, follow_query=follow_query, graph_query=graph_query,
            follow_uf=follow_uf, follow_sort=follow_sort,
            model=settings.openrouter_model,
            error=err_param, notice=notice_param,
            configured=ai_configured, threads_configured=not settings.missing_threads(),
            snapshot_diff=snapshot_diff,
            graph_history=store.list_graph_metric_history(),
            inbox_items=store.list_inbox_items(status="" if inbox_status == "all" else inbox_status) if view == "inbox" else [],
            inbox_status=inbox_status,
            knowledge_nodes=store.list_knowledge_nodes() if view == "knowledge" else [],
            knowledge_edges=store.list_knowledge_edges() if view == "knowledge" else [],
            custom_segments=custom_segments,
            ai_summary=store.ai_usage_summary() if view == "settings" else {},
            watchlist=store.get_watchlist_config() if view in ("settings", "overview") else {},
            autocomplete_results=ac_results,
            autocomplete_seed=ac_seed,
            notifications=store.list_notifications() if view == "settings" else [],
            external_signals=store.list_external_signals() if view in ("settings", "overview", "research") else [],
            mini_app_url=settings.mini_app_url,
            scopes=list(token_meta.get("scopes") or []),
            publications=publications.workspace() if view == "publications" else [],
            csp_nonce=csp_nonce,
        ), logout_action=f'<form method=post action=/logout><input type=hidden name=csrf value="{html_module.escape(csrf, quote=True)}"><button class=signout>Sign out</button></form>')
        response = HTMLResponse(page)
        if not request.cookies.get(CSRF_COOKIE):
            response.set_cookie(CSRF_COOKIE, csrf, httponly=True, secure=settings.secure_cookies, samesite="lax", max_age=SESSION_TTL)
        return response

    @app.get("/publications/{tier}/preview")
    def preview_publication(tier: str):
        try:
            return publications.get(tier, published=False)
        except PublicationError as exc:
            return error(exc.code, str(exc))

    @app.get("/publications/{tier}/export")
    def export_publication(tier: str):
        try:
            item = publications.get(tier, published=True)
        except PublicationError as exc:
            return error(exc.code, str(exc))
        name = f"{tier}-r{item['revision']}.json"
        return JSONResponse(item, headers={"Content-Disposition": f'attachment; filename="{name}"'})

    @app.post("/publications/{tier}/{action}")
    async def change_publication(request: Request, tier: str, action: str):
        try:
            form = await request.form()
            if len(form.multi_items()) != len(form):
                raise PublicationError("Duplicate fields are invalid.")
            item = publications.change(tier, action, dict(form))
        except PublicationError as exc:
            if _wants_html(request):
                return RedirectResponse(f"/?view=publications&err={quote(str(exc))}", status_code=303)
            return error(exc.code, str(exc))
        if _wants_html(request):
            return RedirectResponse("/?view=publications", status_code=303)
        return item

    @app.get("/auth/start")
    def auth_start(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        missing = settings.missing_threads()
        if missing:
            return error(503, "not configured", missing=missing)
        state = secrets.token_urlsafe(24)
        scope_param = request.query_params.get("scope", "")
        include_publish = scope_param == "publish"
        include_expanded = scope_param == "expanded"
        if include_expanded:
            granted = list(EXPANDED_SCOPES)
        elif include_publish:
            granted = list(PUBLISH_SCOPES)
        else:
            granted = list(READ_SCOPES)
        store.save_oauth_state(state, ",".join(granted), ttl_seconds=STATE_TTL, now_ts=time.time())
        response = RedirectResponse(
            ThreadsClient(settings, app.state.http).authorize_url(
                state, include_publish=include_publish, include_expanded=include_expanded
            ),
            status_code=307,
        )
        response.set_cookie("oauth_browser", _signed(state + request.cookies.get(SESSION_COOKIE, ""), app.state.session_key), httponly=True, secure=settings.secure_cookies, samesite="lax", max_age=STATE_TTL)
        return response

    @app.get("/auth/callback")
    def auth_callback(request: Request, code: str = "", state: str = ""):
        now = time.time()
        browser = request.cookies.get("oauth_browser", "")
        expected = _signed(state + request.cookies.get(SESSION_COOKIE, ""), app.state.session_key)
        if not state or not browser or not hmac.compare_digest(browser, expected):
            return error(400, "Invalid or expired authorization state; reconnect.")
        scope_str = store.consume_oauth_state(state, now_ts=now)
        if scope_str is None:
            return error(400, "Invalid or expired authorization state; reconnect.")
        if not code:
            return error(400, "Threads denied the connection; reconnect.")
        try:
            client = ThreadsClient(settings, app.state.http)
            token = client.exchange_code(code)
            expires_at = int(now + token.expires_in)
            store.save_token(token.access_token, expires_at)
            scopes = [s for s in scope_str.split(",") if s]
            profile_id, profile_username = "", ""
            try:
                profile = client.fetch_profile(token.access_token)
                profile_id = str(profile.get("id", ""))
                profile_username = str(profile.get("username", ""))
            except Exception:
                pass
            store.save_token_meta(user_id=profile_id, username=profile_username, scopes=scopes)
            _relay_token_to_web(token.access_token, expires_at)
        except (ThreadsError, StoreError):
            return error(400, "Threads connection failed; reconnect.")
        response = RedirectResponse("/", status_code=303)
        response.delete_cookie("oauth_browser")
        return response

    async def _body_or_form(request: Request) -> dict:
        ctype = request.headers.get("content-type", "").lower()
        if "application/json" in ctype:
            try:
                data = await request.json()
                return data if isinstance(data, dict) else {}
            except Exception:
                return {}
        try:
            return dict(await request.form())
        except Exception:
            try:
                raw = await request.body()
                parsed = json.loads(raw) if raw else {}
                return parsed if isinstance(parsed, dict) else {}
            except Exception:
                return {}

    def _ai_configured() -> bool:
        return bool(
            settings.openrouter_api_key
            or settings.groq_api_key
            or settings.nim_api_key
            or (settings.openai_compat_base_url and settings.openai_compat_api_key)
        )

    def _verify_sync_hmac(request: Request, payload: bytes) -> Response | None:
        if not settings.sync_secret:
            return error(503, "RESEARCH_SYNC_SECRET is not configured.")
        sig_hdr = request.headers.get("x-research-signature", "").strip()
        provided = sig_hdr[7:] if sig_hdr.startswith("sha256=") else sig_hdr
        expected = hmac.new(settings.sync_secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
        if not provided or not hmac.compare_digest(provided, expected):
            return error(401, "Invalid research sync signature.")
        return None

    @app.get("/assets/fonts/{font_name}")
    def font_asset(font_name: str):
        if font_name not in ALLOWED_FONTS:
            return error(404, "Font not found.")
        target = STATIC_FONTS_DIR / font_name
        if not target.is_file():
            return error(404, "Font file missing.")
        return FileResponse(target, media_type="font/woff2", headers={"Cache-Control": "public, max-age=31536000, immutable"})

    @app.get(AVATAR_PATH)
    def threads_avatar():
        profile = (store.get_graph_audience() or {}).get("profile") or {}

        def refresh_profile() -> dict:
            token = store.get_token()
            if not token or token.expires_at <= time.time():
                return {}
            try:
                return ThreadsClient(settings, app.state.http, max_retries=0).fetch_profile(token.access_token, timeout=3.0)
            except ThreadsError:
                return {}

        body, media_type = avatar.resolve(app.state.http, profile, refresh_profile)
        return Response(body, media_type=media_type)

    @app.get("/favicon.ico")
    def favicon():
        return Response(SVG_FAVICON, media_type="image/svg+xml", headers={"Cache-Control": "public, max-age=86400"})

    @app.post("/auth/refresh")
    def auth_refresh(request: Request):
        is_html = _wants_html(request)
        token = store.get_token()
        if not token or token.expires_at <= time.time():
            if is_html:
                return RedirectResponse("/?view=settings&notice=Threads+token+expired;+reconnect+Threads", status_code=303)
            return error(401, "reconnect")
        now = int(time.time())
        try:
            refreshed = ThreadsClient(settings, app.state.http).refresh_token(token.access_token)
            expires_at = now + refreshed.expires_in
            store.save_token(refreshed.access_token, expires_at)
            _relay_token_to_web(refreshed.access_token, expires_at)
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
        token = store.get_token()
        connected = token is not None and token.expires_at > time.time()
        meta = store.get_token_meta() or {}
        return {
            "connected": connected,
            "expires_at": token.expires_at if connected else None,
            "scopes": meta.get("scopes", []),
            "username": meta.get("username", ""),
        }

    @app.post("/research/run")
    async def research_run(request: Request):
        data = await _body_or_form(request)
        if str(data.get("consent", "")) != "on":
            return error(400, "Tick the AI-sharing consent box before running research.")
        token = store.get_token()
        if not token or token.expires_at <= time.time():
            return error(401, "reconnect")
        if not _ai_configured():
            return error(503, "OPENROUTER_API_KEY is not set. Add it to the server secret store to analyze collected Threads text.")
        limits = SampleLimits.from_form(data)
        params = {**limits.as_dict(), "focus": _clean_focus(data.get("focus"))}
        if str(data.get("sync_graph", "")).lower() in ("on", "true", "1"):
            params["sync_graph"] = "on"
        if _wants_html(request):
            job = store.create_job("research", params)
            return RedirectResponse(f"/?view=research&notice=Research+queued+(job+%23{job['id']})", status_code=303)
        try:
            return _perform_research(params)
        except (ThreadsError, ResearchError, StoreError) as exc:
            return error(502, str(exc))

    @app.post("/research/keyword")
    async def research_keyword(request: Request):
        data = await _body_or_form(request)
        keyword = " ".join(str(data.get("keyword", "")).split())[:120]
        if not keyword:
            return RedirectResponse("/?view=research&notice=Enter+a+keyword+first", status_code=303) if _wants_html(request) else error(400, "Keyword is required.")
        mode = str(data.get("mode", "KEYWORD")).upper()
        if mode not in ("KEYWORD", "TAG"):
            mode = "KEYWORD"
        token = store.get_token()
        if not token or token.expires_at <= time.time():
            return RedirectResponse("/?view=research&notice=Connect+Threads+before+keyword+search", status_code=303) if _wants_html(request) else error(401, "reconnect")
        if not _ai_configured():
            return error(503, "AI provider key is not set.")
        params = {"query": keyword, "mode": mode, "limit": min(max(int(data.get("limit", 25) or 25), 5), 50)}
        if _wants_html(request):
            job = store.create_job("keyword_search", params)
            return RedirectResponse(f"/?view=research&notice=Keyword+search+queued+(job+%23{job['id']})", status_code=303)
        try:
            return _perform_keyword_search(params)
        except (ThreadsError, ResearchError, StoreError) as exc:
            return error(502, str(exc))

    @app.get("/research/runs")
    def research_runs(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        return {"runs": store.list_research_runs()}

    @app.get("/research/insights")
    def research_insights(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        return {"insights": store.list_insights()}

    @app.get("/audiences")
    def audiences(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        return {
            "audiences": build_audiences(
                store.list_insights(),
                store.list_drafts(),
                custom_segments=store.list_audience_segments(),
            )
        }

    @app.post("/audiences/segments")
    async def audiences_segment_save(request: Request):
        data = await _body_or_form(request)
        label = " ".join(str(data.get("label", "")).split())[:80]
        raw_kw = data.get("keywords", "")
        if isinstance(raw_kw, list):
            keywords = [str(k).strip() for k in raw_kw if str(k).strip()]
        else:
            keywords = [k.strip() for k in str(raw_kw).split(",") if k.strip()]
        if not label or not keywords:
            return RedirectResponse("/?view=audiences&notice=Provide+segment+label+and+keywords", status_code=303) if _wants_html(request) else error(400, "Label and keywords are required.")
        slug = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")[:48] or "segment"
        saved = store.upsert_audience_segment(
            slug=slug,
            label=label,
            description=" ".join(str(data.get("description", "")).split())[:200],
            keywords=keywords,
        )
        if _wants_html(request):
            return RedirectResponse(f"/?view=audiences&notice=Saved+segment+{quote(label)}", status_code=303)
        return {"segment": saved}

    @app.post("/audiences/segments/{slug}/delete")
    def audiences_segment_delete(request: Request, slug: str):
        deleted = store.delete_audience_segment(slug)
        if _wants_html(request):
            return RedirectResponse("/?view=audiences&notice=Segment+removed", status_code=303)
        return {"deleted": deleted}

    @app.get("/audiences/export.csv")
    def audiences_export(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(("audience_segment", "evidence_count", "themes", "quote", "source_url", "ebook_idea"))
        built = build_audiences(
            store.list_insights(),
            store.list_drafts(),
            custom_segments=store.list_audience_segments(),
        )
        for audience in built:
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
        is_html = _wants_html(request)
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
        updated = store.set_unfollow_status(raw_names, action)
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
        is_html = _wants_html(request)
        token = store.get_token()
        if not token or token.expires_at <= time.time():
            return follow_redirect("Connect Threads first before syncing from the Graph API.") if is_html else error(401, "reconnect")
        data = await _body_or_form(request)
        params = {
            "post_limit": min(max(int(data.get("post_limit", 25) or 25), 1), 50),
            "replies_per_post": min(max(int(data.get("replies_per_post", 50) or 50), 1), 100),
        }
        if str(data.get("queue", "")).lower() in ("on", "true", "1"):
            job = store.create_job("graph_sync", params)
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
        is_html = _wants_html(request)

        def fail(message: str, status: int = 400) -> Response:
            return follow_redirect(message) if is_html else error(status, message)

        try:
            parsed = await read_import(request)
        except UploadRejected as exc:
            return fail(str(exc), exc.status)
        except AudienceError as exc:
            return fail(str(exc))
        imported_at = store.save_audience(parsed["followers"], parsed["following"])
        if is_html:
            return follow_redirect(
                f"Imported {len(parsed['followers']):,} followers and {len(parsed['following']):,} following · {imported_at[:10]}"
            )
        return {"imported_at": imported_at, "followers": len(parsed["followers"]), "following": len(parsed["following"])}

    @app.post("/followers/clear")
    async def followers_clear(request: Request):
        cleared_import = store.clear_audience()
        cleared_graph = store.clear_graph_audience()
        cleared = bool(cleared_import or cleared_graph)
        if _wants_html(request):
            return follow_redirect("Follower import cleared" if cleared else "No follower import to clear")
        return {"cleared": cleared}

    @app.get("/inbox")
    def inbox_index(request: Request, status: str = "open"):
        if not signed_in(request):
            return error(401, "Sign in first.")
        return {"items": store.list_inbox_items(status="" if status == "all" else status)}

    @app.post("/inbox/sync")
    def inbox_sync(request: Request):
        is_html = _wants_html(request)
        token = store.get_token()
        if not token or token.expires_at <= time.time():
            return RedirectResponse("/?view=inbox&notice=Connect+Threads+before+syncing+replies", status_code=303) if is_html else error(401, "reconnect")
        try:
            client = ThreadsClient(settings, app.state.http)
            profile = client.fetch_profile(token.access_token)
            posts = client.fetch_my_posts(token.access_token, limit=15)
            replies = client.fetch_post_replies(token.access_token, posts, replies_per_post=40)
            added = _sync_inbox_from_replies(replies, str(profile.get("username", "")))
        except ThreadsError as exc:
            return RedirectResponse(f"/?view=inbox&notice={quote(str(exc))}", status_code=303) if is_html else error(502, str(exc))
        if is_html:
            return RedirectResponse(f"/?view=inbox&notice=Synced+{added}+reply+item{'' if added == 1 else 's'}", status_code=303)
        return {"synced": added}

    @app.post("/inbox/{item_id}/draft")
    def inbox_draft_reply(request: Request, item_id: int):
        is_html = _wants_html(request)
        item = store.get_inbox_item(item_id)
        if not item:
            return error(404, "Inbox item not found.")
        if not _ai_configured():
            return error(503, "AI provider key is not set.")
        try:
            reply_text = draft_reply(item["text"], item["username"], settings, app.state.http, options={"store": store})
            store.save_inbox_draft_reply(item_id, reply_text)
        except ResearchError as exc:
            return RedirectResponse(f"/?view=inbox&notice={quote(str(exc))}", status_code=303) if is_html else error(502, str(exc))
        if is_html:
            return RedirectResponse("/?view=inbox&notice=AI+reply+draft+ready", status_code=303)
        return {"id": item_id, "draft_reply": reply_text}

    @app.post("/inbox/{item_id}/reply")
    async def inbox_send_reply(request: Request, item_id: int):
        is_html = _wants_html(request)
        item = store.get_inbox_item(item_id)
        if not item:
            return error(404, "Inbox item not found.")
        data = await _body_or_form(request)
        reply_text = str(data.get("reply_text") or item.get("draft_reply") or "").strip()[:POST_TEXT_MAX]
        if not reply_text:
            return error(400, "Reply text cannot be empty.")
        token = store.get_token()
        if not token or token.expires_at <= time.time():
            return RedirectResponse("/?view=inbox&notice=Connect+Threads+before+replying", status_code=303) if is_html else error(401, "reconnect")
        try:
            res = ThreadsClient(settings, app.state.http).reply_to_post(
                token.access_token, reply_to_id=item["reply_id"], text=reply_text
            )
            store.mark_inbox_replied(item_id, reply_text)
        except ThreadsError as exc:
            return RedirectResponse(f"/?view=inbox&notice={quote(str(exc))}", status_code=303) if is_html else error(502, str(exc))
        if is_html:
            return RedirectResponse("/?view=inbox&notice=Reply+sent+on+Threads", status_code=303)
        return {"id": item_id, "published": res}

    @app.post("/inbox/{item_id}/hide")
    async def inbox_hide_reply(request: Request, item_id: int):
        is_html = _wants_html(request)
        item = store.get_inbox_item(item_id)
        if not item:
            return error(404, "Inbox item not found.")
        data = await _body_or_form(request)
        hide = str(data.get("hide", "true")).lower() in ("true", "1", "on", "yes")
        token = store.get_token()
        if not token or token.expires_at <= time.time():
            return RedirectResponse("/?view=inbox&notice=Connect+Threads+before+moderating", status_code=303) if is_html else error(401, "reconnect")
        try:
            ThreadsClient(settings, app.state.http).set_reply_visibility(
                token.access_token, reply_id=item["reply_id"], hide=hide
            )
            store.set_inbox_hidden(item_id, hide)
        except ThreadsError as exc:
            return RedirectResponse(f"/?view=inbox&notice={quote(str(exc))}", status_code=303) if is_html else error(502, str(exc))
        msg = "Reply+hidden+on+Threads" if hide else "Reply+restored+on+Threads"
        if is_html:
            return RedirectResponse(f"/?view=inbox&status=dismissed&notice={msg}" if hide else f"/?view=inbox&notice={msg}", status_code=303)
        return {"id": item_id, "hidden": hide}

    @app.get("/knowledge")
    def knowledge_index(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        ensure_default_knowledge(store)
        return {
            "nodes": store.list_knowledge_nodes(),
            "edges": store.list_knowledge_edges(),
            "fact_sheet": compile_fact_sheet(store),
        }

    @app.post("/knowledge/nodes")
    async def knowledge_upsert(request: Request):
        data = await _body_or_form(request)
        slug = re.sub(r"[^a-z0-9-]+", "-", str(data.get("slug", "")).strip().lower()).strip("-")[:64]
        title = " ".join(str(data.get("title", "")).split())[:140]
        body = str(data.get("body", "")).strip()[:4000]
        if not slug or not title or not body:
            return error(400, "Slug, title, and body are required.")
        node = store.upsert_knowledge_node(
            slug,
            title,
            body,
            meta={
                "category": " ".join(str(data.get("category", "brand")).split())[:40],
                "summary": " ".join(str(data.get("summary", "")).split())[:300],
                "links": extract_wiki_links(body),
            },
        )
        if _wants_html(request):
            return RedirectResponse(f"/?view=knowledge&notice=Saved+knowledge+note+{quote(slug)}", status_code=303)
        return {"node": node}

    @app.post("/knowledge/nodes/{slug}/delete")
    def knowledge_delete(request: Request, slug: str):
        deleted = store.delete_knowledge_node(slug)
        if _wants_html(request):
            return RedirectResponse("/?view=knowledge&notice=Knowledge+note+deleted", status_code=303)
        return {"deleted": deleted}

    @app.post("/content/generate")
    async def content_generate(request: Request):
        is_html = _wants_html(request)
        try:
            form = await request.form()
            raw_ids = form.getlist("insight_ids")
            consent = form.get("consent", "")
            kinds_raw = form.getlist("kinds")
            tone = form.get("tone", "empathetic")
            language = form.get("language", "match evidence")
        except Exception:
            body = await _body_or_form(request)
            raw_ids = body.get("insight_ids", [])
            consent = body.get("consent", "")
            kinds_raw = body.get("kinds", [])
            tone = body.get("tone", "empathetic")
            language = body.get("language", "match evidence")
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
        selected = store.get_insights_by_ids(ids)
        if len(selected) != len(ids):
            return error(400, "One or more selected insights are no longer available.")
        params = {
            "insight_ids": ids,
            "kinds": [kind for kind in DRAFT_KINDS if kind in kinds_raw] or list(DRAFT_KINDS),
            "tone": tone if tone in DRAFT_TONES else DRAFT_TONES[0],
            "language": language if language in DRAFT_LANGUAGES else DRAFT_LANGUAGES[0],
        }
        if is_html:
            job = store.create_job("drafts", params)
            return RedirectResponse(f"/?view=studio&notice=Drafts+queued+(job+%23{job['id']})", status_code=303)
        try:
            return _perform_drafts(params)
        except (ResearchError, StoreError) as exc:
            return error(502, str(exc))

    @app.post("/content/variants")
    async def content_variants(request: Request):
        is_html = _wants_html(request)
        if not _ai_configured():
            return error(503, "AI provider key is not set.")
        data = await _body_or_form(request)
        focus = _clean_focus(data.get("focus"))
        select_str = str(data.get("select", ""))
        selected_ids = [int(v) for v in select_str.split(",") if v.isdigit()][:10]
        selected = store.get_insights_by_ids(selected_ids) if selected_ids else store.list_insights(limit=6)
        if not selected:
            return error(400, "Collect research insights before generating variants.")
        used_ids = [int(i["id"]) for i in selected if i.get("id")]
        try:
            res = generate_variants(
                selected,
                settings,
                app.state.http,
                options={
                    "focus": focus,
                    "tone": str(data.get("tone", DRAFT_TONES[0])),
                    "language": str(data.get("language", DRAFT_LANGUAGES[0])),
                    "store": store,
                },
            )
            variants = res.get("variants", [])
            hooks = [str(v.get("angle", "")) for v in variants if v.get("angle")]
            primary_post = variants[0]["post"] if variants else ""
            saved = store.save_drafts(
                [{"kind": "threads_post", "title": variants[0].get("title", "Hook Lab Trio") if variants else "Hook Lab", "content": {"post": primary_post, "hooks": hooks}}],
                used_ids,
            )
            if saved:
                store.update_draft_variants(int(saved[0]["id"]), variants)
        except (ResearchError, StoreError) as exc:
            return RedirectResponse(f"/?view=studio&notice={quote(str(exc))}", status_code=303) if is_html else error(502, str(exc))
        if is_html:
            return RedirectResponse("/?view=library&notice=Saved+3+variants+with+Hook+Lab", status_code=303)
        return {"draft": store.get_draft(int(saved[0]["id"])) if saved else None, "variants": variants, "hooks": hooks}

    @app.post("/content/drafts/{draft_id}/star")
    def content_draft_star(request: Request, draft_id: int):
        starred = store.toggle_draft_star(draft_id)
        if starred is None:
            return error(404, "Draft not found.")
        if _wants_html(request):
            return RedirectResponse("/?view=library&notice=Updated+favorite", status_code=303)
        return {"id": draft_id, "starred": starred}

    @app.post("/content/drafts/{draft_id}/adjust")
    async def content_draft_adjust(request: Request, draft_id: int):
        is_html = _wants_html(request)
        draft = store.get_draft(draft_id)
        if not draft:
            return error(404, "Draft not found.")
        if not _ai_configured():
            return error(503, "AI provider key is not set.")
        data = await _body_or_form(request)
        modifier = str(data.get("modifier", "warmer")).strip()
        try:
            adjusted = adjust_draft_variant(draft, modifier, settings, app.state.http, store=store)
            store.update_draft_content(draft_id, title=adjusted["title"], content=adjusted["content"])
        except ResearchError as exc:
            return RedirectResponse(f"/?view=library&notice={quote(str(exc))}", status_code=303) if is_html else error(502, str(exc))
        if is_html:
            return RedirectResponse(f"/?view=library&notice=Rewrote+draft+({quote(modifier)})", status_code=303)
        return {"id": draft_id, "title": adjusted["title"], "content": adjusted["content"]}

    @app.post("/content/drafts/{draft_id}/schedule")
    async def content_draft_schedule(request: Request, draft_id: int):
        is_html = _wants_html(request)
        draft = store.get_draft(draft_id)
        if not draft:
            return error(404, "Draft not found.")
        data = await _body_or_form(request)
        raw_when = str(data.get("scheduled_at", "")).strip()
        if not raw_when:
            return error(400, "Provide scheduled_at timestamp.")
        norm = raw_when.replace(" ", "T")
        if len(norm) == 16:
            norm += ":00Z"
        elif not (norm.endswith("Z") or "+" in norm[10:]):
            norm += "Z"
        store.schedule_draft(draft_id, norm)
        if is_html:
            return RedirectResponse("/?view=calendar&notice=Draft+scheduled", status_code=303)
        return {"id": draft_id, "scheduled_at": norm}

    @app.post("/content/drafts/{draft_id}/status")
    async def content_draft_status(request: Request, draft_id: int):
        data = await _body_or_form(request)
        status = str(data.get("status", ""))
        if status not in ("draft", "approved", "scheduled", "published", "archived"):
            return error(400, "Status must be draft, approved, or archived.")
        if not store.update_draft_status(draft_id, status):
            return error(404, "Draft not found.")
        if _wants_html(request):
            return RedirectResponse("/?view=library&notice=Draft+status+updated", status_code=303)
        return {"id": draft_id, "status": status}

    @app.post("/content/drafts/{draft_id}/edit")
    async def content_draft_edit(request: Request, draft_id: int):
        is_html = _wants_html(request)
        draft = store.get_draft(draft_id)
        if not draft:
            return error(404, "Draft not found.")
        chapter_titles: list[str] = []
        chapter_outcomes: list[str] = []
        ctype = request.headers.get("content-type", "").lower()
        if "application/json" in ctype:
            data = await _body_or_form(request)
        else:
            try:
                form = await request.form()
                data = dict(form)
                chapter_titles = [str(v) for v in form.getlist("chapter_title")]
                chapter_outcomes = [str(v) for v in form.getlist("chapter_outcome")]
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
            if chapter_titles or chapter_outcomes:
                content["chapters"] = [
                    {"title": t.strip()[:160], "outcome": (chapter_outcomes[idx] if idx < len(chapter_outcomes) else "").strip()[:400]}
                    for idx, t in enumerate(chapter_titles)
                    if t.strip()
                ]
        elif draft["kind"] == "design_brief":
            for field_name in ("concept", "format", "visual_direction", "copy"):
                if field_name in data:
                    content[field_name] = str(data.get(field_name, "")).strip()[:2000]
        store.update_draft_content(draft_id, title=title, content=content)
        if is_html:
            return RedirectResponse("/?view=library&notice=Draft+updated", status_code=303)
        return {"id": draft_id, "title": title, "content": content}

    @app.post("/content/drafts/{draft_id}/publish")
    async def content_draft_publish(request: Request, draft_id: int):
        is_html = _wants_html(request)
        draft = store.get_draft(draft_id)
        if not draft:
            return error(404, "Draft not found.")
        content = dict(draft["content"])
        data = await _body_or_form(request)
        as_thread = str(data.get("as_thread", "")).lower() in ("on", "true", "1")
        err_msg = (
            "Only Threads post drafts can be published to Threads." if draft["kind"] != "threads_post" and not as_thread
            else "This draft has already been published to Threads." if content.get("published") or draft["status"] == "published"
            else "Approve the draft before publishing to Threads." if draft["status"] not in ("approved", "scheduled")
            else ""
        )
        if err_msg:
            return error(400, err_msg)
        token = store.get_token()
        if not token or token.expires_at <= time.time():
            return RedirectResponse("/?view=library&notice=Connect+Threads+before+publishing", status_code=303) if is_html else error(401, "reconnect")
        post_text = str(content.get("post", "")).strip()
        try:
            client = ThreadsClient(settings, app.state.http)
            if as_thread:
                raw_parts = data.get("posts")
                if isinstance(raw_parts, list) and raw_parts:
                    parts = [str(p).strip() for p in raw_parts if str(p).strip()]
                elif "\n---\n" in post_text:
                    parts = [p.strip() for p in post_text.split("\n---\n") if p.strip()]
                else:
                    parts = [p.strip() for p in post_text.split("\n\n") if p.strip()] or [post_text]
                res = client.publish_thread(token.access_token, parts)
                published = res[0] if res else {"id": "", "permalink": ""}
            else:
                published = client.publish_post(token.access_token, post_text)
        except ThreadsError as exc:
            return RedirectResponse(f"/?view=library&notice={quote(str(exc))}", status_code=303) if is_html else error(502, str(exc))
        pub_meta = {
            "id": published["id"],
            "url": published.get("permalink", ""),
            "published_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        content["published"] = pub_meta
        store.update_draft_content(draft_id, title=draft["title"], content=content)
        store.mark_draft_published(draft_id, post_id=published["id"], permalink=published.get("permalink", ""))
        return RedirectResponse("/?view=library&notice=Published+to+Threads", status_code=303) if is_html else {"id": draft_id, "published": pub_meta}

    @app.get("/content/drafts/{draft_id}/card.html", response_class=HTMLResponse)
    def content_draft_card_html(request: Request, draft_id: int):
        if not signed_in(request):
            return error(401, "Sign in first.")
        draft = store.get_draft(draft_id)
        if not draft:
            return error(404, "Draft not found.")
        style = request.query_params.get("style", "quote-card")
        rendered = render_quote_card_html(draft, style=style)
        store.update_draft_visual(draft_id, rendered)
        return HTMLResponse(rendered)

    @app.get("/content/drafts/{draft_id}/ebook.md")
    def content_draft_ebook_md(request: Request, draft_id: int):
        if not signed_in(request):
            return error(401, "Sign in first.")
        draft = store.get_draft(draft_id)
        if not draft:
            return error(404, "Draft not found.")
        insights = store.get_insights_by_ids(draft.get("source_ids", []))
        md = draft_to_ebook_markdown(draft, insights=insights)
        return Response(
            md,
            media_type="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename=draft-{draft_id}.md"},
        )

    @app.get("/content/export/publish-pack")
    def content_publish_pack(request: Request, format: str = "md"):
        if not signed_in(request):
            return error(401, "Sign in first.")
        insights_map = {int(i["id"]): i for i in store.list_insights() if i.get("id")}
        md, ics = build_publish_pack(store.list_drafts(), insights_by_id=insights_map)
        if format == "ics":
            return Response(
                ics,
                media_type="text/calendar; charset=utf-8",
                headers={"Content-Disposition": "attachment; filename=perpustakaan-hati-schedule.ics"},
            )
        return Response(
            md,
            media_type="text/markdown; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=perpustakaan-hati-publish-pack.md"},
        )

    @app.get("/content/drafts")
    def content_drafts(request: Request, status: str = ""):
        if not signed_in(request):
            return error(401, "Sign in first.")
        return {"drafts": store.list_drafts(status=status)}

    @app.get("/queue")
    def queue_status(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        return {"jobs": store.list_jobs()}

    @app.get("/queue/stream")
    async def queue_stream(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")

        async def _events():
            for _ in range(20):
                jobs = store.list_jobs(limit=15)
                yield f"data: {json.dumps({'jobs': jobs})}\n\n"
                if not any(j["status"] in ("queued", "running") for j in jobs):
                    break
                await asyncio.sleep(0.5)
            yield "event: done\ndata: {}\n\n"

        return StreamingResponse(_events(), media_type="text/event-stream")

    @app.post("/queue/clear")
    def queue_clear(request: Request):
        cleared = store.clear_queued_jobs()
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

    @app.get("/mini", response_class=HTMLResponse)
    def mini_app_view(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        csrf = request.cookies.get(CSRF_COOKIE) or secrets.token_urlsafe(24)
        drafts = [d for d in store.list_drafts(limit=20) if d["status"] in ("draft", "approved", "scheduled")]
        cards = "".join(
            f"<article style='background:{RAISED};border:1px solid #24402f;border-radius:12px;padding:14px;margin-bottom:12px'>"
            f"<div style='font-size:12px;color:#e9cea2'>{html_module.escape(d['kind'])} · {html_module.escape(d['status'])}</div>"
            f"<h3 style='margin:6px 0'>{html_module.escape(d['title'])}</h3>"
            f"<p style='font-size:14px;color:#a9b2a6'>{html_module.escape(str((d.get('content') or {}).get('post', (d.get('content') or {}).get('premise', '')))[:220])}</p>"
            f"<form method=post action=/content/drafts/{int(d['id'])}/status style='display:inline'>"
            f"<input type=hidden name=csrf value='{html_module.escape(csrf, quote=True)}'><input type=hidden name=status value=approved>"
            f"<button style='padding:8px 14px;border-radius:999px;border:0;background:#5b9b7d;color:#07140d'>Approve</button></form></article>"
            for d in drafts[:10]
        ) or "<p>No pending drafts.</p>"
        return HTMLResponse(
            f"<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
            f"<title>PH Mini Studio</title><meta name=color-scheme content=dark></head><body style='margin:0;padding:16px;background:{VOID};color:#e6e2da;font-family:Inter,system-ui,sans-serif'>"
            f"<h1 style='margin:0 0 12px'>Perpustakaan Hati · Mini Review</h1>{cards}</body></html>"
        )

    @app.post("/watchlist/config")
    async def watchlist_config(request: Request):
        data = await _body_or_form(request)
        raw_kw = data.get("keywords", "")
        if isinstance(raw_kw, list):
            keywords = [str(k).strip() for k in raw_kw if str(k).strip()]
        else:
            keywords = [k.strip() for k in str(raw_kw).split(",") if k.strip()]
        saved = store.save_watchlist_config(
            enabled=str(data.get("enabled", "")).lower() in ("on", "true", "1"),
            interval_hours=int(data.get("interval_hours", 24) or 24),
            keywords=keywords,
            focus=_clean_focus(data.get("focus")),
        )
        if _wants_html(request):
            return RedirectResponse("/?view=settings&notice=Watchlist+configuration+saved", status_code=303)
        return {"watchlist": saved}

    @app.post("/watchlist/run")
    def watchlist_run(request: Request):
        wl = store.get_watchlist_config()
        params = {"keywords": wl.get("keywords", []), "focus": wl.get("focus", "")}
        if _wants_html(request):
            job = store.create_job("watchlist", params)
            return RedirectResponse(f"/?view=settings&notice=Watchlist+run+queued+(job+%23{job['id']})", status_code=303)
        try:
            return _perform_watchlist(params)
        except (ThreadsError, ResearchError, StoreError) as exc:
            return error(502, str(exc))

    @app.post("/telegram/test")
    def telegram_test(request: Request):
        recent_insights = store.list_insights(limit=3)
        recent_drafts = store.list_drafts(limit=2)
        lines = [f"Insights: {len(recent_insights)}, Recent drafts: {len(recent_drafts)}"]
        lines.extend(f"- {i.get('theme', '')}: {str(i.get('quote', ''))[:80]}" for i in recent_insights)
        base = settings.redirect_uri.rsplit("/auth/callback", 1)[0] if "/auth/callback" in settings.redirect_uri else ""
        msg = format_digest_html(
            title="Perpustakaan Hati Research Alert",
            lines=lines,
            permalink=f"{base}/?view=overview" if base else "",
        )
        kb = build_draft_keyboard(recent_drafts[0], mini_app_url=settings.mini_app_url) if recent_drafts else None
        res = send_telegram_alert(
            settings,
            store,
            app.state.http,
            msg,
            options={"dedupe_key": f"test:{int(time.time() // 5)}", "reply_markup": kb},
        )
        if _wants_html(request):
            status = "sent" if res.get("ok") else str(res.get("reason", "skipped"))
            return RedirectResponse(f"/?view=settings&notice=Telegram+test%3A+{quote(status)}", status_code=303)
        return res

    @app.get("/backups/latest.db")
    def backup_download(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        backup_path = store.backup_database()
        return FileResponse(backup_path, media_type="application/octet-stream", filename=backup_path.name)

    @app.get("/webhooks/threads")
    def threads_webhook_verify(request: Request):
        mode = request.query_params.get("hub.mode", "")
        token = request.query_params.get("hub.verify_token", "")
        challenge = request.query_params.get("hub.challenge", "")
        if (
            mode == "subscribe"
            and settings.threads_webhook_verify_token
            and hmac.compare_digest(token, settings.threads_webhook_verify_token)
        ):
            return Response(challenge, media_type="text/plain")
        return error(403, "Webhook verification failed.")

    @app.post("/webhooks/threads")
    async def threads_webhook_ingest(request: Request):
        raw = await request.body()
        sig = request.headers.get("x-hub-signature-256", "")
        if not settings.threads_app_secret or not verify_webhook_signature(settings.threads_app_secret, raw, sig):
            return error(401, "Invalid webhook signature.")
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return error(400, "Invalid JSON payload.")
        items = []
        for entry in payload.get("entry", []) if isinstance(payload, dict) else []:
            for change in entry.get("changes", []) if isinstance(entry, dict) else []:
                val = change.get("value") if isinstance(change, dict) else None
                if isinstance(val, dict) and val.get("id") and val.get("text"):
                    items.append({
                        "reply_id": str(val["id"]),
                        "post_id": str(val.get("root_post_id") or val.get("replied_to", {}).get("id", "")),
                        "post_permalink": str(val.get("permalink", "")),
                        "username": str(val.get("username") or "").lstrip("@"),
                        "text": str(val["text"]),
                        "created_at": str(val.get("timestamp", "")),
                    })
        ingested = store.upsert_inbox_items(items) if items else 0
        return {"ok": True, "ingested": ingested}

    @app.post("/internal/ingest/web-signals")
    async def internal_ingest_web_signals(request: Request):
        raw = await request.body()
        rejected = _verify_sync_hmac(request, raw)
        if rejected:
            return rejected
        try:
            body = json.loads(raw.decode("utf-8")) if raw else {}
        except json.JSONDecodeError:
            return error(400, "Invalid JSON body.")
        source = str(body.get("source", "web")).strip() or "web"
        signals = body.get("signals", [])
        if not isinstance(signals, list):
            return error(400, "signals must be a list.")
        count = store.ingest_external_signals(source, signals)
        return {"ok": True, "ingested": count}

    @app.get("/internal/status")
    def internal_status(request: Request):
        rejected = _verify_sync_hmac(request, b"")
        if rejected:
            return rejected
        token = store.get_token()
        connected = token is not None and token.expires_at > time.time()
        all_drafts = store.list_drafts(limit=500)
        return {
            "ok": True,
            "insights_count": len(store.list_insights(limit=500)),
            "drafts_count": len(all_drafts),
            "published_count": sum(1 for d in all_drafts if d.get("status") == "published"),
            "token_connected": connected,
            "token_expires_at": token.expires_at if connected else None,
        }

    @app.get("/healthz")
    def healthz():
        hc = store.health_check()
        if not hc.get("ok"):
            return JSONResponse({"ok": False, "error": hc.get("error", "unhealthy")}, status_code=503)
        return {"ok": True}

    @app.get("/healthz/details")
    def healthz_details(request: Request):
        if not signed_in(request):
            return error(401, "Sign in first.")
        backup = store.latest_backup_path()
        return {
            "db": store.health_check(),
            "ai_summary": store.ai_usage_summary(),
            "jobs": store.list_jobs(limit=10),
            "latest_backup": str(backup) if backup else "",
        }

    return app
