"""Server-rendered Daylight Grove research studio dashboard."""

import html
from dataclasses import dataclass, field
from urllib.parse import quote

from .avatars import AVATAR_PATH
from .content import DRAFT_KINDS, DRAFT_LANGUAGES, DRAFT_TONES
from .discovery import score_posts
from .followers import (
    AUDIENCE_LIST_LABELS,
    AUDIENCE_LISTS,
    FOLLOW_SORT_LABELS,
    FOLLOW_SORTS,
    FOLLOW_VIEW_LISTS,
    GRAPH_COMMUNITY_LABELS,
    GRAPH_COMMUNITY_LISTS,
    TAG_LABELS,
    UNFOLLOW_FILTER_LABELS,
    UNFOLLOW_FILTERS,
    AudienceIndex,
    build_preimport_analysis,
    count_unfollow_filters,
    filter_graph_people,
    filter_people,
    since_date,
)
from .threads_client import POST_LIMIT_MAX, POST_TEXT_MAX, REPLIES_PER_POST_MAX, TOP_POSTS_MAX, SampleLimits


@dataclass(slots=True)
class DashboardData:
    view: str
    connection: str
    expiry: str
    insights: list[dict]
    runs: list[dict]
    audiences: list[dict]
    drafts: list[dict]
    query: str = ""
    selection: str = ""
    status_filter: str = ""
    csrf: str = ""
    error: str = ""
    configured: bool = True
    threads_configured: bool = True
    model: str = ""
    limits: SampleLimits | None = None
    jobs: list[dict] = field(default_factory=list)
    focus: str = ""
    audience: dict | None = None
    graph_audience: dict | None = None
    follow_list: str = ""
    graph_list: str = ""
    follow_query: str = ""
    follow_uf: str = ""
    follow_sort: str = "newest"
    unfollow_queue: list[dict] = field(default_factory=list)
    notice: str = ""
    snapshot_diff: dict | None = None
    graph_history: list[dict] = field(default_factory=list)
    inbox_items: list[dict] = field(default_factory=list)
    inbox_status: str = ""
    knowledge_nodes: list[dict] = field(default_factory=list)
    knowledge_edges: list[dict] = field(default_factory=list)
    custom_segments: list[dict] = field(default_factory=list)
    ai_summary: dict = field(default_factory=dict)
    watchlist: dict = field(default_factory=dict)
    autocomplete_results: list[dict] = field(default_factory=list)
    autocomplete_seed: str = ""
    publishing_limit: dict | None = None
    notifications: list[dict] = field(default_factory=list)
    external_signals: list[dict] = field(default_factory=list)
    mini_app_url: str = ""
    scopes: list[str] = field(default_factory=list)
    csp_nonce: str = ""


def _e(value) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def _limit_field(name: str, label: str, value, low: int, high: int, hint: str) -> str:  # noqa: PLR0913, PLR0917
    clamped = max(low, min(int(value), high))
    return (
        f'<label class="limit-field"><span>{_e(label)}</span>'
        f'<input type="number" name="{name}" min="{low}" max="{high}" step="1" inputmode="numeric" value="{clamped}">'
        f'<small>{_e(hint)}</small></label>'
    )


def _draft_controls(*, kinds=None, tone: str = "empathetic", language: str = "match evidence") -> str:
    chosen = {kind for kind in (kinds or DRAFT_KINDS) if kind in DRAFT_KINDS} or set(DRAFT_KINDS)
    labels = {"threads_post": "Threads post", "ebook_outline": "eBook outline", "design_brief": "Design brief"}
    boxes = "".join(
        f'<label class="check"><input type="checkbox" name="kinds" value="{kind}"{" checked" if kind in chosen else ""}>{_e(labels[kind])}</label>'
        for kind in DRAFT_KINDS
    )
    tone_labels = {"empathetic": "Empathetic", "direct": "Direct", "reflective": "Reflective", "practical": "Practical"}
    tones = "".join(f'<option value="{value}"{" selected" if value == tone else ""}>{_e(tone_labels[value])}</option>' for value in DRAFT_TONES)
    language_labels = {"match evidence": "Match the evidence", "Bahasa Melayu": "Bahasa Melayu", "English": "English"}
    languages = "".join(f'<option value="{value}"{" selected" if value == language else ""}>{_e(language_labels[value])}</option>' for value in DRAFT_LANGUAGES)
    return (
        f'<div class="draft-controls"><span class="field-label">Draft kinds</span><div class="kind-grid">{boxes}</div>'
        f'<label class="select-field"><span>Tone</span><select name="tone">{tones}</select></label>'
        f'<label class="select-field"><span>Language</span><select name="language">{languages}</select></label></div>'
    )


def _svg_sparkline(values: list[int | float], *, label: str = "Trend", stroke: str = "#2F4B3B") -> str:
    nums = [float(v) for v in values if v is not None]
    if len(nums) < 2:
        return ""
    low, high = min(nums), max(nums)
    span = max(1.0, high - low)
    pts = []
    for idx, val in enumerate(nums):
        x = round(4 + (132 * idx / (len(nums) - 1)), 1)
        y = round(28 - (22 * ((val - low) / span)), 1)
        pts.append(f"{x},{y}")
    return (
        f'<svg class="spark" viewBox="0 0 140 32" aria-label="{_e(label)}" role="img">'
        f'<polyline fill="none" stroke="{_e(stroke)}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" points="{" ".join(pts)}"/>'
        f'</svg>'
    )


def _job_summary(job: dict) -> str:
    params = job.get("params", {})
    kind = job["kind"]
    if kind == "research":
        text = f'{params.get("post_limit", 50)} posts · top {params.get("top_posts", 5)} · {params.get("replies_per_post", 50)} replies/post'
        focus = str(params.get("focus", "")).strip()
        if focus:
            text += f' · Focus: {focus[:80]}'
        return text
    if kind == "graph_sync":
        return f'Sync profile, follower count, demographics & up to {params.get("post_limit", 25)} recent posts'
    if kind == "watchlist":
        kws = params.get("keywords") or []
        return f'Watchlist check across {len(kws)} keyword{"" if len(kws) == 1 else "s"}'
    if kind == "keyword_search":
        return f'Keyword search & mining: {params.get("query", "")}'
    if kind == "scheduled_publish":
        return f'Scheduled Threads publish for draft #{params.get("draft_id", "")}'
    kinds = params.get("kinds", list(DRAFT_KINDS))
    return f'{len(kinds)} draft kind{"" if len(kinds) == 1 else "s"} · {params.get("tone", "empathetic")} · {params.get("language", "match evidence")}'


def _queue_panel(jobs: list[dict], csrf: str) -> str:
    if not jobs:
        return ""
    active = any(job.get("status") in ("queued", "running") for job in jobs)
    labels = {
        "research": "Research run",
        "drafts": "Draft generation",
        "graph_sync": "Threads Graph sync",
        "watchlist": "Watchlist check",
        "keyword_search": "Keyword search",
        "scheduled_publish": "Scheduled publish",
    }
    statuses = {"queued": "Queued", "running": "Running", "done": "Done", "failed": "Failed", "cancelled": "Cancelled"}
    token = f'<input type="hidden" name="csrf" value="{_e(csrf)}">'
    rows = []
    for job in jobs[:12]:
        status = str(job.get("status", ""))
        actions = ""
        if status in ("queued", "running"):
            actions += f'<form method="post" action="/queue/{int(job["id"])}/cancel">{token}<button class="button ghost small" type="submit">Cancel</button></form>'
        if status in ("failed", "cancelled"):
            actions += f'<form method="post" action="/queue/{int(job["id"])}/retry">{token}<button class="button ghost small" type="submit">Retry</button></form>'
        error = f'<p class="muted">{_e(job.get("error", ""))}</p>' if status == "failed" and job.get("error") else ""
        rows.append(
            f'<div class="run-row job-row"><div><b>#{int(job["id"])} · {_e(labels.get(job["kind"], job["kind"]))}</b>'
            f'<span>{_e(statuses.get(status, status))} · {_e(str(job.get("created_at", ""))[:16].replace("T", " "))}</span></div>'
            f'<div><p>{_e(_job_summary(job))}</p>{error}<div class="job-actions">{actions}</div></div></div>'
        )
    clear = ""
    if any(job.get("status") == "queued" for job in jobs):
        clear = f'<form method="post" action="/queue/clear">{token}<button class="button ghost small" type="submit">Clear queue</button></form>'
    return (
        f'<section class="panel queue-panel"{" data-queue-active" if active else ""}>'
        f'<div class="section-head"><div><p class="eyebrow">JOB QUEUE</p><h2>Queued work</h2></div>{clear}</div>'
        f'<div class="help">Background tasks run cleanly via SQLite WAL queue. Cancelling a queued job stops it before it starts; live progress updates via SSE.</div>'
        f'{"".join(rows)}</section>'
    )


def _source(item: dict) -> str:
    url = str(item.get("source_url", ""))
    if url.startswith(("http://", "https://")):
        return f'<a class="source" href="{_e(url)}" target="_blank" rel="noreferrer">Open Threads source ↗</a>'
    return '<span class="muted">Source link unavailable</span>'


def _follow_chip(tag: str) -> str:
    """Relationship badge for an insight's source author; '' when no import or unknown."""
    label = TAG_LABELS.get(str(tag or ""), "")
    if not label:
        return ""
    return f'<span class="follow-chip { _e(tag) }">{_e(label)}</span>'


FOLLOW_ROW_TAGS = {
    "not_following_back": "following_only",
    "following": "following_only",
    "unfollow_later": "following_only",
    "fans": "follower",
    "mutuals": "mutual",
}
FOLLOW_SINCE_LABELS = {
    "not_following_back": "You follow since",
    "following": "You follow since",
    "unfollow_later": "You follow since",
    "fans": "Follows Rahimam since",
    "mutuals": "Mutual since",
}


def _follow_row(person: dict, list_key: str) -> str:
    username = _e(str(person.get("username", "")))
    href = str(person.get("href") or person.get("profile_url") or f"https://www.threads.com/@{person.get('username', '')}")
    link = (
        f'<a class="source" href="{_e(href)}" target="_blank" rel="noreferrer">@{username} ↗</a>'
        if href.startswith(("http://", "https://")) else f"@{username}"
    )
    since = since_date(person.get("since"))
    days = person.get("days_followed")
    days_note = f" · {int(days)}d ago" if isinstance(days, int) else ""
    label_prefix = FOLLOW_SINCE_LABELS.get(list_key, "You follow since")
    when = f"{label_prefix} {since}{days_note}" if since else "Date not in the export"
    follows_back = bool(person.get("follows_back", list_key in ("fans", "mutuals")))
    row_tag = "mutual" if (list_key in ("following", "unfollow_later") and follows_back) else FOLLOW_ROW_TAGS.get(list_key, "following_only")
    chips = [_follow_chip(row_tag)]
    replies = int(person.get("replies_count", 0) or 0)
    if not follows_back:
        if replies > 0:
            chips.append(f'<span class="follow-chip follower">Replied · {replies}</span>')
        else:
            chips.append('<span class="follow-chip">Ghost · 0 replies</span>')
    if person.get("unfollow_status") == "later":
        chips.append('<span class="follow-chip following_only">Queued to unfollow</span>')
    if href.startswith(("http://", "https://")) and not follows_back:
        chips.append(f'<a class="text-link" href="{_e(href)}" target="_blank" rel="noreferrer">Open to unfollow ↗</a>')
    selectable = list_key in ("not_following_back", "following", "unfollow_later")
    check = f'<label class="select"><input type="checkbox" name="usernames" value="{username}"> {link}</label>' if selectable else link
    return f'<div class="run-row follow-row"><div>{check}<span>{_e(when)}</span></div><p class="follow-wrap">{"".join(chips)}</p></div>'


def _follow_insights_board(analysis: dict) -> str:
    ins = analysis.get("insights") or {}
    if not ins:
        return ""
    oldest = ins.get("oldest_non_follower")
    oldest_text = f'Oldest: @{_e(oldest["username"])} ({_e(oldest["since_date"])})' if isinstance(oldest, dict) else "No dated non-followers yet"
    median_days = ins.get("median_days_not_following_back")
    median_text = f"Median wait: {median_days}d · " if median_days is not None else ""
    cohorts = ins.get("top_cohorts") or []
    cohort_links = " · ".join(
        f'<a class="text-link" href="/?view=followers&amp;list=not_following_back&amp;q={quote(str(c["month"]), safe="")}">{_e(c["month"])} ({int(c["count"])})</a>'
        for c in cohorts[:3]
        if isinstance(c, dict)
    ) or "Upload dated export to see follow cohorts"
    return (
        '<section class="board">'
        '<article class="card board-card"><p class="eyebrow">UNFOLLOW TRIAGE · GRAPH SYNC</p>'
        f'<b>{int(ins.get("ghost_non_followers", 0))} ghost · {int(ins.get("engaged_non_followers", 0))} engaged</b>'
        '<p>Ghosts neither follow back nor reply on Threads · <a class="text-link" href="/?view=followers&amp;list=following&amp;uf=ghosts">Filter ghosts →</a></p></article>'
        '<article class="card board-card"><p class="eyebrow">FOLLOW TENURE · WAITING TIME</p>'
        f'<b>{int(ins.get("older_90d_count", 0))} ≥90d · {int(ins.get("older_30d_count", 0))} ≥30d · {int(ins.get("recent_30d_count", 0))} &lt;30d</b>'
        f'<p>{_e(median_text)}{oldest_text} · <a class="text-link" href="/?view=followers&amp;list=not_following_back&amp;sort=oldest">Oldest first →</a></p></article>'
        '<article class="card board-card"><p class="eyebrow">UNFOLLOW LATER SHORTLIST</p>'
        f'<b>{int(ins.get("unfollow_later_count", 0))} queued · {int(ins.get("unfollowed_count", 0))} unfollowed</b>'
        '<p>Filter following → save to queue → unfollow on Threads → mark done · <a class="text-link" href="/?view=followers&amp;list=unfollow_later">Open queue →</a></p></article>'
        '<article class="card board-card"><p class="eyebrow">RATIO &amp; FOLLOW COHORTS</p>'
        f'<b>{ins.get("reciprocity_rate", 0.0)}% reciprocity · {ins.get("follower_following_ratio", 0.0)}x ratio</b>'
        f'<p>Top non-follow months: {cohort_links}</p></article>'
        '</section>'
    )


