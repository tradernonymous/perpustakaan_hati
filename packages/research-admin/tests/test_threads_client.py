from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
import respx

from research_admin.config import Settings
from research_admin.threads_client import (
    POST_LIMIT_MAX,
    REPLIES_PER_POST_MAX,
    TOP_POSTS_MAX,
    SampleLimits,
    ThreadsClient,
    ThreadsError,
)

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


def test_sample_limits_default_and_clamp():
    assert SampleLimits().normalized().as_dict() == {"post_limit": 50, "top_posts": 5, "replies_per_post": 50}
    assert SampleLimits.from_form({}).as_dict() == {"post_limit": 50, "top_posts": 5, "replies_per_post": 50}
    assert SampleLimits.from_form({"post_limit": "9999", "top_posts": "9999", "replies_per_post": "-4"}).as_dict() == {
        "post_limit": POST_LIMIT_MAX, "top_posts": TOP_POSTS_MAX, "replies_per_post": 1}
    assert SampleLimits.from_form({"post_limit": "abc", "top_posts": "", "replies_per_post": "none"}).as_dict() == {
        "post_limit": 50, "top_posts": 5, "replies_per_post": 50}
    # Prioritized posts can never exceed the number of posts actually fetched.
    assert SampleLimits.from_form({"post_limit": "3", "top_posts": "10"}).as_dict()["top_posts"] == 3


@respx.mock
def test_research_reports_and_applies_requested_limits(client):
    def posts(request):
        assert request.url.params["limit"] == "12"
        return httpx.Response(200, json={"data": [post(1)]})
    def replies(request):
        assert request.url.params["limit"] == "7"
        return httpx.Response(200, json={"data": [post(3, "How do I rebuild trust?")]})
    respx.get(GRAPH + "/v1.0/me/threads").mock(side_effect=posts)
    respx.get(GRAPH + "/v1.0/1/insights").respond(200, json={"data": [{"name": "likes", "values": [{"value": 4}]}]})
    respx.get(GRAPH + "/v1.0/1/replies").mock(side_effect=replies)
    result = client.collect_research("token", post_limit=12, top_posts=1, replies_per_post=7)
    assert result["limits"] == {"post_limit": 12, "top_posts": 1, "replies_per_post": 7}
    assert "At most 12 recent owned posts" in result["limitations"]
    assert "Up to 7 visible direct replies" in result["limitations"]
    assert result["sources"][-1]["source_type"] == "reply"


@respx.mock
def test_excessive_limits_are_clamped_before_collection(client):
    respx.get(GRAPH + "/v1.0/me/threads").respond(200, json={"data": [post(1)]})
    respx.get(GRAPH + "/v1.0/1/insights").respond(200, json={"data": []})
    respx.get(GRAPH + "/v1.0/1/replies").respond(200, json={"data": []})
    result = client.collect_research("token", post_limit=9999, top_posts=9999, replies_per_post=9999)
    assert result["limits"] == {"post_limit": POST_LIMIT_MAX, "top_posts": TOP_POSTS_MAX, "replies_per_post": REPLIES_PER_POST_MAX}
    # The collection helper pages 50 at a time, so the first request asks for 50.
    assert respx.calls[0].request.url.params["limit"] == "50"


def test_authorization_can_opt_in_to_publish_scope(client):
    url = urlsplit(client.authorize_url("state-2", include_publish=True))
    query = parse_qs(url.query)
    assert set(query["scope"][0].split(",")) == {
        "threads_basic", "threads_read_replies", "threads_manage_insights", "threads_content_publish"
    }


@respx.mock
def test_refresh_token_returns_renewed_long_lived_token(client):
    respx.get(GRAPH + "/refresh_access_token").respond(
        200, json={"access_token": "refreshed-secret", "token_type": "bearer", "expires_in": 5183944}
    )
    token = client.refresh_token("old-token")
    assert token.access_token == "refreshed-secret"
    assert token.expires_in == 5183944
    assert respx.calls[0].request.url.params["grant_type"] == "th_refresh_token"
    assert respx.calls[0].request.url.params["access_token"] == "old-token"


@respx.mock
def test_fetch_profile_and_user_insights_from_graph(client):
    respx.get(GRAPH + "/v1.0/me").respond(200, json={
        "id": "99", "username": "@rahimam", "name": "Rahimam",
        "threads_biography": "Perpustakaan Hati", "threads_profile_picture_url": "https://cdn.threads.net/pic.jpg",
    })
    respx.get(GRAPH + "/v1.0/me/threads_insights").mock(side_effect=lambda req: httpx.Response(200, json={
        "data": (
            [
                {"name": "followers_count", "total_value": {"value": 10540}},
                {"name": "views", "values": [{"value": 1200}, {"value": 800}]},
                {"name": "likes", "total_value": {"value": 430}},
                {"name": "replies", "total_value": {"value": 95}},
                {"name": "reposts", "total_value": {"value": 40}},
                {"name": "quotes", "total_value": {"value": 18}},
            ]
            if "followers_count" in req.url.params.get("metric", "")
            else [{
                "name": "follower_demographics",
                "total_value": {
                    "breakdowns": [{
                        "dimension_keys": [req.url.params.get("breakdown", "country")],
                        "results": [
                            {"dimension_values": ["MY"], "value": 8200},
                            {"dimension_values": ["SG"], "value": 1400},
                        ],
                    }]
                },
            }]
        )
    }))
    profile = client.fetch_profile("token")
    assert profile["username"] == "rahimam"
    assert profile["name"] == "Rahimam"
    insights = client.fetch_user_insights("token")
    assert insights["followers_count"] == 10540
    assert insights["metrics"] == {"views": 2000, "likes": 430, "replies": 95, "reposts": 40, "quotes": 18}
    assert insights["demographics"]["country"][0] == {"key": "MY", "value": 8200}


@respx.mock
def test_fetch_user_insights_tolerates_unavailable_demographics(client):
    def respond(req):
        if req.url.params.get("metric") == "follower_demographics":
            return httpx.Response(400, json={"error": {"message": " Requires 100 followers", "code": 100}})
        return httpx.Response(200, json={"data": [{"name": "followers_count", "total_value": {"value": 42}}]})

    respx.get(GRAPH + "/v1.0/me/threads_insights").mock(side_effect=respond)
    insights = client.fetch_user_insights("token")
    assert insights["followers_count"] == 42
    assert insights["demographics"] == {}


@respx.mock
def test_publish_post_executes_two_step_container_flow(client):
    respx.post(GRAPH + "/v1.0/me/threads").respond(200, json={"id": "container-1"})
    respx.post(GRAPH + "/v1.0/me/threads_publish").respond(200, json={"id": "post-99"})
    respx.get(GRAPH + "/v1.0/post-99").respond(200, json={"id": "post-99", "permalink": "https://www.threads.com/@rahimam/post/XYZ"})
    published = client.publish_post("token", "Trust grows in small moments.")
    assert published == {"id": "post-99", "permalink": "https://www.threads.com/@rahimam/post/XYZ"}


def test_publish_post_validates_empty_and_overlong_text(client):
    with pytest.raises(ThreadsError, match="empty"):
        client.publish_post("token", "   ")
    with pytest.raises(ThreadsError, match="500 characters"):
        client.publish_post("token", "x" * 501)

