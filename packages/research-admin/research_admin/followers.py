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
AUDIENCE_LIST_LABELS = {"not_following_back": "Not following back", "fans": "Fans", "mutuals": "Mutuals"}
GRAPH_COMMUNITY_LISTS = ("all_engagers", "insight_contributors", "frequent_engagers")
GRAPH_COMMUNITY_LABELS = {
    "all_engagers": "Active repliers",
    "insight_contributors": "Insight contributors",
    "frequent_engagers": "Frequent engagers (2+)",
}
TAG_LABELS = {"mutual": "Mutual", "follower": "Follows Rahimam", "following_only": "Doesn't follow back", "none": "Not connected"}

PERMALINK = re.compile(r"@([A-Za-z0-9._]{1,30})", re.IGNORECASE)


class AudienceError(ValueError):
    """Rejected export file, with a message safe to show in the browser."""


def author_of(url) -> str:
    """The account a Threads permalink points at, lower-cased, or ''."""
    match = PERMALINK.search(str(url or ""))
    return match.group(1).casefold() if match else ""


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


def analyze_audience(followers: list[dict], following: list[dict]) -> dict:
    """Split the two exports into the three relationships, newest first."""
    followed_by = {person["username"].casefold(): person for person in followers}
    following_now = {person["username"].casefold(): person for person in following}
    not_following_back = [
        {"username": person["username"], "href": person["href"], "since": person["timestamp"]}
        for key, person in following_now.items() if key not in followed_by
    ]
    fans = [
        {"username": person["username"], "href": person["href"], "since": person["timestamp"]}
        for key, person in followed_by.items() if key not in following_now
    ]
    mutuals = [
        {"username": person["username"], "href": person["href"], "since": _since(person["timestamp"], following_now[key]["timestamp"])}
        for key, person in followed_by.items() if key in following_now
    ]
    for group in (not_following_back, fans, mutuals):
        group.sort(key=lambda person: (-person["since"], person["username"].casefold()))
    following_count = len(following_now)
    return {
        "counts": {
            "followers": len(followed_by),
            "following": following_count,
            "not_following_back": len(not_following_back),
            "fans": len(fans),
            "mutuals": len(mutuals),
            "percent_not_following_back": round(100 * len(not_following_back) / following_count, 1) if following_count else 0.0,
        },
        "not_following_back": not_following_back,
        "fans": fans,
        "mutuals": mutuals,
    }


def filter_people(analysis: dict, list_key: str, query: str = "", *, limit: int = 200) -> tuple[list[dict], int]:
    """One bounded page of a list, optionally filtered by username."""
    key = list_key if list_key in AUDIENCE_LISTS else AUDIENCE_LISTS[0]
    needle = " ".join(str(query or "").split()).casefold()[:MAX_USERNAME]
    people = analysis.get(key, [])
    if needle:
        people = [person for person in people if needle in str(person.get("username", "")).casefold()]
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
        people = [
            person for person in people
            if needle in str(person.get("username", "")).casefold()
            or needle in str(person.get("sample_quote", "")).casefold()
            or any(needle in str(t).casefold() for t in person.get("themes", []))
        ]
    return people[:max(1, int(limit))], len(people)