def _snapshot_diff_banner(diff: dict | None) -> str:
    if not diff:
        return ""
    new_c = int(diff.get("new_followers_count", 0))
    lost_c = int(diff.get("unfollowed_you_count", 0))
    unfol_c = int(diff.get("you_unfollowed_count", 0))
    mut_c = int(diff.get("newly_mutual_count", 0))
    samples = []
    if diff.get("new_followers"):
        samples.append("New: " + ", ".join(f"@{_e(u)}" for u in diff["new_followers"][:5]))
    if diff.get("unfollowed_you"):
        samples.append("Unfollowed you: " + ", ".join(f"@{_e(u)}" for u in diff["unfollowed_you"][:5]))
    sample_line = f'<p class="help">{" | ".join(samples)}</p>' if samples else ""
    return (
        '<section class="panel"><div class="section-head"><div><p class="eyebrow">IMPORT SNAPSHOT DELTA</p>'
        f'<h2>Since previous JSON ({_e(str(diff.get("previous_imported_at", ""))[:10])})</h2></div></div>'
        f'<div class="stats">'
        f'<article class="stat card"><span>New followers</span><b>+{new_c}</b></article>'
        f'<article class="stat card"><span>Unfollowed you</span><b>-{lost_c}</b></article>'
        f'<article class="stat card"><span>You unfollowed</span><b>{unfol_c}</b></article>'
        f'<article class="stat card"><span>Newly mutual</span><b>{mut_c}</b></article>'
        f'</div>{sample_line}</section>'
    )


def _render_followers_view(data: DashboardData, follow_index: AudienceIndex, csrf_input: str, *, status_class: str, is_connected: bool) -> str:
    has_import = data.audience is not None
    graph_engagers = (data.graph_audience or {}).get("engagers") or []
    analysis = data.audience or build_preimport_analysis(data.unfollow_queue, graph_engagers)
    list_key = data.follow_list if data.follow_list in FOLLOW_VIEW_LISTS else AUDIENCE_LISTS[0]
    follow_q = data.follow_query
    uf = data.follow_uf if data.follow_uf in UNFOLLOW_FILTERS else "all"
    sort = data.follow_sort if data.follow_sort in FOLLOW_SORTS else "newest"
    graph_section = _graph_followers_section(data, follow_index, csrf_input, connected=is_connected)
    download_help = (
        '<p class="help">Instagram does not expose full follower lists through the Threads API, so this view reads the files from '
        '<b>Accounts Center → Your information and permissions → Download your information → Threads → JSON</b>. '
        'The upload stays in this admin’s local database and is never sent to the AI provider.</p>'
        '<p class="help">Comparison approach credited to <a class="text-link" href="https://github.com/Xiang511/Threads-Follower" target="_blank" rel="noreferrer">Threads-Follower</a>.</p>'
    )
    counts = analysis["counts"]
    ins = analysis.get("insights") or {}
    exported = quote(follow_q, safe="")
    uf_qs = f"&amp;uf={quote(uf, safe='')}" if uf != "all" else ""
    sort_qs = f"&amp;sort={quote(sort, safe='')}" if sort != "newest" else ""
    q_qs = f"&amp;q={exported}" if exported else ""
    glist_qs = f"&amp;glist={quote(data.graph_list, safe='')}" if data.graph_list else ""
    pills = "".join(
        f'<a class="{"selected" if key == list_key else ""}" href="/?view=followers&amp;list={key}{uf_qs}{sort_qs}{q_qs}{glist_qs}">'
        f'{_e(AUDIENCE_LIST_LABELS[key])} · {len(analysis.get(key, []))}</a>'
        for key in FOLLOW_VIEW_LISTS
    )
    subfilter_bar = ""
    if list_key in ("not_following_back", "following", "unfollow_later"):
        uf_Counts = count_unfollow_filters(analysis, list_key)
        uf_pills = "".join(
            f'<a class="{"selected" if fkey == uf else ""}" href="/?view=followers&amp;list={list_key}&amp;uf={fkey}{sort_qs}{q_qs}{glist_qs}">'
            f'{_e(UNFOLLOW_FILTER_LABELS[fkey])} · {uf_Counts[fkey]}</a>'
            for fkey in UNFOLLOW_FILTERS
        )
        sort_pills = "".join(
            f'<a class="{"selected" if skey == sort else ""}" href="/?view=followers&amp;list={list_key}{uf_qs}&amp;sort={skey}{q_qs}{glist_qs}">'
            f'{_e(FOLLOW_SORT_LABELS[skey])}</a>'
            for skey in FOLLOW_SORTS
        )
        quick_add = (
            f'<form class="search" method="post" action="/followers/unfollow" style="margin:8px 0">{csrf_input}'
            f'<input type="hidden" name="action" value="later">'
            f'<input type="hidden" name="return_list" value="unfollow_later">'
            f'<input name="usernames" placeholder="Add @username1, @username2 to Unfollow Later">'
            f'<button class="button ghost small" type="submit">+ Queue to Unfollow Later</button></form>'
        )
        subfilter_bar = (
            f'<div class="filter-pills"><span class="muted" style="font-size:11px;align-self:center">Filter following:</span>{uf_pills}</div>'
            f'<div class="filter-pills"><span class="muted" style="font-size:11px;align-self:center">Sort:</span>{sort_pills}</div>'
            f'{quick_add}'
        )
    people, shown_total = filter_people(analysis, list_key, follow_q, uf=uf, sort=sort, limit=200)
    empty_msg = (
        '<div class="empty">Nobody matches this list yet.</div>'
        if has_import
        else '<div class="empty">Upload <b>followers.json</b> and <b>following.json</b> below to load your full Following &amp; Not-Following-Back list, or queue @usernames above.</div>'
    )
    rows = "".join(_follow_row(person, list_key) for person in people) or empty_msg
    if list_key in ("not_following_back", "following", "unfollow_later") and people:
        rows = (
            f'<form method="post" action="/followers/unfollow">{csrf_input}'
            f'<input type="hidden" name="return_list" value="{_e(list_key)}">'
            f'<input type="hidden" name="return_uf" value="{_e(uf)}">'
            f'<input type="hidden" name="return_sort" value="{_e(sort)}">'
            f'<input type="hidden" name="return_q" value="{_e(follow_q)}">'
            '<div class="actions" style="margin:10px 0">'
            '<button class="button ghost small" type="button" data-select-follow="true">Select all visible</button>'
            '<button class="button ghost small" type="button" data-select-follow="false">Clear selection</button>'
            '<button class="button small" type="submit" name="action" value="later">Save selected to Unfollow Later</button>'
            '<button class="button ghost small" type="submit" name="action" value="unfollowed">Mark selected as Unfollowed ✓</button>'
            '<button class="button ghost small" type="submit" name="action" value="keep">Remove from Unfollow Later</button>'
            '<button class="button ghost small" type="button" data-copy-usernames="true">Copy @usernames</button>'
            f'</div>{rows}</form>'
        )
    page_note = f'<p class="help">Showing {len(people)} of {shown_total} matches. Export the CSV for the full list.</p>' if shown_total > len(people) else ""
    tag_totals = {"mutual": 0, "follower": 0, "following_only": 0, "none": 0}
    for item in data.insights:
        tag = follow_index.tag(item.get("source_url"))
        if tag in tag_totals:
            tag_totals[tag] += 1
    tie_in = (
        f'<p class="small-copy">{tag_totals["mutual"]} mutual · {tag_totals["follower"]} fan · '
        f'{tag_totals["following_only"]} not-following-back · {tag_totals["none"]} not connected, '
        f'{tag_totals["mutual"] + tag_totals["follower"] + tag_totals["following_only"]} of {len(data.insights)} saved insights '
        'come from accounts already linked to this import.</p>'
    ) if follow_index.enabled and data.insights else ""
    search_form = (
        f'<form class="search" method="get"><input type="hidden" name="view" value="followers">'
        f'<input type="hidden" name="list" value="{_e(list_key)}">'
        f'<input type="hidden" name="uf" value="{_e(uf)}">'
        f'<input type="hidden" name="sort" value="{_e(sort)}">'
        f'<input name="q" value="{_e(follow_q)}" placeholder="Search @username or YYYY-MM"><button class="button ghost small">Search</button></form>'
    )
    stats_and_board = (
        f'<div class="stats">'
        f'<article class="stat card"><span>Followers</span><b>{counts["followers"]}</b><small>Accounts following Rahimam · {ins.get("fan_rate", 0.0)}% one-way fans</small></article>'
        f'<article class="stat card"><span>Following</span><b>{counts["following"]}</b><small>Accounts Rahimam follows · {ins.get("follower_following_ratio", 0.0)}x follower ratio</small></article>'
        f'<article class="stat card"><span>Mutuals</span><b>{counts["mutuals"]}</b><small>You follow each other · {ins.get("reciprocity_rate", 0.0)}% reciprocity</small></article>'
        f'<article class="stat card"><span>Not following back</span><b>{counts["percent_not_following_back"]}%</b><small>{counts["not_following_back"]} of who she follows · {int(ins.get("unfollow_later_count", 0))} queued</small></article>'
        f'</div>'
        f'{_follow_insights_board(analysis)}'
        f'{_snapshot_diff_banner(data.snapshot_diff)}'
        f'{tie_in}'
    ) if has_import else _follow_insights_board(analysis)
    import_panel = (
        f'<section class="panel"><div class="section-head"><div><p class="eyebrow">REFRESH</p><h2>Re-import or clear</h2></div>'
        f'<form method="post" action="/followers/clear">{csrf_input}<button class="button ghost small" data-confirm="Clear the saved follower import and unfollow queue?">Clear import</button></form></div>{_import_form(csrf_input)}{download_help}</section>'
        if has_import
        else f'<section class="panel"><div class="section-head"><div><p class="eyebrow">NOT IMPORTED YET</p><h2>Upload the two export files</h2></div></div>{_import_form(csrf_input)}{download_help}</section>'
    )
    header_right = (
        f'<div class="actions"><a class="button ghost small" href="/followers/export.csv?list={_e(list_key)}{uf_qs}{sort_qs}{q_qs}">Export CSV</a></div>'
        if has_import
        else f'<span class="status {status_class}">{_e(data.connection)}</span>'
    )
    return (
        f'<div class="page-head"><div><p class="eyebrow">FOLLOW-BACK INSIGHT &amp; UNFOLLOW PLANNER</p><h1>Followers</h1>'
        f'<p class="lead">Filter your following list by non-followers, ghost accounts (0 replies), or follow age to unfollow them later, synchronized with live Threads Graph telemetry.</p></div>'
        f'{header_right}</div>'
        f'{stats_and_board}'
        f'<section class="panel"><div class="section-head"><div><p class="eyebrow">LISTS &amp; UNFOLLOW FILTERS</p><h2>{_e(AUDIENCE_LIST_LABELS[list_key])}</h2></div>{search_form}</div>'
        f'<div class="filter-pills">{pills}</div>{subfilter_bar}{rows}{page_note}</section>'
        f'{import_panel}'
        f'{graph_section}'
    )


def _import_form(csrf_input: str) -> str:
    return (
        f'<form class="import-grid" method="post" action="/followers/import" enctype="multipart/form-data">{csrf_input}'
        '<label class="file-field"><span>followers.json</span><input type="file" name="followers" accept=".json,application/json" required></label>'
        '<label class="file-field"><span>following.json</span><input type="file" name="following" accept=".json,application/json" required></label>'
        '<button class="button">Import export</button></form>'
    )



def _insight_card(item: dict, *, selectable: bool = False, selected: bool = False, follow: str = "", engager: dict | None = None) -> str:
    checkbox = f'<label class="select"><input type="checkbox" name="insight_ids" value="{int(item["id"])}"{" checked" if selected else ""}> Use this evidence</label>' if selectable else ""
    engager_chip = ""
    if isinstance(engager, dict) and int(engager.get("replies_count", 0)) >= 2:
        engager_chip = f'<span class="follow-chip follower">Active replier · {int(engager["replies_count"])} replies</span>'
    return f'''<article class="evidence card" id="insight-{int(item["id"])}">
      <div class="card-top"><span class="tag">{_e(item["theme"])}</span><time>{_e(item.get("created_at", "")[:10])}</time></div>
      <blockquote>“{_e(item["quote"])}”</blockquote><p class="idea"><b>Product angle</b> · {_e(item["ebook_idea"])}</p>
      <div class="card-bottom">{_source(item)}<span class="follow-wrap">{engager_chip}{_follow_chip(follow)}{checkbox}</span></div>
    </article>'''


