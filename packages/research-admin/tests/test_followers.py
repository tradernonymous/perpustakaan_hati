import json
import time

import pytest

from research_admin.app import create_app
from research_admin.config import Settings
from research_admin.followers import (
    MAX_ENTRIES,
    AudienceError,
    AudienceIndex,
    analyze_audience,
    author_of,
    filter_people,
    parse_export,
    since_date,
)
from research_admin.store import Store

NOW = int(time.time())


def meta_entry(username, href, timestamp):
    return {"title": username, "string_list_data": [{"href": href, "value": username, "timestamp": timestamp}]}


def flat_entry(username, timestamp):
    return {"value": username, "href": f"https://www.threads.net/@{username}", "timestamp": timestamp}


# -- parsing ---------------------------------------------------------------


def test_parse_export_accepts_the_raw_meta_shape():
    payload = [meta_entry("Aida", "https://www.threads.net/@Aida", 1700000000)]
    people = parse_export(payload, label="followers.json")
    assert people == [{"username": "Aida", "href": "https://www.threads.net/@Aida", "timestamp": 1700000000}]


def test_parse_export_accepts_the_flat_shape_third_party_tools_emit():
    people = parse_export([flat_entry("ben", 1710000000)], label="following.json")
    assert people[0]["username"] == "ben"
    assert people[0]["timestamp"] == 1710000000


def test_parse_export_accepts_wrapped_lists_and_plain_usernames():
    wrapped = {"following": [{"string_list_data": [{"value": "Cik", "timestamp": 5}]}]}
    people = parse_export(wrapped, label="following.json")
    assert people[0]["username"] == "Cik"
    assert parse_export(["dana", "dana"], label="followers.json") == [{"username": "dana", "href": "", "timestamp": 0}]


def test_parse_export_accepts_profile_urls_and_dedupes_case_insensitively():
    people = parse_export(["https://www.threads.net/@Ehsan", {"value": "@ehsan"}], label="followers.json")
    assert [person["username"] for person in people] == ["Ehsan"]


def test_parse_export_rejects_files_without_accounts():
    with pytest.raises(AudienceError):
        parse_export({"nothing": "here"}, label="followers.json")
    with pytest.raises(AudienceError):
        parse_export([], label="followers.json")


def test_parse_export_caps_each_file():
    entries = [{"value": f"user{i}"} for i in range(MAX_ENTRIES + 1)]
    with pytest.raises(AudienceError):
        parse_export(entries, label="followers.json")


def test_author_of_reads_the_permalink_username():
    assert author_of("https://www.threads.net/@Rahimam.Posts/post/C123") == "rahimam.posts"
    assert author_of("no name here") == ""


def test_since_date_is_safe_against_missing_and_corrupt_timestamps():
    assert since_date(1700000000) == "2023-11-14"
    assert since_date("not-a-number") == ""
    assert since_date(99999999999) == ""
    assert since_date(None) == ""


# -- analysis --------------------------------------------------------------


def test_analyze_splits_the_three_relationships_newest_first():
    followers = [parse_export([flat_entry("mut", 100), flat_entry("fan", 300)], label="followers.json")]
    following = [parse_export([flat_entry("mut", 50), flat_entry("gone", 200)], label="following.json")]
    analysis = analyze_audience(followers[0], following[0])
    assert analysis["counts"] == {
        "followers": 2, "following": 2, "not_following_back": 1,
        "fans": 1, "mutuals": 1, "percent_not_following_back": 50.0,
    }
    assert [p["username"] for p in analysis["not_following_back"]] == ["gone"]
    assert [p["username"] for p in analysis["fans"]] == ["fan"]
    assert analysis["mutuals"][0]["since"] == 100  # newest of both timestamps


def test_analyze_handles_an_empty_following_list_without_dividing_by_zero():
    analysis = analyze_audience([{"username": "x", "href": "", "timestamp": 1}], [])
    assert analysis["counts"]["percent_not_following_back"] == 0.0
    assert analysis["counts"]["following"] == 0


def test_filter_people_searches_and_bounds_the_page():
    analysis = analyze_audience([], [{"username": f"user{i}", "href": "", "timestamp": i} for i in range(300)])
    page, total = filter_people(analysis, "not_following_back", "user2", limit=5)
    assert total == 111  # user2, user20..user299
    assert len(page) == 5
    page, total = filter_people(analysis, "not_following_back", "", limit=200)
    assert (len(page), total) == (200, 300)
    assert [p["username"] for p in page][:2] == ["user299", "user298"]  # newest first


def test_filter_people_falls_back_to_the_first_list_for_an_unknown_key():
    analysis = analyze_audience([], [{"username": "zoe", "href": "", "timestamp": 5}])
    assert filter_people(analysis, "bogus")[0][0]["username"] == "zoe"


