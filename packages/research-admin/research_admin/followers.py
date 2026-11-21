"""Follow-back analysis from a Threads data export.

The Threads Graph API exposes a profile's own posts, replies and insights but
no follower or following list, so this works from the JSON files in Instagram's
"Download your data" export — the same source the Threads-Follower tool uses
(https://github.com/Xiang511/Threads-Follower). Nothing read here is ever sent
to the AI provider.
"""

import re
from datetime import UTC, datetime

# Server-side ceilings, independent of what the form accepts.
MAX_ENTRIES = 50_000
MAX_HREF = 300
MAX_USERNAME = 60
MAX_EPOCH = 4102444800  # 2101-01-01, so a corrupt timestamp cannot crash a render.

AUDIENCE_LISTS = ("not_following_back", "fans", "mutuals")
FOLLOW_VIEW_LISTS = ("not_following_back", "following", "unfollow_later", "fans", "mutuals")
AUDIENCE_LIST_LABELS = {
    "not_following_back": "Not following back",
    "following": "Following",
    "unfollow_later": "Unfollow later",
    "fans": "Fans",
    "mutuals": "Mutuals",
}
UNFOLLOW_FILTERS = (
    "all",
    "not_following_back",
    "ghosts",
    "older_90d",
    "older_30d",
    "recent_30d",
    "engaged",
    "unfollow_later",
)
UNFOLLOW_FILTER_LABELS = {
    "all": "All",
    "not_following_back": "Not following back",
    "ghosts": "Ghost (0 replies)",
    "older_90d": "Followed 90+ days",
    "older_30d": "Followed 30+ days",
    "recent_30d": "Recent (<30d)",
    "engaged": "Replied on Threads",
    "unfollow_later": "Unfollow later queue",
}
FOLLOW_SORTS = ("newest", "oldest", "az")
FOLLOW_SORT_LABELS = {
    "newest": "Newest followed",
    "oldest": "Oldest followed first",
    "az": "Username A–Z",
}
GRAPH_COMMUNITY_LISTS = ("all_engagers", "insight_contributors", "frequent_engagers")
GRAPH_COMMUNITY_LABELS = {
    "all_engagers": "Active repliers",
    "insight_contributors": "Insight contributors",
    "frequent_engagers": "Frequent engagers (2+)",
}
TAG_LABELS = {"mutual": "Mutual", "follower": "Follows Rahimam", "following_only": "Doesn't follow back", "none": "Not connected"}

PERMALINK = re.compile(r"@([A-Za-z0-9._]{1,30})", re.IGNORECASE)
THREADS_POST_URL = re.compile(
    r"https://(?:www\.)?threads\.(?:com|net)/@([A-Za-z0-9._]{1,30})/post/[A-Za-z0-9_-]+/?",
    re.IGNORECASE,
)


class AudienceError(ValueError):
    """Rejected export file, with a message safe to show in the browser."""


def author_of(url) -> str:
    """The account a Threads permalink points at, lower-cased, or ''."""
    match = PERMALINK.search(str(url or ""))
    return match.group(1).casefold() if match else ""


def community_source_url(person: dict) -> str:
    """Allow only a direct Threads post or reply owned by this account."""
    url = str(person.get("last_url") or "")
    match = THREADS_POST_URL.fullmatch(url)
    if match and match.group(1).casefold() == str(person.get("username", "")).casefold():
        return url
    return ""


def since_date(timestamp) -> str:
    """ISO date for a Unix timestamp, or '' when it is missing or corrupt."""
    try:
        value = int(timestamp or 0)
    except (TypeError, ValueError):
        return ""
    if not 0 < value < MAX_EPOCH:
        return ""
    try:
        return datetime.fromtimestamp(value, UTC).strftime("%Y-%m-%d")
    except (OverflowError, OSError, ValueError):
        return ""