def _demographics_grid(demographics: dict) -> str:
    if not isinstance(demographics, dict) or not demographics:
        return ""
    titles = {"country": "Top countries", "city": "Top cities", "age": "Age distribution", "gender": "Gender split"}
    cards = []
    for key in ("country", "city", "age", "gender"):
        rows = demographics.get(key)
        if not isinstance(rows, list) or not rows:
            continue
        total = max(1, sum(int(r.get("value", 0)) for r in rows if isinstance(r, dict)))
        items_html = []
        for row in rows[:5]:
            if not isinstance(row, dict):
                continue
            label = _e(str(row.get("key", "")))
            val = int(row.get("value", 0))
            pct = round(100 * val / total, 1)
            items_html.append(
                f'<div class="demo-row"><div class="demo-meta"><b>{label}</b><span>{val:,} ({pct}%)</span></div>'
                f'<div class="demo-bar"><i style="width:{min(100.0, max(4.0, pct))}%"></i></div></div>'
            )
        if items_html:
            cards.append(f'<article class="card board-card"><p class="eyebrow">{_e(titles[key].upper())}</p>{"".join(items_html)}</article>')
    if not cards:
        return ""
    return f'<div class="board">{"".join(cards)}</div>'


def _graph_community_row(person: dict, follow_index: AudienceIndex) -> str:
    username = _e(str(person.get("username", "")))
    href = str(person.get("href", ""))
    link = (
        f'<a class="source" href="{_e(href)}" target="_blank" rel="noreferrer">@{username} ↗</a>'
        if href.startswith(("http://", "https://")) else f"@{username}"
    )
    replies = int(person.get("replies_count", 1) or 1)
    insight_ids = [int(i) for i in person.get("insight_ids", []) if str(i).isdigit()]
    last_seen = str(person.get("last_seen", "")).strip()
    meta_parts = [f"{replies} repl{'y' if replies == 1 else 'ies'}"]
    if insight_ids:
        meta_parts.append(f"{len(insight_ids)} saved insight{'' if len(insight_ids) == 1 else 's'}")
    if last_seen:
        meta_parts.append(f"Last active {_e(last_seen)}")
    sample = str(person.get("sample_quote", "")).strip()
    quote_line = f'<p class="muted">“{_e(sample[:130])}”</p>' if sample else ""
    themes = "".join(f'<span class="follow-chip">{_e(t)}</span>' for t in person.get("themes", [])[:3])
    follow_tag = follow_index.tag(href)
    follow_badge = _follow_chip(follow_tag) if follow_tag and follow_tag != "none" else ""
    actions = f'<a class="text-link" href="/?view=research&amp;q={quote(str(person.get("username", "")), safe="")}">Search replies →</a>'
    if insight_ids:
        sel = ",".join(str(i) for i in insight_ids[:10])
        actions += f' · <a class="text-link" href="/?view=studio&amp;select={sel}">Draft in Studio →</a>'
    return (
        f'<div class="run-row follow-row"><div>{link}<span>{" · ".join(meta_parts)}</span></div>'
        f'<div>{quote_line}<div class="follow-wrap">{follow_badge}{themes}{actions}</div></div></div>'
    )


def _graph_followers_section(data: DashboardData, follow_index: AudienceIndex, csrf_input: str, *, connected: bool = False) -> str:
    graph = data.graph_audience
    glist = data.graph_list
    query = data.follow_query
    sync_btn = (
        f'<form method="post" action="/followers/sync">{csrf_input}'
        f'<input type="hidden" name="queue" value="on">'
        f'<button class="button small" {"" if connected else "disabled"}>Sync from Threads Graph ↻</button></form>'
    )
    if not graph:
        return (
            '<section class="panel"><div class="section-head"><div><p class="eyebrow">THREADS GRAPH API · AUTOMATIC SYNC</p>'
            '<h2>Live follower telemetry &amp; active community</h2></div>'
            f'{sync_btn}</div>'
            '<p class="help">Pull live <b>followers_count</b>, <b>follower_demographics</b> (country, city, age, gender), '
            'and an automatic <b>Active Community Roster</b> from your Threads replies directly via the Graph API, no manual JSON download needed. '
            'Running a Research job also updates your active community automatically.</p></section>'
        )
    counts = graph["counts"]
    delta = counts.get("followers_delta")
    delta_label = f"+{delta:,} since previous sync" if isinstance(delta, int) and delta > 0 else (f"{delta:,} since previous sync" if isinstance(delta, int) and delta < 0 else "Synced from /v1.0/me/threads_insights")
    profile = graph.get("profile") or {}
    handle = f'@{_e(profile["username"])}' if profile.get("username") else "Connected profile"
    metrics = graph.get("metrics") or {}
    reach = int(metrics.get("views", 0))
    likes = int(metrics.get("likes", 0))
    gkey = glist if glist in GRAPH_COMMUNITY_LISTS else GRAPH_COMMUNITY_LISTS[0]
    exported_q = quote(query, safe="")
    list_qs = f"&amp;list={quote(data.follow_list, safe='')}" if data.follow_list else ""
    uf_qs = f"&amp;uf={quote(data.follow_uf, safe='')}" if data.follow_uf and data.follow_uf != "all" else ""
    sort_qs = f"&amp;sort={quote(data.follow_sort, safe='')}" if data.follow_sort and data.follow_sort != "newest" else ""
    pills = "".join(
        f'<a class="{"selected" if key == gkey else ""}" href="/?view=followers&amp;glist={key}{list_qs}{uf_qs}{sort_qs}{f"&amp;q={exported_q}" if exported_q else ""}">'
        f'{_e(GRAPH_COMMUNITY_LABELS[key])} · {len(graph.get(key, []))}</a>'
        for key in GRAPH_COMMUNITY_LISTS
    )
    people, shown_total = filter_graph_people(graph, gkey, query, limit=100)
    rows = "".join(_graph_community_row(p, follow_index) for p in people) or '<div class="empty">No community replies recorded for this filter yet. Run research or click Sync from Threads Graph.</div>'
    more_note = f'<p class="help">Showing {len(people)} of {shown_total} active community accounts.</p>' if shown_total > len(people) else ""
    synced_stamp = _e(str(graph.get("synced_at", ""))[:16].replace("T", " "))
    follower_spark = _svg_sparkline([int(h.get("followers_count", 0)) for h in data.graph_history], label="Followers trend")
    demographics_block = _demographics_grid(graph.get("demographics") or {})
    if not demographics_block and counts["followers_count"] < 100:
        demographics_block = '<p class="help">Follower demographics breakdown (country, city, age, gender) unlocks automatically once your account reaches 100 followers on Threads.</p>'
    return (
        f'<section class="panel"><div class="section-head"><div><p class="eyebrow">LIVE THREADS GRAPH · {_e(handle.upper())}</p>'
        f'<h2>Graph followers &amp; active community</h2><p class="help">Last synced {synced_stamp or "just now"} · automatic from Threads Graph API</p></div>'
        f'<div class="actions"><a class="button ghost small" href="/followers/graph.csv?glist={_e(gkey)}{f"&amp;q={exported_q}" if exported_q else ""}">Export Graph CSV</a>{sync_btn}</div></div>'
        f'<div class="stats">'
        f'<article class="stat card"><span>Graph followers</span><b>{counts["followers_count"]:,}</b>{follower_spark}<small>{_e(delta_label)}</small></article>'
        f'<article class="stat card"><span>Active repliers</span><b>{counts["active_repliers"]:,}</b><small>Discovered automatically from thread replies</small></article>'
        f'<article class="stat card"><span>Insight contributors</span><b>{counts["insight_contributors"]:,}</b><small>Community members cited in saved evidence</small></article>'
        f'<article class="stat card"><span>Account engagement</span><b>{reach:,}</b><small>Views · {likes:,} likes across insights window</small></article>'
        f'</div>'
        f'{demographics_block}'
        f'<div class="filter-pills">{pills}</div>{rows}{more_note}</section>'
    )


def _draft_references(content: dict) -> str:
    rows = []
    for reference in content.get("references", []):
        if not isinstance(reference, dict):
            continue
        url = str(reference.get("url", "")).strip()
        if not url.startswith(("https://", "http://")):
            continue
        theme = str(reference.get("theme", "")).strip()
        label = f"{_e(theme)} · " if theme else ""
        rows.append(f'<li>{label}<a href="{_e(url)}" target="_blank" rel="noreferrer">{_e(url)}</a></li>')
    if not rows:
        return ""
    return f'<div class="draft-refs"><b>Reference posts</b><ul>{"".join(rows)}</ul></div>'


def _draft_content(draft: dict) -> str:
    content = draft["content"]
    if draft["kind"] == "threads_post":
        return f'<div class="draft-copy">{_e(content.get("post", ""))}</div>'
    if draft["kind"] == "ebook_outline":
        chapters = "".join(f'<li><b>{_e(ch.get("title", ""))}</b><span>{_e(ch.get("outcome", ""))}</span></li>' for ch in content.get("chapters", []) if isinstance(ch, dict))
        return f'<p><b>Premise:</b> {_e(content.get("premise", ""))}</p><p><b>Reader need:</b> {_e(content.get("intended_reader_need", ""))}</p><ol class="chapter-list">{chapters}</ol>{_draft_references(content)}'
    return f'<p><b>Concept:</b> {_e(content.get("concept", ""))}</p><p><b>Format:</b> {_e(content.get("format", ""))}</p><p><b>Visual direction:</b> {_e(content.get("visual_direction", ""))}</p><div class="draft-copy">{_e(content.get("copy", ""))}</div>{_draft_references(content)}'


def _draft_edit_drawer(draft: dict, token: str) -> str:
    content = draft["content"]
    did = int(draft["id"])
    title_input = f'<label class="limit-field"><span>Title</span><input name="title" maxlength="160" value="{_e(draft["title"])}" required></label>'
    if draft["kind"] == "threads_post":
        post_text = str(content.get("post", ""))
        fields = (
            f'<label class="focus-field"><span>Threads post (<b data-char-count="{did}">{len(post_text)}</b> / {POST_TEXT_MAX} chars · split blank lines for multi-post thread)</span>'
            f'<textarea name="post" data-char-source="{did}" required>{_e(post_text)}</textarea></label>'
        )
    elif draft["kind"] == "ebook_outline":
        chapters = [ch for ch in content.get("chapters", []) if isinstance(ch, dict)]
        ch_inputs = "".join(
            f'<div class="two-col">'
            f'<label class="limit-field"><span>Chapter {idx} title</span><input name="chapter_title" value="{_e(ch.get("title", ""))}"></label>'
            f'<label class="limit-field"><span>Chapter {idx} outcome</span><input name="chapter_outcome" value="{_e(ch.get("outcome", ""))}"></label>'
            f'</div>'
            for idx, ch in enumerate(chapters, 1)
        )
        fields = (
            f'<label class="limit-field"><span>Premise</span><input name="premise" value="{_e(content.get("premise", ""))}"></label>'
            f'<label class="limit-field"><span>Intended reader need</span><input name="intended_reader_need" value="{_e(content.get("intended_reader_need", ""))}"></label>'
            f'{ch_inputs}'
        )
    else:
        fields = (
            f'<label class="limit-field"><span>Format</span><input name="format" value="{_e(content.get("format", "Quote Card"))}"></label>'
            f'<label class="limit-field"><span>Concept</span><input name="concept" value="{_e(content.get("concept", ""))}"></label>'
            f'<label class="limit-field"><span>Visual direction</span><input name="visual_direction" value="{_e(content.get("visual_direction", ""))}"></label>'
            f'<label class="focus-field"><span>Copy</span><textarea name="copy">{_e(content.get("copy", ""))}</textarea></label>'
        )
    return (
        f'<details class="edit-drawer"><summary class="text-link">Edit draft</summary>'
        f'<form class="edit-form" method="post" action="/content/drafts/{did}/edit">{token}{title_input}{fields}'
        f'<button class="button small" type="submit">Save changes</button></form></details>'
    )


