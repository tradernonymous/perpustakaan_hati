"""Search demand mining, post outlier analytics, and source text sanitization."""

from datetime import UTC, datetime, timedelta
from statistics import median
from urllib.parse import urlencode

import httpx

AUTOCOMPLETE_URL = "https://suggestqueries.google.com/complete/search"
MY_TZ = timedelta(hours=8)
DEFAULT_SUFFIXES = ("", "apa", "kenapa", "cara", "bila", "untuk", "dalam islam", "macam mana")

ICP_KEYWORDS = {
    "hati",
    "tenang",
    "sembuh",
    "luka",
    "hubungan",
    "pasangan",
    "suami",
    "isteri",
    "jodoh",
    "rindu",
    "sedih",
    "sunyi",
    "overthinking",
    "penat",
    "move on",
    "boundaries",
    "communication",
    "self worth",
    "healing",
    "keluarga",
    "doa",
    "ikhlas",
    "redha",
}

RISK_KEYWORDS = {"diagnose", "medication", "prescription", "suicide", "self-harm", "disorder", "bipolar"}


def sanitize_source_text(text: str) -> tuple[bool, str, str]:
    """Validate and normalise post/reply text before AI analysis.

    Returns ``(ok, cleaned_text, refusal_reason)``.
    """
    cleaned = " ".join(str(text or "").split())
    if not cleaned:
        return False, "", "empty_text"
    if len(cleaned) < 8:
        return False, "", "too_short"
    lower = cleaned.casefold()
    if lower.count("http://") + lower.count("https://") >= 3 and len(cleaned) < 120:
        return False, "", "link_spam"
    tokens = [t for t in lower.split() if len(t) > 1]
    if len(tokens) >= 6 and len(set(tokens)) <= 2:
        return False, "", "repetitive_text"
    return True, cleaned[:2000], ""


def score_keyword_opportunity(suggestion: str, *, rank_index: int = 0) -> dict:
    """Compute a bounded risk-weighted OpportunityScore for a search suggestion."""
    clean = " ".join(str(suggestion or "").split())
    lower = clean.casefold()
    demand = round(max(0.35, 1.0 - (rank_index * 0.08)) + (0.15 if len(clean.split()) >= 3 else 0.0), 2)
    icp_hits = sum(1 for word in ICP_KEYWORDS if word in lower)
    icp = round(min(1.0, 0.35 + (icp_hits * 0.25)), 2)
    risk_hits = sum(1 for word in RISK_KEYWORDS if word in lower)
    risk = round(min(0.9, risk_hits * 0.45), 2)
    score = round(demand * icp * (1.0 - risk), 3)
    return {
        "query": clean,
        "demand": min(1.0, demand),
        "icp_fit": icp,
        "risk": risk,
        "opportunity_score": score,
    }


def expand_google_autocomplete(
    seed: str,
    http: httpx.Client,
    *,
    suffixes: tuple[str, ...] = DEFAULT_SUFFIXES,
    limit: int = 25,
) -> list[dict]:
    """Query Malaysia Google Autocomplete (`hl=ms&gl=my`) across local intent suffixes."""
    clean_seed = " ".join(str(seed or "").split())[:80]
    if not clean_seed:
        return []
    seen: set[str] = set()
    scored: list[dict] = []
    for suffix in suffixes[:8]:
        query = f"{clean_seed} {suffix}".strip()
        try:
            url = f"{AUTOCOMPLETE_URL}?{urlencode({'client': 'firefox', 'hl': 'ms', 'gl': 'my', 'q': query})}"
            response = http.get(url, timeout=8.0)
            if not response.is_success:
                continue
            payload = response.json()
            suggestions = payload[1] if isinstance(payload, list) and len(payload) > 1 and isinstance(payload[1], list) else []
        except (httpx.HTTPError, ValueError, TypeError):
            continue
        for idx, raw_item in enumerate(suggestions[:10]):
            item_text = " ".join(str(raw_item or "").split())
            key = item_text.casefold()
            if not item_text or key in seen:
                continue
            seen.add(key)
            scored.append(score_keyword_opportunity(item_text, rank_index=idx))
    scored.sort(key=lambda item: (-item["opportunity_score"], -item["icp_fit"], item["query"].casefold()))
    return scored[:max(1, int(limit))]


def _parse_iso_myt(timestamp: str) -> datetime | None:
    text = str(timestamp or "").strip()
    if not text:
        return None
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC) + MY_TZ
    except ValueError:
        return None


def score_posts(posts: list[dict]) -> dict:
    """Rank posts by weighted engagement rate, outlier multiple vs median, and MYT posting hour."""
    if not posts:
        return {"posts": [], "median_weighted": 0.0, "best_hours": []}
    enriched: list[dict] = []
    weighted_values: list[float] = []
    hour_buckets: dict[int, list[float]] = {}
    for post in posts:
        metrics = post.get("metrics") if isinstance(post.get("metrics"), dict) else {}
        views = max(0, int(metrics.get("views", 0) or 0))
        likes = max(0, int(metrics.get("likes", 0) or 0))
        replies = max(0, int(metrics.get("replies", 0) or 0))
        reposts = max(0, int(metrics.get("reposts", 0) or 0))
        quotes = max(0, int(metrics.get("quotes", 0) or 0))
        weighted = float(likes + (2 * replies) + (3 * (reposts + quotes)))
        weighted_rate = round((weighted / max(views, 1)) * 100.0, 2) if views > 0 else 0.0
        weighted_values.append(weighted)
        myt_dt = _parse_iso_myt(str(post.get("timestamp", "")))
        if myt_dt is not None:
            hour_buckets.setdefault(myt_dt.hour, []).append(weighted)
        enriched.append({
            **post,
            "weighted_score": int(weighted),
            "weighted_rate": weighted_rate,
            "myt_hour": myt_dt.hour if myt_dt is not None else None,
        })

    baseline = float(median(weighted_values)) if weighted_values else 0.0
    for item in enriched:
        denom = baseline if baseline > 0 else 1.0
        ratio = round(item["weighted_score"] / denom, 2)
        item["outlier_ratio"] = ratio
        item["is_outlier"] = ratio >= 2.0 and item["weighted_score"] > 0

    best_hours = sorted(
        (
            {"hour": hour, "label": f"{hour:02d}:00 MYT", "avg_score": round(sum(vals) / len(vals), 1), "posts": len(vals)}
            for hour, vals in hour_buckets.items()
        ),
        key=lambda h: (-h["avg_score"], h["hour"]),
    )
    enriched.sort(key=lambda p: (-p["weighted_score"], -p["weighted_rate"]))
    return {
        "posts": enriched,
        "median_weighted": round(baseline, 1),
        "best_hours": best_hours[:5],
    }
