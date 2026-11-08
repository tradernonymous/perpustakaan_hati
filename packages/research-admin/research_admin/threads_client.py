"""Read-only Threads OAuth and bounded research collection."""

from dataclasses import dataclass, field
from urllib.parse import parse_qs, urlencode, urlsplit

import httpx

from .config import Settings

GRAPH = "https://graph.threads.com"
FIELDS = "id,text,permalink,timestamp"
METRICS = ("views", "likes", "replies", "reposts", "quotes")


class ThreadsError(RuntimeError):
    """Sanitized provider failure."""


@dataclass
class TokenResponse:
    access_token: str = field(repr=False)
    expires_in: int


class ThreadsClient:
    def __init__(self, settings: Settings, http: httpx.Client):
        self.settings = settings
        self.http = http

    def authorize_url(self, state: str) -> str:
        return "https://threads.com/oauth/authorize?" + urlencode({
            "client_id": self.settings.threads_client_id,
            "redirect_uri": self.settings.redirect_uri,
            "scope": "threads_basic,threads_read_replies,threads_manage_insights",
            "response_type": "code", "state": state,
        })

    def _request(self, method: str, path: str, token: str = "", **kwargs) -> dict:
        try:
            response = self.http.request(method, GRAPH + path,
                headers={"Authorization": f"Bearer {token}"} if token else {},
                follow_redirects=False, **kwargs)
            payload = response.json()
        except (httpx.HTTPError, ValueError):
            raise ThreadsError("Threads unavailable or returned an invalid response. Retry later.") from None
        if not isinstance(payload, dict):
            raise ThreadsError("Threads returned an invalid response.")
        error = payload.get("error")
        if response.status_code == 401 or (isinstance(error, dict) and error.get("code") == 190):
            raise ThreadsError("Threads token expired or revoked; reconnect your account.")
        if response.status_code == 429:
            raise ThreadsError("Threads rate limit reached. Retry later.")
        if not response.is_success or error:
            raise ThreadsError(f"Threads request failed (HTTP {response.status_code}). Check app permissions and reconnect.")
        return payload

    def exchange_code(self, code: str) -> TokenResponse:
        short = self._request("POST", "/oauth/access_token", data={
            "client_id": self.settings.threads_client_id,
            "client_secret": self.settings.threads_client_secret,
            "redirect_uri": self.settings.redirect_uri,
            "grant_type": "authorization_code", "code": code,
        })
        try:
            short_token = short["access_token"]
            if not isinstance(short_token, str) or not short_token:
                raise ValueError
            long = self._request("GET", "/access_token", params={
                "grant_type": "th_exchange_token", "client_secret": self.settings.threads_client_secret,
                "access_token": short_token,
            })
            if not isinstance(long["access_token"], str) or not long["access_token"]:
                raise ValueError
            expires = int(long["expires_in"])
            if expires <= 0:
                raise ValueError
            return TokenResponse(long["access_token"], expires)
        except (KeyError, ValueError, TypeError):
            raise ThreadsError("Threads returned an invalid token response; reconnect.") from None

    def _collection(self, path: str, token: str, limit: int) -> list[dict]:
        items = []
        after = None
        seen = set()
        for _ in range(3):
            params = {"fields": FIELDS, "limit": min(50, limit)}
            if after:
                params["after"] = after
            payload = self._request("GET", path, token, params=params)
            data = payload.get("data")
            if not isinstance(data, list) or any(not isinstance(i, dict) for i in data):
                raise ThreadsError("Threads returned an invalid response.")
            for item in data:
                if item.get("id") and item["id"] not in seen:
                    seen.add(item["id"])
                    items.append(item)
            if len(items) >= limit:
                return items[:limit]
            paging = payload.get("paging", {})
            if not isinstance(paging, dict):
                raise ThreadsError("Threads returned invalid pagination.")
            next_page = paging.get("next")
            if next_page is None or next_page == "":
                break
            cursors = paging.get("cursors", {})
            if not isinstance(next_page, str) or not isinstance(cursors, dict):
                raise ThreadsError("Threads returned invalid pagination.")
            # Never follow provider-supplied URLs with our bearer token.
            try:
                cursor = cursors.get("after") or parse_qs(urlsplit(next_page).query).get("after", [None])[0]
            except ValueError:
                raise ThreadsError("Threads returned invalid pagination.") from None
            if cursor is not None and not isinstance(cursor, str):
                raise ThreadsError("Threads returned invalid pagination.")
            if not cursor or cursor == after:
                break
            after = cursor
        return items

    def fetch_my_posts(self, access_token: str, limit: int = 50) -> list[dict]:
        return self._collection("/v1.0/me/threads", access_token, min(max(limit, 1), 150))

    def collect_research(self, access_token: str, *, top_posts: int = 5) -> dict:
        posts = self.fetch_my_posts(access_token)
        for post in posts:
            media_id = str(post["id"])
            if not media_id.isdecimal():
                raise ThreadsError("Threads returned an invalid media ID.")
            payload = self._request("GET", f"/v1.0/{media_id}/insights", access_token, params={"metric": ",".join(METRICS)})
            try:
                metrics = {m["name"]: int(m["values"][0]["value"]) for m in payload["data"]}
            except (KeyError, TypeError, ValueError, IndexError):
                raise ThreadsError("Threads returned invalid engagement metrics.") from None
            post["metrics"] = metrics
            post["engagement_score"] = sum(metrics.get(k, 0) for k in METRICS if k != "views")
            post["source_type"] = "post"
        selected = sorted(posts, key=lambda p: (p["engagement_score"], p["metrics"].get("views", 0)), reverse=True)[:top_posts]
        sources = []
        for post in selected:
            sources.append(post)
            for reply in self._collection(f"/v1.0/{post['id']}/replies", access_token, 50):
                sources.append({**reply, "source_type": "reply", "parent_id": post["id"]})
        return {
            "sources": sources, "posts": posts, "selected_posts_data": selected, "posts_sampled": len(posts), "selected_posts": len(selected),
            "limitations": "At most 50 recent owned posts (3 pages), top 5 by likes + replies + reposts + quotes; views break ties. Up to 50 visible direct replies per selected post (3 pages). This is a sample, not all-time virality. Other users' reply-level virality is not available. Missing metrics are not proof of zero engagement.",
        }
