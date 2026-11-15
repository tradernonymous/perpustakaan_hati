"""Multi-provider pain-point mining, grounded quotes, and keyword search research."""

import json

import httpx

from .ai_client import (
    FREE,
    HEADERS,
    MAX_TOKENS,
    OPENROUTER_URL,
    PAID_MODELS,
    ResearchError,
    build_openrouter_payload,
    complete_json,
    content_text,
    extract_json_object,
    is_free_model,
    openrouter_headers,
    openrouter_http_failure,
    parse_json_body,
    resolve_openrouter_model,
    strip_em_dashes,
)
from .config import Settings
from .discovery import sanitize_source_text

URL = OPENROUTER_URL
__all__ = [
    "FREE",
    "HEADERS",
    "MAX_TOKENS",
    "PAID_MODELS",
    "PAIN_POINT_PROMPT",
    "ResearchError",
    "URL",
    "mine_keyword_sources",
    "mine_pain_points",
]

PAIN_POINT_PROMPT = (
    "You are a qualitative research assistant for Perpustakaan Hati, a Malaysian relationship-healing ebook brand. "
    "The user messages contain Threads posts and public replies authored or received by one account. "
    "Identify recurring audience pain points about relationships, healing and self-worth. "
    "For each insight: theme (short label), quote (a SHORT VERBATIM EXCERPT copied exactly from the supplied material, max 30 words, used as evidence), "
    "source_url (the permalink field of the exact item the quote comes from), and ebook_idea (one sentence, how an ebook chapter could address it). "
    "Return only JSON: {\"insights\": [{\"theme\": str, \"quote\": str, \"source_url\": str, \"ebook_idea\": str}]}. "
    "Never invent quotes or permalinks. If there is insufficient material, return {\"insights\": []}."
)

_model = resolve_openrouter_model
_is_free = is_free_model
_completion_payload = build_openrouter_payload
_request_headers = openrouter_headers
_http_failure = openrouter_http_failure
_content_text = content_text
_json_body = parse_json_body
_extract = extract_json_object


def _parse_sources(sources: list[dict]) -> list[dict]:
    material = []
    for item in sources:
        ok, cleaned_text, _ = sanitize_source_text(str(item.get("text") or ""))
        raw_text = str(item.get("text") or "").strip()
        text = raw_text if raw_text else cleaned_text
        if not ok and len(raw_text) >= 1:
            # Keep short direct replies if permalink exists so backward-compat short test strings still work.
            text = raw_text
        permalink = str(item.get("permalink") or "").strip()
        if text and permalink:
            material.append({"text": text, "permalink": permalink})
    if not material:
        raise ResearchError("No linked post or reply text available to analyse; nothing was sent to the AI provider.")
    return material


def _validate(insight: dict, material: list[dict], seen_quotes: set[str], *, source_type: str = "") -> dict | None:
    if not isinstance(insight, dict):
        return None
    quote = " ".join(str(insight.get("quote", "")).split())
    theme = strip_em_dashes(str(insight.get("theme", "")).strip())
    source_url = str(insight.get("source_url", "")).strip()
    ebook_idea = strip_em_dashes(str(insight.get("ebook_idea", "")).strip())
    if not (theme and quote and source_url and ebook_idea):
        return None
    normalized_quote = quote.lower()
    if normalized_quote in seen_quotes:
        return None
    if not any(item["permalink"] == source_url and normalized_quote in item["text"].lower() for item in material):
        return None
    seen_quotes.add(normalized_quote)
    row = {"theme": theme, "quote": quote, "source_url": source_url, "ebook_idea": ebook_idea}
    if source_type:
        row["source_type"] = source_type
    return row


def _focus_instruction(focus: str) -> str:
    """Bounded, whitespace-normalised user focus for the next run."""
    return " ".join(str(focus or "").split())[:500]


def mine_pain_points(
    sources: list[dict],
    settings: Settings,
    http: httpx.Client,
    *,
    focus: str = "",
    options: dict | None = None,
) -> list[dict]:
    if not sources:
        return []
    opts = options or {}
    fact_sheet = str(opts.get("fact_sheet", ""))
    store = opts.get("store")
    material = _parse_sources(sources)
    prompt = PAIN_POINT_PROMPT
    if fact_sheet.strip():
        prompt += f"\nBrand Context Fact-Sheet:\n{fact_sheet.strip()[:1600]}"
    if _focus_instruction(focus):
        prompt += f"\nFocus for this run: {_focus_instruction(focus)}"
    extracted, _ = complete_json(
        settings,
        http,
        (prompt, json.dumps(material, ensure_ascii=False)),
        {"list_key": "insights", "operation": "research_mine", "store": store},
    )
    seen_quotes: set[str] = set()
    validated = [v for v in (_validate(i, material, seen_quotes) for i in extracted["insights"]) if v]
    if extracted["insights"] and not validated:
        raise ResearchError("AI analysis failed evidence checks; quotes must be verbatim excerpts from the sampled posts. Retry the research run.")
    return validated


def mine_keyword_sources(
    query: str,
    sources: list[dict],
    settings: Settings,
    http: httpx.Client,
    options: dict | None = None,
) -> list[dict]:
    """Mine pain-point insights from Threads `/keyword_search` results."""
    if not sources:
        return []
    opts = options or {}
    store = opts.get("store")
    material = _parse_sources(sources)
    prompt = PAIN_POINT_PROMPT + f"\nKeyword Search Query: {query[:100]}"
    extracted, _ = complete_json(
        settings,
        http,
        (prompt, json.dumps(material, ensure_ascii=False)),
        {"list_key": "insights", "operation": "keyword_mine", "store": store},
    )
    seen_quotes: set[str] = set()
    return [v for v in (_validate(i, material, seen_quotes, source_type="keyword_search") for i in extracted["insights"]) if v]
