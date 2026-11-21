"""Lay a manuscript out as the branded interior HTML.

The CSS lives in ``templates/ebook-interior.html`` — the brand's master
interior template — so the builder never re-implements the design system.
This module only decides *which* layout each block gets and fills it in.

Layout rules come from docs/brand/ui-kit.md -> "Master layouts".

The template controls page breaks for covers, chapters and worksheets.
Consecutive paragraphs flow together. Watermarks repeat in page margin boxes.
"""

from __future__ import annotations

import json
import re
from functools import cache
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

# The seal that goes on the printed cover. Each tier has its own
# silhouette, so the cover tells the reader which edition it is even
# before the title is read.
TIER_SEALS = {
    "poket": "seal-edisi-poket.svg",
    "membangun": "seal-edisi-membangun.svg",
    "teman-hidup": "seal-teman-hidup.svg",
}

BRAND_ASSETS = Path(__file__).resolve().parents[3] / "docs" / "brand" / "assets"
EDITION_NAMES = {"poket": "Edisi Poket", "membangun": "Edisi Membangun", "teman-hidup": "Teman Hidup"}
POCKET_TREATMENTS = {
    "Kad Refleksi": ("reflection", 4),
    "Ceklis Pencetus Attach": ("checklist", 0),
    "Tujuh Hari Reset": ("seven-days", 0),
    "Catatan Hari Ini": ("notes", 7),
}

# Roman numerals for chapter numbers, 1..12 is plenty for these books.
ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
INDEX_COLUMNS = 5


@cache
def _edition_tokens() -> dict:
    return json.loads((BRAND_ASSETS.parent / "design-tokens.json").read_text(encoding="utf-8"))["ebook"]


def _chart_art(tier: str) -> str:
    """Tier-specific vector ornaments that render without raster assets."""
    if tier == "poket":
        paths = """
  <path d="M15 59C44 57 55 32 65 9M35 54C20 54 12 42 9 32C24 32 34 40 35 54Z
    M46 45C44 31 32 22 22 21C23 33 33 45 46 45Z
    M53 35C59 22 75 18 87 18C83 30 67 38 53 35Z
    M60 24C57 12 61 5 71 3C75 12 69 21 60 24Z
    M22 59C34 62 53 61 68 51"/>
"""
    elif tier == "membangun":
        paths = """
  <path d="M13 59H88M16 59V14M25 48H43V38H57V27H73V16H85
    M25 52V56M43 42V56M57 32V56M73 20V56" />
  <circle cx="25" cy="48" r="2.7"/><circle cx="43" cy="38" r="2.7"/>
  <circle cx="57" cy="27" r="2.7"/><circle cx="73" cy="16" r="2.7"/>
"""
    else:
        paths = """
  <path d="M8 33H92M50 2V64M18 10H82V56H18Z
    M50 4L82 33L50 62L18 33Z M50 13L72 33L50 53L28 33Z
    M50 23L60 33L50 43L40 33Z M8 29V37M92 29V37" />
  <ellipse cx="50" cy="33" rx="39" ry="13" transform="rotate(-20 50 33)"/>
  <ellipse cx="50" cy="33" rx="39" ry="13" transform="rotate(20 50 33)"/>
  <circle cx="18" cy="33" r="2"/><circle cx="82" cy="33" r="2"/>
"""
    stroke = _edition_tokens().get(tier, _edition_tokens()["poket"])["rule"]
    return (
        '<svg class="chapter-art" viewBox="0 0 100 66" aria-hidden="true" fill="none" '
        f'stroke="{stroke}">{paths}</svg>'
    )


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
    seal = BRAND_ASSETS / TIER_SEALS.get(tier, TIER_SEALS["poket"])
    emblem = (BRAND_ASSETS / "emblem-book-heart.svg").as_uri()
    seal_markup = ""
    if seal.is_file():
        seal_markup = f'<img class="tier-seal" src="{_escape(seal.as_uri())}" alt="" />'
    return f"""
<section class="page layout-cover {tier_class}">
  <div class="wordmark">Perpustakaan Hati</div>
  {f'<div class="cover-orbit">{_chart_art(tier)}</div>' if tier == "teman-hidup" else ""}
  <img class="cover-emblem" src="{_escape(emblem)}" alt="" />
  <div class="tier-bar"></div>
  <h1>{title}</h1>
  <p class="tagline">{subtitle}</p>
  <div class="byline">@rahimam</div>
  {seal_markup}
</section>
"""


