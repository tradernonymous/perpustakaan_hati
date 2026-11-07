"""Lay a manuscript out as the branded interior HTML.

The CSS lives in ``templates/ebook-interior.html`` — the brand's master
interior template — so the builder never re-implements the design system.
This module only decides *which* layout each block gets and fills it in.

Layout rules come from docs/brand/ui-kit.md -> "Master layouts".

Pagination is CSS's job, not this module's: the brand template gives every
``.page`` a ``page-break-after``, and the watermark lives in ``@page`` margin
boxes so it repeats on every printed page. This module groups consecutive
body blocks into a single flowing section so a chapter's prose does not
break one paragraph per page.
"""

from __future__ import annotations

import re
from pathlib import Path

from .manuscript import Block, BlockKind, Manuscript
from .watermark import Buyer, Watermark, build_watermark_css, watermark_label

TEMPLATES = Path(__file__).resolve().parents[1] / "templates"
INTERIOR_TEMPLATE = TEMPLATES / "ebook-interior.html"

TIER_CLASSES = {
    "poket": "tier-free",
    "membangun": "tier-standard",
    "teman-hidup": "tier-premium",
}

# Roman numerals for chapter numbers, 1..12 is plenty for these books.
ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]


def _escape(text: str) -> str:
    return (
        str(text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _style_block() -> str:
    """The template's CSS, minus the demo body it ships with."""
    raw = INTERIOR_TEMPLATE.read_text(encoding="utf-8")
    match = re.search(r"<style>(.*?)</style>", raw, re.DOTALL)
    return match.group(1).strip() if match else ""


def _fonts_css() -> str:
    """The brand font faces, with paths rewritten to absolute file URLs.

    WeasyPrint resolves relative URLs against the HTML's base URL, and the
    builder renders from a temp directory, so the fonts must be absolute.
    """
    fonts = Path(__file__).resolve().parents[1].parent / "brand-tools" / "fonts"
    faces = []
    for family, filename, style in (
        ("Fraunces", "FrauncesDisplay.woff2", "normal"),
        ("Fraunces", "FrauncesDisplayItalic.woff2", "italic"),
        ("Source Serif 4", "SourceSerifText.woff2", "normal"),
        ("Inter", "InterUI.woff2", "normal"),
    ):
        url = (fonts / filename).as_uri()
        faces.append(
            "@font-face {\n"
            f"  font-family: '{family}';\n"
            f"  src: url('{url}') format('woff2');\n"
            "  font-weight: 400 700;\n"
            f"  font-style: {style};\n"
            "  font-display: swap;\n"
            "}"
        )
    return "\n".join(faces)


def _cover(manuscript: Manuscript) -> str:
    tier = manuscript.tier or "poket"
    tier_class = TIER_CLASSES.get(tier, TIER_CLASSES["poket"])
    title = _escape(manuscript.title or "Edisi Poket")
    subtitle = _escape(manuscript.subtitle)
    return f"""
<section class="page layout-cover {tier_class}">
  <div class="wordmark">Perpustakaan Hati</div>
  <div class="tier-bar"></div>
  <h1>{title}</h1>
  <div class="byline">— by @rahimam —</div>
  <p class="tagline">{subtitle}</p>
</section>
"""


def _title_page(manuscript: Manuscript) -> str:
    tagline = _escape(manuscript.tagline)
    return f"""
<section class="page layout-title-page">
  <div class="wordmark">Perpustakaan Hati</div>
  <p class="tagline">{tagline}</p>
  <div class="folio">i</div>
</section>
"""


def _chapter_opener(number: int, title: str) -> str:
    numeral = ROMAN[number] if number < len(ROMAN) else str(number)
    return f"""
<section class="page layout-chapter-opener">
  <div class="numeral">{numeral}</div>
  <h2>{_escape(title)}</h2>
  <div class="rule"></div>
</section>
"""


def _body(parts: list[str]) -> str:
    return f"""
<section class="page layout-body">
  {chr(10).join('  ' + part for part in parts)}
</section>
"""


def _pull_quote(text: str) -> str:
    return f"""
<section class="page layout-pull-quote">
  <div class="rule"></div>
  <p class="quote">"{_escape(text)}"</p>
  <div class="rule"></div>
</section>
"""


def _worksheet(title: str, content: str = "") -> str:
    lines = '<div class="checkbox-column"></div><div class="write-line"></div>' * 4
    return f"""
<section class="page layout-worksheet">
  <h3>{_escape(title)}</h3>
  {content}
  {lines}
</section>
"""


def _reflection_card(text: str) -> str:
    return f"""
<section class="page layout-reflection-card-page">
  <div class="layout-reflection-card">
    <div class="healing-marker"></div>
    <p class="card-quote">"{_escape(text)}"</p>
    <p class="card-prompt">KAD REFLEKSI · HATI</p>
  </div>
</section>
"""


def _script_row(block: Block) -> str:
    column = block.meta.get("column", "other")
    return f"""
<section class="page layout-script-page">
  <div class="script-row {column}">
    <div class="col-head">{_escape(block.title)}</div>
    {block.text}
  </div>
</section>
"""


def _back_matter(text: str) -> str:
    return f"""
<section class="page layout-back-matter">
  {text}
</section>
"""


def typeset(manuscript: Manuscript, buyer: Buyer | None = None) -> str:
    """Render the manuscript to a complete, branded HTML document."""
    buyer = buyer or Buyer()
    label = watermark_label(buyer)
    watermark = Watermark(buyer_label="" if buyer.is_anonymous else label)

    pages = [_cover(manuscript), _title_page(manuscript)]
    chapter = 0
    body_parts: list[str] = []

    def flush_body() -> None:
        if body_parts:
            pages.append(_body(list(body_parts)))
            body_parts.clear()

    for block in manuscript.blocks:
        if block.kind is BlockKind.BODY:
            # Consecutive prose flows on one page; a heading or a special
            # layout ends the flow.
            body_parts.append(block.text)
        else:
            flush_body()
            if block.kind is BlockKind.CHAPTER_OPENER:
                chapter += 1
                pages.append(_chapter_opener(chapter, block.title))
            elif block.kind is BlockKind.PULL_QUOTE:
                pages.append(_pull_quote(block.text))
            elif block.kind is BlockKind.WORKSHEET:
                pages.append(_worksheet(block.title, block.text))
            elif block.kind is BlockKind.REFLECTION_CARD:
                pages.append(_reflection_card(block.text))
            elif block.kind is BlockKind.SCRIPT_ROW:
                pages.append(_script_row(block))
            elif block.kind is BlockKind.BACK_MATTER:
                pages.append(_back_matter(block.text))
            # PAGE_BREAK ends the flow without adding a page of its own.
    flush_body()

    body = "\n".join(pages)

    return f"""<!DOCTYPE html>
<html lang="ms">
<head>
<meta charset="utf-8" />
<title>{_escape(manuscript.title or "Perpustakaan Hati")}</title>
<style>
{_fonts_css()}
{_style_block()}
{build_watermark_css(watermark)}
</style>
</head>
<body>
{body}
</body>
</html>
"""
