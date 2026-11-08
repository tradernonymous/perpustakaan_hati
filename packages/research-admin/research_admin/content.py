"""Grounded content ideation; all generated output is a local draft for review."""

import json

import httpx

from .config import Settings
from .research import URL, ResearchError, _extract, _model

CONTENT_PROMPT = """You are an editorial assistant for Perpustakaan Hati, a Malaysian relationship-healing ebook brand. Create grounded content ideas from supplied, evidence-linked research insights. Do not state psychological diagnoses, promise outcomes, or invent audience quotes or statistics. Preserve an empathetic, non-judgmental voice in Bahasa Melayu or casual Malaysian English, matching the evidence. Return JSON only: {\"drafts\":[{\"kind\":\"threads_post\"|\"ebook_outline\"|\"design_brief\",\"title\":string,\"content\":object,\"source_ids\":[integer]}]}. Produce 1 short Threads post (include a gentle reflective question, no hashtags unless useful), 1 practical ebook chapter outline, and 1 visual/design brief. Every draft must cite one or more supplied insight IDs in source_ids. For ebook_outline, content should contain a short premise, intended reader need, and 3-5 chapter objects with title and one-sentence outcome. For threads_post, content has one post string. For design_brief, content has concept, format, visual_direction, and copy. Never output anything other than the requested JSON."""

ALLOWED_KINDS = {"threads_post", "ebook_outline", "design_brief"}


def _validate_drafts(payload: dict, insights: list[dict]) -> list[dict]:
    by_id = {int(item["id"]): item for item in insights}
    drafts = []
    for raw in payload.get("drafts", []):
        if not isinstance(raw, dict) or raw.get("kind") not in ALLOWED_KINDS:
            continue
        title = " ".join(str(raw.get("title", "")).split())[:160]
        content = raw.get("content")
        try:
            cited = sorted({int(value) for value in raw.get("source_ids", []) if int(value) in by_id})
        except (TypeError, ValueError):
            cited = []
        if not title or not isinstance(content, dict) or not cited:
            continue
        serialized = json.dumps(content, ensure_ascii=False)
        if len(serialized) > 12000:
            continue
        if raw["kind"] == "threads_post" and not str(content.get("post", "")).strip():
            continue
        if raw["kind"] == "ebook_outline" and not isinstance(content.get("chapters"), list):
            continue
        if raw["kind"] == "ebook_outline":
            chapters = [item for item in content["chapters"] if isinstance(item, dict) and str(item.get("title", "")).strip() and str(item.get("outcome", "")).strip()]
            if not 3 <= len(chapters) <= 5:
                continue
            content = {**content, "chapters": chapters}
        if raw["kind"] == "design_brief" and not str(content.get("concept", "")).strip():
            continue
        drafts.append({"kind": raw["kind"], "title": title, "content": content, "source_ids": cited})
    if {draft["kind"] for draft in drafts} != ALLOWED_KINDS:
        raise ResearchError("AI content drafts must include a Threads post, ebook outline, and design brief with selected-source citations. Retry with selected insights.")
    return drafts


def generate_drafts(insights: list[dict], settings: Settings, http: httpx.Client) -> list[dict]:
    if not insights:
        raise ResearchError("Select at least one saved insight before creating content drafts.")
    model = _model(settings)
    material = [{"id": int(item["id"]), "theme": item["theme"], "quote": item["quote"], "ebook_idea": item["ebook_idea"]} for item in insights]
    try:
        response = http.post(
            URL,
            headers={"Authorization": f"Bearer {settings.openrouter_api_key}"},
            json={"model": model, "messages": [{"role": "system", "content": CONTENT_PROMPT}, {"role": "user", "content": json.dumps(material, ensure_ascii=False)}],
                  "response_format": {"type": "json_object"}, "provider": {"max_price": {"prompt": 0, "completion": 0}}, "max_tokens": 2200},
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
        raise ResearchError("AI provider returned an unexpected content format; retry.") from None
    return _validate_drafts(_extract(content, list_key="drafts"), insights)