def _draft_card(draft: dict, csrf: str = "", *, connected: bool = False) -> str:
    labels = {"threads_post": "Threads post", "ebook_outline": "eBook outline", "design_brief": "Design brief"}
    statuses = {"draft": "Needs review", "approved": "Approved", "scheduled": "Scheduled", "published": "Published", "archived": "Archived"}
    did = int(draft["id"])
    token = f'<input type="hidden" name="csrf" value="{_e(csrf)}">'
    source_ids = draft.get("source_ids", [])
    evidence = ", ".join(f'<a href="/?view=research&amp;q={int(i)}#insight-{int(i)}">#{int(i)}</a>' for i in source_ids if str(i).isdigit())
    content = draft["content"]
    published = content.get("published") if isinstance(content, dict) else None
    char_badge = ""
    if draft["kind"] == "threads_post":
        length = len(str(content.get("post", "")))
        char_badge = f'<span class="follow-chip">{length} / {POST_TEXT_MAX} chars</span>'
    pub_badge = ""
    if isinstance(published, dict):
        pub_url = str(published.get("url", ""))
        pub_badge = (
            f'<a class="status approved" href="{_e(pub_url)}" target="_blank" rel="noreferrer">Published on Threads ↗</a>'
            if pub_url.startswith(("http://", "https://"))
            else '<span class="status approved">Published on Threads</span>'
        )
    sched_badge = f'<span class="follow-chip mutual">Scheduled {_e(draft["scheduled_at"][:16].replace("T", " "))}</span>' if draft.get("scheduled_at") else ""
    star_label = "★ Starred" if draft.get("starred") else "☆ Star"
    actions = f'<form method="post" action="/content/drafts/{did}/star">{token}<button class="button ghost small">{star_label}</button></form>'
    if draft["status"] != "approved" and draft["status"] != "published":
        actions += f'<form method="post" action="/content/drafts/{did}/status">{token}<input type="hidden" name="status" value="approved"><button class="button small">Approve for use</button></form>'
    if draft["kind"] == "threads_post" and draft["status"] in ("approved", "scheduled") and not published:
        actions += f'<form method="post" action="/content/drafts/{did}/publish">{token}<button class="button small" {"" if connected else "disabled"}>Publish to Threads ↗</button></form>'
        actions += f'<form method="post" action="/content/drafts/{did}/publish">{token}<input type="hidden" name="as_thread" value="on"><button class="button ghost small" {"" if connected else "disabled"}>Publish as Thread</button></form>'
    if draft["status"] != "archived":
        actions += f'<form method="post" action="/content/drafts/{did}/status">{token}<input type="hidden" name="status" value="archived"><button class="button ghost small">Archive</button></form>'
    actions += f'<button class="button ghost small" type="button" data-copy="draft-{did}">Copy text</button>'
    actions += f'<a class="button ghost small" href="/content/drafts/{did}/card.html" target="_blank" rel="noreferrer">Card preview</a>'
    actions += f'<a class="button ghost small" href="/content/drafts/{did}/ebook.md">Export .md</a>'

    rewrites = (
        '<div class="actions" style="margin-top:8px">'
        + "".join(
            f'<form method="post" action="/content/drafts/{did}/adjust">{token}<input type="hidden" name="modifier" value="{mod}"><button class="button ghost small">{lbl}</button></form>'
            for mod, lbl in (("shorter", "Shorter"), ("warmer", "Warmer"), ("bm", "BM"), ("en", "EN"), ("question_hook", "+ Question"))
        )
        + '</div>'
    ) if draft["kind"] == "threads_post" and not published else ""

    sched_form = (
        f'<form class="actions" method="post" action="/content/drafts/{did}/schedule" style="margin-top:8px">{token}'
        f'<input type="datetime-local" name="scheduled_at" value="{_e(str(draft.get("scheduled_at", ""))[:16])}" style="min-height:34px;border:1px solid var(--line);border-radius:8px;padding:4px 8px">'
        f'<button class="button ghost small" type="submit">Schedule</button></form>'
    ) if not published else ""

    return f'''<article class="draft card">
      <div class="card-top"><span class="tag">{_e(labels.get(draft["kind"], draft["kind"]))}</span><span class="follow-wrap">{char_badge}{sched_badge}{pub_badge}<span class="status {draft["status"]}">{_e(statuses.get(draft["status"], draft["status"]))}</span></span></div>
      <h3>{_e(draft["title"])}</h3><div id="draft-{did}" class="draft-body">{_draft_content(draft)}</div>
      <p class="muted small-copy">Grounded in insight {evidence or "none"} · {_e(draft.get("created_at", "")[:10])}</p>
      <div class="actions">{actions}</div>{rewrites}{sched_form}
      {_draft_edit_drawer(draft, token)}
    </article>'''


def _theme_filter_pills(insights: list[dict], query: str) -> str:
    theme_counts: dict[str, int] = {}
    for item in insights:
        t = str(item.get("theme", "")).strip()
        if t:
            theme_counts[t] = theme_counts.get(t, 0) + 1
    top_themes = sorted(theme_counts.items(), key=lambda x: (-x[1], x[0]))[:8]
    if not top_themes:
        return ""
    return '<div class="filter-pills"><a class="' + ("selected" if not query else "") + '" href="/?view=research">All</a>' + "".join(
        f'<a class="{"selected" if query.casefold() == t.casefold() else ""}" href="/?view=research&amp;q={quote(t, safe="")}">{_e(t)} · {cnt}</a>'
        for t, cnt in top_themes
    ) + "</div>"


def _render_discovery_panel(data: DashboardData, csrf_input: str, *, is_connected: bool, configured: bool) -> str:
    seed = _e(data.autocomplete_seed)
    ac_rows = "".join(
        f'<tr><td>{_e(item["query"])}</td><td>{item["demand"]}</td><td>{item["icp_fit"]}</td><td>{item["risk"]}</td><td><b>{item["opportunity_score"]}</b></td></tr>'
        for item in data.autocomplete_results[:15]
    )
    ac_table = (
        f'<div class="table-wrap" style="margin-top:12px"><table class="metrics"><thead><tr><th>MY Search Suggestion</th><th>Demand</th><th>ICP Fit</th><th>Risk</th><th>Opportunity</th></tr></thead><tbody>{ac_rows}</tbody></table></div>'
        if ac_rows
        else ""
    )
    return (
        '<section class="panel"><div class="section-head"><div><p class="eyebrow">DISCOVERY · THREADS SEARCH &amp; MY AUTOCOMPLETE</p>'
        '<h2>Topic &amp; demand mining</h2><p class="help">Expand Malaysian relationship search phrases (`hl=ms&amp;gl=my`) or mine public Threads posts via `keyword_search`.</p></div></div>'
        '<div class="two-col">'
        f'<form class="search" method="get" action="/"><input type="hidden" name="view" value="research">'
        f'<input name="ac" value="{seed}" placeholder="Google MY seed, e.g. tenang hati, boundaries"><button class="button ghost small">Expand Demand</button></form>'
        f'<form class="search" method="post" action="/research/keyword">{csrf_input}'
        f'<input name="keyword" placeholder="Threads keyword_search, e.g. penat hubungan">'
        f'<select name="mode" style="min-height:40px;border:1px solid var(--line);border-radius:8px;padding:6px 8px"><option value="KEYWORD">Keyword</option><option value="TAG">Tag</option></select>'
        f'<button class="button small" {"" if is_connected and configured else "disabled"}>Mine Threads Search</button></form>'
        f'</div>{ac_table}</section>'
    )


def _render_inbox_view(data: DashboardData, csrf_input: str, *, is_connected: bool, configured: bool) -> str:
    status = data.inbox_status or "open"
    pills = "".join(
        f'<a class="{"selected" if st == status else ""}" href="/?view=inbox&amp;status={st}">{_e(lbl)}</a>'
        for st, lbl in (("open", "Open replies"), ("replied", "Replied"), ("dismissed", "Hidden / Dismissed"), ("all", "All"))
    )
    rows = []
    for item in data.inbox_items:
        iid = int(item["id"])
        uname = _e(item.get("username") or "reader")
        link = f'<a class="source" href="{_e(item.get("post_permalink", ""))}" target="_blank" rel="noreferrer">View thread ↗</a>' if str(item.get("post_permalink", "")).startswith(("http://", "https://")) else ""
        draft_val = _e(item.get("draft_reply", ""))
        hide_action = "false" if item.get("is_hidden") else "true"
        hide_label = "Unhide reply" if item.get("is_hidden") else "Hide on Threads"
        rows.append(
            f'<article class="card draft">'
            f'<div class="card-top"><span class="tag">@{uname}</span><span class="status { _e(item.get("status", "open")) }">{_e(item.get("status", "open"))}</span></div>'
            f'<blockquote style="margin:10px 0">{_e(item.get("text", ""))}</blockquote>'
            f'<p class="muted small-copy">{link} · {_e(str(item.get("created_at", ""))[:16].replace("T", " "))}</p>'
            f'<form method="post" action="/inbox/{iid}/draft" style="margin-top:8px">{csrf_input}'
            f'<button class="button ghost small" {"" if configured else "disabled"}>AI Draft Reply</button></form>'
            f'<form class="edit-form" method="post" action="/inbox/{iid}/reply">{csrf_input}'
            f'<textarea name="reply_text" maxlength="{POST_TEXT_MAX}" placeholder="Write a warm non-clinical reply..." required>{draft_val}</textarea>'
            f'<div class="actions"><button class="button small" {"" if is_connected else "disabled"}>Send Reply on Threads</button>'
            f'</div></form>'
            f'<form method="post" action="/inbox/{iid}/hide" style="margin-top:8px">{csrf_input}<input type="hidden" name="hide" value="{hide_action}"><button class="button ghost small" {"" if is_connected else "disabled"}>{hide_label}</button></form>'
            '</article>'
        )
    cards = "".join(rows) or '<div class="empty">Inbox is clear. Sync replies from Threads or configure the `/webhooks/threads` webhook endpoint.</div>'
    sync_form = f'<form method="post" action="/inbox/sync">{csrf_input}<button class="button small" {"" if is_connected else "disabled"}>Pull recent replies ↻</button></form>'
    return (
        f'<div class="page-head"><div><p class="eyebrow">ENGAGEMENT MODERATION &amp; REPLIES</p><h1>Engagement inbox</h1>'
        f'<p class="lead">Triage incoming Threads replies, draft safe non-clinical responses, reply via API, or moderate spam with /manage_reply.</p></div>{sync_form}</div>'
        f'<div class="filter-pills">{pills}</div><div class="draft-grid">{cards}</div>'
    )


def _render_knowledge_view(data: DashboardData, csrf_input: str) -> str:
    node_cards = "".join(
        f'<article class="card">'
        f'<div class="card-top"><span class="tag">{_e(node.get("category", "brand"))}</span>'
        f'<span class="muted">[[{_e(node["slug"])}]]</span></div>'
        f'<h3>{_e(node["title"])}</h3>'
        f'<p class="help">{_e(node.get("summary", ""))}</p>'
        f'<p class="small-copy">{_e(node.get("body", ""))}</p>'
        f'<div class="chips">{"".join(f"<span>[[{_e(lk)}]]</span>" for lk in node.get("links", []))}</div>'
        f'<form method="post" action="/knowledge/nodes/{_e(node["slug"])}/delete">{csrf_input}'
        f'<button class="button ghost small" data-confirm="Delete this knowledge note?">Delete</button></form>'
        '</article>'
        for node in data.knowledge_nodes
    ) or '<div class="empty">No knowledge nodes saved yet.</div>'
    edge_list = "".join(
        f'<li><code>[[{_e(e["source_slug"])}]]</code> → <code>[[{_e(e["target_slug"])}]]</code></li>'
        for e in data.knowledge_edges[:24]
    ) or '<li class="muted">Add [[slug]] links inside note bodies to connect brand concepts.</li>'
    return (
        '<div class="page-head"><div><p class="eyebrow">BRAND MEMORY &amp; WIKI-LINKS</p><h1>Knowledge graph</h1>'
        '<p class="lead">Structured Book-of-Knowledge notes compiled into bounded Fact-Sheets before every AI research and drafting call.</p></div></div>'
        f'<section class="panel"><div class="section-head"><div><p class="eyebrow">ADD OR UPDATE NOTE</p><h2>Knowledge node</h2></div></div>'
        f'<form class="edit-form" method="post" action="/knowledge/nodes">{csrf_input}'
        '<div class="two-col">'
        '<label class="limit-field"><span>Slug</span><input name="slug" placeholder="e.g. story-kopi-senja" required></label>'
        '<label class="limit-field"><span>Category</span><select name="category"><option value="brand">brand</option><option value="guardrails">guardrails</option><option value="formats">formats</option><option value="catalog">catalog</option><option value="story">story</option></select></label>'
        '</div>'
        '<label class="limit-field"><span>Title</span><input name="title" placeholder="Short memorable title" required></label>'
        '<label class="limit-field"><span>Summary (used in prompts)</span><input name="summary" placeholder="One concise takeaway line" required></label>'
        '<label class="focus-field"><span>Body (use [[other-slug]] for links)</span><textarea name="body" required></textarea></label>'
        '<button class="button small" type="submit">Save knowledge note</button></form></section>'
        f'<div class="draft-grid">{node_cards}</div>'
        f'<section class="panel"><div class="section-head"><div><p class="eyebrow">WIKI-LINK CONNECTIONS</p><h2>Concept edges</h2></div></div><ul>{edge_list}</ul></section>'
    )


