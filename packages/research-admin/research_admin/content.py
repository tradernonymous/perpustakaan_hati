"""Grounded content ideation, multi-variant Hook Lab, and safe reply drafting."""

import json

import httpx

from .ai_client import ResearchError, complete_json, strip_em_dashes, strip_em_dashes_deep
from .config import Settings

CONTENT_PROMPT = """You are an editorial assistant for Perpustakaan Hati, a Malaysian relationship-healing ebook brand. Create grounded content ideas from supplied, evidence-linked research insights. Do not state psychological diagnoses, promise outcomes, or invent audience quotes or statistics. Preserve an empathetic, non-judgmental voice in Bahasa Melayu or casual Malaysian English, matching the evidence. Return JSON only: {\"drafts\":[{\"kind\":\"threads_post\"|\"ebook_outline\"|\"design_brief\",\"title\":string,\"content\":object,\"source_ids\":[integer]}]}. Produce 1 short Threads post (include a gentle reflective question, no hashtags unless useful), 1 practical ebook chapter outline, and 1 visual/design brief. Every draft must cite one or more supplied insight IDs in source_ids. For ebook_outline, content must be an object with a short premise, intended_reader_need, and 3-5 chapter objects with title and one-sentence outcome. For threads_post, content must be an object {"post": string}, never a bare string. For design_brief, content must be an object with concept, format, visual_direction, and copy. source_ids must always be a JSON array of integers. Never output anything other than the requested JSON."""

ALLOWED_KINDS = {"threads_post", "ebook_outline", "design_brief"}
DRAFT_KINDS = ("threads_post", "ebook_outline", "design_brief")
DRAFT_TONES = ("empathetic", "direct", "reflective", "practical")
DRAFT_LANGUAGES = ("match evidence", "Bahasa Melayu", "English")
QUICK_MODIFIERS = {
    "shorter": "Shorten this Threads draft tightly below 280 characters while keeping the reflective hook.",
    "warmer": "Rewrite with a warmer, gentler conversational tone.",
    "bm": "Translate or adapt cleanly into natural conversational Bahasa Melayu without em dashes.",
    "en": "Rewrite in calm, warm casual Malaysian English without em dashes.",
    "question_hook": "Keep the body concise and end with a gentle reflective question for Threads replies.",
}
DISTRESS_TERMS = ("bunuh diri", "suicide", "self harm", "self-harm", "nak mati", "end my life")


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
        title = strip_em_dashes(" ".join(str(raw.get("title", "")).split())[:160])
        content = strip_em_dashes_deep(_normalise_content(raw["kind"], raw.get("content")))
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


def generate_drafts(  # noqa: PLR0913
    insights: list[dict],
    settings: Settings,
    http: httpx.Client,
    *,
    kinds=None,
    tone: str = "empathetic",
    language: str = "match evidence",
    options: dict | None = None,
) -> list[dict]:
    if not insights:
        raise ResearchError("Select at least one saved insight before creating content drafts.")
    opts = options or {}
    fact_sheet = str(opts.get("fact_sheet", ""))
    store = opts.get("store")
    chosen_kinds, chosen_tone, chosen_language = _draft_options(kinds, tone, language)
    material = [{"id": int(item["id"]), "theme": item["theme"], "quote": item["quote"], "ebook_idea": item["ebook_idea"]} for item in insights]
    prompt = CONTENT_PROMPT + (
        f" Generate only these draft kinds: {', '.join(chosen_kinds)}."
        f" Tone: {chosen_tone}. Language: {chosen_language}"
        + (" (match the dominant language of the supplied evidence)." if chosen_language == "match evidence" else ".")
    )
    if fact_sheet.strip():
        prompt += f"\nBrand Context Fact-Sheet:\n{fact_sheet.strip()[:1600]}"
    extracted, _ = complete_json(
        settings,
        http,
        (prompt, json.dumps(material, ensure_ascii=False)),
        {"list_key": "drafts", "operation": "content_drafts", "store": store},
    )
    return _attach_references(_validate_drafts(extracted, insights, required_kinds=chosen_kinds), insights)