# -- insight cross-reference ----------------------------------------------


def test_index_flags_each_relationship_for_a_source_permalink():
    analysis = analyze_audience(
        [{"username": "fan", "href": "", "timestamp": 1}, {"username": "mut", "href": "", "timestamp": 1}],
        [{"username": "mut", "href": "", "timestamp": 1}, {"username": "gone", "href": "", "timestamp": 1}],
    )
    index = AudienceIndex(analysis)
    assert index.enabled is True
    assert index.tag("https://www.threads.net/@mut/post/X") == "mutual"
    assert index.tag("https://www.threads.net/@fan/post/X") == "follower"
    assert index.tag("https://www.threads.net/@gone/post/X") == "following_only"
    assert index.tag("https://www.threads.net/@stranger/post/X") == "none"
    assert index.tag("") == ""


def test_index_is_disabled_without_an_import():
    index = AudienceIndex(None)
    assert index.enabled is False
    assert index.tag("https://www.threads.net/@anyone/post/X") == ""


# -- store -----------------------------------------------------------------


def test_audience_is_persisted_and_clearable(tmp_path):
    store = Store(str(tmp_path / "research.db"))
    store.init_schema()
    assert store.get_audience() is None
    assert store.clear_audience() is False
    saved_at = store.save_audience([{"username": "a", "href": "", "timestamp": 1}], [{"username": "b", "href": "", "timestamp": 2}])
    stored = store.get_audience()
    assert stored["followers"][0]["username"] == "a"
    assert stored["following"][0]["username"] == "b"
    assert stored["imported_at"] == saved_at
    store.save_audience([{"username": "c", "href": "", "timestamp": 3}], [])
    assert store.get_audience()["followers"][0]["username"] == "c"  # one row, replaced
    assert store.clear_audience() is True
    assert store.get_audience() is None


# -- app routes ------------------------------------------------------------


FOLLOWERS_JSON = json.dumps([flat_entry("mut", 1700000000), flat_entry("fan", 1705000000)])
FOLLOWING_JSON = json.dumps([flat_entry("mut", 1690000000), flat_entry("gone", 1710000000)])


def make_client(tmp_path, *, password="admin-pass", base_url="http://testserver"):
    settings = Settings(
        threads_client_id="id", threads_client_secret="sec", openrouter_api_key="key",
        admin_password=password, db_path=str(tmp_path / "research.db"))

    class MemoryVault:
        def __init__(self): self.value = "stored-token"
        def get(self): return self.value
        def set(self, v): self.value = v
        def delete(self): self.value = None

    from fastapi.testclient import TestClient
    app = create_app(settings, vault_factory=lambda: MemoryVault())
    app.state.store.init_schema()
    client = TestClient(app, base_url=base_url, headers={"Origin": base_url})
    response = client.post("/login", data={"password": password}, follow_redirects=False)
    assert response.status_code == 303
    return client


def upload(client, *, followers=FOLLOWERS_JSON, following=FOLLOWING_JSON, browser=True, **kwargs):
    files = {}
    if followers is not None:
        files["followers"] = ("followers.json", followers.encode(), "application/json")
    if following is not None:
        files["following"] = ("following.json", following.encode(), "application/json")
    if browser:
        kwargs.setdefault("headers", {})
        kwargs["headers"] = {**kwargs["headers"], "Accept": "text/html"}
    return client.post("/followers/import", files=files, **kwargs)


@pytest.fixture
def client(tmp_path):
    return make_client(tmp_path)


def test_import_route_requires_sign_in(tmp_path):
    settings = Settings(admin_password="admin-pass", db_path=str(tmp_path / "research.db"))
    from fastapi.testclient import TestClient
    app = create_app(settings)
    app.state.store.init_schema()
    with TestClient(app, base_url="http://testserver", headers={"Origin": "http://testserver"}) as anon:
        assert anon.get("/followers").status_code == 401
        assert anon.get("/followers/export.csv").status_code == 401
        assert anon.post("/followers/clear").status_code == 401
        assert anon.post("/followers/import").status_code == 401


def test_import_round_trip_updates_the_json_api(client):
    response = upload(client, follow_redirects=False)
    assert response.status_code == 303
    assert "view=followers" in response.headers["location"]
    body = client.get("/followers").json()
    assert body["audience"]["counts"] == {
        "followers": 2, "following": 2, "not_following_back": 1,
        "fans": 1, "mutuals": 1, "percent_not_following_back": 50.0,
    }
    assert [p["username"] for p in body["audience"]["lists"]["not_following_back"]["people"]] == ["gone"]
    assert body["audience"]["lists"]["fans"]["people"][0]["username"] == "fan"
    assert body["audience"]["lists"]["mutuals"]["people"][0]["username"] == "mut"
    assert body["audience"]["imported_at"]


