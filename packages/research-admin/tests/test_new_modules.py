"""Tests for Phase 1-6 new modules, store upgrades, and API routes."""

import hashlib
import hmac
import json
import sqlite3
import time

import httpx
import respx
from fastapi.testclient import TestClient

from research_admin.ai_client import GROQ_URL, OPENROUTER_URL, complete_json, strip_em_dashes_deep
from research_admin.app import create_app
from research_admin.cards import build_publish_pack, draft_to_ebook_markdown, render_quote_card_html
from research_admin.config import Settings
from research_admin.discovery import (
    AUTOCOMPLETE_URL,
    expand_google_autocomplete,
    sanitize_source_text,
    score_posts,
)
from research_admin.knowledge import compile_fact_sheet, ensure_default_knowledge, extract_wiki_links
from research_admin.store import Store
from research_admin.telegram_ops import (
    build_draft_keyboard,
    callback_id,
    send_telegram_alert,
    split_telegram_message,
)

GRAPH = "https://graph.threads.com"


class MemoryVault:
    def __init__(self, initial: str | None = None):
        self.value = initial

    def get(self):
        return self.value

    def set(self, v):
        self.value = v

    def delete(self):
        self.value = None


def login(client):
    response = client.post("/login", data={"password": "admin-pass"}, follow_redirects=False)
    assert response.status_code == 303


def make_app(tmp_path, *, connected=True, **overrides):
    settings = _settings(tmp_path, **overrides)
    app = create_app(settings, vault_factory=lambda: MemoryVault("stored-token" if connected else None))
    app.state.store.init_schema()
    if connected:
        app.state.store.save_token("stored-token", int(time.time()) + 5000)
    return TestClient(app, base_url="http://testserver", headers={"Origin": "http://testserver"})


def _settings(tmp_path, **overrides) -> Settings:
    base = {
        "threads_client_id": "client-id",
        "threads_client_secret": "client-secret",
        "redirect_uri": "http://testserver/auth/callback",
        "openrouter_api_key": "or-key",
        "openrouter_model": "openai/gpt-6-luna",
        "admin_password": "admin-pass",
        "db_path": str(tmp_path / "research.db"),
        "secure_cookies": False,
        "allowed_hosts": ("testserver", "localhost", "127.0.0.1"),
    }
    base.update(overrides)
    return Settings(**base)


@respx.mock
def test_ai_client_failover_openrouter_to_groq_and_telemetry(tmp_path):
    store = Store(str(tmp_path / "research.db"), vault=MemoryVault())
    store.init_schema()
    settings = _settings(tmp_path, groq_api_key="groq-key", ai_provider_priority=("openrouter", "groq"))
    respx.post(OPENROUTER_URL).respond(429, json={"error": "rate limit"})
    respx.post(GROQ_URL).respond(
        200,
        json={
            "choices": [{"message": {"content": json.dumps({"insights": [{"quote": "quiet — pause"}]})}}],
            "usage": {"prompt_tokens": 11, "completion_tokens": 7},
        },
    )
    with httpx.Client() as http:
        parsed, meta = complete_json(
            settings,
            http,
            ("sys", "usr"),
            {"list_key": "insights", "operation": "test_op", "store": store},
        )
    assert meta["provider"] == "groq"
    assert parsed["insights"][0]["quote"] == "quiet — pause"
    cleaned = strip_em_dashes_deep(parsed)
    assert cleaned["insights"][0]["quote"] == "quiet , pause"
    summary = store.ai_usage_summary()
    providers = {row["provider"]: row for row in summary["by_provider"]}
    assert providers["openrouter"]["calls"] == 1
    assert providers["openrouter"]["ok_calls"] == 0
    assert providers["groq"]["calls"] == 1
    assert providers["groq"]["ok_calls"] == 1


