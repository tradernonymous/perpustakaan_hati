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


def test_calendar_uses_malaysia_date_and_keeps_unscheduled_approval_separate():
    from research_admin.dashboard import DashboardData, _render_calendar_view

    data = DashboardData(
        view="calendar", connection="", expiry="", insights=[], runs=[], audiences=[],
        drafts=[
            {"id": 1, "title": "Midnight post", "status": "scheduled", "scheduled_at": "2026-11-19T16:15:00Z"},
            {"id": 2, "title": "Approved without date", "status": "approved", "created_at": "2026-11-20T00:00:00Z"},
        ],
        calendar_mode="day", calendar_date="2026-11-20",
    )
    html = _render_calendar_view(data)
    agenda, queue = html.split("Ready to schedule")
    assert "00:15" in agenda and "Midnight post" in agenda
    assert "Approved without date" in queue
    data.calendar_date = "2026-11-19"
    assert "Midnight post" not in _render_calendar_view(data)
    data.calendar_mode = "month"
    month_html = _render_calendar_view(data)
    assert "mode=day&amp;date=2026-11-20" in month_html
    assert '<div class="cal-weekday">Mon</div>' in month_html
    assert "November 2026" in month_html
    # 2026-11-01 is a Sunday (weekday() == 6), so 6 leading pad cells precede day 1.
    assert month_html.count('class="cal-cell is-pad"') == 6


def test_studio_and_publications_and_shell_ui_ux_refinements():
    from research_admin.dashboard import DashboardData, render_dashboard

    studio_html = render_dashboard(
        DashboardData(
            view="studio",
            connection="Connected · expires 2026-12-01",
            expiry="2026-12-01",
            insights=[{"id": 11, "theme": "Tenang", "quote": "Saya penat.", "ebook_idea": "Bab 1", "source_url": ""}],
            runs=[],
            audiences=[],
            drafts=[],
        )
    )
    assert ".actions{display:flex" in studio_html
    assert 'class="studio-fieldset"' in studio_html
    assert 'id="studio-evidence-search" class="studio-evidence-search"' in studio_html
    assert 'data-studio-evidence="visible"' in studio_html
    assert 'data-studio-evidence="clear"' in studio_html
    assert 'aria-controls="mobile-drawer"' in studio_html
    assert 'aria-expanded="false"' in studio_html
    assert "#1C2D23" not in studio_html.split(".mobile-bar")[1]

    pub_html = render_dashboard(
        DashboardData(
            view="publications",
            connection="Connected",
            expiry="",
            insights=[],
            runs=[],
            audiences=[],
            drafts=[],
            publications=[
                {
                    "tier": "poket",
                    "label": "Edisi Poket",
                    "latest": {"revision": 2, "title": "Edisi Poket", "summary": "Ringkas.", "sample": "/#bab", "status": "review"},
                    "history": [1],
                    "confirmed": None,
                    "event": ("approve", "Needs review first."),
                }
            ],
        )
    )
    assert 'class="pub-stepper"' in pub_html
    assert 'class="pub-step is-done">Draft</span>' in pub_html
    assert 'class="pub-step is-current">Review</span>' in pub_html
    assert 'class="notice error" role="alert"' in pub_html


def test_followers_search_shows_clear_reset_link():
    from research_admin.dashboard import DashboardData, render_dashboard

    html = render_dashboard(
        DashboardData(
            view="followers",
            connection="Connected",
            expiry="",
            insights=[],
            runs=[],
            audiences=[],
            drafts=[],
            follow_query="ali",
            graph_query="tenang",
            graph_audience={
                "profile": {"username": "rahimam"},
                "counts": {"followers_count": 120, "active_repliers": 3, "insight_contributors": 1},
                "metrics": {"views": 1000, "likes": 50},
                "engagers": [],
                "contributors": [],
                "frequent": [],
            },
        )
    )
    assert ">Clear</a>" in html
