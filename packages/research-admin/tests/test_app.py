import json
import re
import sqlite3
import time
from unittest.mock import patch

import pytest
import respx
from fastapi.testclient import TestClient

from research_admin.app import create_app
from research_admin.config import Settings

GRAPH = "https://graph.threads.com"
OPENROUTER = "https://openrouter.ai/api/v1/chat/completions"
NOW = int(time.time())


def make_app(tmp_path, *, connected=True, password="admin-pass", base_url="http://testserver", **overrides):
    settings = Settings(
        threads_client_id="id", threads_client_secret="sec", openrouter_api_key="key",
        admin_password=password, db_path=str(tmp_path / "research.db"), **overrides)
    class MemoryVault:
        def __init__(self): self.value = "stored-token" if connected else None
        def get(self): return self.value
        def set(self, v): self.value = v
        def delete(self): self.value = None
    app = create_app(settings, vault_factory=lambda: MemoryVault())
    app.state.store.init_schema()
    if connected:
        app.state.store.save_token("stored-token", NOW + 5000)
    client = TestClient(app, base_url=base_url, headers={"Origin": base_url})
    return client


def login(client):
    response = client.post("/login", data={"password": "admin-pass"}, follow_redirects=False)
    assert response.status_code == 303


@pytest.fixture
def client(tmp_path):
    c = make_app(tmp_path)
    login(c)
    return c


def make_anon(tmp_path):
    return make_app(tmp_path)


def test_status_shows_connection_state(client):
    body = client.get("/auth/status").json()
    assert body["connected"] is True
    assert body["expires_at"] > NOW


def test_protected_routes_require_password(tmp_path):
    anon = make_app(tmp_path)
    assert anon.get("/auth/status").status_code == 401
    assert anon.get("/").status_code == 401
    assert anon.post("/research/run").status_code == 401
    assert anon.post("/logout").status_code == 401


def test_bad_password_rejected(tmp_path):
    c = make_app(tmp_path)
    response = c.post("/login", data={"password": "wrong"})
    assert response.status_code == 401


def test_missing_admin_password_locks_everything(tmp_path):
    settings = Settings(db_path=str(tmp_path / "research.db"))
    app = create_app(settings)
    app.state.store.init_schema()
    with TestClient(app) as c:
        assert c.get("/auth/status").status_code == 503
        assert c.get("/login").status_code == 503


def test_unconfigured_threads_shows_missing(tmp_path):
    c = make_app(tmp_path)
    login(c)
    c.app.state.settings.threads_client_id = ""
    c.app.state.settings.threads_client_secret = ""
    response = c.get("/auth/start", follow_redirects=False)
    assert response.status_code == 503
    assert response.json()["missing"] == ["THREADS_CLIENT_ID", "THREADS_CLIENT_SECRET"]


def test_login_page_has_no_password_and_logout_needs_post(client):
    assert "admin-pass" not in client.get("/login").text
    body = client.get("/").text
    assert 'method=post' in body and "/logout" in body
    response = client.post("/logout", follow_redirects=False)
    assert response.status_code == 303
    assert client.get("/auth/status").status_code == 401


@respx.mock
def test_callback_binds_state_to_browser_and_stores_token(tmp_path):
    c = make_app(tmp_path, connected=False)
    respx.post(GRAPH + "/oauth/access_token").respond(200, json={"access_token": "short"})
    respx.get(GRAPH + "/access_token").respond(200, json={"access_token": "long-token", "expires_in": 5184000})
    login(c)
    start = c.get("/auth/start", follow_redirects=False)
    assert start.status_code == 307
    state = re.search(r"state=([^&]+)", start.headers["location"]).group(1)
    fresh = make_app(tmp_path, connected=False)
    fresh.get("/login")
    hijacked = fresh.get(f"/auth/callback?code=code&state={state}", follow_redirects=False)
    assert hijacked.status_code == 400
    assert "reconnect" in hijacked.json()["error"]
    ok = c.get(f"/auth/callback?code=code&state={state}", follow_redirects=False)
    assert ok.status_code == 303
    assert c.get("/auth/status").json()["connected"] is True
    with sqlite3.connect(c.app.state.settings.db_path) as db:
        assert "long-token" not in "".join(db.iterdump())


