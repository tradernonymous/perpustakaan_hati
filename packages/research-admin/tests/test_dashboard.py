from research_admin.dashboard import _draft_content

DRAFT = {
    "kind": "design_brief",
    "title": "Trust, quietly",
    "content": {
        "concept": "Open hands, not a locked door.",
        "format": "Square social card",
        "visual_direction": "Warm paper texture.",
        "copy": "Trust is rebuilt in small, kept promises.",
        "references": [{"insight_id": 7, "theme": "Trust", "url": "https://www.threads.net/@rahimah/post/ABC123"}],
    },
}


def test_design_brief_shows_the_source_link_as_copyable_text():
    html = _draft_content(DRAFT)
    assert "Reference posts" in html
    assert '<a href="https://www.threads.net/@rahimah/post/ABC123"' in html
    assert ">https://www.threads.net/@rahimah/post/ABC123</a>" in html


def test_threads_post_never_renders_references():
    draft = {"kind": "threads_post", "title": "A note", "content": {
        "post": "Trust grows in small, honest moments.",
        "references": [{"insight_id": 7, "url": "https://www.threads.net/@rahimah/post/ABC123"}],
    }}
    html = _draft_content(draft)
    assert "Reference posts" not in html
    assert "threads.net" not in html


def test_reference_urls_are_escaped():
    draft = {"kind": "ebook_outline", "title": "Outline", "content": {
        "premise": "Premise", "intended_reader_need": "Need", "chapters": [],
        "references": [{"insight_id": 7, "theme": "<b>Trust</b>", "url": 'https://example.test/"><script>alert(1)</script>'}],
    }}
    html = _draft_content(draft)
    assert "<script>" not in html
    assert "&lt;b&gt;Trust&lt;/b&gt;" in html
