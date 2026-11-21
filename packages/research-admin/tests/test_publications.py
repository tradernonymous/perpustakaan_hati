"""The operator boundary and immutable public revisions, through real HTTP routes."""
from concurrent.futures import ThreadPoolExecutor

from test_app import login, make_app


def save(client, expected=0, title="Edisi Poket", **extra):
    return client.post("/publications/poket/draft", data={
        "expected": str(expected), "title": title, "summary": "Satu bacaan ringkas.", **extra,
    })


def transition(client, action, expected, **extra):
    return client.post("/publications/poket/" + action, data={"expected": str(expected), **extra})


def test_permissions_and_public_projection(tmp_path):
    client = make_app(tmp_path)
    assert client.get("/publications/poket/preview").status_code == 401
    assert client.get("/publications/poket/export").status_code == 401
    assert save(client).status_code == 401
    assert transition(client, "publish", 1).status_code == 401
    login(client)
    assert client.post("/publications/poket/draft", headers={"Origin": "https://other.invalid"}).status_code == 403
    assert save(client, price="0").status_code == 422
    assert save(client, sample="https://other.invalid/private").status_code == 422
    assert save(client, title="A\nB").status_code == 422
    client.app.state.store.save_drafts([{"kind": "threads_post", "title": "Private source title",
                                         "content": {"post": "private-evidence-canary"}}], [])
    assert save(client, sample="/#bab").status_code == 200
    assert client.get("/publications/poket/preview").json()["status"] == "draft"
    assert client.get("/publications/poket/export").status_code == 404
    assert transition(client, "publish", 1).status_code == 409
    for action in ("review", "approve", "publish", "publish"):
        assert transition(client, action, 1).status_code == 200
    expected = {
        "schema_version": 1, "id": "poket", "slug": "poket", "tier": "poket", "revision": 1,
        "title": "Edisi Poket", "summary": "Satu bacaan ringkas.", "artwork": "/ebooks/cover-poket.png",
        "sample": "/#bab", "status": "published",
    }
    assert client.get("/publications/poket/export").json() == expected
    assert save(client, 1, title="Edited privately").status_code == 200
    assert transition(client, "publish", 1).status_code == 409
    assert client.get("/publications/poket/export").json() == expected
    for action in ("review", "approve", "publish"):
        assert transition(client, action, 2).status_code == 200
    assert save(client, 2, title="Unreleased revision").status_code == 200
    assert 'action="/publications/poket/rollback"' in client.get("/?view=publications").text
    assert transition(client, "rollback", 3, target="2").status_code == 409
    for _ in range(2):
        assert transition(client, "rollback", 3, target="1").status_code == 200
    assert client.get("/publications/poket/export").json() == {**expected, "revision": 4}
    page = client.get("/?view=publications").text
    assert 'action="/publications/poket/draft"' in page
    assert "Export revision 4" in page and "Pending storefront confirmation" in page
    assert transition(client, "confirm-live", 2).status_code == 409
    assert transition(client, "confirm-live", 4).status_code == 200
    assert "Synchronization confirmed by editor" in client.get("/?view=publications").text


def test_concurrent_edits_do_not_overwrite_each_other(tmp_path):
    client = make_app(tmp_path)
    login(client)
    with ThreadPoolExecutor(max_workers=2) as pool:
        codes = sorted(pool.map(lambda name: save(client, title=name).status_code, ["First", "Second"]))
    assert codes == [200, 409]


def test_packaged_admin_surfaces_match_canonical_tokens():
    from pathlib import Path

    from research_admin.theme import RAISED, SOFT, VOID

    css = (Path(__file__).resolve().parents[3] / "docs/brand/design-tokens.css").read_text()
    for name, value in (("void", VOID), ("void-raised", RAISED), ("void-soft", SOFT)):
        assert f"--ph-{name}: {value};" in css