def test_callback_rejects_stale_state(client):
    response = client.get("/auth/callback?code=code&state=forged", follow_redirects=False)
    assert response.status_code == 400
    assert "reconnect" in response.json()["error"]


def test_research_requires_consent_and_same_origin(client):
    r1 = client.post("/research/run")
    assert r1.status_code == 400
    r2 = client.post("/research/run", headers={"Origin": "https://attacker.example"})
    assert r2.status_code == 403


@respx.mock
def test_research_run_happy_path_stores_and_labels_sample(client, tmp_path):
    respx.get(GRAPH + "/v1.0/me/threads").respond(200, json={"data": [
        {"id": "1", "text": "How do I rebuild trust?", "permalink": "https://www.threads.com/@sample/post/1", "timestamp": "2026-11-05T12:00:00+0000"}]})
    respx.get(GRAPH + "/v1.0/1/insights").respond(200, json={"data": [{"name": "likes", "values": [{"value": 3}]}]})
    respx.get(GRAPH + "/v1.0/1/replies").respond(200, json={"data": []})
    respx.post(OPENROUTER).respond(200, json={"choices": [{"message": {"content": json.dumps({"insights": [
        {"theme": "Trust", "quote": "rebuild trust", "source_url": "https://www.threads.com/@sample/post/1", "ebook_idea": "Reflection on boundaries"}]})}}]})
    response = client.post("/research/run", data={"consent": "on"})
    assert response.status_code == 200
    body = response.json()
    assert body["insights"][0]["theme"] == "Trust"
    assert body["limitations"]
    listed = client.get("/research/insights").json()
    assert listed["insights"][0]["ebook_idea"] == "Reflection on boundaries"


@respx.mock
def test_research_run_expired_token(tmp_path):
    c = make_app(tmp_path)
    login(c)
    c.app.state.store.save_token("stored-token", NOW - 10)
    r = c.post("/research/run", data={"consent": "on"})
    assert r.status_code == 401 and r.json()["error"] == "reconnect"


def test_empty_profile_returns_empty_insights(client):
    def fake_collect(token, **kw):
        return {"sources": [], "posts_sampled": 0, "selected_posts": 0, "limitations": "empty profile"}
    with patch("research_admin.app.ThreadsClient.collect_research", side_effect=fake_collect):
        response = client.post("/research/run", data={"consent": "on"})
    assert response.status_code == 200
    assert response.json()["insights"] == []


def test_upstream_errors_are_sanitized(client):
    import httpx as _httpx
    def boom(token, **kw):
        raise _httpx.ConnectError("secret-token")
    with patch("research_admin.app.ThreadsClient.collect_research", side_effect=boom):
        response = client.post("/research/run", data={"consent": "on"})
    assert response.status_code == 502
    assert "secret-token" not in response.text


def test_html_page_shows_expiry_and_sample_limit(client):
    body = client.get("/").text
    assert "Threads research" in body
    assert "sample" in body.lower()


def test_cross_origin_login_and_logout_blocked(client):
    for path, data in [("/login", {"password": "admin-pass"}), ("/logout", {})]:
        response = client.post(path, data=data, headers={"Origin": "https://attacker.example"}, follow_redirects=False)
        assert response.status_code == 403
    assert client.get("/auth/status").status_code == 200


def test_missing_origin_rejected(client):
    client.headers.pop("origin")
    response = client.post("/research/run", data={"consent": "on"})
    assert response.status_code == 403


def test_bad_host_rejected(client):
    response = client.get("/auth/status", headers={"Host": "attacker.example"})
    assert response.status_code == 400


def test_expired_token_status_disconnected(client):
    client.app.state.store.save_token("expired", NOW - 10)
    assert client.get("/auth/status").json()["connected"] is False
    assert "connect Threads" in client.get("/").text


@respx.mock
def test_state_bound_to_session_on_same_server(client):
    start = client.get("/auth/start", follow_redirects=False)
    state = re.search(r"state=([^&]+)", start.headers["location"]).group(1)
    other = TestClient(client.app, headers={"Origin": "http://testserver"})
    login(other)
    other.cookies.set("oauth_browser", client.cookies.get("oauth_browser"))
    denied = other.get(f"/auth/callback?code=code&state={state}", follow_redirects=False)
    assert denied.status_code == 400
    assert not respx.calls