def _title_page(manuscript: Manuscript) -> str:
    links = []
    chapter = section = 0
    for block in manuscript.blocks:
        if block.kind is BlockKind.CHAPTER_OPENER:
            chapter += 1
            links.append(f'<li><a href="#bab-{chapter}">{_escape(block.title)}</a></li>')
        elif manuscript.tier == "poket" and block.kind is BlockKind.BODY and block.text.startswith("<h2>"):
            section += 1
            links.append(f'<li><a href="#topik-{section}">{block.text[4:-5]}</a></li>')
    if any(block.kind is BlockKind.WORKSHEET for block in manuscript.blocks):
        links.append('<li><a href="#peta-latihan">Peta Latihan</a></li>')
    return f"""
<section class="page layout-title-page" id="kandungan">
  <div class="wordmark">{_escape(manuscript.title)}</div>
  <h2>Kandungan</h2>
  <ol>{"".join(links)}</ol>
  <div class="folio"></div>
</section>
"""


def _chapter_opener(number: int, title: str, tier: str) -> str:
    numeral = ROMAN[number] if number < len(ROMAN) else str(number)
    if tier == "poket":
        numeral = f"{number:02}"
    return f"""
<section class="page layout-chapter-opener" id="bab-{number}">
  {_chart_art(tier) if tier in TIER_CLASSES else ""}
  <div class="numeral">{numeral}</div>
  <h2>{_escape(title)}</h2>
  <div class="rule"></div>
  <a class="section-link" href="#kandungan">Kandungan</a>
</section>
"""


def _body(parts: list[str], treatment: str = "", lines: int = 0) -> str:
    style = f" topic-{treatment}" if treatment else ""
    reading_path = """
<div class="reading-path">
  <p class="field-label">Cara menggunakan edisi ini</p>
  <ol><li>Baca satu muka surat</li><li>Namakan perasaan</li><li>Tulis satu ayat</li></ol>
</div>
""" if treatment == "opening" else ""
    return f"""
<section class="page layout-body{style}">
  {chr(10).join('  ' + part for part in parts)}
  {reading_path}
  {_writing_space(f"poket-{treatment}", "Tulis catatan kamu", lines) if lines else ""}
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


def _writing_space(name: str, label: str, lines: int) -> str:
    rules = '<div class="write-rule"></div>' * lines
    return f"""
<div class="writing-space">
  <label class="field-label" for="{name}">{_escape(label)}</label>
  <div class="writing-area" style="--writing-lines: {lines}">
    <div class="writing-rules" aria-hidden="true">{rules}</div>
    <textarea id="{name}" name="{name}" title="{_escape(label)}" rows="{lines}"></textarea>
  </div>
</div>
"""


def _worksheet_index(total: int, tier: str) -> str:
    heading = f"Peta {total} Hari" if tier == "teman-hidup" else "Peta Latihan"
    entry = "Hari" if tier == "teman-hidup" else "Latihan"
    cells = [
        f'<td><a href="#latihan-{i}" aria-label="{entry} {i}"><span>{entry}</span>{i:02}</a></td>'
        for i in range(1, total + 1)
    ]
    cells.extend(["<td></td>"] * (-len(cells) % INDEX_COLUMNS))
    rows = "".join(
        f'<tr>{"".join(cells[start:start + INDEX_COLUMNS])}</tr>'
        for start in range(0, len(cells), INDEX_COLUMNS)
    )
    return f"""
<section class="page layout-index" id="peta-latihan">
  {_chart_art(tier)}
  <h2>{heading}</h2>
  <p>Pilih nombor untuk terus ke latihan. Isi dalam pembaca PDF yang menyokong borang, atau cetak untuk menulis.</p>
  <nav aria-label="{heading}"><table class="index-grid" role="presentation"><tbody>{rows}</tbody></table></nav>
  <a class="section-link" href="#kandungan">Kandungan</a>
</section>
"""


def _worksheet(block: Block, number: int, total: int, tier: str) -> str:
    slug = f"latihan-{number}"
    title = _escape(block.title)
    label = "Jurnal" if tier == "teman-hidup" else "Kit Refleksi"
    next_day = f'<a href="#latihan-{number + 1}">Seterusnya</a>' if number < total else ""
    progress = ""
    if tier == "teman-hidup":
        positions = "".join(
            '<i class="is-current"></i>' if position == number else "<i></i>"
            for position in range(1, total + 1)
        )
        progress = f'<div class="journal-progress" aria-hidden="true">{positions}</div>'
    followup = (
        _writing_space(f"{slug}-langkah", f"Satu langkah kecil — {block.title}", 2)
        if tier == "teman-hidup" else ""
    )
    return f"""