def _render_calendar_view(data: DashboardData) -> str:
    scheduled = [d for d in data.drafts if d.get("scheduled_at") or d.get("status") in ("scheduled", "approved", "published")]
    scheduled.sort(key=lambda d: (0 if d.get("scheduled_at") else 1, str(d.get("scheduled_at") or d.get("created_at") or "")))
    rows = "".join(
        f'<tr><td>{_e(str(d.get("scheduled_at") or d.get("created_at", ""))[:16].replace("T", " "))}</td>'
        f'<td><b>{_e(d.get("title", ""))}</b></td><td>{_e(d.get("kind", ""))}</td>'
        f'<td><span class="status {_e(d.get("status", "draft"))}">{_e(d.get("status", "draft"))}</span></td>'
        f'<td><a class="text-link" href="/content/drafts/{int(d["id"])}/card.html" target="_blank" rel="noreferrer">Card ↗</a> · '
        f'<a class="text-link" href="/content/drafts/{int(d["id"])}/ebook.md">.md ↓</a></td></tr>'
        for d in scheduled
    ) or '<tr><td colspan="5" class="muted">No approved or scheduled drafts yet. Schedule items from the Draft Library.</td></tr>'
    return (
        '<div class="page-head"><div><p class="eyebrow">QUEUE &amp; PUBLISHING SCHEDULE</p><h1>Publishing calendar</h1>'
        '<p class="lead">Upcoming scheduled Threads posts, approved drafts, and ebook handoff packs.</p></div>'
        '<div class="actions"><a class="button ghost small" href="/content/export/publish-pack?format=md">Download Publish Pack (.md)</a>'
        '<a class="button small" href="/content/export/publish-pack?format=ics">Export .ics Calendar</a></div></div>'
        f'<section class="panel"><div class="table-wrap"><table class="metrics"><thead><tr><th>When (UTC)</th><th>Title</th><th>Kind</th><th>Status</th><th>Exports</th></tr></thead><tbody>{rows}</tbody></table></div></section>'
    )


