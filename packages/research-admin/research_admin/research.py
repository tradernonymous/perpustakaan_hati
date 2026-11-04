"""OpenRouter-powered pain-point mining, restricted to free models and grounded quotes."""

import json
import re

import httpx

from .config import Settings

URL = "https://openrouter.ai/api/v1/chat/completions"
FREE = re.compile(r"^(openrouter/free|[a-z0-9./_-]+:free)$", re.IGNORECASE)

PAIN_POINT_PROMPT = (
    "You are a qualitative research assistant for Perpustakaan Hati, a Malaysian relationship-healing ebook brand. "
    "The user messages contain Threads posts and public replies authored or received by one account. "
    "Identify recurring audience pain points about relationships, healing and self-worth. "
    "For each insight: theme (short label), quote (a SHORT VERBATIM EXCERPT copied exactly from the supplied material, max 30 words, used as evidence), "
    "source_url (the permalink field of the exact item the quote comes from), and ebook_idea (one sentence, how an ebook chapter could address it). "
    "Return only JSON: {\"insights\": [{\"theme\": str, \"quote\": str, \"source_url\": str, \"ebook_idea\": str}]}. "
    "Never invent quotes or permalinks. If there is insufficient material, return {\"insights\": []}."
)


class ResearchError(RuntimeError):
    """Sanitized provider or validation failure."""


def _model(settings: Settings) -> str:
    if not settings.openrouter_api_key:
        raise ResearchError("OPENROUTER_API_KEY is not set. Add it to the environment and retry.")
    model = settings.openrouter_model
    if not FREE.search(model):
        raise ResearchError(f"Model '{model}' is not a free OpenRouter model. Use a :free model; paid models are not allowed.")
    return model


def _parse_sources(sources: list[dict]) -> tuple[list[str], set[str]]:
    texts, permalinks = [], set()
    for item in sources:
        text = str(item.get("text") or "").strip()
        permalink = str(item.get("permalink") or "").strip()
        if text:
            texts.append(text)
        if permalink:
            permalinks.add(permalink)
    if not texts:
        raise ResearchError("No post or reply text available to analyse; nothing was sent to the AI provider.")
    return texts, permalinks


def _extract(content: str) -> dict:
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if not match:
        raise ResearchError("AI provider returned malformed JSON; retry the research run.")
    try:
        payload = json.loads(match.group(0))
    except ValueError:
        raise ResearchError("AI provider returned malformed JSON; retry the research run.") from None
    if not isinstance(payload, dict) or not isinstance(payload.get("insights"), list):
        raise ResearchError("AI provider returned an unexpected analysis format; retry the research run.")
    return payload


def _validate(insight: dict, texts: list[str], permalinks: set[str], seen_quotes: set[str]) -> dict | None:
    if not isinstance(insight, dict):
        return None
    quote = " ".join(str(insight.get("quote", "")).split())
    theme = str(insight.get("theme", "")).strip()
    source_url = str(insight.get("source_url", "")).strip()
    ebook_idea = str(insight.get("ebook_idea", "")).strip()
    if not (theme and quote and source_url and ebook_idea):
        return None
    if source_url not in permalinks:
        return None
    normalized_quote = quote.lower()
    if normalized_quote in seen_quotes:
        return None
    if not any(normalized_quote in text.lower() for text in texts):
        return None
    seen_quotes.add(normalized_quote)
    return {"theme": theme, "quote": quote, "source_url": source_url, "ebook_idea": ebook_idea}


def mine_pain_points(sources: list[dict], settings: Settings, http: httpx.Client) -> list[dict]:
    if not sources:
        return []
    model = _model(settings)
    texts, permalinks = _parse_sources(sources)
    material = [{"text": str(i.get("text") or "").strip(), "permalink": str(i.get("permalink") or "").strip()}
                for i in sources]
    material = [m for m in material if m["text"] and m["permalink"]]
    try:
        response = http.post(
            URL,
            headers={"Authorization": f"Bearer {settings.openrouter_api_key}"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": PAIN_POINT_PROMPT},
                    {"role": "user", "content": json.dumps(material, ensure_ascii=False)},
                ],
                "response_format": {"type": "json_object"},
                "provider": {"max_price": {"prompt": 0, "completion": 0}},
                "max_tokens": 2000,
            },
        )
    except httpx.HTTPError:
        raise ResearchError("Could not reach OpenRouter; check your connection and retry.") from None
    if response.status_code == 429:
        raise ResearchError("OpenRouter free tier rate limit reached; retry later.")
    if not response.is_success:
        raise ResearchError(f"OpenRouter error (HTTP {response.status_code}); check the API key and retry.")
    try:
        content = response.json()["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError):
        raise ResearchError("AI provider returned an unexpected analysis format; retry the research run.") from None
    payload = _extract(content)
    seen_quotes: set[str] = set()
    validated = [v for v in (_validate(i, texts, permalinks, seen_quotes) for i in payload["insights"]) if v]
    if payload["insights"] and not validated:
        raise ResearchError("AI analysis failed evidence checks; quotes must be verbatim excerpts from the sampled posts. Retry the research run.")
    return validated
