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
    """O(1) relationship lookup for insight source permalinks."""

    def __init__(self, analysis: dict | None):
        source = analysis or {}
        followers = {str(person.get("username", "")).casefold() for person in source.get("fans", [])}
        followers |= {str(person.get("username", "")).casefold() for person in source.get("mutuals", [])}
        following = {str(person.get("username", "")).casefold() for person in source.get("not_following_back", [])}
        following |= {str(person.get("username", "")).casefold() for person in source.get("mutuals", [])}
        self._followers = followers
        self._following = following

    @property
    def enabled(self) -> bool:
        return bool(self._followers or self._following)

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
