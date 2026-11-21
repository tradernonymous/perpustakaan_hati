"""Serve the connected Threads avatar without a third-party browser request."""

from collections.abc import Callable
from html import escape
from threading import Lock
from time import monotonic
from urllib.parse import urlsplit

import httpx

AVATAR_PATH = "/assets/threads-avatar"
MAX_AVATAR_BYTES = 512 * 1024
MAX_AVATAR_URL_LENGTH = 4096
AVATAR_HOSTS = ("cdninstagram.com", "fbcdn.net", "cdn.threads.net")


def _avatar_url_allowed(url: str) -> bool:
    if not url or len(url) > MAX_AVATAR_URL_LENGTH:
        return False
    try:
        parts = urlsplit(url)
        host = parts.hostname or ""
        return (
            parts.scheme == "https"
            and parts.port in (None, 443)
            and parts.username is None
            and parts.password is None
            and any(host == domain or host.endswith("." + domain) for domain in AVATAR_HOSTS)
        )
    except ValueError:
        return False


def _raster_type(body: bytes) -> str:
    if body.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if body.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if body.startswith(b"RIFF") and body[8:12] == b"WEBP":
        return "image/webp"
    return ""


def _download_avatar(http: httpx.Client, url: str) -> tuple[bytes, str] | None:
    if not _avatar_url_allowed(url):
        return None
    deadline = monotonic() + 5
    try:
        with http.stream(
            "GET", url, follow_redirects=False, timeout=3.0,
            headers={"Accept": "image/jpeg, image/png, image/webp", "Accept-Encoding": "identity"},
        ) as response:
            if response.status_code != 200 or response.headers.get("Content-Encoding", "identity") != "identity":
                return None
            body = bytearray()
            for chunk in response.iter_bytes(8192):
                if len(body) + len(chunk) > MAX_AVATAR_BYTES or monotonic() > deadline:
                    return None
                body.extend(chunk)
            image = bytes(body)
            media_type = _raster_type(image)
            return (image, media_type) if media_type else None
    except (httpx.HTTPError, httpx.InvalidURL):
        return None


def _initial_avatar(username: str) -> tuple[bytes, str]:
    initial = escape(username[:1].upper() or "R")
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
        '<circle cx="12" cy="12" r="12" fill="#214333"/>'
        f'<text x="12" y="16.5" text-anchor="middle" fill="#e9cea2" font-size="13" '
        f'font-family="sans-serif" font-weight="700">{initial}</text></svg>'
    )
    return svg.encode(), "image/svg+xml"


class ThreadsAvatar:
    """Cache one resolved image per admin process and retry expired CDN URLs."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._key = ("", "", "")
        self._expires = 0.0
        self._image = _initial_avatar("")

    def resolve(
        self, http: httpx.Client, profile: dict, refresh: Callable[[], dict],
    ) -> tuple[bytes, str]:
        profile_id = str(profile.get("id") or "")
        username = str(profile.get("username") or "").lstrip("@")
        url = str(profile.get("profile_picture_url") or "")
        key = (profile_id, username, url)
        with self._lock:
            if key == self._key and self._expires > monotonic():
                return self._image
            photo = _download_avatar(http, url)
            if photo is None and (profile_id or username):
                fresh = refresh()
                same_profile = (
                    str(fresh.get("id") or "") == profile_id if profile_id
                    else str(fresh.get("username") or "").casefold() == username.casefold()
                )
                fresh_url = str(fresh.get("profile_picture_url") or "")
                if same_profile and fresh_url != url:
                    photo = _download_avatar(http, fresh_url)
            self._key = key
            self._expires = monotonic() + (3600 if photo else 60)
            self._image = photo or _initial_avatar(username)
            return self._image
