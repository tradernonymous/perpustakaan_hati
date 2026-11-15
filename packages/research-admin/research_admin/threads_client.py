"""Read-only Threads OAuth and bounded research collection."""

from dataclasses import dataclass, field
from urllib.parse import parse_qs, urlencode, urlsplit

import httpx

from .config import Settings

GRAPH = "https://graph.threads.com"
FIELDS = "id,text,username,permalink,timestamp"
PROFILE_FIELDS = "id,username,name,threads_profile_picture_url,threads_biography"
METRICS = ("views", "likes", "replies", "reposts", "quotes")
USER_METRICS = ("followers_count", "views", "likes", "replies", "reposts", "quotes")
DEMOGRAPHIC_BREAKDOWNS = ("country", "city", "age", "gender")
READ_SCOPES = "threads_basic,threads_read_replies,threads_manage_insights"
PUBLISH_SCOPES = "threads_basic,threads_read_replies,threads_manage_insights,threads_content_publish"
# Hard ceilings, independent of what the form asks for. Three pages of 50 is
# the most the collection helper will ever walk.
POST_LIMIT_MAX = 150
TOP_POSTS_MAX = 25
REPLIES_PER_POST_MAX = 100
POST_TEXT_MAX = 500


class ThreadsError(RuntimeError):
    """Sanitized provider failure."""


@dataclass
class TokenResponse:
    access_token: str = field(repr=False)
    expires_in: int


def _int(value, default: int) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True, slots=True)
class SampleLimits:
    """Sample sizes for one run, bounded in one place."""

    post_limit: int = 50
    top_posts: int = 5
    replies_per_post: int = 50

    def normalized(self) -> "SampleLimits":
        posts = min(max(_int(self.post_limit, 50), 1), POST_LIMIT_MAX)
        return SampleLimits(
            post_limit=posts,
            top_posts=min(max(_int(self.top_posts, 5), 1), TOP_POSTS_MAX, posts),
            replies_per_post=min(max(_int(self.replies_per_post, 50), 1), REPLIES_PER_POST_MAX),
        )

    @classmethod
    def from_form(cls, data) -> "SampleLimits":
        return cls(data.get("post_limit", 50), data.get("top_posts", 5), data.get("replies_per_post", 50)).normalized()

    @classmethod
    def from_row(cls, row: dict | None) -> "SampleLimits":
        if not row:
            return cls()
        return cls(row.get("post_limit", 50), row.get("top_posts", 5), row.get("replies_per_post", 50)).normalized()

    def as_dict(self) -> dict[str, int]:
        return {"post_limit": self.post_limit, "top_posts": self.top_posts, "replies_per_post": self.replies_per_post}

    def describe(self) -> str:
        return (
            f"At most {self.post_limit} recent owned posts (up to 3 pages of 50), top {self.top_posts} by likes + replies + reposts + quotes; "
            f"views break ties. Up to {self.replies_per_post} visible direct replies per selected post. This is a sample, not all-time virality. "
            "Other users' reply-level virality is not available. Missing metrics are not proof of zero engagement."
        )