def test_import_failure_returns_json_for_api_clients(client):
    response = upload(client, following=FOLLOWERS_JSON, browser=False, follow_redirects=False)
    assert response.status_code == 400
    assert "identical" in response.json()["error"]
    response = client.post("/followers/import", files={
        "followers": ("f.json", b"{oops", "application/json"),
        "following": ("following.json", FOLLOWING_JSON.encode(), "application/json"),
    }, follow_redirects=False)
    assert response.status_code == 400
    assert "not valid JSON" in response.json()["error"]


def test_missing_file_is_rejected(client):
    response = upload(client, following=None, browser=False, follow_redirects=False)
    assert response.status_code == 400
    assert "following.json is missing" in response.json()["error"]


def test_oversized_upload_is_rejected(tmp_path, monkeypatch):
    client = make_client(tmp_path)
    monkeypatch.setattr("research_admin.app.MAX_IMPORT_BYTES", 40)
    response = upload(client, browser=False, follow_redirects=False)
    assert response.status_code == 413


def test_import_errors_show_as_a_dashboard_notice_for_browsers(client):
    response = upload(client, followers=None, follow_redirects=False)
    assert response.status_code == 303
    location = response.headers["location"]
    assert "view=followers" in location and "notice=" in location
    page = client.get(location).text
    assert "followers.json is missing" in page


def test_followers_view_renders_import_form_stats_and_lists(client):
    upload(client)
    body = client.get("/?view=followers").text
    assert "Followers" in body
    assert 'action="/followers/import"' in body
    assert 'name="followers"' in body and 'name="following"' in body
    assert "50.0%" in body
    assert "Mutuals · 1" in body and "Fans · 1" in body
    assert "@gone" in body
    assert "You follow since 2024-03-09" in body  # 1710000000, newest first
    assert 'href="/followers/export.csv' in body
    assert "/followers/clear" in body


def test_followers_view_empty_state_explains_the_upload(client):
    body = client.get("/?view=followers").text
    assert "NOT IMPORTED YET" in body
    assert "Accounts Center" in body
    assert "Xiang511/Threads-Follower" in body


def test_list_search_and_pills_keep_the_selection(client):
    upload(client)
    body = client.get("/?view=followers&list=fans&q=zzz").text
    assert "Nobody matches this list yet." in body
    body = client.get("/?view=followers&list=mutuals").text
    assert 'class="follow-chip mutual"' in body  # the badge on the row
    assert "@mut" in body


def test_export_csv_is_formula_safe_and_filterable(client):
    upload(client, followers=json.dumps([{"value": "=danger", "timestamp": 5}, flat_entry("fan", 6)]))
    body = client.get("/followers/export.csv").text
    assert body.splitlines()[0] == "list,username,profile_url,since"
    assert "'=danger" in body  # leading = neutralised
    filtered = client.get("/followers/export.csv?list=fans").text
    assert "fan" in filtered and "gone" not in filtered
    assert client.get("/followers/export.csv?q=nobody").text.count("\n") == 1


def test_export_csv_without_an_import_is_404(client):
    response = client.get("/followers/export.csv")
    assert response.status_code == 404


def test_clear_removes_the_import(client):
    upload(client)
    response = client.post("/followers/clear", headers={"Accept": "text/html"}, follow_redirects=False)
    assert response.status_code == 303
    assert "view=followers" in response.headers["location"]
    assert client.get("/followers").json() == {"audience": None}
    assert client.post("/followers/clear").json() == {"cleared": False}


def test_insight_cards_carry_the_relationship_badge(client):
    store = client.app.state.store
    store.save_insights([
        {"theme": "Trust", "quote": "I feel unheard.", "source_url": "https://www.threads.net/@gone/post/A1", "ebook_idea": ""},
        {"theme": "Worth", "quote": "Second guessing.", "source_url": "https://www.threads.net/@stranger/post/A2", "ebook_idea": ""},
    ])
    upload(client)
    body = client.get("/?view=research").text
    assert "Doesn&#x27;t follow back" in body
    assert "Not connected" in body
    assert "Mutual" not in body and "Follows Rahimam" not in body
    # the Followers view counts the tie-in
    followers_view = client.get("/?view=followers").text
    assert "1 not-following-back · 1 not connected" in followers_view
    # no import, no badges
    client.post("/followers/clear")
    assert "Doesn&#x27;t follow back" not in client.get("/?view=research").text


def test_nav_has_a_followers_entry_after_research(client):
    body = client.get("/").text
    assert body.index("view=research") < body.index("view=followers") < body.index("view=audiences")
