"""Daylight Grove HTML Quote-Card / Carousel renderer, ebook-builder Markdown exporter, and Publish Pack."""

from datetime import UTC, datetime, timedelta
from html import escape

CARD_THEMES = {
    "quote-card": {
        "bg": "#FBF7F0",
        "card": "#F5EFE3",
        "ink": "#1C241E",
        "muted": "#5E685E",
        "accent": "#2F4B3B",
        "border": "#E3DAC8",
        "label": "Warm Parchment",
    },
    "quote-card-b": {
        "bg": "#182920",
        "card": "#21362B",
        "ink": "#F6F0E4",
        "muted": "#B8C7BA",
        "accent": "#8FC1A2",
        "border": "#335241",
        "label": "Forest Botanical",
    },
    "quote-card-c": {
        "bg": "#FDF5EE",
        "card": "#F7E6D7",
        "ink": "#2B1E18",
        "muted": "#7A5B4E",
        "accent": "#B96444",
        "border": "#E8C7B1",
        "label": "Dawn Terracotta",
    },
}


def _card_slides(draft: dict) -> list[dict]:
    kind = draft.get("kind", "threads_post")
    content = draft.get("content") if isinstance(draft.get("content"), dict) else {}
    title = str(draft.get("title") or "Perpustakaan Hati")
    if kind == "threads_post":
        text = str(content.get("post", "")).strip()
        parts = [p.strip() for p in text.split("\n\n") if p.strip()]
        if len(parts) >= 2:
            return [{"eyebrow": "Threads Reflection", "heading": title, "body": p} for p in parts[:4]]
        return [{"eyebrow": "Threads Reflection", "heading": title, "body": text or title}]
    if kind == "ebook_outline":
        slides = [
            {
                "eyebrow": "Ebook Cover Concept",
                "heading": title,
                "body": str(content.get("premise", "") or content.get("intended_reader_need", "")),
            }
        ]
        for idx, ch in enumerate(content.get("chapters", [])[:5], 1):
            if isinstance(ch, dict):
                slides.append({
                    "eyebrow": f"Chapter {idx}",
                    "heading": str(ch.get("title", f"Chapter {idx}")),
                    "body": str(ch.get("outcome", "")),
                })
        return slides
    return [
        {
            "eyebrow": str(content.get("format", "Quote Card")),
            "heading": title,
            "body": str(content.get("copy", "") or content.get("concept", "")),
            "note": str(content.get("visual_direction", "")),
        }
    ]


def render_quote_card_html(draft: dict, *, style: str = "quote-card", handle: str = "rahimam") -> str:
    """Render a self-contained Daylight Grove Quote Card or Carousel HTML document."""
    theme = CARD_THEMES.get(style, CARD_THEMES["quote-card"])
    clean_handle = str(handle or "rahimam").lstrip("@")
    slides = _card_slides(draft)
    total = len(slides)
    cards_markup = []
    for idx, slide in enumerate(slides, 1):
        note_html = f"<p class='direction'>{escape(slide['note'])}</p>" if slide.get("note") else ""
        pager = f"<span class='pager'>{idx}/{total}</span>" if total > 1 else ""
        cards_markup.append(
            "<article class='card'>"
            f"<header class='top'><span class='eyebrow'>{escape(slide.get('eyebrow', 'Quote Card'))}</span>{pager}</header>"
            f"<div class='body'><h1>{escape(slide.get('heading', ''))}</h1>"
            f"<p class='copy'>{escape(slide.get('body', ''))}</p>{note_html}</div>"
            f"<footer class='foot'><span class='brand'>Perpustakaan Hati</span>"
            f"<span class='ph-at'>@{escape(clean_handle)}</span></footer>"
            "</article>"
        )
    page_title = escape(str(draft.get("title") or "Quote Card"))
    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<title>{page_title} - Daylight Grove Card</title>"
        "<style>"
        f":root{{--bg:{theme['bg']};--card:{theme['card']};--ink:{theme['ink']};--muted:{theme['muted']};--accent:{theme['accent']};--border:{theme['border']};}}"
        "*{box-sizing:border-box}body{margin:0;padding:32px;background:var(--bg);color:var(--ink);"
        "font-family:'Inter',system-ui,-apple-system,sans-serif;display:flex;flex-direction:column;align-items:center;gap:24px}"
        ".deck{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,380px));gap:24px;width:100%;max-width:1240px;justify-content:center}"
        ".card{background:var(--card);border:1px solid var(--border);border-radius:20px;padding:28px;min-height:460px;"
        "display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 16px 38px rgba(28,36,30,.08)}"
        ".top,.foot{display:flex;justify-content:space-between;align-items:center;gap:12px}"
        ".eyebrow,.pager{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:600}"
        ".body{margin:24px 0}h1{font-family:'Fraunces',Georgia,serif;font-size:26px;line-height:1.25;margin:0 0 16px;font-weight:600}"
        ".copy{font-family:'Source Serif 4',Georgia,serif;font-size:18px;line-height:1.65;margin:0;white-space:pre-line}"
        ".direction{margin:16px 0 0;padding-top:12px;border-top:1px dashed var(--border);font-size:13px;color:var(--muted);line-height:1.5}"
        ".brand{font-family:'Fraunces',Georgia,serif;font-size:14px;color:var(--muted)}"
        ".ph-at{display:inline-flex;align-items:center;padding:4px 10px;border-radius:999px;font-size:13px;font-weight:700;"
        "background:linear-gradient(120deg,#f59e0b,#ef4444,#8b5cf6,#10b981);color:#fff;letter-spacing:.01em}"
        "@media print{body{padding:12px}.card{box-shadow:none;break-inside:avoid}}"
        "</style></head><body>"
        f"<section class='deck'>{''.join(cards_markup)}</section>"
        "</body></html>"
    )