class ThreadsClient:
    def __init__(self, settings: Settings, http: httpx.Client):
        self.settings = settings
        self.http = http

    def authorize_url(self, state: str, *, include_publish: bool = False) -> str:
        return "https://threads.com/oauth/authorize?" + urlencode({
            "client_id": self.settings.threads_client_id,
            "redirect_uri": self.settings.redirect_uri,
            "scope": PUBLISH_SCOPES if include_publish else READ_SCOPES,
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

    def refresh_token(self, access_token: str) -> TokenResponse:
        payload = self._request("GET", "/refresh_access_token", params={
            "grant_type": "th_refresh_token",
            "access_token": access_token,
        })
        try:
            refreshed = payload["access_token"]
            if not isinstance(refreshed, str) or not refreshed:
                raise ValueError
            expires = int(payload.get("expires_in", 5184000))
            if expires <= 0:
                raise ValueError
            return TokenResponse(refreshed, expires)
        except (KeyError, ValueError, TypeError):
            raise ThreadsError("Threads returned an invalid token refresh response; reconnect.") from None

    def fetch_profile(self, access_token: str) -> dict:
        payload = self._request("GET", "/v1.0/me", access_token, params={"fields": PROFILE_FIELDS})
        return {
            "id": str(payload.get("id", "")).strip()[:80],
            "username": str(payload.get("username", "")).strip().lstrip("@")[:60],
            "name": str(payload.get("name", "")).strip()[:120],
            "biography": str(payload.get("threads_biography", "")).strip()[:500],
            "profile_picture_url": str(payload.get("threads_profile_picture_url", "")).strip()[:500],
        }

    @staticmethod
    def _extract_metric_value(item: dict) -> int:
        total = item.get("total_value")
        if isinstance(total, dict) and str(total.get("value", "")).lstrip("-").isdigit():
            return max(0, int(total["value"]))
        values = item.get("values")
        if isinstance(values, list):
            return max(0, sum(
                int(entry["value"])
                for entry in values
                if isinstance(entry, dict) and str(entry.get("value", "")).lstrip("-").isdigit()
            ))
        return 0

    @staticmethod
    def _extract_breakdown(payload: dict) -> list[dict]:
        data = payload.get("data")
        if not isinstance(data, list):
            return []
        rows: list[dict] = []
        for item in data:
            if not isinstance(item, dict) or item.get("name") != "follower_demographics":
                continue
            total = item.get("total_value")
            if not isinstance(total, dict):
                continue
            for group in total.get("breakdowns", []):
                if not isinstance(group, dict):
                    continue
                for res in group.get("results", []):
                    if not isinstance(res, dict):
                        continue
                    dims = res.get("dimension_values")
                    key = str(dims[0]).strip()[:80] if isinstance(dims, list) and dims else ""
                    val = res.get("value", 0)
                    if key and str(val).lstrip("-").isdigit() and int(val) > 0:
                        rows.append({"key": key, "value": int(val)})
        rows.sort(key=lambda r: (-r["value"], r["key"]))
        return rows[:25]

    def fetch_user_insights(self, access_token: str, *, include_demographics: bool = True) -> dict:
        payload = self._request("GET", "/v1.0/me/threads_insights", access_token, params={"metric": ",".join(USER_METRICS)})
        data = payload.get("data")
        if not isinstance(data, list):
            raise ThreadsError("Threads returned invalid user insights.")
        followers_count = 0
        metrics = {key: 0 for key in METRICS}
        for item in data:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", ""))
            val = self._extract_metric_value(item)
            if name == "followers_count":
                followers_count = val
            elif name in metrics:
                metrics[name] = val
        demographics: dict[str, list[dict]] = {}
        if include_demographics:
            for breakdown in DEMOGRAPHIC_BREAKDOWNS:
                try:
                    demo_payload = self._request(
                        "GET", "/v1.0/me/threads_insights", access_token,
                        params={"metric": "follower_demographics", "breakdown": breakdown},
                    )
                except ThreadsError as exc:
                    msg = str(exc).lower()
                    if "expired" in msg or "revoked" in msg or "rate limit" in msg:
                        raise
                    continue
                rows = self._extract_breakdown(demo_payload)
                if rows:
                    demographics[breakdown] = rows
        return {"followers_count": followers_count, "metrics": metrics, "demographics": demographics}

    def sync_graph_audience(self, access_token: str, *, post_limit: int = 25, replies_per_post: int = 50) -> dict:
        profile = self.fetch_profile(access_token)
        insights = self.fetch_user_insights(access_token, include_demographics=True)
        posts = self.fetch_my_posts(access_token, min(max(int(post_limit), 1), 50))
        replies = []
        for post in posts[:10]:
            media_id = str(post.get("id", ""))
            if not media_id.isdecimal():
                continue
            for reply in self._collection(f"/v1.0/{media_id}/replies", access_token, min(max(int(replies_per_post), 1), 100)):
                replies.append({**reply, "source_type": "reply", "parent_id": media_id, "parent_permalink": post.get("permalink", "")})
        return {
            "profile": profile,
            "followers_count": insights["followers_count"],
            "metrics": insights["metrics"],
            "demographics": insights["demographics"],
            "posts_sampled": len(posts),
            "replies": replies,
        }

    def publish_post(self, access_token: str, text: str, *, reply_to_id: str = "") -> dict:
        clean_text = str(text or "").strip()
        if not clean_text:
            raise ThreadsError("Post text cannot be empty.")
        if len(clean_text) > POST_TEXT_MAX:
            raise ThreadsError(f"Threads posts are limited to {POST_TEXT_MAX} characters (got {len(clean_text)}).")
        form = {"media_type": "TEXT", "text": clean_text}
        if str(reply_to_id or "").strip():
            form["reply_to_id"] = str(reply_to_id).strip()
        container = self._request("POST", "/v1.0/me/threads", access_token, data=form)
        creation_id = str(container.get("id", "")).strip()
        if not creation_id:
            raise ThreadsError("Threads did not return a media container ID.")
        published = self._request("POST", "/v1.0/me/threads_publish", access_token, data={"creation_id": creation_id})
        media_id = str(published.get("id", "")).strip()
        if not media_id:
            raise ThreadsError("Threads did not return a published post ID.")
        permalink = ""
        try:
            meta = self._request("GET", f"/v1.0/{media_id}", access_token, params={"fields": "id,permalink"})
            permalink = str(meta.get("permalink", "")).strip()
        except ThreadsError:
            permalink = ""
        return {"id": media_id, "permalink": permalink}

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

    def collect_research(self, access_token: str, *, post_limit: int = 50, top_posts: int = 5, replies_per_post: int = 50) -> dict:
        limits = SampleLimits(post_limit, top_posts, replies_per_post).normalized()
        posts = self.fetch_my_posts(access_token, limits.post_limit)
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
        selected = sorted(posts, key=lambda p: (p["engagement_score"], p["metrics"].get("views", 0)), reverse=True)[:limits.top_posts]
        sources = []
        for post in selected:
            sources.append(post)
            for reply in self._collection(f"/v1.0/{post['id']}/replies", access_token, limits.replies_per_post):
                sources.append({**reply, "source_type": "reply", "parent_id": post["id"]})
        return {
            "sources": sources, "posts": posts, "selected_posts_data": selected, "posts_sampled": len(posts),
            "selected_posts": len(selected), "limits": limits.as_dict(), "limitations": limits.describe(),
        }