@respx.mock
def test_discovery_autocomplete_sanitizer_and_outlier_scoring():
    respx.get(AUTOCOMPLETE_URL).respond(
        200,
        json=[
            "tenang hati",
            [
                "cara tenang hati bila overthinking",
                "tenang hati dalam islam",
                "diagnose medication bipolar",
            ],
        ],
    )
    with httpx.Client() as http:
        results = expand_google_autocomplete("tenang hati", http, suffixes=("", "dalam islam"))
    assert len(results) >= 2
    by_q = {item["query"]: item for item in results}
    assert by_q["cara tenang hati bila overthinking"]["opportunity_score"] > by_q["diagnose medication bipolar"]["opportunity_score"]

    assert sanitize_source_text("short")[0] is False
    assert sanitize_source_text("foo foo foo foo foo foo")[0] is False
    assert sanitize_source_text("https://a.co https://b.co https://c.co")[0] is False
    ok, clean, _ = sanitize_source_text("  Kadang rasa sunyi walaupun ramai orang.  ")
    assert ok is True and clean == "Kadang rasa sunyi walaupun ramai orang."

    scored = score_posts([
        {"id": "p1", "timestamp": "2026-05-01T13:00:00Z", "metrics": {"views": 1000, "likes": 100, "replies": 20, "reposts": 5, "quotes": 2}},
        {"id": "p2", "timestamp": "2026-05-01T01:00:00Z", "metrics": {"views": 1000, "likes": 5, "replies": 0, "reposts": 0, "quotes": 0}},
        {"id": "p3", "timestamp": "2026-05-01T02:00:00Z", "metrics": {"views": 1000, "likes": 4, "replies": 1, "reposts": 0, "quotes": 0}},
    ])
    assert scored["posts"][0]["id"] == "p1"
    assert scored["posts"][0]["is_outlier"] is True
    assert scored["best_hours"][0]["label"] == "21:00 MYT"


def test_knowledge_graph_links_and_fact_sheet(tmp_path):
    store = Store(str(tmp_path / "research.db"), vault=MemoryVault())
    store.init_schema()
    ensure_default_knowledge(store)
    nodes = store.list_knowledge_nodes()
    assert len(nodes) >= 4
    edges = store.list_knowledge_edges()
    assert any(edge["target_slug"] == "guardrails-no-diagnosis" for edge in edges)
    assert extract_wiki_links("See [[Brand Voice]] and [[Custom-Node]]") == ["brand-voice", "custom-node"]
    sheet = compile_fact_sheet(store)
    assert "Editorial Guardrails" in sheet


def test_cards_ebook_markdown_and_publish_pack():
    draft = {
        "id": 7,
        "kind": "ebook_outline",
        "title": "Tenang Selepas Hujan",
        "status": "scheduled",
        "scheduled_at": "2026-06-01T12:00:00Z",
        "source_ids": [1],
        "content": {
            "premise": "Step-by-step reflection for tired hearts.",
            "intended_reader_need": "Calm boundaries.",
            "chapters": [{"title": "Bab 1: Nafas", "outcome": "Slow down"}],
        },
    }
    html_doc = render_quote_card_html(draft, style="quote-card-b", handle="rahimam")
    assert "@rahimam" in html_doc
    assert "Tenang Selepas Hujan" in html_doc
    md = draft_to_ebook_markdown(draft, insights=[{"id": 1, "quote": "Rasa penat", "source_url": "https://www.threads.com/@u/post/1"}])
    assert "# Tenang Selepas Hujan" in md
    assert "Bab 1: Nafas" in md
    pack_md, pack_ics = build_publish_pack([draft])
    assert "Tenang Selepas Hujan" in pack_md
    assert "BEGIN:VCALENDAR" in pack_ics and "BEGIN:VEVENT" in pack_ics


@respx.mock
def test_telegram_ops_formatting_limits_and_dedupe(tmp_path):
    store = Store(str(tmp_path / "research.db"), vault=MemoryVault())
    store.init_schema()
    assert len(callback_id("approve", "x" * 100).encode("utf-8")) <= 64
    chunks = split_telegram_message("word " * 1200)
    assert len(chunks) >= 2 and all(len(c) <= 4096 for c in chunks)
    kb = build_draft_keyboard({"id": 5, "content": {"post": "Gentle note"}}, mini_app_url="https://example.up.railway.app")
    assert kb["inline_keyboard"][0][0]["copy_text"]["text"] == "Gentle note"

    settings = _settings(tmp_path, telegram_bot_token="bot-token", telegram_chat_id="12345")
    respx.post("https://api.telegram.org/botbot-token/sendMessage").respond(200, json={"ok": True, "result": {"message_id": 1}})
    with httpx.Client() as http:
        first = send_telegram_alert(settings, store, http, "<b>Alert</b>", {"dedupe_key": "k1"})
        second = send_telegram_alert(settings, store, http, "<b>Alert</b>", {"dedupe_key": "k1"})
    assert first["ok"] is True
    assert second["skipped"] is True and second["reason"] == "dedupe_suppressed"