def _entries(payload, label: str) -> list:
    """Every export shape we accept ends in a list of accounts."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for value in payload.values():
            if isinstance(value, list):
                return value
    raise AudienceError(
        f"{label} is not a list of accounts. Upload followers.json and following.json from the Threads data export (JSON format)."
    )


def _fields(entry) -> tuple[str, str, int]:
    if isinstance(entry, str):
        return entry.strip(), "", 0
    if not isinstance(entry, dict):
        return "", "", 0
    inner = entry.get("string_list_data")
    source = inner[0] if isinstance(inner, list) and inner and isinstance(inner[0], dict) else entry
    username = str(source.get("value") or entry.get("title") or entry.get("username") or "").strip()
    href = str(source.get("href") or entry.get("href") or "").strip()[:MAX_HREF]
    try:
        timestamp = max(0, int(source.get("timestamp", entry.get("timestamp", 0)) or 0))
    except (TypeError, ValueError):
        timestamp = 0
    return username, href, timestamp


def parse_export(payload, *, label: str) -> list[dict]:
    """Normalise one export file into {username, href, timestamp} rows.

    Accepts the raw Meta export (title + string_list_data), the flat
    {value, href, timestamp} shape third-party tools emit, plain username
    strings, and objects wrapping any of those in a list.
    """
    entries = _entries(payload, label)
    if not entries:
        raise AudienceError(f"No accounts found in {label}. Upload followers.json and following.json from the Threads data export.")
    if len(entries) > MAX_ENTRIES:
        raise AudienceError(f"{label} lists more than {MAX_ENTRIES:,} accounts; this admin imports up to {MAX_ENTRIES:,} per file.")
    people, seen = [], set()
    for entry in entries:
        username, href, timestamp = _fields(entry)
        if username.startswith(("http://", "https://")):
            href = href or username
            found = PERMALINK.search(username)
            username = found.group(1) if found else username.rstrip("/").rsplit("/", 1)[-1]
        username = username.lstrip("@").strip()[:MAX_USERNAME]
        if not username:
            continue
        key = username.casefold()
        if key in seen:
            continue
        seen.add(key)
        people.append({"username": username, "href": href, "timestamp": timestamp})
    if not people:
        raise AudienceError(f"No usernames found in {label}. Upload followers.json and following.json from the Threads data export.")
    return people


def _since(*values) -> int:
    known = [value for value in values if value]
    return max(known) if known else 0


def _days_since(timestamp: int, now_ts: int) -> int | None:
    if not 0 < timestamp < MAX_EPOCH or now_ts <= 0:
        return None
    return max(0, (now_ts - timestamp) // 86400)


def _tenure_bucket(days: int | None) -> str:
    if days is None:
        return "unknown"
    if days >= 90:
        return "90d_plus"
    if days >= 30:
        return "30d_plus"
    return "recent_30d"


def _person_row(
    person: dict,
    *,
    since_ts: int,
    follows_back: bool,
    now_ts: int,
    meta: tuple[str, dict | None] = ("", None),
) -> dict:
    unfollow_status, engager = meta
    uname = str(person["username"])
    href = str(person.get("href", ""))
    profile_url = href if href.startswith(("http://", "https://")) else f"https://www.threads.com/@{uname}"[:MAX_HREF]
    days = _days_since(since_ts, now_ts)
    replies_count = int(engager.get("replies_count", 0) or 0) if isinstance(engager, dict) else 0
    insight_count = len(engager.get("insight_ids", [])) if isinstance(engager, dict) else 0
    return {
        "username": uname,
        "href": href,
        "profile_url": profile_url,
        "since": since_ts,
        "follows_back": follows_back,
        "days_followed": days,
        "tenure_bucket": _tenure_bucket(days),
        "unfollow_status": unfollow_status,
        "replies_count": replies_count,
        "insight_count": insight_count,
    }


def _compute_follow_insights(counts: dict, groups: dict[str, list[dict]]) -> dict:
    followers_count = int(counts["followers"])
    following_count = int(counts["following"])
    not_following_back = groups["not_following_back"]
    fans = groups["fans"]
    mutuals = groups["mutuals"]
    unfollow_later = groups["unfollow_later"]
    unfollowed = groups["unfollowed"]
    ghosts = sum(1 for p in not_following_back if int(p.get("replies_count", 0)) == 0)
    engaged = sum(1 for p in not_following_back if int(p.get("replies_count", 0)) > 0)
    older_90d = sum(1 for p in not_following_back if (p.get("days_followed") or -1) >= 90)
    older_30d = sum(1 for p in not_following_back if (p.get("days_followed") or -1) >= 30)
    recent_30d = sum(1 for p in not_following_back if p.get("days_followed") is not None and int(p["days_followed"]) < 30)
    unknown_date = sum(1 for p in not_following_back if p.get("days_followed") is None)
    dated_days = sorted(int(p["days_followed"]) for p in not_following_back if p.get("days_followed") is not None)
    median_days = dated_days[len(dated_days) // 2] if dated_days else None
    dated_people = [p for p in not_following_back if int(p.get("since", 0)) > 0]
    oldest_person = min(dated_people, key=lambda p: (int(p["since"]), p["username"].casefold())) if dated_people else None
    oldest_summary = (
        {
            "username": oldest_person["username"],
            "since_date": since_date(oldest_person["since"]),
            "days_followed": oldest_person["days_followed"],
            "profile_url": oldest_person["profile_url"],
        }
        if oldest_person
        else None
    )
    cohorts: dict[str, int] = {}
    for person in dated_people:
        day_str = since_date(person["since"])
        if len(day_str) >= 7:
            ym = day_str[:7]
            cohorts[ym] = cohorts.get(ym, 0) + 1
    top_cohorts = [
        {"month": ym, "count": cnt}
        for ym, cnt in sorted(cohorts.items(), key=lambda item: (-item[1], item[0]))[:4]
    ]
    return {
        "reciprocity_rate": round(100 * len(mutuals) / following_count, 1) if following_count else 0.0,
        "follower_following_ratio": round(followers_count / following_count, 2) if following_count else float(followers_count),
        "fan_rate": round(100 * len(fans) / followers_count, 1) if followers_count else 0.0,
        "ghost_non_followers": ghosts,
        "engaged_non_followers": engaged,
        "older_90d_count": older_90d,
        "older_30d_count": older_30d,
        "recent_30d_count": recent_30d,
        "unknown_date_count": unknown_date,
        "median_days_not_following_back": median_days,
        "oldest_non_follower": oldest_summary,
        "top_cohorts": top_cohorts,
        "unfollow_later_count": len(unfollow_later),
        "unfollowed_count": len(unfollowed),
    }


def analyze_audience(
    followers: list[dict],
    following: list[dict],
    *,
    unfollow_map: dict[str, str] | None = None,
    engagers: list[dict] | None = None,
    now_ts: int | None = None,
) -> dict:
    """Split the two exports into relationships and compute unfollow/follow-back insights."""
    now_val = int(now_ts if now_ts is not None else datetime.now(UTC).timestamp())
    uf_map = {str(k).casefold(): str(v) for k, v in (unfollow_map or {}).items()}
    engager_map = {
        str(e.get("username", "")).casefold(): e
        for e in (engagers or [])
        if isinstance(e, dict) and str(e.get("username", "")).strip()
    }
    followed_by = {person["username"].casefold(): person for person in followers}
    following_now = {}
    unfollowed = []
    for person in following:
        key = person["username"].casefold()
        if uf_map.get(key) == "unfollowed":
            unfollowed.append(
                _person_row(person, since_ts=person["timestamp"], follows_back=key in followed_by, now_ts=now_val, meta=("unfollowed", engager_map.get(key)))
            )
        else:
            following_now[key] = person

    not_following_back = [
        _person_row(
            person,
            since_ts=person["timestamp"],
            follows_back=False,
            now_ts=now_val,
            meta=("later" if uf_map.get(key) == "later" else "", engager_map.get(key)),
        )
        for key, person in following_now.items()
        if key not in followed_by
    ]
    fans = [
        _person_row(
            person,
            since_ts=person["timestamp"],
            follows_back=True,
            now_ts=now_val,
            meta=("", engager_map.get(key)),
        )
        for key, person in followed_by.items()
        if key not in following_now
    ]
    mutuals = [
        _person_row(
            person,
            since_ts=_since(person["timestamp"], following_now[key]["timestamp"]),
            follows_back=True,
            now_ts=now_val,
            meta=("later" if uf_map.get(key) == "later" else "", engager_map.get(key)),
        )
        for key, person in followed_by.items()
        if key in following_now
    ]
    all_following = [
        _person_row(
            person,
            since_ts=person["timestamp"],
            follows_back=key in followed_by,
            now_ts=now_val,
            meta=("later" if uf_map.get(key) == "later" else "", engager_map.get(key)),
        )
        for key, person in following_now.items()
    ]
    unfollow_later = [p for p in all_following if p.get("unfollow_status") == "later"]
    for group in (not_following_back, fans, mutuals, all_following, unfollow_later, unfollowed):
        group.sort(key=lambda person: (-person["since"], person["username"].casefold()))
    following_count = len(following_now)
    counts = {
        "followers": len(followed_by),
        "following": following_count,
        "not_following_back": len(not_following_back),
        "fans": len(fans),
        "mutuals": len(mutuals),
        "percent_not_following_back": round(100 * len(not_following_back) / following_count, 1) if following_count else 0.0,
    }
    groups = {
        "not_following_back": not_following_back,
        "following": all_following,
        "unfollow_later": unfollow_later,
        "unfollowed": unfollowed,
        "fans": fans,
        "mutuals": mutuals,
    }
    return {"counts": counts, **groups, "insights": _compute_follow_insights(counts, groups)}


_UNFOLLOW_PREDICATES = {
    "not_following_back": lambda p: not p.get("follows_back", False),
    "ghosts": lambda p: not p.get("follows_back", False) and int(p.get("replies_count", 0)) == 0,
    "older_90d": lambda p: not p.get("follows_back", False) and (p.get("days_followed") or -1) >= 90,
    "older_30d": lambda p: not p.get("follows_back", False) and (p.get("days_followed") or -1) >= 30,
    "recent_30d": lambda p: not p.get("follows_back", False) and p.get("days_followed") is not None and int(p["days_followed"]) < 30,
    "engaged": lambda p: not p.get("follows_back", False) and int(p.get("replies_count", 0)) > 0,
    "unfollow_later": lambda p: p.get("unfollow_status") == "later",
}


def _apply_unfollow_filter(people: list[dict], uf: str) -> list[dict]:
    pred = _UNFOLLOW_PREDICATES.get(uf)
    return [p for p in people if pred(p)] if pred else people


def count_unfollow_filters(analysis: dict, list_key: str) -> dict[str, int]:
    """Compute accurate filter chip counts scoped to the currently selected audience tab."""
    key = list_key if list_key in FOLLOW_VIEW_LISTS else AUDIENCE_LISTS[0]
    people = list(analysis.get(key, []))
    counts = {"all": len(people)}
    for uf_key, pred in _UNFOLLOW_PREDICATES.items():
        counts[uf_key] = sum(1 for person in people if pred(person))
    return counts


def build_preimport_analysis(unfollow_queue: list[dict], engagers: list[dict] | None = None) -> dict:
    """Build lightweight audience analysis from persisted unfollow queue and Graph engagers prior to JSON upload."""
    engager_map = {
        str(e.get("username", "")).casefold(): e
        for e in (engagers or [])
        if isinstance(e, dict) and str(e.get("username", "")).strip()
    }
    hydrated = []
    for row in unfollow_queue or []:
        item = dict(row)
        eng = engager_map.get(str(item.get("username", "")).casefold())
        if eng:
            item["replies_count"] = max(int(item.get("replies_count", 0) or 0), int(eng.get("replies_count", 0) or 0))
            item["insight_count"] = max(int(item.get("insight_count", 0) or 0), len(eng.get("insight_ids", [])))
        hydrated.append(item)
    later_rows = [p for p in hydrated if p.get("unfollow_status") == "later"]
    done_rows = [p for p in hydrated if p.get("unfollow_status") == "unfollowed"]
    empty_counts = {
        "followers": 0,
        "following": 0,
        "not_following_back": 0,
        "fans": 0,
        "mutuals": 0,
        "percent_not_following_back": 0.0,
    }
    groups = {
        "not_following_back": [],
        "following": [],
        "unfollow_later": later_rows,
        "unfollowed": done_rows,
        "fans": [],
        "mutuals": [],
    }
    return {"counts": empty_counts, **groups, "insights": _compute_follow_insights(empty_counts, groups)}


def diff_snapshots(previous: dict | None, current_followers: list[dict], current_following: list[dict]) -> dict | None:
    """Compare a previous audience snapshot against the current JSON export."""
    if not previous:
        return None
    prev_followers = {str(p.get("username", "")).casefold(): str(p.get("username", "")) for p in previous.get("followers", []) if p.get("username")}
    prev_following = {str(p.get("username", "")).casefold(): str(p.get("username", "")) for p in previous.get("following", []) if p.get("username")}
    curr_followers = {str(p.get("username", "")).casefold(): str(p.get("username", "")) for p in current_followers if p.get("username")}
    curr_following = {str(p.get("username", "")).casefold(): str(p.get("username", "")) for p in current_following if p.get("username")}
    prev_mutuals = set(prev_followers) & set(prev_following)
    curr_mutuals = set(curr_followers) & set(curr_following)
    new_followers = [curr_followers[k] for k in sorted(set(curr_followers) - set(prev_followers))]
    unfollowed_you = [prev_followers[k] for k in sorted(set(prev_followers) - set(curr_followers))]
    you_unfollowed = [prev_following[k] for k in sorted(set(prev_following) - set(curr_following))]
    newly_mutual = [curr_followers[k] for k in sorted(curr_mutuals - prev_mutuals)]
    return {
        "previous_imported_at": str(previous.get("imported_at", "")),
        "new_followers": new_followers[:50],
        "new_followers_count": len(new_followers),
        "unfollowed_you": unfollowed_you[:50],
        "unfollowed_you_count": len(unfollowed_you),
        "you_unfollowed": you_unfollowed[:50],
        "you_unfollowed_count": len(you_unfollowed),
        "newly_mutual": newly_mutual[:50],
        "newly_mutual_count": len(newly_mutual),
    }


def filter_people(  # noqa: PLR0913
    analysis: dict,
    list_key: str,
    query: str = "",
    *,
    uf: str = "",
    sort: str = "newest",
    limit: int = 200,
) -> tuple[list[dict], int]:
    """One bounded page of a list, optionally filtered by username/cohort, unfollow segment, and sort order."""
    key = list_key if list_key in FOLLOW_VIEW_LISTS else AUDIENCE_LISTS[0]
    needle = " ".join(str(query or "").split()).casefold()[:MAX_USERNAME]
    people = list(analysis.get(key, []))
    if uf in UNFOLLOW_FILTERS and uf != "all":
        people = _apply_unfollow_filter(people, uf)
    if needle:
        people = [
            person for person in people
            if needle in str(person.get("username", "")).casefold()
            or needle in since_date(person.get("since"))
        ]
    if sort == "oldest":
        people.sort(key=lambda p: (0 if int(p.get("since", 0)) > 0 else 1, int(p.get("since", 0)), p["username"].casefold()))
    elif sort == "az":
        people.sort(key=lambda p: p["username"].casefold())
    else:
        people.sort(key=lambda p: (-int(p.get("since", 0)), p["username"].casefold()))
    return people[:max(1, int(limit))], len(people)


class AudienceIndex:
    """O(1) relationship and Graph-community lookup for insight source permalinks."""

    def __init__(self, analysis: dict | None, graph: dict | None = None):
        source = analysis or {}
        followers = {str(person.get("username", "")).casefold() for person in source.get("fans", [])}
        followers |= {str(person.get("username", "")).casefold() for person in source.get("mutuals", [])}
        following = {str(person.get("username", "")).casefold() for person in source.get("not_following_back", [])}
        following |= {str(person.get("username", "")).casefold() for person in source.get("mutuals", [])}
        self._followers = followers
        self._following = following
        graph_source = graph or {}
        self._engagers = {
            str(person.get("username", "")).casefold(): person
            for person in graph_source.get("engagers", [])
            if isinstance(person, dict) and str(person.get("username", "")).strip()
        }

    @property
    def enabled(self) -> bool:
        return bool(self._followers or self._following)

    @property
    def graph_enabled(self) -> bool:
        return bool(self._engagers)

    def tag(self, url) -> str:
        name = author_of(url)
        if not name or not self.enabled:
            return ""
        if name in self._followers and name in self._following:
            return "mutual"
        if name in self._followers:
            return "follower"
        if name in self._following:
            return "following_only"
        return "none"

    def engager(self, url) -> dict | None:
        name = author_of(url)
        if not name or not self._engagers:
            return None
        return self._engagers.get(name)


def _iso_day(value) -> str:
    text = str(value or "").strip()
    if len(text) >= 10 and text[4:5] == "-" and text[7:8] == "-":
        return text[:10]
    return since_date(value)


def _ensure_engager(by_user: dict[str, dict], uname: str, *, day: str = "", quote: str = "", url: str = "") -> dict:
    key = uname.casefold()
    record = by_user.get(key)
    if not record:
        record = {
            "username": uname,
            "href": f"https://www.threads.com/@{uname}"[:MAX_HREF],
            "replies_count": 0,
            "seen_urls": set(),
            "insight_ids": set(),
            "themes": set(),
            "last_seen": day,
            "sample_quote": quote,
            "last_url": url,
        }
        by_user[key] = record
    return record


def _merge_reply_engager(by_user: dict[str, dict], item: dict, owners: set[str]) -> None:
    if not isinstance(item, dict) or item.get("source_type") == "post":
        return
    url = str(item.get("permalink") or "").strip()[:MAX_HREF]
    raw_name = str(item.get("username") or "").strip().lstrip("@") or author_of(url)
    uname = raw_name[:MAX_USERNAME]
    if not uname or uname.casefold() in owners:
        return
    day = _iso_day(item.get("timestamp"))
    text = " ".join(str(item.get("text") or "").split())[:160]
    reply_key = (url or str(item.get("id") or text))[:MAX_HREF]
    record = _ensure_engager(by_user, uname, day=day, quote=text, url=url)
    if reply_key and reply_key not in record["seen_urls"]:
        record["seen_urls"].add(reply_key)
        record["replies_count"] = max(record["replies_count"], len(record["seen_urls"]))
    elif not reply_key:
        record["replies_count"] += 1
    if day and (not record["last_seen"] or day >= record["last_seen"]):
        record["last_seen"] = day
        record["sample_quote"] = text or record["sample_quote"]
        record["last_url"] = url or record["last_url"]
    elif text and not record["sample_quote"]:
        record["sample_quote"] = text


def extract_engagers(
    sources: list[dict],
    insights: list[dict] | None = None,
    *,
    owner_username: str = "",
    existing: list[dict] | None = None,
) -> list[dict]:
    """Build an active community roster from Threads Graph replies and saved insights."""
    owners = {owner_username.strip().lstrip("@").casefold()} if owner_username and owner_username.strip() else set()
    for item in sources or []:
        if isinstance(item, dict) and item.get("source_type") == "post":
            post_author = str(item.get("username") or author_of(item.get("permalink")) or "").strip().lstrip("@").casefold()
            if post_author:
                owners.add(post_author)

    by_user: dict[str, dict] = {}
    for prev in existing or []:
        if not isinstance(prev, dict):
            continue
        uname = str(prev.get("username", "")).strip().lstrip("@")[:MAX_USERNAME]
        if not uname or uname.casefold() in owners:
            continue
        by_user[uname.casefold()] = {
            "username": uname,
            "href": str(prev.get("href") or f"https://www.threads.com/@{uname}")[:MAX_HREF],
            "replies_count": max(1, int(prev.get("replies_count", 1) or 1)),
            "seen_urls": set(prev.get("seen_urls", [])),
            "insight_ids": {int(i) for i in prev.get("insight_ids", []) if str(i).isdigit()},
            "themes": {str(t).strip() for t in prev.get("themes", []) if str(t).strip()},
            "last_seen": str(prev.get("last_seen", ""))[:10],
            "sample_quote": str(prev.get("sample_quote", ""))[:160],
            "last_url": str(prev.get("last_url", ""))[:MAX_HREF],
        }

    for item in sources or []:
        _merge_reply_engager(by_user, item, owners)

    for item in insights or []:
        if not isinstance(item, dict):
            continue
        url = str(item.get("source_url") or "").strip()[:MAX_HREF]
        uname = author_of(url)[:MAX_USERNAME]
        if not uname or uname.casefold() in owners:
            continue
        quote_text = " ".join(str(item.get("quote") or "").split())[:160]
        record = _ensure_engager(by_user, uname, day=_iso_day(item.get("created_at")), quote=quote_text, url=url)
        if url:
            record["seen_urls"].add(url)
        record["replies_count"] = max(1, record["replies_count"], len(record["seen_urls"]))
        if str(item.get("id", "")).isdigit():
            record["insight_ids"].add(int(item["id"]))
        theme = str(item.get("theme") or "").strip()
        if theme:
            record["themes"].add(theme)
        if not record["sample_quote"] and quote_text:
            record["sample_quote"] = quote_text

    result = [
        {
            "username": record["username"],
            "href": record["href"],
            "replies_count": max(1, int(record["replies_count"])),
            "seen_urls": sorted(record["seen_urls"])[:50],
            "insight_ids": sorted(record["insight_ids"]),
            "themes": sorted(record["themes"]),
            "last_seen": record["last_seen"],
            "sample_quote": record["sample_quote"],
            "last_url": record["last_url"],
        }
        for record in by_user.values()
    ]
    result.sort(key=lambda p: (-len(p["insight_ids"]), -p["replies_count"], p["username"].casefold()))
    return result[:500]


def analyze_graph_community(graph_data: dict | None, insights: list[dict] | None = None) -> dict | None:
    """Enrich stored Graph API audience telemetry and active community with saved insights."""
    if not graph_data:
        return None
    profile = graph_data.get("profile") if isinstance(graph_data.get("profile"), dict) else {}
    owner = str(profile.get("username", "")).strip()
    engagers = extract_engagers([], insights or [], owner_username=owner, existing=graph_data.get("engagers", []))
    followers_count = max(0, int(graph_data.get("followers_count", 0) or 0))
    prev = graph_data.get("previous_followers_count")
    delta = (followers_count - int(prev)) if prev is not None and str(prev).lstrip("-").isdigit() else None
    insight_contributors = [p for p in engagers if p.get("insight_ids")]
    frequent_engagers = [p for p in engagers if int(p.get("replies_count", 0)) >= 2]
    return {
        "profile": profile,
        "synced_at": str(graph_data.get("synced_at", "")),
        "metrics": graph_data.get("metrics") if isinstance(graph_data.get("metrics"), dict) else {},
        "demographics": graph_data.get("demographics") if isinstance(graph_data.get("demographics"), dict) else {},
        "engagers": engagers,
        "all_engagers": engagers,
        "insight_contributors": insight_contributors,
        "frequent_engagers": frequent_engagers,
        "counts": {
            "followers_count": followers_count,
            "followers_delta": delta,
            "active_repliers": len(engagers),
            "insight_contributors": len(insight_contributors),
            "frequent_engagers": len(frequent_engagers),
        },
    }


def filter_graph_people(graph_analysis: dict, list_key: str, query: str = "", *, limit: int = 200) -> tuple[list[dict], int]:
    """Filter active community members from the Threads Graph by list and search query."""
    key = list_key if list_key in GRAPH_COMMUNITY_LISTS else GRAPH_COMMUNITY_LISTS[0]
    needle = " ".join(str(query or "").split()).casefold()[:MAX_USERNAME]
    people = graph_analysis.get(key, [])
    if needle:
        handle = needle.removeprefix("@")
        people = [
            person for person in people
            if (handle and handle in str(person.get("username", "")).casefold())
            or needle in str(person.get("sample_quote", "")).casefold()
            or any(needle in str(t).casefold() for t in person.get("themes", []))
        ]
    return people[:max(1, int(limit))], len(people)

