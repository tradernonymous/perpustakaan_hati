"""Grounded content ideation; all generated output is a local draft for review."""

import json

import httpx

from .config import Settings
from .research import URL, ResearchError, _completion_payload, _extract, _http_failure, _model, _request_headers

CONTENT_PROMPT = """You are an editorial assistant for Perpustakaan Hati, a Malaysian relationship-healing ebook brand. Create grounded content ideas from supplied, evidence-linked research insights. Do not state psychological diagnoses, promise outcomes, or invent audience quotes or statistics. Preserve an empathetic, non-judgmental voice in Bahasa Melayu or casual Malaysian English, matching the evidence. Return JSON only: {\"drafts\":[{\"kind\":\"threads_post\"|\"ebook_outline\"|\"design_brief\",\"title\":string,\"content\":object,\"source_ids\":[integer]}]}. Produce 1 short Threads post (include a gentle reflective question, no hashtags unless useful), 1 practical ebook chapter outline, and 1 visual/design brief. Every draft must cite one or more supplied insight IDs in source_ids. For ebook_outline, content must be an object with a short premise, intended_reader_need, and 3-5 chapter objects with title and one-sentence outcome. For threads_post, content must be an object {"post": string}, never a bare string. For design_brief, content must be an object with concept, format, visual_direction, and copy. source_ids must always be a JSON array of integers. Never output anything other than the requested JSON."""

ALLOWED_KINDS = {"threads_post", "ebook_outline", "design_brief"}
DRAFT_KINDS = ("threads_post", "ebook_outline", "design_brief")
DRAFT_TONES = ("empathetic", "direct", "reflective", "practical")
DRAFT_LANGUAGES = ("match evidence", "Bahasa Melayu", "English")


def _normalise_content(kind: str, content):
    """Accept the shapes a model actually returns for `content`.

    Models routinely answer a Threads post as a bare string rather than the
    {"post": ...} object the prompt asks for; that is still a usable draft, so
    it is normalised instead of discarded as a missing kind.
    """
    if kind == "threads_post":
        if isinstance(content, str):
            content = {"post": content.strip()}
        if not isinstance(content, dict):
            return None
        if not str(content.get("post", "")).strip():
            for alternative in ("text", "body", "caption"):
                if str(content.get(alternative, "")).strip():
                    content = {**content, "post": str(content[alternative]).strip()}
                    break
    return content


def _draft_options(kinds, tone: str, language: str) -> tuple[tuple[str, ...], str, str]:
    chosen = tuple(kind for kind in DRAFT_KINDS if kind in (kinds or DRAFT_KINDS)) or DRAFT_KINDS
    chosen_tone = tone if tone in DRAFT_TONES else DRAFT_TONES[0]
    chosen_language = language if language in DRAFT_LANGUAGES else DRAFT_LANGUAGES[0]
    return chosen, chosen_tone, chosen_language


def _validate_drafts(payload: dict, insights: list[dict], required_kinds=None) -> list[dict]:
    required = set(required_kinds or ALLOWED_KINDS)
    by_id = {int(item["id"]): item for item in insights}
    drafts = []
    for raw in payload.get("drafts", []):
        if not isinstance(raw, dict) or raw.get("kind") not in required:
            continue
        title = " ".join(str(raw.get("title", "")).split())[:160]
        content = _normalise_content(raw["kind"], raw.get("content"))
        source_ids = raw.get("source_ids", [])
        if isinstance(source_ids, (int, str)):
            source_ids = [source_ids]
        try:
            cited = sorted({int(value) for value in source_ids if int(value) in by_id})
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
    if {draft["kind"] for draft in drafts} != required:
        raise ResearchError("AI content drafts did not include every selected kind with saved-source citations. Retry with selected insights.")
    return drafts


def _attach_references(drafts: list[dict], insights: list[dict]) -> list[dict]:
    """Add the original Threads permalink to every non-post draft.

    A copy of an outline or brief travels into a designer's app without this
    page, so the evidence link has to travel with the text. It is written here
    from saved insight rows, never from model output, and the Threads post
    draft itself is left without references by request.
    """
    by_id = {int(item["id"]): item for item in insights}
    for draft in drafts:
        content = draft["content"]
        content.pop("references", None)
        if draft["kind"] == "threads_post":
            continue
        references = []
        for insight_id in draft["source_ids"]:
            item = by_id.get(insight_id) or {}
            url = str(item.get("source_url", "")).strip()
            if not url.startswith(("https://", "http://")):
                continue
            references.append({"insight_id": insight_id, "theme": str(item.get("theme", "")).strip(), "url": url})
        if references:
            content["references"] = references
    return drafts


def generate_drafts(insights: list[dict], settings: Settings, http: httpx.Client, *, kinds=None, tone: str = "empathetic", language: str = "match evidence") -> list[dict]:  # noqa: PLR0913
    if not insights:
        raise ResearchError("Select at least one saved insight before creating content drafts.")
    chosen_kinds, chosen_tone, chosen_language = _draft_options(kinds, tone, language)
    model = _model(settings)
    material = [{"id": int(item["id"]), "theme": item["theme"], "quote": item["quote"], "ebook_idea": item["ebook_idea"]} for item in insights]
    prompt = CONTENT_PROMPT + (
        f" Generate only these draft kinds: {', '.join(chosen_kinds)}."
        f" Tone: {chosen_tone}. Language: {chosen_language}"
        + (" (match the dominant language of the supplied evidence)." if chosen_language == "match evidence" else ".")
    )
    payload = _completion_payload(model, prompt, json.dumps(material, ensure_ascii=False))
    try:
        response = http.post(
            URL,
            headers=_request_headers(settings),
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
        raise ResearchError("AI provider returned an unexpected content format; retry.") from None
    return _attach_references(_validate_drafts(_extract(content, list_key="drafts", finish_reason=str(choice.get("finish_reason") or "")), insights, required_kinds=chosen_kinds), insights)