<section class="page layout-worksheet" id="{slug}">
  <div class="worksheet-kicker"><span>{label}</span><span>{number:02} / {total:02}</span></div>
  {progress}
  <h3>{title}</h3>
  <div class="rule"></div>
  <div class="worksheet-prompt">{block.text}</div>
  {_writing_space(f"{slug}-catatan", f"Catatan — {block.title}", 6 if followup else 8)}
  {followup}
  <nav class="worksheet-nav" aria-label="Navigasi latihan"><a href="#peta-latihan">Peta latihan</a>{next_day}</nav>
</section>
"""


def _reflection_card(text: str) -> str:
    return f"""
<section class="page layout-reflection-card-page">
  <div class="layout-reflection-card">
    <span class="card-diamond" aria-hidden="true"></span>
    <p class="card-prompt">KAD REFLEKSI · HATI</p>
    <p class="card-quote">{_escape(text)}</p>
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
    chapter = section = 0
    total_worksheets = sum(block.kind is BlockKind.WORKSHEET for block in manuscript.blocks)
    worksheet = 0
    body_parts: list[str] = []
    treatment, lines = "", 0

    def flush_body() -> None:
        nonlocal treatment, lines
        if body_parts:
            pages.append(_body(body_parts, treatment, lines))
            body_parts.clear()
        treatment, lines = "", 0

    for block in manuscript.blocks:
        if block.kind is BlockKind.BODY:
            # Consecutive prose flows on one page; a heading or a special
            # layout ends the flow.
            if manuscript.tier == "poket" and block.text.startswith("<h2>"):
                flush_body()
                section += 1
                title = block.text[4:-5]
                treatment, lines = POCKET_TREATMENTS.get(title, ("", 0))
                pages.append(f"""
<section class="page layout-topic" id="topik-{section}">
  {_chart_art("poket") if treatment in {"reflection", "notes"} else ""}
  <div class="numeral">{chapter + section:02}</div>
  <h2>{title}</h2>
  <div class="rule"></div>
</section>
""")
            else:
                if manuscript.tier == "teman-hidup" and re.match(r"<h2>Script \d+:", block.text):
                    flush_body()
                    treatment = "script"
                body_parts.append(block.text)
        else:
            flush_body()
            if block.kind is BlockKind.CHAPTER_OPENER:
                chapter += 1
                pages.append(_chapter_opener(chapter, block.title, manuscript.tier))
                if manuscript.tier == "poket" and block.title == "Kenapa Buku Ini":
                    treatment = "opening"
            elif block.kind is BlockKind.PULL_QUOTE:
                pages.append(_pull_quote(block.text))
            elif block.kind is BlockKind.WORKSHEET:
                worksheet += 1
                if worksheet == 1:
                    pages.append(_worksheet_index(total_worksheets, manuscript.tier))
                pages.append(_worksheet(block, worksheet, total_worksheets, manuscript.tier))
            elif block.kind is BlockKind.REFLECTION_CARD:
                pages.append(_reflection_card(block.text))
            elif block.kind is BlockKind.SCRIPT_ROW:
                pages.append(_script_row(block))
            elif block.kind is BlockKind.BACK_MATTER:
                pages.append(_back_matter(block.text))
            elif block.kind is BlockKind.PAGE_BREAK:
                pages.append('<span class="manuscript-break" hidden></span>')
    flush_body()

    body = "\n".join(pages)
    tier = manuscript.tier if manuscript.tier in TIER_CLASSES else "poket"
    tokens = _edition_tokens()[tier]
    palette = "; ".join(f"--book-{name}: {value}" for name, value in tokens.items())
    edition = EDITION_NAMES[tier]

    return f"""<!DOCTYPE html>
<html lang="ms">
<head>
<meta charset="utf-8" />
<title>{_escape(manuscript.title or "Perpustakaan Hati")}</title>
<style>
{_fonts_css()}
{_style_block()}
:root {{
    {palette}; --book-edition: "{edition}";
    --gold-deep: var(--book-ornament); --sepia-deep: var(--book-ink);
}}
{build_watermark_css(watermark)}
</style>
</head>
<body class="{TIER_CLASSES[tier]}">
{body}
</body>
</html>
"""