def draft_to_ebook_markdown(draft: dict, insights: list[dict] | None = None, *, handle: str = "rahimam") -> str:
    """Format a draft in Markdown ready for `packages/ebook-builder` ingestion."""
    content = draft.get("content") if isinstance(draft.get("content"), dict) else {}
    title = str(draft.get("title") or "Untitled Draft").replace('"', "'")
    source_ids = ", ".join(str(i) for i in draft.get("source_ids", []))
    lines = [
        "---",
        f'title: "{title}"',
        f'kind: "{draft.get("kind", "threads_post")}"',
        f'author_handle: "@{str(handle or "rahimam").lstrip("@")}"',
        f'created_at: "{draft.get("created_at", "")}"',
        f"source_insight_ids: [{source_ids}]",
        "---",
        "",
        f"# {title}",
        "",
    ]
    kind = draft.get("kind")
    if kind == "ebook_outline":
        if content.get("premise"):
            lines.extend(["## Premise", "", str(content["premise"]).strip(), ""])
        if content.get("intended_reader_need"):
            lines.extend(["## Intended Reader Need", "", str(content["intended_reader_need"]).strip(), ""])
        for idx, ch in enumerate(content.get("chapters", []), 1):
            if isinstance(ch, dict):
                ch_title = str(ch.get("title", f"Chapter {idx}")).strip()
                ch_outcome = str(ch.get("outcome", "")).strip()
                lines.extend([f"## Chapter {idx}: {ch_title}", "", ch_outcome, ""])
    elif kind == "threads_post":
        lines.extend([str(content.get("post", "")).strip(), ""])
    else:
        for field_name in ("format", "concept", "visual_direction", "copy"):
            if content.get(field_name):
                lines.extend([f"## {field_name.replace('_', ' ').title()}", "", str(content[field_name]).strip(), ""])

    if insights:
        lines.extend(["## Grounded Reader Evidence", ""])
        for ins in insights:
            lines.append(f"- [{ins.get('theme', '')}] \"{ins.get('quote', '')}\" ({ins.get('source_url', '')})")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def build_publish_pack(drafts: list[dict], insights_by_id: dict[int, dict] | None = None, *, handle: str = "rahimam") -> tuple[str, str]:
    """Generate a combined Markdown Publish Pack and `.ics` calendar for scheduled or approved drafts."""
    md_sections: list[str] = [f"# Perpustakaan Hati Publish Pack (@{str(handle or 'rahimam').lstrip('@')})\n"]
    cal_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Perpustakaan Hati//Research Admin//EN",
        "CALSCALE:GREGORIAN",
    ]
    base_dt = datetime.now(UTC).replace(hour=13, minute=0, second=0, microsecond=0) + timedelta(days=1)
    for idx, draft in enumerate(drafts):
        cited = [insights_by_id[i] for i in draft.get("source_ids", []) if insights_by_id and i in insights_by_id]
        md_sections.append(draft_to_ebook_markdown(draft, cited, handle=handle))
        sched = str(draft.get("scheduled_at") or "").strip()
        event_dt = base_dt + timedelta(days=idx)
        if sched:
            try:
                parsed = datetime.fromisoformat(sched.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=UTC)
                event_dt = parsed.astimezone(UTC)
            except ValueError:
                pass
        stamp = event_dt.strftime("%Y%m%dT%H%M%SZ")
        summary = str(draft.get("title") or "Threads Draft").replace("\n", " ")[:120]
        cal_lines.extend([
            "BEGIN:VEVENT",
            f"UID:ph-draft-{draft.get('id', idx)}@perpustakaanhati",
            f"DTSTAMP:{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART:{stamp}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:Kind={draft.get('kind', '')} Status={draft.get('status', 'draft')}",
            "END:VEVENT",
        ])
    cal_lines.append("END:VCALENDAR")
    return "\n---\n\n".join(md_sections) + "\n", "\r\n".join(cal_lines) + "\r\n"