def render_dashboard(data: DashboardData, *, logout_action: str = "") -> str:
    view, connection, expiry = data.view, data.connection, data.expiry
    insights, runs, audiences, drafts = data.insights, data.runs, data.audiences, data.drafts
    query, error, configured = data.query, data.error, data.configured
    selection, status_filter = data.selection, data.status_filter
    csrf = data.csrf
    model = data.model
    csrf_input = f'<input type="hidden" name="csrf" value="{_e(csrf)}">'
    threads_configured = data.threads_configured
    is_connected = connection.startswith("Connected")
    follow_index = AudienceIndex(data.audience, data.graph_audience)
    views = {"overview", "research", "followers", "audiences", "studio", "library", "calendar", "inbox", "knowledge", "settings"}
    view = view if view in views else "overview"
    labels = {
        "overview": "Overview",
        "research": "Research",
        "followers": "Followers",
        "audiences": "Audiences",
        "studio": "Studio",
        "library": "Draft library",
        "calendar": "Calendar",
        "inbox": "Inbox",
        "knowledge": "Knowledge",
        "settings": "Connections & settings",
    }
    nav = "".join(f'<a class="nav-link {"active" if view == key else ""}" href="/?view={key}"><span class="nav-mark"></span>{label}</a>' for key, label in labels.items())
    total_evidence = len(insights)
    latest = runs[0] if runs else None
    total_runs = len(runs)
    total_drafts = len(drafts)
    topic_text = " · ".join(latest["themes"][:4]) if latest else "No research run yet"
    status_class = "connected" if is_connected else "disconnected"
    nav_error = f'<div class="notice error">{_e(error)}</div>' if error else ""
    notice_banner = f'<div class="notice">{_e(data.notice)}</div>' if data.notice else ""
    source_count = sum(item["evidence_count"] for item in audiences)
    latest_posts = latest.get("posts", []) if latest else []
    scored_analytics = score_posts(latest_posts)
    top_posts = scored_analytics["posts"][:6]
    post_rows = "".join(
        f'<tr><td><a class="source" href="{_e(p.get("permalink", ""))}" target="_blank" rel="noreferrer">{_e((p.get("text") or "Untitled")[:95])} ↗</a></td>'
        f'<td>{_e(p.get("metrics", {}).get("views", "-"))}</td><td>{_e(p.get("metrics", {}).get("likes", "-"))}</td>'
        f'<td>{_e(p.get("metrics", {}).get("replies", "-"))}</td><td>{_e(p.get("metrics", {}).get("reposts", "-"))}</td>'
        f'<td>{_e(p.get("weighted_score", 0))} ({_e(p.get("weighted_rate", 0.0))}%){" · <span class=tag>Outlier " + str(p.get("outlier_ratio")) + "x</span>" if p.get("is_outlier") else ""}</td></tr>'
        for p in top_posts if str(p.get("permalink", "")).startswith(("https://", "http://"))
    ) or '<tr><td colspan="6" class="muted">No post metrics saved yet. Run research to capture a bounded sample.</td></tr>'

    best_hours_line = ""
    if scored_analytics["best_hours"]:
        best_hours_line = '<p class="small-copy"><b>Best MYT posting hours (weighted avg):</b> ' + " · ".join(
            f'{_e(h["label"])} ({h["avg_score"]})' for h in scored_analytics["best_hours"][:3]
        ) + "</p>"

    profile = (data.graph_audience or {}).get("profile") or {}
    acct_handle = str(profile.get("username") or "rahimam").lstrip("@")
    avatar_img = (
        f'<img src="{AVATAR_PATH}" alt="" width="22" height="22" '
        'style="border-radius:50%;object-fit:cover;display:block;flex-shrink:0">'
    )
    account_badge = f'<span class="account"><i class="dot {status_class}"></i>{avatar_img}<span class="ph-at">@{_e(acct_handle)}</span> Threads</span>'

    graph_summary = ""
    if data.graph_audience:
        gc = data.graph_audience["counts"]
        graph_summary = f' · <a class="text-link" href="/?view=followers">{gc["followers_count"]:,} Graph followers &amp; {gc["active_repliers"]} active repliers</a>'

    follower_spark = _svg_sparkline([int(h.get("followers_count", 0)) for h in data.graph_history], label="Followers trend")
    engagement_spark = _svg_sparkline(
        [int(h.get("likes", 0)) + 2 * int(h.get("replies", 0)) for h in data.graph_history],
        label="Engagement trend",
        stroke="#B96444",
    )

    if view == "overview":
        run_note = f"Last run: {_e(latest['created_at'][:16].replace('T', ' '))} · {_e(latest['posts_sampled'])} posts · {_e(latest['insights_count'])} insights" if latest else "Your first run creates a traceable research baseline."
        top_audiences = "".join(
            f'<a class="segment-row" href="/?view=audiences"><span>{_e(a["name"])}'
            f'{(" · <small class=muted>" + str(a.get("draft_count", 0)) + " drafts</small>") if a.get("draft_count") else " · <small class=muted>Underserved</small>"}'
            f'</span><b>{a["evidence_count"]}</b></a>'
            for a in audiences[:4]
        ) or '<p class="muted">Run research to find recurring themes.</p>'
        latest_drafts = "".join(_draft_card(d, csrf, connected=is_connected) for d in drafts[:2]) or '<div class="empty">Turn a few saved insights into a post, ebook outline, or design brief.</div>'
        recent_evidence = "".join(_insight_card(item, follow=follow_index.tag(item.get("source_url")), engager=follow_index.engager(item.get("source_url"))) for item in insights[:3]) or '<div class="empty">No evidence saved yet. Start with a bounded sample of the authorized Threads account.</div>'
        connect_link = (
            '<a class="button" href="/auth/start">connect Threads →</a>'
            if not is_connected
            else f'<div class="actions"><a class="text-link" href="/?view=settings">Manage connection →</a><form method="post" action="/followers/sync">{csrf_input}<input type="hidden" name="queue" value="on"><button class="button ghost small">Sync Threads Graph ↻</button></form></div>'
        )
        checklist = (
            '<div class="panel"><div class="section-head"><div><p class="eyebrow">GETTING STARTED</p><h2>Quick start checklist</h2></div></div>'
            '<div class="steps">'
            f'<a href="/?view=settings"><i>{"✓" if is_connected else "1"}</i><b>Connect Threads</b><small>OAuth token &amp; scopes</small></a><span class="step-arrow">→</span>'
            f'<a href="/?view=research"><i>{"✓" if total_runs else "2"}</i><b>Run Sample</b><small>Collect &amp; mine replies</small></a><span class="step-arrow">→</span>'
            f'<a href="/?view=studio"><i>{"✓" if total_drafts else "3"}</i><b>Create Drafts</b><small>Evidence-cited Studio</small></a><span class="step-arrow">→</span>'
            f'<a href="/?view=followers"><i>{"✓" if data.audience else "4"}</i><b>Review Followers</b><small>Graph &amp; unfollow triage</small></a>'
            '</div></div>'
        ) if not (is_connected and total_runs and total_drafts) else ""
        quota_note = (
            f' · Publishing quota {data.publishing_limit["quota_usage"]}/{data.publishing_limit["quota_total"]}'
            if isinstance(data.publishing_limit, dict)
            else ""
        )
        content = f'''<div class="welcome"><div><p class="eyebrow">PERPUSTAKAAN HATI · THREADS RESEARCH WORKSPACE</p><h1>From conversation<br>to something helpful.</h1><p class="lead">A careful path from Rahimam’s Threads sample to audience needs, grounded ideas, and reviewed content.</p></div><a class="button" href="/?view=research">Start with research <span>→</span></a></div>
          <div class="stats"><article class="stat card"><span>Evidence points</span><b>{total_evidence}</b><small>Saved, source-linked insights · {len(data.external_signals)} web signals</small></article><article class="stat card"><span>Working segments</span><b>{len(audiences)}</b><small>Inferred from sampled language</small></article><article class="stat card"><span>Drafts in library</span><b>{total_drafts}</b>{follower_spark}<small>Approval never auto-publishes{quota_note}</small></article><article class="stat card"><span>Research runs</span><b>{total_runs}</b>{engagement_spark}<small>{run_note}</small></article></div>
          {checklist}
          <div class="workflow card"><div class="section-head"><div><p class="eyebrow">YOUR WORKFLOW</p><h2>Evidence before ideas</h2></div><span class="step-count">4 steps</span></div><div class="steps"><a href="/?view=research"><i>01</i><b>Collect</b><small>Sample posts & public replies</small></a><span class="step-arrow">→</span><a href="/?view=audiences"><i>02</i><b>Understand</b><small>Group evidence by recurring need</small></a><span class="step-arrow">→</span><a href="/?view=studio"><i>03</i><b>Create</b><small>Draft posts, ebooks, design briefs</small></a><span class="step-arrow">→</span><a href="/?view=library"><i>04</i><b>Review</b><small>Approve, schedule, export card</small></a></div></div>
          <div class="two-col"><section class="panel"><div class="section-head"><div><p class="eyebrow">AUDIENCE SIGNALS</p><h2>Emerging needs</h2></div><a class="text-link" href="/?view=audiences">All segments →</a></div>{top_audiences}</section><section class="panel"><div class="section-head"><div><p class="eyebrow">THREADS CONNECTION</p><h2>Research account</h2></div><span class="status {status_class}">{_e(connection)}</span></div><p class="muted">{_e(expiry) if expiry else "Connect the authorized Threads account to sample your own posts and visible replies."}</p>{connect_link}<p class="small-copy">{_e(topic_text)} · Sampled data from own-account research only{graph_summary}.</p></section></div>
          <section class="panel"><div class="section-head"><div><p class="eyebrow">EVIDENCE · LATEST SAVED INSIGHTS</p><h2>Source-linked findings</h2></div><a class="text-link" href="/?view=research">Search all evidence →</a></div><div class="evidence-grid">{recent_evidence}</div></section>
          <section class="panel"><div class="section-head"><div><p class="eyebrow">POST PERFORMANCE · WEIGHTED OUTLIER SCORING</p><h2>Top posts by engagement</h2></div><span class="tag">Median weighted {scored_analytics["median_weighted"]}</span></div><div class="table-wrap"><table class="metrics"><thead><tr><th>Post</th><th>Views</th><th>Likes</th><th>Replies</th><th>Reposts</th><th>Weighted Score</th></tr></thead><tbody>{post_rows}</tbody></table></div>{best_hours_line}</section>
          <section class="panel"><div class="section-head"><div><p class="eyebrow">RECENT WORK</p><h2>Drafts to review</h2></div><a class="text-link" href="/?view=library">Open library →</a></div><div class="draft-grid">{latest_drafts}</div></section>'''
    elif view == "research":
        limits = (data.limits or SampleLimits()).normalized()
        selected_ids = {str(value) for value in selection.split(",") if value.isdigit()}
        cards = "".join(_insight_card(item, selectable=True, selected=str(item["id"]) in selected_ids, follow=follow_index.tag(item.get("source_url")), engager=follow_index.engager(item.get("source_url"))) for item in insights) or '<div class="empty">No evidence saved yet. Connect Threads, then run the consented sample.</div>'
        limit_fields = "".join((
            _limit_field("post_limit", "Owned posts to fetch", limits.post_limit, 1, POST_LIMIT_MAX, "Newest first, up to 3 pages of 50."),
            _limit_field("top_posts", "Posts to prioritize", limits.top_posts, 1, TOP_POSTS_MAX, "Highest likes + replies + reposts + quotes."),
            _limit_field("replies_per_post", "Replies per post", limits.replies_per_post, 1, REPLIES_PER_POST_MAX, "Visible direct replies, newest first."),
        ))
        last_run = (
            f'{_e(latest["created_at"][:16].replace("T", " "))} · {_e(latest["posts_sampled"])} sampled · '
            f'{_e(latest["selected_posts"])} prioritized · {_e(latest["insights_count"])} insights'
            if latest else "No run recorded yet"
        )
        last_themes = (_e(" · ".join(latest["themes"][:3]) or "No recurring themes") if latest else "Your first run creates the baseline")
        board = f'''<section class="board">
          <article class="card board-card"><p class="eyebrow">THREADS CONNECTION</p><b>{_e(connection)}</b><p>{"Token saved" if expiry else "No saved token"}<br>Own posts and visible direct replies only</p></article>
          <article class="card board-card"><p class="eyebrow">AI MODEL</p><b>{_e(model or "not set")}</b><p>{"Fact-Sheet grounded · quotes evidence-checked" if configured else "OPENROUTER_API_KEY not configured"}</p></article>
          <article class="card board-card"><p class="eyebrow">LAST RUN</p><b>{last_run}</b><p>{last_themes}</p></article>
          <article class="card board-card"><p class="eyebrow">LIBRARY</p><b>{total_evidence} evidence · {total_runs} runs · {total_drafts} drafts</b><p>Sources stay clickable; approval never publishes</p></article>
        </section>'''
        history = "".join(f'<div class="run-row"><div><b>{_e(r["created_at"][:16].replace("T", " "))}</b><span>{_e(r["posts_sampled"])} sampled · {_e(r["selected_posts"])} prioritized · {_e(r.get("replies_per_post", 50))} replies/post · {_e(r["insights_count"])} insights</span></div><p>{_e(" · ".join(r["themes"][:3]) or "No recurring themes")}{(" · Focus: " + _e(str(r.get("focus", ""))[:80])) if r.get("focus") else ""}</p></div>' for r in runs) or '<p class="muted">Run history appears here after your first sample.</p>'
        focus_field = (
            f'<label class="focus-field"><span>Research focus · optional</span>'
            f'<textarea name="focus" maxlength="500" placeholder="e.g. Pay special attention to readers healing after a breakup, or on feeling unheard.">{_e(data.focus)}</textarea>'
            f'<small>Steers the next run only. Sent with the sample to the AI provider, never published.</small></label>'
            f'<label class="check" style="margin-top:8px"><input type="checkbox" name="sync_graph" value="on" checked> Also sync live follower count &amp; demographics from Threads Graph</label>'
        )
        theme_pills = _theme_filter_pills(insights, query)
        quick_select = (
            '<div class="actions" style="margin-bottom:12px">'
            '<button class="button ghost small" type="button" data-select-all="true">Select all visible</button>'
            '<button class="button ghost small" type="button" data-select-all="false">Clear selection</button>'
            '<button class="button ghost small" type="button" data-open-studio="true">Open selected in Studio →</button>'
            '</div>'
        ) if insights else ""
        discovery_panel = _render_discovery_panel(data, csrf_input, is_connected=is_connected, configured=configured)
        content = f'''<div class="page-head"><div><p class="eyebrow">01 · COLLECT & INSPECT</p><h1>Research desk</h1><p class="lead">Sample your own recent Threads posts and visible public replies, then inspect every insight against its source.</p></div><span class="status {status_class}">{_e(connection)}</span></div>
        {board}
        <form class="run-card card" method="post" action="/research/run">{csrf_input}<div><p class="eyebrow">SAMPLE SETTINGS</p><h2>How much to read per run</h2><p class="help">Applies to the next run. The server clamps every value to {POST_LIMIT_MAX} posts, {TOP_POSTS_MAX} prioritized posts, and {REPLIES_PER_POST_MAX} replies per post before calling Threads.</p></div><div class="limits-grid">{limit_fields}</div>{focus_field}<div class="run-actions"><label class="consent"><input type="checkbox" name="consent" required><span>I understand that sampled posts and public replies will be sent to the configured AI provider for analysis.</span></label><button class="button" {"" if threads_configured and configured else "disabled"}>Run consented research <span>→</span></button></div></form>
        {discovery_panel}
        {_queue_panel(data.jobs, csrf)}
        <section class="panel"><div class="section-head"><div><p class="eyebrow">EVIDENCE IN LIBRARY</p><h2>{total_evidence} saved insight{'' if total_evidence == 1 else 's'}</h2></div><form class="search" method="get"><input type="hidden" name="view" value="research"><input name="q" value="{_e(query)}" placeholder="Search themes, quotes, ideas"><button class="button ghost small">Search</button></form></div>{theme_pills}{quick_select}<form method="post" action="/content/generate">{csrf_input}<div class="evidence-grid">{cards}</div>{_draft_controls()}<div class="selection-bar"><label><input type="checkbox" name="consent" required> I consent to send selected saved insights to the configured AI provider to generate drafts.</label><button class="button" {"" if insights and configured else "disabled"}>Create grounded drafts <span>→</span></button></div></form></section>
        <section class="panel"><div class="section-head"><div><p class="eyebrow">RUN LOG</p><h2>Research history</h2></div></div>{history}</section>'''
    elif view == "followers":
        content = _render_followers_view(data, follow_index, csrf_input, status_class=status_class, is_connected=is_connected)
    elif view == "audiences":
        audience_cards = "".join(
            f'''<article class="audience card"><div class="card-top"><span class="tag">WORKING SEGMENT</span>'''
            f'''<span class="follow-wrap"><span class="follow-chip {"following_only" if a.get("needs_drafts") else "mutual"}">{_e("Underserved · 0 drafts" if a.get("needs_drafts") else f'{a.get("draft_count", 0)} draft{"" if a.get("draft_count", 0) == 1 else "s"}')}</span><b class="count">{a["evidence_count"]}<small> signals</small></b></span></div>'''
            f'''<h2>{_e(a["name"])}</h2><p class="muted">{_e(a["basis"])}</p>'''
            f'''<div class="chips">{"".join(f'<span>{_e(t)}</span>' for t in a["themes"][:6])}</div>'''
            f'''{('<p class="small-copy"><b>Community voices:</b> ' + ", ".join(f'<a class="text-link" href="/?view=research&amp;q={quote(v, safe="")}">@{_e(v)}</a>' for v in a.get("voices", [])[:5]) + "</p>") if a.get("voices") else ""}'''
            f'''<h3>Evidence</h3><div class="audience-evidence">{"".join(f'<blockquote>“{_e(e["quote"])}”<br>{_source(e)}</blockquote>' for e in a["evidence"][:3])}</div>'''
            f'''<h3>Potential product angles</h3><ul>{"".join(f'<li>{_e(x)}</li>' for x in a["ebook_angles"][:4]) or '<li>Collect more evidence before proposing a product.</li>'}</ul>'''
            f'''<div class="actions"><a class="text-link" href="/?view=studio&amp;select={",".join(str(value) for value in a["source_ids"])}">Create content from this segment →</a></div></article>'''
            for a in audiences
        ) or '<div class="empty">Audience segments appear when saved evidence is available. These are qualitative working hypotheses, not demographic claims.</div>'
        seg_form = (
            f'<section class="panel"><div class="section-head"><div><p class="eyebrow">CUSTOM SEGMENTS</p><h2>Define brand segments</h2></div></div>'
            f'<form class="edit-form" method="post" action="/audiences/segments">{csrf_input}'
            '<div class="two-col"><label class="limit-field"><span>Label</span><input name="label" placeholder="e.g. Late-night Overthinkers" required></label>'
            '<label class="limit-field"><span>Comma keywords</span><input name="keywords" placeholder="overthinking, sunyi, malam, penat" required></label></div>'
            '<button class="button ghost small" type="submit">Save segment rule</button></form></section>'
        )
        content = f'''<div class="page-head"><div><p class="eyebrow">02 · UNDERSTAND</p><h1>Audience signals</h1><p class="lead">Evidence-led working segments from sampled language. Each claim links back to source insights; no demographic inference is made.</p></div><div class="actions"><span class="tag">{source_count} evidence points</span><a class="button ghost small" href="/audiences/export.csv">Export evidence CSV</a></div></div><div class="audience-grid">{audience_cards}</div>{seg_form}'''
    elif view == "studio":
        selected = {value for value in selection.split(",") if value.isdigit()}
        options = "".join(f'<option value="{int(i["id"])}"{" selected" if str(i["id"]) in selected else ""}>#{int(i["id"])} · {_e(i["theme"])}, {_e(i["quote"][:90])}</option>' for i in insights)
        preview_list = [i for i in insights if str(i["id"]) in selected] or insights[:4]
        source_preview = "".join(_insight_card(i, follow=follow_index.tag(i.get("source_url")), engager=follow_index.engager(i.get("source_url"))) for i in preview_list[:6]) or '<div class="empty">Run research before drafting so every idea can cite evidence.</div>'
        segment_shortcuts = ""
        if audiences:
            segment_shortcuts = '<div class="filter-pills">' + "".join(
                f'<a href="/?view=studio&amp;select={",".join(str(v) for v in a["source_ids"][:20])}">{_e(a["name"])} · {a["evidence_count"]}</a>'
                for a in audiences[:5]
            ) + "</div>"
        variants_form = (
            f'<form class="panel" method="post" action="/content/variants">{csrf_input}'
            '<div class="section-head"><div><p class="eyebrow">STUDIO 2.0 · 4-ANGLE HOOK LAB</p><h2>Generate 3 Variants (Short, Story, Carousel)</h2></div></div>'
            '<div class="search"><input name="focus" placeholder="Optional hook angle focus (e.g. letting go without bitterness)">'
            f'<input type="hidden" name="select" value="{_e(selection)}">'
            f'<button class="button ghost small" {"" if insights and configured else "disabled"}>Generate 3 Variants + Hook Lab</button></div></form>'
        )
        content = f'''<div class="page-head"><div><p class="eyebrow">03 · CREATE</p><h1>Content studio</h1><p class="lead">Choose research evidence; get a small, grounded set of content directions for a human to edit.</p></div><span class="tag">Draft only · no auto-publishing</span></div><div class="studio-layout"><form class="studio-form card" method="post" action="/content/generate">{csrf_input}<label class="field-label" for="source_ids">Evidence to use</label>{segment_shortcuts}<input type="hidden" name="selected_ids" value="{_e(query)}"><select id="source_ids" name="insight_ids" multiple size="10" required>{options}</select><p class="help">Select multiple insights on desktop with Ctrl/Cmd-click. Segment-linked evidence is preselected. Drafts retain the chosen IDs as citations.</p>{_draft_controls()}<label class="consent"><input type="checkbox" name="consent" required><span>I consent to send selected saved insights to the configured AI provider to generate draft content.</span></label><button class="button" {"" if insights and configured else "disabled"}>Generate selected drafts <span>→</span></button><p class="help">Drafts run in the queue below; non-post drafts carry the source Threads links.</p></form><section><h2 class="subhead">Available evidence</h2><div class="stack">{source_preview}</div></section></div>{variants_form}{_queue_panel(data.jobs, csrf)}'''
    elif view == "library":
        draft_cards = "".join(_draft_card(d, csrf, connected=is_connected) for d in drafts) or '<div class="empty">No drafts yet. Select evidence in Research or open the Content Studio.</div>'
        content = f'''<div class="page-head"><div><p class="eyebrow">04 · REVIEW &amp; REUSE</p><h1>Draft library</h1><p class="lead">Review, edit inline, rewrite tone, preview Daylight Grove Quote Cards, export Markdown, or publish approved Threads posts.</p></div><div class="actions"><a class="button ghost small" href="/content/export/publish-pack?format=md">Publish Pack (.md)</a><a class="button" href="/?view=studio">New evidence-led drafts →</a></div></div><div class="filter-pills"><a class="{"selected" if not status_filter else ""}" href="/?view=library">All</a><a class="{"selected" if status_filter == "draft" else ""}" href="/?view=library&amp;status=draft">Needs review</a><a class="{"selected" if status_filter == "approved" else ""}" href="/?view=library&amp;status=approved">Approved</a><a class="{"selected" if status_filter == "scheduled" else ""}" href="/?view=library&amp;status=scheduled">Scheduled</a><a class="{"selected" if status_filter == "published" else ""}" href="/?view=library&amp;status=published">Published</a><a class="{"selected" if status_filter == "archived" else ""}" href="/?view=library&amp;status=archived">Archived</a></div><div class="draft-grid">{draft_cards}</div>'''
    elif view == "calendar":
        content = _render_calendar_view(data)
    elif view == "inbox":
        content = _render_inbox_view(data, csrf_input, is_connected=is_connected, configured=configured)
    elif view == "knowledge":
        content = _render_knowledge_view(data, csrf_input)
    else:
        refresh_btn = f'<form method="post" action="/auth/refresh" style="display:inline">{csrf_input}<button class="button ghost small">Refresh 60-day token</button></form>' if is_connected else ""
        publish_connect = '<a class="button ghost small" href="/auth/start?scope=publish">Connect with Publish scope</a> <a class="button ghost small" href="/auth/start?scope=expanded">Connect Expanded scopes</a>'
        scope_list = ", ".join(data.scopes) if data.scopes else "Standard research scopes"
        provider_rows = "".join(
            f'<tr><td>{_e(r["provider"])}</td><td>{int(r["calls"])}</td><td>{int(r["ok_calls"] or 0)}</td><td>{int(r["prompt_tokens"] or 0)} / {int(r["completion_tokens"] or 0)}</td><td>{round(float(r["avg_ms"] or 0))} ms</td></tr>'
            for r in (data.ai_summary.get("by_provider") or [])
        ) or '<tr><td colspan="5" class="muted">No AI calls recorded yet.</td></tr>'
        wl = data.watchlist or {"enabled": False, "interval_hours": 24, "keywords": [], "focus": "", "last_run_at": ""}
        wl_keywords = ", ".join(wl.get("keywords") or [])
        notif_rows = "".join(
            f'<li>[{_e(n["status"])}] {_e(n["created_at"][:16].replace("T", " "))} · {_e(n["message"][:80])}</li>'
            for n in data.notifications[:5]
        ) or '<li class="muted">No notifications sent yet.</li>'
        content = f'''<div class="page-head"><div><p class="eyebrow">WORKSPACE SETTINGS</p><h1>Connections &amp; settings</h1><p class="lead">Private data access, AI provider waterfall, Watchlist automation, Telegram alerts, and SQLite backup.</p></div></div>
        <div class="settings-grid">
          <article class="card settings-card"><p class="eyebrow">THREADS · OFFICIAL API</p><h2>{_e(connection)}</h2><p>{_e(expiry) if expiry else "Connect the authorized Threads profile used by this admin."}</p><p class="help">Granted scopes: <code>{_e(scope_list)}</code></p><div class="actions"><a class="button" href="/auth/start">{"Reconnect Threads" if is_connected else "Connect Threads"}</a>{publish_connect}{refresh_btn}</div></article>
          <article class="card settings-card"><p class="eyebrow">AI PROVIDER WATERFALL</p><h2>{"Ready for explicit-consent workflows" if configured else "API key not configured"}</h2><p>Primary model <code>{_e(model or "not set")}</code>; reasoning disabled, quotes evidence-checked, zero em dashes enforced.</p><div class="table-wrap"><table class="metrics"><thead><tr><th>Provider</th><th>Calls</th><th>OK</th><th>Tokens (in/out)</th><th>Avg Latency</th></tr></thead><tbody>{provider_rows}</tbody></table></div></article>
          <article class="card settings-card"><p class="eyebrow">WATCHLIST &amp; SCHEDULE</p><h2>Autonomous monitoring</h2>
            <form class="edit-form" method="post" action="/watchlist/config">{csrf_input}
              <label class="check"><input type="checkbox" name="enabled" value="on" {"checked" if wl.get("enabled") else ""}> Enable periodic watchlist research</label>
              <label class="limit-field"><span>Interval (hours)</span><input type="number" name="interval_hours" min="1" max="168" value="{int(wl.get("interval_hours", 24))}"></label>
              <label class="limit-field"><span>Watchlist keywords (comma-separated)</span><input name="keywords" value="{_e(wl_keywords)}" placeholder="tenang hati, boundaries, redha"></label>
              <label class="limit-field"><span>Focus prompt</span><input name="focus" value="{_e(wl.get("focus", ""))}"></label>
              <div class="actions"><button class="button small" type="submit">Save Watchlist</button></div>
            </form>
            <form method="post" action="/watchlist/run" style="margin-top:8px">{csrf_input}<button class="button ghost small">Run Watchlist Now ↻</button></form>
            <p class="small-copy">Last automated run: {_e(wl.get("last_run_at") or "Never")}</p>
          </article>
          <article class="card settings-card"><p class="eyebrow">TELEGRAM OPS &amp; DATABASE BACKUP</p><h2>Alerts &amp; disaster recovery</h2>
            <p class="help">{total_evidence} evidence points · {total_runs} runs · {total_drafts} drafts · {len(data.external_signals)} web signals</p>
            <div class="actions">
              <form method="post" action="/telegram/test">{csrf_input}<button class="button ghost small">Send Test Telegram Alert</button></form>
              <a class="button ghost small" href="/backups/latest.db">Download SQLite Backup ↓</a>
              <a class="button ghost small" href="/mini" target="_blank" rel="noreferrer">Open Mini App View ↗</a>
            </div>
            <ul class="small-copy">{notif_rows}</ul>
          </article>
        </div>'''

    mobile_more = "".join(
        f'<a class="drawer-link {"active" if view == key else ""}" href="/?view={key}">{label}</a>'
        for key, label in labels.items()
    )
    nonce_attr = f' nonce="{_e(data.csp_nonce)}"' if data.csp_nonce else ""
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark"><title>Threads research · {_e(labels[view])} · Perpustakaan Hati</title><link rel="icon" href="/favicon.ico">
<style>
@font-face{{font-family:"Fraunces";src:url("/assets/fonts/FrauncesDisplay.woff2") format("woff2");font-weight:100 900;font-display:swap}}
@font-face{{font-family:"Fraunces";src:url("/assets/fonts/FrauncesDisplayItalic.woff2") format("woff2");font-style:italic;font-weight:100 900;font-display:swap}}
@font-face{{font-family:"Inter";src:url("/assets/fonts/InterUI.woff2") format("woff2");font-weight:100 900;font-display:swap}}
@font-face{{font-family:"Source Serif 4";src:url("/assets/fonts/SourceSerifText.woff2") format("woff2");font-weight:200 900;font-display:swap}}
:root{{--bg:#07140d;--paper:#0d2117;--sage:#142c20;--ink:#e6e2da;--muted:#a9b2a6;--line:#24402f;--gold:#e9cea2;--green:#3f9167;--link:#9de1c1;--deep:#2d7954;--danger:#f0a3a0;--shadow:0 14px 40px -28px rgb(0 0 0/.5)}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 "Inter",ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}}a{{color:inherit}}:focus-visible{{outline:2px solid #9de1c1;outline-offset:2px}}::selection{{background:#1d5a3d;color:#fdfee6}}::placeholder{{color:#a49c8d;opacity:1}}input,select,textarea{{color-scheme:dark}}button,input,select,textarea{{font:inherit}}.shell{{min-height:100vh;display:grid;grid-template-columns:250px minmax(0,1fr)}}aside{{position:sticky;top:0;height:100vh;overflow-y:auto;padding:24px 18px;background:#0b1d14;color:#e6e2da;display:flex;flex-direction:column;gap:20px}}.brand{{display:flex;align-items:center;gap:12px;padding:0 8px}}.brand-mark{{height:38px;width:38px;display:grid;place-items:center;border-radius:12px;background:#C99B6B;color:#1C2D23;font:bold 18px "Fraunces",Georgia,serif}}.brand b{{display:block;font:600 15px "Fraunces",Georgia,serif;letter-spacing:.02em}}.brand small{{display:block;color:#C8D2C9;font-size:11px;margin-top:2px}}.nav-label,.eyebrow{{font-size:10px;letter-spacing:.17em;font-weight:700;color:var(--gold);margin:0 0 8px}}aside .nav-label{{color:#A5B8AA;padding:0 12px}}nav{{display:grid;gap:4px}}.nav-link{{display:flex;align-items:center;gap:11px;padding:9px 12px;text-decoration:none;border-radius:9px;color:#DBE5DC;font-size:13px;min-height:40px}}.nav-link:hover,.nav-link.active{{background:#2d7954;color:#fdfee6}}.nav-link.active{{box-shadow:inset 3px 0 #C99B6B}}.nav-mark{{height:7px;width:7px;border:1px solid #97B19D;border-radius:2px}}.nav-link.active .nav-mark{{background:#C99B6B;border-color:#C99B6B}}.side-bottom{{margin-top:auto;border-top:1px solid #385143;padding:15px 8px 0;color:#B8C8BB;font-size:12px}}.side-bottom a{{color:#F6E0B2}}.signout{{margin-top:12px;padding:0;border:0;background:transparent;color:#DBE5DC;font-size:12px;text-decoration:underline;cursor:pointer}}main{{min-width:0;max-width:1500px;width:100%;margin:auto;padding:34px clamp(20px,4vw,58px) 72px}}.topline{{display:flex;justify-content:space-between;align-items:center;margin-bottom:26px;color:var(--muted);font-size:12px;gap:12px;flex-wrap:wrap}}.crumb{{font-weight:600;color:var(--ink)}}.account{{display:flex;align-items:center;gap:8px}}.dot{{width:8px;height:8px;border-radius:50%;background:#d4746f}}.dot.connected{{background:#3B8A5B}}.ph-at{{display:inline-flex;align-items:center;padding:3px 9px;border-radius:999px;font-size:12px;font-weight:700;background:linear-gradient(120deg,#f59e0b,#ef4444,#8b5cf6,#10b981);color:#fff}}h1,h2,h3,p{{margin-top:0}}h1{{font:500 clamp(32px,4vw,48px)/1.08 "Fraunces",Georgia,serif;letter-spacing:-.025em;margin:0 0 12px}}h2{{font:500 23px/1.2 "Fraunces",Georgia,serif;margin:0}}h3{{font:600 16px "Fraunces",Georgia,serif;margin:16px 0 8px}}.lead{{max-width:700px;color:var(--muted);font-size:15px;margin:0}}.welcome,.page-head{{display:flex;align-items:flex-end;justify-content:space-between;gap:24px;margin-bottom:27px}}.welcome{{align-items:center;padding:22px 0 30px}}.welcome .eyebrow{{margin-bottom:12px}}.page-head .eyebrow{{margin-bottom:10px}}.button{{display:inline-flex;justify-content:center;align-items:center;gap:10px;border:0;border-radius:9px;background:var(--deep);color:#fdfee6;text-decoration:none;font-weight:650;font-size:13px;padding:11px 16px;min-height:42px;cursor:pointer;white-space:nowrap}}.button:hover{{background:#1d5a3d}}.button:disabled{{opacity:.45;cursor:not-allowed}}.button.ghost{{background:transparent;color:var(--link);border:1px solid var(--line)}}.button.small{{padding:7px 11px;font-size:12px;min-height:36px}}.card,.panel{{background:var(--paper);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow)}}.card{{padding:18px}}.stats{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-bottom:18px}}.stat{{display:flex;flex-direction:column;gap:6px}}.stat>span{{color:var(--muted);font-size:12px}}.stat>b{{font:500 34px "Fraunces",Georgia,serif}}.stat small{{color:var(--muted);font-size:11px;line-height:1.45}}.spark{{width:100%;max-width:140px;height:28px;margin-top:2px}}.workflow,.panel{{padding:22px;margin:16px 0}}.section-head{{display:flex;align-items:center;justify-content:space-between;gap:14px;margin-bottom:16px}}.section-head .eyebrow{{margin-bottom:6px}}.step-count,.tag{{display:inline-flex;align-items:center;border:1px solid #4a5b45;border-radius:999px;padding:4px 9px;color:var(--gold);background:#142c20;font-size:10px;font-weight:700;letter-spacing:.07em}}
.follow-chip{{display:inline-flex;align-items:center;border:1px solid var(--line);border-radius:999px;padding:3px 9px;font-size:10px;font-weight:700;letter-spacing:.05em;background:#142c20;color:var(--muted);white-space:nowrap}}
.follow-chip.mutual{{border-color:#2d7954;background:#12301f;color:#9de1c1}}
.follow-chip.follower{{border-color:#2d7954;background:#12301f;color:var(--link)}}
.follow-chip.following_only{{border-color:#6f5d2e;background:#2e2a17;color:var(--gold)}}
.follow-wrap{{display:inline-flex;align-items:center;gap:8px;flex-wrap:wrap}}
.follow-row p{{margin:0}}
.follow-row .follow-chip{{margin:0}}
.demo-row{{display:grid;gap:4px;margin-top:8px;font-size:11px}}
.demo-meta{{display:flex;justify-content:space-between;gap:8px}}
.demo-bar{{height:6px;background:var(--sage);border-radius:999px;overflow:hidden}}
.demo-bar i{{display:block;height:100%;background:var(--green);border-radius:999px}}
.edit-drawer{{margin-top:12px;border-top:1px solid #1b3426;padding-top:10px}}
.edit-drawer summary{{cursor:pointer;list-style:none}}
.edit-form{{display:grid;gap:10px;margin-top:10px}}
.edit-form textarea{{min-height:80px;border:1px solid var(--line);border-radius:8px;background:#142c20;color:var(--ink);padding:8px 10px;width:100%}}
.import-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:13px;align-items:end}}
.file-field{{display:grid;gap:6px;font-size:12px;font-weight:650}}
.file-field input{{min-height:42px;border:1px dashed var(--line);border-radius:8px;background:#142c20;color:var(--muted);padding:9px 10px;width:100%;font-size:12px;font-weight:400}}
.file-field input::file-selector-button{{font:inherit;margin-right:10px;padding:6px 11px;border:1px solid var(--line);border-radius:7px;background:#0d2117;color:var(--ink);cursor:pointer}}.steps{{display:grid;grid-template-columns:1fr auto 1fr auto 1fr auto 1fr;align-items:center;gap:12px}}.steps>a{{display:grid;gap:4px;text-decoration:none;padding:12px 4px}}.steps i{{color:var(--gold);font:italic 14px "Fraunces",Georgia,serif}}.steps b{{font:600 16px "Fraunces",Georgia,serif}}.steps small{{font-size:11px;color:var(--muted)}}.step-arrow{{color:#a49c8d}}.two-col{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}.panel{{box-shadow:none}}.panel .section-head{{margin-bottom:14px}}.text-link,.source{{font-size:12px;font-weight:650;color:var(--link);text-decoration:none}}.text-link:hover,.source:hover{{text-decoration:underline}}.segment-row{{display:flex;justify-content:space-between;padding:10px 0;border-top:1px solid #1b3426;text-decoration:none;font-size:13px}}.segment-row b{{color:var(--gold)}}.status{{font-size:11px;padding:5px 9px;border-radius:999px;background:#3a1c1f;color:var(--danger)}}.status.connected,.status.approved,.status.published,.status.replied{{background:#12301f;color:#9de1c1}}.status.scheduled{{background:#2e2a17;color:#e9cea2}}.status.archived,.status.dismissed{{background:#1b3426;color:#a9b2a6}}.muted,.help{{color:var(--muted);font-size:12px}}.small-copy{{color:var(--muted);font-size:11px;margin:12px 0 0}}.table-wrap{{overflow-x:auto}}.metrics{{width:100%;border-collapse:collapse;font-size:12px;text-align:left}}.metrics th,.metrics td{{padding:10px 8px;border-top:1px solid #1b3426;white-space:nowrap}}.metrics th{{color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.08em}}.metrics td:first-child{{max-width:420px;overflow:hidden;text-overflow:ellipsis}}.draft-grid,.audience-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}}.draft{{min-width:0}}.card-top,.card-bottom{{display:flex;align-items:center;justify-content:space-between;gap:12px}}.card-top time{{color:var(--muted);font-size:10px}}.evidence blockquote{{font:500 17px/1.4 "Source Serif 4",Georgia,serif;margin:14px 0;color:#e6e2da}}.idea{{font-size:12px;color:var(--muted)}}.card-bottom{{border-top:1px solid #1b3426;padding-top:11px;flex-wrap:wrap}}.select,.consent{{display:flex;align-items:flex-start;gap:9px;color:var(--muted);font-size:12px}}input[type=checkbox]{{accent-color:var(--green);margin-top:4px}}.page-head{{align-items:center}}.notice{{border:1px solid #5b4f2f;background:#2a2a18;color:#e9cea2;border-radius:10px;padding:12px 15px;font-size:12px;margin:0 0 16px}}.notice.error{{background:#3a1c1f;border-color:#7d3a3d;color:var(--danger)}}.run-bar{{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-bottom:16px}}.board{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-bottom:16px}}.board-card{{padding:15px}}.board-card b{{display:block;font-size:13px;line-height:1.4;margin:4px 0 5px}}.board-card p{{font-size:11px;color:var(--muted);margin:0}}.run-card{{display:grid;gap:14px;margin-bottom:16px}}.run-card h2{{font-size:20px;margin:2px 0 6px}}.limits-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}}.limit-field{{display:grid;gap:5px;font-size:12px;font-weight:650}}.limit-field input,.limit-field select{{min-height:40px;border:1px solid var(--line);border-radius:8px;background:#142c20;color:var(--ink);padding:8px 10px;width:100%}}.limit-field small{{font-weight:400;color:var(--muted);font-size:11px;line-height:1.4}}.focus-field{{display:grid;gap:5px;font-size:12px;font-weight:650;margin-top:12px}}.focus-field textarea{{min-height:64px;border:1px solid var(--line);border-radius:8px;background:#142c20;color:var(--ink);padding:9px 10px;width:100%;resize:vertical;font:inherit}}.focus-field small{{font-weight:400;color:var(--muted);font-size:11px;line-height:1.4}}.draft-controls{{display:grid;gap:11px;margin-top:14px;border-top:1px solid #1b3426;padding-top:14px}}.kind-grid{{display:flex;gap:14px;flex-wrap:wrap;font-size:12px}}.check{{display:flex;align-items:center;gap:6px;font-weight:400}}.select-field{{display:grid;gap:5px;font-size:12px;font-weight:650}}.select-field select{{min-height:40px;border:1px solid var(--line);border-radius:8px;background:#142c20;color:var(--ink);padding:8px 10px;width:100%}}.job-actions{{display:flex;gap:7px;flex-wrap:wrap;margin-top:6px}}.queue-panel{{margin:16px 0}}.run-actions{{display:flex;align-items:center;justify-content:space-between;gap:18px}}.evidence-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}}.selection-bar{{display:flex;align-items:center;justify-content:space-between;gap:16px;border-top:1px solid var(--line);padding-top:16px;margin-top:18px}}.search{{display:flex;gap:7px;flex-wrap:wrap}}.search input,.studio-form select{{min-height:40px;border:1px solid var(--line);border-radius:8px;background:#142c20;color:var(--ink);padding:8px 10px;min-width:210px}}.run-row{{display:grid;grid-template-columns:250px 1fr;gap:15px;padding:12px 0;border-top:1px solid #1b3426;font-size:12px}}.run-row div{{display:grid;gap:3px}}.run-row span,.run-row p{{color:var(--muted);margin:0}}.audience{{padding:21px}}.audience h2{{margin:13px 0 8px}}.audience .count{{font:500 23px "Fraunces",Georgia,serif;color:var(--link)}}.audience .count small{{font:11px system-ui;color:var(--muted)}}.chips,.filter-pills{{display:flex;gap:7px;flex-wrap:wrap;margin:12px 0}}.chips span,.filter-pills a{{font-size:11px;color:var(--muted);background:var(--sage);padding:6px 10px;border-radius:999px;text-decoration:none}}.audience-evidence blockquote{{font:italic 14px "Source Serif 4",Georgia,serif;border-left:2px solid #C99B6B;padding:2px 0 2px 11px;margin:9px 0}}.audience-evidence .source{{display:inline-block;margin-top:5px;font:600 11px system-ui}}.audience ul{{padding-left:18px;color:var(--muted);font-size:12px}}.studio-layout{{display:grid;grid-template-columns:minmax(300px,.8fr) minmax(0,1.2fr);gap:22px}}.studio-form{{height:max-content;display:grid;gap:12px}}.field-label{{font-weight:700;font-size:13px}}.studio-form select{{width:100%;height:260px;min-width:0}}.subhead{{font:500 22px "Fraunces",Georgia,serif}}.stack{{display:grid;gap:10px}}.draft h3{{font-size:19px;margin:12px 0}}.draft-body{{font-size:13px;color:#d7dfd5}}.draft-copy{{white-space:pre-wrap;background:var(--sage);border-radius:8px;padding:13px;font-size:14px}}.draft-refs{{margin-top:12px;border-top:1px solid #1b3426;padding-top:10px;font-size:12px}}.draft-refs b{{display:block;font-size:11px;color:var(--muted);margin-bottom:5px}}.draft-refs ul{{margin:0;padding-left:16px;display:grid;gap:4px}}.draft-refs a{{color:var(--link);word-break:break-all}}.chapter-list{{padding-left:20px}}.chapter-list li{{padding:5px 0}}.chapter-list span{{display:block;color:var(--muted);font-size:12px}}.draft .actions{{display:flex;gap:7px;flex-wrap:wrap;margin-top:14px}}.draft .actions form{{margin:0}}.filter-pills a.selected{{background:var(--deep);color:#fdfee6}}.settings-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}}.settings-card h2{{font-size:20px;margin:8px 0}}.settings-card .button{{margin-top:12px}}.empty{{padding:25px;border:1px dashed #365243;border-radius:10px;color:var(--muted);font-size:13px;text-align:center;grid-column:1/-1}}.mobile-bar,.mobile-drawer{{display:none}}
@media(max-width:950px){{.shell{{grid-template-columns:205px minmax(0,1fr)}}aside{{padding-inline:12px}}main{{padding-inline:25px}}.stats,.board{{grid-template-columns:repeat(2,minmax(0,1fr))}}.steps{{grid-template-columns:1fr 1fr;gap:5px}}.step-arrow{{display:none}}.steps>a{{border:1px solid #1b3426;border-radius:9px;padding:10px}}.two-col{{grid-template-columns:1fr}}}}
@media(max-width:680px){{.shell{{display:block;padding-bottom:78px}}aside{{display:none}}.mobile-bar{{position:fixed;z-index:20;left:0;right:0;bottom:0;display:flex;justify-content:space-around;align-items:center;padding:6px 6px calc(6px + env(safe-area-inset-bottom));background:#1C2D23;border-top:1px solid #385143}}.mobile-bar a,.mobile-bar button{{flex:1;min-height:44px;display:grid;place-items:center;font-size:11px;color:#DBE5DC;text-decoration:none;background:none;border:0;cursor:pointer}}.mobile-bar a.active{{color:#F6E0B2;font-weight:700}}.mobile-drawer.open{{display:grid;grid-template-columns:1fr 1fr;gap:8px;position:fixed;z-index:25;left:12px;right:12px;bottom:68px;background:#1C2D23;padding:14px;border-radius:14px;border:1px solid #385143;box-shadow:0 16px 40px rgba(0,0,0,.32)}}.drawer-link{{min-height:44px;display:flex;align-items:center;padding:8px 12px;border-radius:8px;color:#DBE5DC;text-decoration:none;font-size:13px}}.drawer-link.active{{background:#2d7954;color:#fdfee6}}main{{padding:19px 15px 36px}}.topline{{margin-bottom:20px}}.welcome,.page-head{{display:block}}.welcome .button,.page-head>.button{{margin-top:17px}}.welcome{{padding:14px 0 22px}}h1{{font-size:34px}}.stats{{gap:8px}}.stat{{padding:13px}}.stat>b{{font-size:28px}}.stat small{{font-size:10px}}.workflow,.panel{{padding:16px;margin:12px 0}}.steps{{gap:6px}}.steps b{{font-size:14px}}.steps small{{font-size:10px}}.draft-grid,.audience-grid,.evidence-grid,.settings-grid,.studio-layout,.board,.limits-grid{{grid-template-columns:1fr}}.run-bar,.selection-bar,.run-actions{{align-items:stretch;flex-direction:column}}.run-bar .button,.selection-bar .button,.run-card .button{{width:100%}}.section-head{{align-items:flex-start;flex-direction:column}}.search{{width:100%}}.search input{{min-width:0;flex:1}}.run-row{{grid-template-columns:1fr;gap:5px}}.status{{display:inline-flex;margin-top:5px}}.filter-pills{{gap:5px}}}}
</style></head><body><div class="shell"><aside><div class="brand"><div class="brand-mark">PH</div><div><b>Perpustakaan Hati</b><small>Research studio</small></div></div><div><p class="nav-label">WORKSPACE</p><nav>{nav}</nav></div><div class="side-bottom">Research is a sample, not a census.<br><a href="/?view=settings">Privacy &amp; connections →</a>{logout_action}</div></aside><main><div class="topline"><span class="crumb">Workspace <span class="muted">/</span> {_e(labels[view])}</span>{account_badge}</div>{notice_banner}{nav_error}{content}</main></div>
<nav class="mobile-bar"><a class="{"active" if view == "overview" else ""}" href="/?view=overview">Home</a><a class="{"active" if view == "research" else ""}" href="/?view=research">Research</a><a class="{"active" if view == "followers" else ""}" href="/?view=followers">Followers</a><a class="{"active" if view == "library" else ""}" href="/?view=library">Drafts</a><button type="button" data-toggle-more="true">More ☰</button></nav>
<div class="mobile-drawer" id="mobile-drawer">{mobile_more}</div>
<script{nonce_attr}>
document.addEventListener('click',async e=>{{
  const cf=e.target.closest('[data-confirm]');if(cf&&!confirm(cf.dataset.confirm)){{e.preventDefault();return;}}
  const tm=e.target.closest('[data-toggle-more]');if(tm){{const d=document.getElementById('mobile-drawer');if(d)d.classList.toggle('open');return;}}
  const b=e.target.closest('[data-copy]');if(b){{const el=document.getElementById(b.dataset.copy);if(!el)return;const text=el.innerText;try{{await navigator.clipboard.writeText(text);b.textContent='Copied';setTimeout(()=>b.textContent='Copy text',1400)}}catch{{const ta=document.createElement('textarea');ta.value=text;document.body.appendChild(ta);ta.select();document.execCommand('copy');ta.remove();b.textContent='Copied'}}return}}
  const sa=e.target.closest('[data-select-all]');if(sa){{const v=sa.dataset.selectAll==='true';document.querySelectorAll('input[name="insight_ids"]').forEach(c=>{{c.checked=v}});return}}
  const sf=e.target.closest('[data-select-follow]');if(sf){{const v=sf.dataset.selectFollow==='true';document.querySelectorAll('input[name="usernames"]').forEach(c=>{{c.checked=v}});return}}
  const cu=e.target.closest('[data-copy-usernames]');if(cu){{const checked=[...document.querySelectorAll('input[name="usernames"]:checked')].map(c=>'@'+c.value);const all=[...document.querySelectorAll('input[name="usernames"]')].map(c=>'@'+c.value);const list=checked.length?checked:all;if(!list.length)return;try{{await navigator.clipboard.writeText(list.join('\\n'));cu.textContent='Copied '+list.length;setTimeout(()=>cu.textContent='Copy @usernames',1400)}}catch{{}}return}}
  const os=e.target.closest('[data-open-studio]');if(os){{const ids=[...document.querySelectorAll('input[name="insight_ids"]:checked')].map(c=>c.value);location.href='/?view=studio'+(ids.length?'&select='+ids.join(','):'');return}}
}});
document.addEventListener('input',e=>{{
  const src=e.target.closest('[data-char-source]');
  if(src){{const out=document.querySelector('[data-char-count="'+src.dataset.charSource+'"]');if(out)out.textContent=String(src.value.length);}}
}});
const qEl=document.querySelector('[data-queue-active]');
if(qEl){{
  if(window.EventSource){{
    const es=new EventSource('/queue/stream');
    es.addEventListener('done',()=>{{es.close();if(!document.activeElement||document.activeElement===document.body)location.reload();}});
    es.onerror=()=>{{es.close();}};
  }}else{{
    setTimeout(()=>{{if(!document.activeElement||document.activeElement===document.body)location.reload();}},8000);
  }}
}}
</script></body></html>'''