def generate_variants(
    insights: list[dict],
    settings: Settings,
    http: httpx.Client,
    *,
    options: dict | None = None,
) -> dict:
    """Create 3 draft formats (short, story, carousel) and 4-Angle Hook Lab."""
    if not insights:
        raise ResearchError("Select at least one saved insight before generating variants.")
    opts = options or {}
    focus = str(opts.get("focus", ""))
    fact_sheet = str(opts.get("fact_sheet", ""))
    store = opts.get("store")
    material = [{"id": int(item["id"]), "theme": item["theme"], "quote": item["quote"], "ebook_idea": item["ebook_idea"]} for item in insights[:8]]
    prompt = (
        "You are an editorial strategist for Perpustakaan Hati. Create 4 Threads opening hooks (Contrarian, Storytelling, Relatable Pain, Question) "
        "and 3 post variants (short under 280 chars, story thread split into 2-3 paragraphs, and carousel 4-slide copy). "
        "Never use em dashes or clinical diagnoses. "
        'Return JSON: {"variants":[{"style":"short"|"story"|"carousel","title":string,"post":string,"angle":string}]}.'
    )
    if fact_sheet.strip():
        prompt += f"\nBrand Context:\n{fact_sheet.strip()[:1200]}"
    if focus:
        prompt += f"\nTopic focus: {focus[:200]}"
    extracted, _ = complete_json(
        settings,
        http,
        (prompt, json.dumps(material, ensure_ascii=False)),
        {"list_key": "variants", "operation": "content_variants", "store": store},
    )
    variants = []
    for item in extracted.get("variants", []):
        if not isinstance(item, dict) or not str(item.get("post", "")).strip():
            continue
        variants.append({
            "style": str(item.get("style", "short"))[:24],
            "title": strip_em_dashes(str(item.get("title", "Draft Variant"))[:120]),
            "post": strip_em_dashes(str(item.get("post", ""))[:2000]),
            "angle": strip_em_dashes(str(item.get("angle", "Relatable Pain"))[:40]),
        })
    return {"variants": variants}


def adjust_draft_variant(
    draft: dict,
    modifier: str,
    settings: Settings,
    http: httpx.Client,
    *,
    store=None,
) -> dict:
    """Apply a quick editorial modifier (shorter, warmer, bm, en, question_hook) to an existing draft."""
    instruction = QUICK_MODIFIERS.get(modifier, str(modifier or "Refine clarity cleanly without em dashes.")[:240])
    prompt = (
        "Revise the provided draft content carefully according to the editorial instruction. "
        "Keep core meaning grounded and avoid em dashes. "
        'Return JSON: {"drafts":[{"title":string,"content":object}]}.'
    )
    user_payload = json.dumps({"instruction": instruction, "kind": draft.get("kind"), "title": draft.get("title"), "content": draft.get("content")}, ensure_ascii=False)
    extracted, _ = complete_json(
        settings,
        http,
        (prompt, user_payload),
        {"list_key": "drafts", "operation": f"draft_adjust_{modifier}", "store": store},
    )
    items = extracted.get("drafts", [])
    if not items or not isinstance(items[0], dict):
        raise ResearchError("Could not adjust draft right now.")
    first = items[0]
    norm = _normalise_content(str(draft.get("kind", "threads_post")), first.get("content"))
    if not isinstance(norm, dict):
        raise ResearchError("Could not normalise adjusted draft.")
    return {
        "title": strip_em_dashes(str(first.get("title") or draft.get("title") or "Draft")[:160]),
        "content": strip_em_dashes_deep(norm),
    }


def draft_reply(
    reply_text: str,
    username: str,
    settings: Settings,
    http: httpx.Client,
    *,
    options: dict | None = None,
) -> str:
    """Draft a warm, non-clinical Threads reply with crisis-keyword safety guardrails."""
    opts = options or {}
    fact_sheet = str(opts.get("fact_sheet", ""))
    store = opts.get("store")
    clean_text = " ".join(str(reply_text or "").split())[:600]
    lower = clean_text.casefold()
    if any(term in lower for term in DISTRESS_TERMS):
        return (
            "Terima kasih kerana berkongsi. Anda tidak perlu lalui ini seorang diri. "
            "Jika hati terasa terlalu berat sekarang, sila hubungi Befrienders KL di 03-7627 2929 (24 jam) "
            "atau orang tersayang yang anda percayai."
        )
    prompt = (
        "Draft a brief, warm, empathetic reply from @rahimam (Perpustakaan Hati) under 320 characters. "
        "Acknowledge the reader's feeling without giving clinical diagnoses or using em dashes. "
        'Return JSON: {"replies":[{"text":string}]}.'
    )
    if fact_sheet.strip():
        prompt += f"\nVoice context:\n{fact_sheet.strip()[:800]}"
    extracted, _ = complete_json(
        settings,
        http,
        (prompt, json.dumps({"reader": username, "reply": clean_text}, ensure_ascii=False)),
        {"list_key": "replies", "operation": "inbox_draft_reply", "store": store},
    )
    rows = extracted.get("replies", [])
    if not rows or not isinstance(rows[0], dict) or not str(rows[0].get("text", "")).strip():
        raise ResearchError("Could not draft reply.")
    return strip_em_dashes(str(rows[0]["text"]).strip()[:480])
