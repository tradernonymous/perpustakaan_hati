from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
import respx

from research_admin.config import Settings
from research_admin.threads_client import ThreadsClient, ThreadsError

GRAPH = "https://graph.threads.com"


def post(number, text="A reader's concern"):
    return {"id": str(number), "text": text, "permalink": f"https://www.threads.com/@sample/post/{number}", "timestamp": "2026-11-05T12:00:00+0000"}


@pytest.fixture
def client():
    with httpx.Client() as http:
        yield ThreadsClient(Settings(threads_client_id="id", threads_client_secret="private-secret"), http)


def test_authorization_uses_documented_read_only_permissions(client):
    url = urlsplit(client.authorize_url("random-state"))
    query = parse_qs(url.query)
    assert url.netloc == "threads.com"
    assert query["state"] == ["random-state"]
    assert query["client_id"] == ["id"]
    assert query["redirect_uri"] == [client.settings.redirect_uri]
    assert set(query["scope"][0].split(",")) == {"threads_basic", "threads_read_replies", "threads_manage_insights"}


@respx.mock
def test_exchange_code_gets_long_lived_token(client):
    respx.post(GRAPH + "/oauth/access_token").respond(200, json={"access_token": "short"})
    respx.get(GRAPH + "/access_token").respond(200, json={"access_token": "long-secret", "expires_in": 5184000})
    token = client.exchange_code("code")
    assert token.access_token == "long-secret"
    assert token.expires_in == 5184000
    assert "long-secret" not in repr(token)


@respx.mock
def test_pagination_uses_fixed_host_and_cursor(client):
    def respond(request):
        assert request.headers["authorization"] == "Bearer token"
        if request.url.params.get("after") == "page2":
            return httpx.Response(200, json={"data": [post(2)]})
        return httpx.Response(200, json={"data": [post(1)], "paging": {"next": "https://attacker.example/?after=page2&access_token=secret"}})
    respx.get(GRAPH + "/v1.0/me/threads").mock(side_effect=respond)
    assert [p["id"] for p in client.fetch_my_posts("token")] == ["1", "2"]


@respx.mock
def test_pagination_stops_after_three_pages(client):
    def respond(request):
        number = int(request.url.params.get("after", "1"))
        return httpx.Response(200, json={"data": [post(number)], "paging": {"next": "present", "cursors": {"after": str(number + 1)}}})
    respx.get(GRAPH + "/v1.0/me/threads").mock(side_effect=respond)
    assert len(client.fetch_my_posts("token")) == 3


@respx.mock
def test_research_ranks_owned_posts_and_collects_visible_replies(client):
    respx.get(GRAPH + "/v1.0/me/threads").respond(200, json={"data": [post(1), post(2)]})
    for number, likes in [(1, 2), (2, 90)]:
        respx.get(GRAPH + f"/v1.0/{number}/insights").respond(200, json={"data": [{"name": "likes", "values": [{"value": likes}]}]})
    respx.get(GRAPH + "/v1.0/2/replies").respond(200, json={"data": [post(3, "How do I rebuild trust?")]})
    result = client.collect_research("token", top_posts=1)
    assert result["posts_sampled"] == 2
    assert result["sources"][0]["id"] == "2"
    assert result["sources"][0]["engagement_score"] == 90
    assert result["sources"][1]["source_type"] == "reply"
    assert "reply-level virality" in result["limitations"]


@pytest.mark.parametrize("status,payload,match", [(400, {"error": {"code": 190, "message": "token-secret"}}, "reconnect"), (429, {}, "rate limit"), (200, [], "invalid response")])
@respx.mock
def test_safe_upstream_failures(client, status, payload, match):
    respx.get(GRAPH + "/v1.0/me/threads").respond(status, json=payload)
    with pytest.raises(ThreadsError, match=match) as error:
        client.fetch_my_posts("token-secret")
    assert "token-secret" not in str(error.value)


@respx.mock
def test_empty_account_is_valid(client):
    respx.get(GRAPH + "/v1.0/me/threads").respond(200, json={"data": []})
    assert client.collect_research("token")["sources"] == []


@pytest.mark.parametrize("paging", [[], None, {"next": 123}, {"next": "https://graph.threads.com/?after=2", "cursors": []}, {"next": "present", "cursors": {"after": [2]}}])
@respx.mock
def test_malformed_paging_is_safe_error(client, paging):
    respx.get(GRAPH + "/v1.0/me/threads").respond(200, json={"data": [post(1)], "paging": paging})
    with pytest.raises(ThreadsError, match="invalid"):
        client.fetch_my_posts("token")