def test_oauth_state_expires(client):
    start = client.get("/auth/start", follow_redirects=False)
    state = re.search(r"state=([^&]+)", start.headers["location"]).group(1)
    with patch("research_admin.app.time.time", return_value=time.time() + 601):
        response = client.get(f"/auth/callback?code=code&state={state}", follow_redirects=False)
    assert response.status_code == 400


def test_insights_visible_and_escaped(client):
    client.app.state.store.save_insights([{"theme": "<script>attack</script>", "quote": "A quote", "source_url": "javascript:alert(1)", "ebook_idea": "A draft idea"}])
    response = client.get("/")
    assert "A draft idea" in response.text
    assert "<script>attack</script>" not in response.text
    assert 'href="javascript:' not in response.text
    assert response.headers["cache-control"] == "no-store"


def test_launcher_defaults_to_loopback(tmp_path):
    import runpy
    with patch.dict("os.environ", {"RESEARCH_DB_PATH": str(tmp_path / "launch.db")}):
        with patch("uvicorn.run") as server:
            runpy.run_module("research_admin", run_name="__main__")
    assert server.call_args.kwargs["host"] == "127.0.0.1"
    assert server.call_args.kwargs["access_log"] is False


def test_unicode_passwords_work_and_wrong_password_is_rejected(tmp_path):
    c = make_app(tmp_path, password="rahsia-心-é")
    assert c.post("/login", data={"password": "wrong-心"}, follow_redirects=False).status_code == 401
    assert c.post("/login", data={"password": "rahsia-心-é"}, follow_redirects=False).status_code == 303
    assert c.get("/auth/status").status_code == 200


def test_healthcheck_is_public_and_ignores_host(tmp_path):
    anon = make_app(tmp_path)
    response = anon.get("/healthz", headers={"Host": "healthcheck.railway.app"})
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_railway_host_is_accepted_and_cookie_is_secure(tmp_path):
    c = make_app(tmp_path, password="a-long-admin-password", secure_cookies=True,
                 allowed_hosts=("perpustakaan.up.railway.app",),
                 base_url="https://perpustakaan.up.railway.app")
    response = c.post("/login", data={"password": "a-long-admin-password"}, follow_redirects=False)
    assert response.status_code == 303
    assert "secure" in response.headers["set-cookie"].lower()
    assert c.get("/auth/status").status_code == 200


def test_https_origin_matches_host_behind_proxy(tmp_path):
    c = make_app(tmp_path, allowed_hosts=("perpustakaan.up.railway.app",), secure_cookies=True,
                 base_url="https://perpustakaan.up.railway.app")
    login(c)
    response = c.post("/research/run", data={"consent": "on"})
    assert response.status_code != 403


def test_unlisted_host_rejected_when_allowlist_is_custom(tmp_path):
    c = make_app(tmp_path, allowed_hosts=("perpustakaan.up.railway.app",))
    assert c.get("/auth/status", headers={"Host": "attacker.example"}).status_code == 400


def test_login_is_rate_limited(tmp_path):
    c = make_app(tmp_path)
    for _ in range(5):
        assert c.post("/login", data={"password": "wrong"}).status_code == 401
    blocked = c.post("/login", data={"password": "admin-pass"})
    assert blocked.status_code == 429


def test_launcher_uses_railway_port_and_public_host(tmp_path):
    import runpy
    env = {
        "RESEARCH_DB_PATH": str(tmp_path / "launch.db"),
        "PORT": "8080",
        "RAILWAY_ENVIRONMENT": "production",
        "RESEARCH_ADMIN_PASSWORD": "a-long-admin-password",
        "THREADS_REDIRECT_URI": "https://perpustakaan.up.railway.app/auth/callback",
        "RESEARCH_VAULT": "sqlite",
        "RESEARCH_TOKEN_KEY": "a-long-random-token-key",
    }
    with patch.dict("os.environ", env):
        with patch("uvicorn.run") as server:
            runpy.run_module("research_admin", run_name="__main__")
    assert server.call_args.kwargs["host"] == "0.0.0.0"
    assert server.call_args.kwargs["port"] == 8080
    assert server.call_args.kwargs["proxy_headers"] is False