def test_store_wal_backup_compaction_and_persistent_lockout(tmp_path):
    store = Store(str(tmp_path / "research.db"), vault=MemoryVault())
    store.init_schema()
    assert store.health_check()["journal_mode"] == "wal"
    backup = store.backup_database()
    assert backup.is_file()
    assert store.latest_backup_path() == backup
    with sqlite3.connect(backup) as bdb:
        tables = {row[0] for row in bdb.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"insights", "content_drafts", "knowledge_nodes", "engagement_inbox"}.issubset(tables)

    job = store.create_job("research", {"focus": "test"})
    store.claim_job()
    store.finish_job(job["id"], {"summary": "ok", "insights": [{"quote": "q" * 5000} for _ in range(5)]})
    listed = next(j for j in store.list_jobs() if j["id"] == job["id"])
    assert listed["status"] == "done"

    # Rate lockout persists across app restart (new create_app sharing same DB)
    c1 = make_app(tmp_path)
    for _ in range(5):
        assert c1.post("/login", data={"password": "wrong"}).status_code == 401
    c2 = make_app(tmp_path)
    assert c2.post("/login", data={"password": "admin-pass"}).status_code == 429


@respx.mock
def test_app_assets_health_discovery_inbox_webhooks_knowledge_and_studio(tmp_path):
    respx.get(GRAPH + "/v1.0/me").respond(200, json={"id": "me-1", "username": "rahimam"})
    c = make_app(tmp_path)
    login(c)
    assert c.get("/healthz").json() == {"ok": True}
    assert c.get("/assets/fonts/InterUI.woff2").status_code == 200
    assert c.get("/assets/fonts/evil.txt").status_code == 404
    assert c.get("/favicon.ico").status_code == 200
    assert c.get("/healthz/details").json()["db"]["ok"] is True

    # Knowledge Graph & Segments CRUD
    k_res = c.post("/knowledge/nodes", json={"slug": "story-senja", "title": "Senja", "summary": "Quiet", "body": "Links [[brand-voice-malaysia]]"})
    assert k_res.status_code == 200
    assert c.get("/knowledge").json()["fact_sheet"]
    seg_res = c.post("/audiences/segments", json={"label": "Midnight Calm", "keywords": "ramai, sunyi"})
    assert seg_res.status_code == 200

    # Keyword Search Research
    respx.get(GRAPH + "/v1.0/keyword_search").respond(
        200,
        json={"data": [{"id": "kw-1", "text": "Kadang rasa sunyi walau ramai", "username": "ali", "permalink": "https://www.threads.com/@ali/post/KW1", "timestamp": "2026-05-01T12:00:00Z"}]},
    )
    respx.post(OPENROUTER_URL).respond(
        200,
        json={"choices": [{"message": {"content": json.dumps({"insights": [{"theme": "Loneliness", "quote": "Kadang rasa sunyi walau ramai", "source_url": "https://www.threads.com/@ali/post/KW1", "ebook_idea": "Quiet company"}]})}}]},
    )
    kw_run = c.post("/research/keyword", json={"keyword": "sunyi", "mode": "KEYWORD"})
    assert kw_run.status_code == 200
    assert kw_run.json()["insights_count"] == 1
    assert any(a["name"] == "Midnight Calm" for a in c.get("/audiences").json()["audiences"])

    # Webhook verification + signed reply ingestion + Inbox draft/reply/hide
    s = _settings(tmp_path, threads_webhook_verify_token="verify-tok", threads_app_secret="app-sec", sync_secret="sync-sec")
    w_app = create_app(s, vault_factory=MemoryVault)
    w_app.state.store.init_schema()
    wc = TestClient(w_app, base_url="http://testserver", headers={"Origin": "http://testserver"})
    login(wc)
    assert wc.get("/webhooks/threads?hub.mode=subscribe&hub.verify_token=verify-tok&hub.challenge=12345").text == "12345"
    assert wc.get("/webhooks/threads?hub.mode=subscribe&hub.verify_token=bad&hub.challenge=12345").status_code == 403

    hook_payload = json.dumps({
        "entry": [{"changes": [{"value": {"id": "rep-1", "root_post_id": "p-1", "username": "amina", "text": "Terima kasih atas kata-kata ini"}}]}]
    }).encode("utf-8")
    good_sig = "sha256=" + hmac.new(b"app-sec", hook_payload, hashlib.sha256).hexdigest()
    assert wc.post("/webhooks/threads", content=hook_payload, headers={"x-hub-signature-256": "sha256=bad"}).status_code == 401
    hook_ok = wc.post("/webhooks/threads", content=hook_payload, headers={"x-hub-signature-256": good_sig})
    assert hook_ok.json() == {"ok": True, "ingested": 1}

    wc.app.state.store.save_token("tok", int(time.time()) + 3600)
    inbox_items = wc.get("/inbox").json()["items"]
    assert len(inbox_items) == 1
    item_id = inbox_items[0]["id"]
    respx.post(OPENROUTER_URL).respond(200, json={"choices": [{"message": {"content": json.dumps({"replies": [{"text": "Sama-sama, semoga hati sentiasa tenang."}]})}}]})
    assert wc.post(f"/inbox/{item_id}/draft").status_code == 200
    respx.post(GRAPH + "/v1.0/me/threads").respond(200, json={"id": "rc-1"})
    respx.post(GRAPH + "/v1.0/me/threads_publish").respond(200, json={"id": "rp-1"})
    respx.get(GRAPH + "/v1.0/rp-1").respond(200, json={"id": "rp-1", "permalink": "https://www.threads.com/@rahimam/post/RP1"})
    assert wc.post(f"/inbox/{item_id}/reply", json={"reply_text": "Terima kasih kembali!"}).status_code == 200
    respx.post(GRAPH + "/v1.0/rep-1/manage_reply").respond(200, json={"success": True})
    assert wc.post(f"/inbox/{item_id}/hide", json={"hide": True}).json()["hidden"] is True

    # Signed /internal/* contract
    assert wc.get("/internal/status").status_code == 401
    status_sig = "sha256=" + hmac.new(b"sync-sec", b"", hashlib.sha256).hexdigest()
    st_res = wc.get("/internal/status", headers={"X-Research-Signature": status_sig})
    assert st_res.status_code == 200 and st_res.json()["token_connected"] is True
    sig_body = json.dumps({"source": "web", "signals": [{"id": "sig-1", "theme": "Calm", "quote": "Rasa lebih tenang malam ini"}]}).encode("utf-8")
    in_sig = "sha256=" + hmac.new(b"sync-sec", sig_body, hashlib.sha256).hexdigest()
    assert wc.post("/internal/ingest/web-signals", content=sig_body, headers={"X-Research-Signature": in_sig}).json() == {"ok": True, "ingested": 1}

    # Studio 2.0: variants, star, adjust, schedule, publish as thread, card/md/ics, queue stream, backup, mini
    wc.app.state.store.save_insights([{"theme": "Calm", "quote": "Nafas tenang", "source_url": "https://www.threads.com/@a/post/1", "ebook_idea": "Nafas"}])
    respx.post(OPENROUTER_URL).respond(
        200,
        json={"choices": [{"message": {"content": json.dumps({
            "variants": [
                {"style": "short", "title": "Letting Go", "angle": "Contrarian", "post": "Post satu.\n---\nPost dua."},
                {"style": "story", "title": "Cerita Hujan", "angle": "Storytelling", "post": "Cerita pendek."},
                {"style": "carousel", "title": "Slide Tenang", "angle": "Question", "post": "Slide 1"},
            ],
        })}}]},
    )
    var_res = wc.post("/content/variants", json={"focus": "letting go"})
    assert var_res.status_code == 200 and len(var_res.json()["variants"]) == 3
    did = var_res.json()["draft"]["id"]
    assert wc.post(f"/content/drafts/{did}/star").json()["starred"] is True
    respx.post(OPENROUTER_URL).respond(200, json={"choices": [{"message": {"content": json.dumps({"drafts": [{"title": "Letting Go Warm", "content": {"post": "Part one.\n---\nPart two."}}]})}}]})
    assert "Part one" in wc.post(f"/content/drafts/{did}/adjust", json={"modifier": "warmer"}).json()["content"]["post"]
    assert wc.post(f"/content/drafts/{did}/schedule", json={"scheduled_at": "2026-06-01T12:00"}).status_code == 200

    respx.post(GRAPH + "/v1.0/me/threads").respond(200, json={"id": "c-t1"})
    respx.post(GRAPH + "/v1.0/me/threads_publish").respond(200, json={"id": "p-t1"})
    respx.get(GRAPH + "/v1.0/p-t1").respond(200, json={"id": "p-t1", "permalink": "https://www.threads.com/@rahimam/post/PT1"})
    pub_thread = wc.post(f"/content/drafts/{did}/publish", json={"as_thread": True})
    assert pub_thread.status_code == 200

    assert "@rahimam" in wc.get(f"/content/drafts/{did}/card.html").text
    assert wc.get(f"/content/drafts/{did}/ebook.md").status_code == 200
    assert "BEGIN:VCALENDAR" in wc.get("/content/export/publish-pack?format=ics").text
    assert "event: done" in wc.get("/queue/stream").text
    assert wc.get("/mini").status_code == 200
    assert wc.get("/backups/latest.db").status_code == 200

    respx.get(AUTOCOMPLETE_URL).respond(200, json=["tenang", ["tenang hati", "tenang sebelum tidur"]])
    assert "tenang sebelum tidur" in wc.get("/?view=research&ac=tenang").text
    wl = wc.post("/watchlist/config", json={"enabled": True, "interval_hours": 12, "keywords": ["tenang", "redha"], "focus": "sleep"})
    assert wl.status_code == 200 and wl.json()["watchlist"]["interval_hours"] == 12
    assert wc.post("/telegram/test").json()["reason"] == "telegram_unconfigured"
