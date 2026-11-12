"""OpenRouter-powered pain-point mining, restricted to free models and grounded quotes."""

import json
import re

import httpx

from .config import Settings

URL = "https://openrouter.ai/api/v1/chat/completions"
FREE = re.compile(r"^(openrouter/free|[a-z0-9./_-]+:free)$", re.IGNORECASE)
# Paid models are opt-in by name so a typo cannot quietly run up a bill.
# Qwen3.7 Flash is cheap and does not spend the answer budget on reasoning.
PAID_MODELS = {"qwen/qwen3.7-flash"}
MAX_TOKENS = 4000

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
    if model not in PAID_MODELS and not FREE.search(model):
        raise ResearchError(f"Model '{model}' is not allowlisted. Use a free model, or add it to PAID_MODELS if it is worth paying for.")
    return model


def _is_free(model: str) -> bool:
    return bool(FREE.search(model))


def _completion_payload(model: str, system: str, user: str, *, max_tokens: int = MAX_TOKENS) -> dict:
    """One request shape for both research and drafts.

    Paid models reject the zero-price provider cap with a 404 "no endpoints"
    error, so that cap is only sent for free models. Reasoning stays off so a
    thinking model cannot spend the whole budget before answering JSON.
    """
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "response_format": {"type": "json_object"},
        "reasoning": {"enabled": False},
        "max_tokens": max_tokens,
    }
    if _is_free(model):
        payload["provider"] = {"max_price": {"prompt": 0, "completion": 0}}
    return payload


def _http_failure(status_code: int) -> "ResearchError":
    if status_code == 429:
        return ResearchError("OpenRouter rate limit reached; retry later.")
    if status_code == 404:
        return ResearchError(
            "OpenRouter found no endpoint for the configured model (HTTP 404). "
            "Check OPENROUTER_MODEL, and that a provider still serves it, then retry."
        )
    return ResearchError(f"OpenRouter error (HTTP {status_code}); check the API key and retry.")


def _parse_sources(sources: list[dict]) -> list[dict]:
    material = []
    for item in sources:
        text = str(item.get("text") or "").strip()
        permalink = str(item.get("permalink") or "").strip()
        if text and permalink:
            material.append({"text": text, "permalink": permalink})
    if not material:
        raise ResearchError("No linked post or reply text available to analyse; nothing was sent to the AI provider.")
    return material


def _content_text(content) -> str:
    """Provider text, which some backends send as a list of parts."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [part["text"] for part in content if isinstance(part, dict) and isinstance(part.get("text"), str)]
        return "".join(parts)
    return ""


def _json_body(text: str):
    fenced = re.search(r"```(?:json)?\s*(.+?)```", text, re.DOTALL)
    whole = fenced.group(1).strip() if fenced else text.strip()
    embedded = re.search(r"\{.*\}", text, re.DOTALL)
    for candidate in (whole, embedded.group(0) if embedded else ""):
        if not candidate:
            continue
        try:
            return json.loads(candidate)
        except ValueError:
            continue
    raise ResearchError("AI provider returned malformed JSON; retry the research run.")


def _extract(content, *, list_key: str = "insights", finish_reason: str = "") -> dict:
    text = _content_text(content)
    if not text.strip():
        if finish_reason == "length":
            raise ResearchError(
                "The AI provider spent its whole output budget before answering, which is what a reasoning model does with no room left for JSON. "
                "Retry, or set OPENROUTER_MODEL to a model that answers directly."
            )
        raise ResearchError("AI provider returned an unexpected analysis format; retry the research run.")
    payload = _json_body(text)
    if isinstance(payload, list):
        if not payload:
            raise ResearchError("AI provider returned an unexpected analysis format; retry the research run.")
        payload = {list_key: payload}
    if not isinstance(payload, dict) or not isinstance(payload.get(list_key), list):
        raise ResearchError("AI provider returned an unexpected analysis format; retry the research run.")
    return payload


def _validate(insight: dict, material: list[dict], seen_quotes: set[str]) -> dict | None:
    if not isinstance(insight, dict):
        return None
    quote = " ".join(str(insight.get("quote", "")).split())
    theme = str(insight.get("theme", "")).strip()
    source_url = str(insight.get("source_url", "")).strip()
    ebook_idea = str(insight.get("ebook_idea", "")).strip()
    if not (theme and quote and source_url and ebook_idea):
        return None
    normalized_quote = quote.lower()
    if normalized_quote in seen_quotes:
        return None
    if not any(item["permalink"] == source_url and normalized_quote in item["text"].lower() for item in material):
        return None
    seen_quotes.add(normalized_quote)
    return {"theme": theme, "quote": quote, "source_url": source_url, "ebook_idea": ebook_idea}


def mine_pain_points(sources: list[dict], settings: Settings, http: httpx.Client) -> list[dict]:
    if not sources:
        return []
    model = _model(settings)
    material = _parse_sources(sources)
    payload = _completion_payload(model, PAIN_POINT_PROMPT, json.dumps(material, ensure_ascii=False))
    try:
        response = http.post(
            URL,
            headers={"Authorization": f"Bearer {settings.openrouter_api_key}"},
            json=payload,
        )
    except httpx.HTTPError:
        raise ResearchError("Could not reach OpenRouter; check your connection and retry.") from None
    if not response.is_success:
        raise _http_failure(response.status_code)
    try:
        choice = response.json()["choices"][0]
        content = choice["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError):
        raise ResearchError("AI provider returned an unexpected analysis format; retry the research run.") from None
    extracted = _extract(content, finish_reason=str(choice.get("finish_reason") or ""))
    seen_quotes: set[str] = set()
    validated = [v for v in (_validate(i, material, seen_quotes) for i in extracted["insights"]) if v]
    if extracted["insights"] and not validated:
        raise ResearchError("AI analysis failed evidence checks; quotes must be verbatim excerpts from the sampled posts. Retry the research run.")
    return validated
