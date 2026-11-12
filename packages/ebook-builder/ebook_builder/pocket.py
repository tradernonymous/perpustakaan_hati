"""Build the Edisi Poket pocket edition as an A4 PDF.

The pocket edition is a fixed-composition artefact: each page is authored
as one ``::: page`` block and laid out as a single A4 sheet, so the reading
experience matches the poster the thread came from. It is not a flowing
book, which is why it does not reuse the interior typesetter.

The renderer is headless Chrome, not WeasyPrint. WeasyPrint does not
implement ``-webkit-background-clip: text``, so the foil wordmark on the
cover renders as a solid block instead of a gradient. Chrome renders it
correctly and gives us exact page control through ``@page { size: A4 }``.

Layout rules come from docs/brand/ui-kit.md and docs/brand/DESIGN-SYSTEM.md.
Colours come from docs/brand/design-tokens.css, which the output links
rather than re-typing, so the brand tokens stay the single source.
"""

from __future__ import annotations

import html as html_lib
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOKENS = ROOT / "docs" / "brand" / "design-tokens.css"
FONTS = ROOT / "packages" / "brand-tools" / "fonts"
ASSETS = ROOT / "docs" / "brand" / "assets"

# The edition's own illustration store. Generated gold-line art lives with
# the manuscript it belongs to, not in the shared brand folder, so the
# design-system lock only guards the files every edition shares.
BOOK_ASSETS = ROOT / "content" / "ebooks" / "edisi-poket-cuma-kawan-pejabat" / "assets"

CHROME_CANDIDATES = (
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "chrome-headless-shell",
    "microsoft-edge",
)

# The foil wordmark. Chrome's print path drops ``background-clip: text``,
# so the metallic gradient would print as a flat band behind the letters
# instead of inside them. The brand's own lockup SVG has the same
# problem in print. The way through is to rasterise the wordmark in the
# screenshot path, where the gradient does clip to the glyphs, and embed
# the resulting PNG. The screenshot is taken against a transparent
# ground, so only the letters carry pixels.
FOIL_MARKUP = """
<html>
<head>
<meta charset="utf-8" />
<style>
  @font-face {
    font-family: 'Fraunces';
    src: url('%(font)s') format('woff2');
    font-weight: 400 700;
    font-display: block;
  }
  html, body { margin: 0; padding: 0; background: transparent; }
  .wrap {
    width: %(width)dpx;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .wordmark {
    font-family: 'Fraunces', Georgia, serif;
    font-weight: 560;
    font-size: %(wordmark_px)dpx;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    white-space: nowrap;
    align-self: center;
    background-image: linear-gradient(178deg, #fff4d6 0%%, #f0d08e 20%%, #c49a52 46%%, #9a7638 54%%, #d9b46c 62%%, #f6e2ad 84%%, #b8904a 100%%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .accent {
    font-family: 'Fraunces', Georgia, serif;
    font-weight: 660;
    font-size: %(accent_px)dpx;
    letter-spacing: 0.06em;
    white-space: nowrap;
    align-self: center;
    margin-top: 0.06em;
    background-image: linear-gradient(178deg, #d9f3df 0%%, #8fd0a6 22%%, #3f9167 46%%, #2d7954 58%%, #a7d3b6 76%%, #3f9167 100%%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }
</style>
</head>
<body>
  <div class="wrap">
    <div class="wordmark">%(wordmark)s</div>
    <div class="accent">%(accent)s</div>
  </div>
</body>
</html>
"""

PAGE_KINDS = {"cover", "thread", "content", "backmatter"}


class PocketError(ValueError):
    """The manuscript is not something we can typeset."""


# --------------------------------------------------------------------------
# model
# --------------------------------------------------------------------------


@dataclass
class Chart:
    title: str = ""
    source: str = ""
    note: str = ""
    rows: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class Steps:
    label: str = ""
    items: list[str] = field(default_factory=list)
    icons: list[str] = field(default_factory=list)


@dataclass
class Reflection:
    prompts: list[str] = field(default_factory=list)


@dataclass
class Page:
    kind: str = "content"
    numeral: str = ""
    title: str = ""
    subtitle: str = ""
    tagline: str = ""
    kicker: str = ""
    wordmark: str = ""
    wordmark_accent: str = ""
    tier_ribbon: str = ""
    byline: str = ""
    text: str = ""
    thread: str = ""
    art: str = ""
    ornament: bool = False
    charts: list[Chart] = field(default_factory=list)
    steps: list[Steps] = field(default_factory=list)
    sayings: list[tuple[str, str]] = field(default_factory=list)
    reflection: list[str] = field(default_factory=list)
    pull_quotes: list[str] = field(default_factory=list)


@dataclass
class PocketDoc:
    title: str = ""
    tier: str = ""
    subtitle: str = ""
    tagline: str = ""
    pages: list[Page] = field(default_factory=list)


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------


def _front_matter(lines: list[str]) -> tuple[dict, list[str]]:
    if not lines or lines[0].strip() != "---":
        return {}, lines
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            meta = {}
            for raw in lines[1:index]:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                key, separator, value = line.partition(":")
                if not separator:
                    continue
                meta[key.strip().lower()] = value.strip().strip('"').strip("'")
            return meta, lines[index + 1 :]
    raise PocketError("Front matter is never closed with '---'.")


def _parse_page(raw: str) -> Page:
    """Read one ``::: page`` block's key/value header."""
    page = Page()
    for raw_line in raw.strip().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise PocketError(f"Page header line {line!r} is not a key: value pair.")
        key = key.strip().lower()
        value = value.strip()
        if key == "kind":
            if value not in PAGE_KINDS:
                raise PocketError(f"Unknown page kind {value!r}.")
            page.kind = value
        elif key in {
            "numeral",
            "title",
            "subtitle",
            "tagline",
            "kicker",
            "wordmark",
            "wordmark_accent",
            "tier_ribbon",
            "byline",
            "art",
        }:
            setattr(page, key, value)
        elif key == "ornament":
            if value.lower() not in {"true", "false"}:
                raise PocketError(f"Page header ornament must be true or false, not {value!r}.")
            page.ornament = value.lower() == "true"
        else:
            raise PocketError(f"Unknown page header key {key!r}.")
    return page


def _parse_chart(raw: str) -> Chart:
    chart = Chart()
    rows: list[str] = []
    for raw_line in raw.strip().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.lower().startswith("title:"):
            chart.title = line.partition(":")[2].strip()
        elif line.lower().startswith("source:"):
            chart.source = line.partition(":")[2].strip()
        elif line.lower().startswith("note:"):
            chart.note = line.partition(":")[2].strip()
        else:
            # Rows are written as a Markdown list in the manuscript, so
            # the leading marker is stripped before the label is split.
            rows.append(re.sub(r"^[-*]\s+", "", line))
    for row in rows:
        label, separator, value = row.rpartition("|")
        if not separator:
            raise PocketError(f"Chart row {row!r} has no '| value' part.")
        try:
            float(value.strip())
        except ValueError as exc:
            raise PocketError(f"Chart row {row!r} has a non-numeric value.") from exc
        chart.rows.append((label.strip(), value.strip()))
    if not chart.rows:
        raise PocketError("A chart needs at least one row.")
    if not chart.source:
        raise PocketError(f"Chart {chart.title!r} has no source line.")
    return chart


def _parse_steps(raw: str) -> Steps:
    steps = Steps()
    items: list[str] = []
    icons: list[str] = []
    for raw_line in raw.strip().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.lower().startswith("label:"):
            steps.label = line.partition(":")[2].strip()
        elif line.lower().startswith("icons:"):
            # One icon per step, comma separated, so a card without icons
            # stays exactly the card it was.
            icons = [name.strip() for name in line.partition(":")[2].split(",") if name.strip()]
        else:
            # The manuscript writes steps as a Markdown list, so the
            # leading marker is stripped: the printed step carries a
            # number in its own disc, not a hyphen.
            items.append(re.sub(r"^[-*]\s+", "", line))
    steps.items = items
    if icons and len(icons) != len(items):
        raise PocketError(
            f"Steps has {len(items)} items but {len(icons)} icons; they must match."
        )
    steps.icons = icons
    return steps


def _parse_sayings(raw: str) -> list[tuple[str, str]]:
    sayings: list[tuple[str, str]] = []
    for raw_line in raw.strip().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        # The sayings are written as a Markdown list, so the leading
        # marker is stripped: the printed card opens on the quote, not
        # on a stray hyphen.
        line = re.sub(r"^[-*]\s+", "", line)
        text, separator, source = line.rpartition("|")
        if not separator:
            raise PocketError(f"Saying {line!r} has no '| attribution' part.")
        sayings.append((text.strip(), source.strip()))
    return sayings


def _parse_reflection(raw: str) -> list[str]:
    prompts = []
    for line in raw.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        prompts.append(re.sub(r"^[-*]\s+", "", line))
    return prompts


def parse_pocket(source: str) -> PocketDoc:
    """Parse a pocket manuscript into typed pages."""
    if not isinstance(source, str):
        raise PocketError("Manuscript must be text.")
    lines = source.replace("\r\n", "\n").split("\n")
    meta, body = _front_matter(lines)

    doc = PocketDoc(
        title=str(meta.get("title", "")),
        tier=str(meta.get("tier", "")),
        subtitle=str(meta.get("subtitle", "")),
        tagline=str(meta.get("tagline", "")),
    )

    index = 0
    prose: list[str] = []
    current: Page | None = None

    def flush_prose() -> None:
        nonlocal prose
        if not prose:
            return
        text = "\n\n".join(p.strip() for p in prose if p.strip())
        if current is not None and text:
            current.text = f"{current.text}\n\n{text}".strip()
        prose = []

    while index < len(body):
        line = body[index]
        stripped = line.strip()

        if stripped.startswith(":::"):
            flush_prose()
            marker = stripped[3:].strip().lower()
            closing = index + 1
            while closing < len(body) and body[closing].strip() != ":::":
                closing += 1
            if closing >= len(body):
                raise PocketError(f"Marker '::: {marker}' is never closed.")
            inner = "\n".join(body[index + 1 : closing]).strip()

            if marker == "page":
                if current is not None:
                    doc.pages.append(current)
                current = _parse_page(inner)
            elif marker == "thread":
                if current is None:
                    raise PocketError("A thread block must sit inside a page.")
                current.thread = f"{current.thread}\n\n{inner}".strip()
            elif marker == "chart":
                if current is None:
                    raise PocketError("A chart block must sit inside a page.")
                current.charts.append(_parse_chart(inner))
            elif marker == "steps":
                if current is None:
                    raise PocketError("A steps block must sit inside a page.")
                current.steps.append(_parse_steps(inner))
            elif marker == "sayings":
                if current is None:
                    raise PocketError("A sayings block must sit inside a page.")
                current.sayings.extend(_parse_sayings(inner))
            elif marker == "reflection":
                if current is None:
                    raise PocketError("A reflection block must sit inside a page.")
                current.reflection = _parse_reflection(inner)
            else:
                raise PocketError(f"Unknown manuscript marker '::: {marker}'.")

            index = closing + 1
            continue

        if stripped.startswith(">"):
            flush_prose()
            if current is None:
                raise PocketError("A pull quote must sit inside a page.")
            current.pull_quotes.append(stripped.lstrip("> ").strip())
            index += 1
            continue

        if not stripped:
            flush_prose()
            index += 1
            continue

        prose.append(stripped)
        index += 1

    flush_prose()
    if current is not None:
        doc.pages.append(current)

    if not doc.pages:
        raise PocketError("The manuscript has no pages.")
    return doc


# --------------------------------------------------------------------------
# typesetting
# --------------------------------------------------------------------------


def _e(text: str) -> str:
    return html_lib.escape(str(text or ""), quote=True)


def _paragraphs(text: str) -> str:
    """Render prose with its emphasis marks, one paragraph per blank line."""
    out = []
    for block in re.split(r"\n\s*\n", text or ""):
        block = block.strip()
        if not block:
            continue
        rendered = _e(block)
        rendered = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", rendered)
        rendered = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", rendered)
        out.append(f"<p>{rendered}</p>")
    return "\n".join(out)


def _thread_block(text: str) -> str:
    """Rahimam's post, verbatim — caps and shorthand kept as sent."""
    posts = []
    for block in re.split(r"\n\s*\n", text or ""):
        block = block.strip()
        if not block:
            continue
        posts.append(f'<p class="thread-line">{_e(block)}</p>')
    return f"""
    <blockquote class="thread">
{chr(10).join(posts)}
    </blockquote>"""


def _art_block(name: str, variant: str = "panel") -> str:
    """One generated illustration, feathered into the page ground.

    The art ships on its own dark-green field which is close to, but not
    exactly, the page's vignetted ground. A mask fades every edge to
    transparent so the rectangle dissolves instead of showing a seam.
    """
    source = BOOK_ASSETS / name
    if not source.is_file():
        raise PocketError(f"Art file {name!r} is missing from {BOOK_ASSETS}.")
    return f"""
    <figure class="art-{variant}"><img src="{_e(source.as_uri())}" alt="" /></figure>"""


def _ornament_block() -> str:
    return _art_block("ornament-divider.png", variant="ornament")


def _chart_block(chart: Chart) -> str:
    rows = []
    for label, value in chart.rows:
        width = max(0.0, min(100.0, float(value)))
        rows.append(
            f"""      <div class="bar-row">
        <span class="bar-label">{_e(label)}</span>
        <span class="bar-track"><span class="bar-fill" style="width: {width}%"></span></span>
        <span class="bar-value">{_e(value)}%</span>
      </div>"""
        )
    note = f'<p class="chart-note">{_e(chart.note)}</p>' if chart.note else ""
    # One shared 0-100 scale under every chart: the ticks line up with
    # the tracks because the row copies the bar-row columns exactly, so
    # a reader can measure any bar against the same ruler.
    scale = """
      <div class="chart-scale" aria-hidden="true">
        <span></span>
        <span class="scale-ticks"><i>0</i><i>25</i><i>50</i><i>75</i><i>100</i></span>
        <span class="bar-value"></span>
      </div>"""
    return f"""
    <figure class="chart">
      <figcaption class="chart-title">{_e(chart.title)}</figcaption>
      {note}
      <div class="bars">
{chr(10).join(rows)}
      </div>
      {scale}
      <p class="source">{_e(chart.source)}</p>
    </figure>"""


def _steps_block(steps: Steps) -> str:
    items = []
    for number, item in enumerate(steps.items, start=1):
        # With icons the gold disc shrinks to a corner badge and the
        # icon tile takes its place; without them the numbered disc the
        # edition has always printed.
        if steps.icons:
            icon = BOOK_ASSETS / steps.icons[number - 1]
            if not icon.is_file():
                raise PocketError(f"Step icon {steps.icons[number - 1]!r} is missing.")
            mark = (
                f'<span class="step-mark">'
                f'<span class="step-ico"><img src="{_e(icon.as_uri())}" alt="" /></span>'
                f'<span class="step-number">{number}</span></span>'
            )
        else:
            mark = f'<span class="step-number">{number}</span>'
        items.append(
            f"""      <li class="step">
        {mark}
        <span class="step-text">{_e(item)}</span>
      </li>"""
        )
    variant = " has-icons" if steps.icons else ""
    return f"""
    <div class="steps{variant}">
      <p class="steps-label">{_e(steps.label)}</p>
      <ol>
{chr(10).join(items)}
      </ol>
    </div>"""


def _sayings_block(sayings: list[tuple[str, str]]) -> str:
    items = []
    for text, source in sayings:
        items.append(
            f"""      <li class="saying">
        <p class="saying-text">“{_e(text)}”</p>
        <p class="saying-source">{_e(source)}</p>
      </li>"""
        )
    return f"""
    <ul class="sayings">
{chr(10).join(items)}
    </ul>"""


def _reflection_block(prompts: list[str]) -> str:
    items = []
    for number, prompt in enumerate(prompts, start=1):
        lines = "".join('<span class="write-line"></span>' for _ in range(3))
        items.append(
            f"""      <li class="prompt">
        <p class="prompt-text"><span class="prompt-number">{number}</span>{_e(prompt)}</p>
        <div class="prompt-lines">{lines}</div>
      </li>"""
        )
    return f"""
    <ul class="reflection">
{chr(10).join(items)}
    </ul>"""


def _emphasis(text: str) -> str:
    """Escape, then honour the italic accent the house style uses in titles."""
    rendered = _e(text)
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", rendered)


def _cover_page(page: Page, foil: str | None = None) -> str:
    if foil:
        wordmark = f'<img class="foil" src="{_e(foil)}" alt="" />'
    else:
        wordmark = (
            f'<p class="wordmark">{_e(page.wordmark)}</p>\n'
            f'        <p class="wordmark-accent">{_e(page.wordmark_accent)}</p>'
        )
    return f"""
  <section class="page cover">
    <div class="cover-frame">
      <div class="cover-inner">
        <p class="kicker"><span class="rule"></span>{_e(page.kicker)}<span class="rule"></span></p>
        <img class="emblem" src="{_e((ASSETS / 'emblem-book-heart.svg').as_uri())}" alt="" />
        {wordmark}
        <h1 class="cover-title">{_emphasis(page.title)}</h1>
        <p class="cover-tagline">{_e(page.tagline)}</p>
        <p class="tier-ribbon">{_e(page.tier_ribbon)}</p>
        <p class="kicker byline"><span class="rule"></span>{_e(page.byline)}<span class="rule"></span></p>
      </div>
    </div>
    <img class="seal" src="{_e((ASSETS / 'seal-edisi-poket.svg').as_uri())}" alt="Meterai Edisi Poket" />
  </section>"""


def _interior_page(page: Page, folio: int) -> str:
    head: list[str] = []
    if page.numeral:
        head.append(f'<p class="numeral">{_e(page.numeral)}</p>')
    head.append(f'<h2 class="page-title">{_e(page.title)}</h2>')
    if page.subtitle:
        head.append(f'<p class="page-subtitle">{_e(page.subtitle)}</p>')

    blocks: list[str] = []
    # The ornament sits directly under the section head, so it reads as
    # part of the opener rather than as another body block.
    if page.ornament:
        blocks.append(_ornament_block())
    if page.text:
        blocks.append(f'<div class="prose">{_paragraphs(page.text)}</div>')
    if page.thread:
        blocks.append(_thread_block(page.thread))
    for chart in page.charts:
        blocks.append(_chart_block(chart))
    for steps in page.steps:
        blocks.append(_steps_block(steps))
    if page.sayings:
        blocks.append(_sayings_block(page.sayings))
    if page.reflection:
        blocks.append(_reflection_block(page.reflection))
    # The illustration fills the foot of the page; the pull quote still
    # closes it, so the last beat of the page stays words.
    if page.art:
        blocks.append(_art_block(page.art))
    for quote in page.pull_quotes:
        blocks.append(f'<p class="pull-quote">“{_e(quote)}”</p>')

    if page.kind == "backmatter":
        # The closing page is a notice, not a chapter: no numeral, and the
        # helpline block is the only body content. The lantern art hangs
        # above it, not beside it.
        art = _art_block(page.art) if page.art else ""
        return f"""
  <section class="page backmatter">
    <p class="kicker"><span class="rule"></span>EDISI POKET · CUMA KAWAN PEJABAT<span class="rule"></span></p>
    <div class="page-body">
      {art}
      <h2 class="page-title">{_e(page.title)}</h2>
      <div class="prose">{_paragraphs(page.text)}</div>
    </div>
    <p class="folio-back">BY @RAHIMAM</p>
  </section>"""

    body = "\n".join(blocks)
    return f"""
  <section class="page">
    <p class="kicker running-head"><span class="rule"></span>EDISI POKET · CUMA KAWAN PEJABAT<span class="rule"></span></p>
    <div class="page-body">
      <header class="page-head">
        {chr(10).join('        ' + line for line in head)}
      </header>
{body}
    </div>
    <p class="folio"><span>BY @RAHIMAM</span><span>Halaman {folio}</span></p>
  </section>"""


def _page_css() -> str:
    """The page composition: A4 sheet, dark stage, brand type.

    One type scale for the whole edition. The base size is fixed at
    ``--base`` and every other size is an ``em`` of it, so the same role
    renders at the same size on every page: a body paragraph is the same
    size on page 3 as on page 11. Earlier revisions scaled each page to
    fill its sheet, which made identical elements differ by more than
    double between pages and is why the edition read as inconsistent.

    Spacing is one rhythm, not a set of per-block margins. Every direct
    child of ``.page-body`` sits ``--rhythm`` apart, so the gaps between
    a paragraph, a chart, a card and a closing quote are equal by
    construction. A page that cannot hold its copy at this scale gets
    less copy, not smaller type.
    """
    return """
  @page { size: A4; margin: 0; }

  * { box-sizing: border-box; }

  html, body {
    margin: 0;
    padding: 0;
    background: var(--forest-night);
    color: var(--text-on-dark);
    font-family: var(--font-reading);
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  .page {
    /* ---- the single type scale ------------------------------------ */
    --base: 21px;
    --rhythm: 1.3em;
    position: relative;
    width: 210mm;
    height: 297mm;
    padding: 20mm 20mm 16mm;
    font-size: var(--base);
    overflow: hidden;
    background-color: var(--forest-night);
    background-image: var(--vignette), var(--glow-emerald);
    page-break-after: always;
    break-after: page;
    display: flex;
    flex-direction: column;
  }
  .page:last-child { page-break-after: auto; break-after: auto; }

  /* The body of a page is a single column with one gap between blocks.
     Nothing inside it carries its own vertical margin, so the spacing
     cannot drift from page to page. It takes the height that is left,
     which lets the closing quote sit on the page's bottom rule instead
     of leaving the foot of the sheet empty. */
  .page-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: var(--rhythm);
  }
  .page-head {
    display: flex;
    flex-direction: column;
    gap: 0.34em;
  }

  /* ---- running head ------------------------------------------------ */
  .kicker {
    display: flex;
    align-items: center;
    gap: 1.1em;
    margin: 0 0 1.25em;
    font: 500 0.5em/1 var(--font-body);
    letter-spacing: 0.32em;
    text-transform: uppercase;
    color: var(--gold-light);
  }
  .kicker .rule { flex: 1 1 3em; height: 1px; background: var(--rule-flank); }

  /* ---- headings ---------------------------------------------------- */
  .numeral {
    margin: 0;
    font: 660 3.2em/1 var(--font-display);
    letter-spacing: 0.04em;
    color: var(--green-300);
  }
  .page-title {
    margin: 0;
    font: 520 1.8em/1.15 var(--font-display);
    color: var(--cream);
    text-wrap: balance;
  }
  .page-subtitle {
    margin: 0;
    font: italic 400 0.98em/1.5 var(--font-reading);
    color: var(--green-300);
    text-wrap: pretty;
  }

  /* ---- prose ------------------------------------------------------- */
  .prose p {
    margin: 0 0 1em;
    font: 400 0.88em/1.72 var(--font-reading);
    color: var(--text-on-dark);
    text-align: justify;
    text-wrap: pretty;
    hyphens: none;
  }
  .prose p:last-child { margin-bottom: 0; }
  .prose strong { color: var(--green-300); font-weight: 600; }
  .prose em { color: var(--gold-light); font-style: italic; }

  /* ---- thread post (verbatim, Rahimam's own caps and shorthand) ----- */
  .thread {
    margin: 0;
    padding: 0.85em 1em;
    border-left: 2px solid var(--green-400);
    border-radius: 0 var(--radius-lg) var(--radius-lg) 0;
    background: var(--card-v3-bg);
  }
  .thread-line {
    margin: 0 0 0.62em;
    font: 400 0.85em/1.66 var(--font-reading);
    color: var(--text-on-dark);
    text-wrap: pretty;
  }
  .thread-line:last-child { margin-bottom: 0; }
  .thread-line:first-child {
    font-weight: 600;
    letter-spacing: 0.01em;
    color: var(--cream);
  }

  /* ---- pull quote --------------------------------------------------
     The closing line of a page: one line, smaller than the body, and
     separated from the copy above by the page's one rhythm plus a
     hairline rule, so it reads as its own beat. */
  .pull-quote {
    margin: 0;
    padding-top: 0.9em;
    border-top: 1px solid var(--forest-edge);
    font: italic 400 0.78em/1.4 var(--font-reading);
    color: var(--gold-light);
    text-align: center;
    text-wrap: nowrap;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  /* ---- generated art ------------------------------------------------
     The illustrations arrive on their own dark-green field that is
     close to, but not exactly, the page's vignetted ground. A mask
     fades every edge to transparent so the rectangle dissolves into
     the sheet instead of showing a seam. */
  .art-panel, .art-ornament { margin: 0; overflow: hidden; }
  .art-panel { height: 56mm; }
  .art-panel img, .art-ornament img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
    -webkit-mask-image:
      linear-gradient(to right, transparent 0, #000 9%, #000 91%, transparent 100%),
      linear-gradient(to bottom, transparent 0, #000 12%, #000 88%, transparent 100%);
    -webkit-mask-composite: source-in;
    mask-image:
      linear-gradient(to right, transparent 0, #000 9%, #000 91%, transparent 100%),
      linear-gradient(to bottom, transparent 0, #000 12%, #000 88%, transparent 100%);
    mask-composite: intersect;
  }
  /* The divider crops to its centre strip. Its field is darker than the
     page ground, which would print a rectangle around it, so instead of
     fading the edges the whole background is dropped: a lighten blend
     keeps the gold motif and lets the ground show through everything
     darker than itself, seam or no seam. */
  .art-ornament { height: 9mm; }
  .art-ornament img {
    -webkit-mask-image: none;
    mask-image: none;
    mix-blend-mode: lighten;
  }

  /* ---- chart ------------------------------------------------------- */
  .chart {
    margin: 0;
    padding: 1.15em 1.25em 1.05em;
    border: 1px solid var(--forest-edge);
    border-radius: var(--radius-lg);
    background: var(--card-v3-bg);
  }
  .chart-title {
    margin: 0 0 0.75em;
    font: 600 0.55em/1.35 var(--font-body);
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--gold-light);
    text-align: center;
    text-wrap: balance;
  }
  .chart-note {
    margin: 0 0 0.95em;
    font: 400 0.53em/1.5 var(--font-body);
    color: var(--text-muted-on-dark);
    text-align: center;
    text-wrap: pretty;
  }
  .bars { display: grid; gap: 0.55em; }
  .bar-row {
    /* The columns are proportional, not measured in em: an em column
       would scale with the page's type and starve the bar track. */
    display: grid;
    grid-template-columns: minmax(0, 1fr) 40% max-content;
    align-items: center;
    gap: 0.6em;
  }
  .bar-label {
    font: 500 0.56em/1.3 var(--font-body);
    color: var(--text-on-dark);
    text-align: right;
    text-wrap: nowrap;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    min-width: 0;
  }
  .bar-track {
    height: 0.5em;
    border-radius: var(--radius-pill);
    background-color: var(--chart-track);
    /* Quarter ticks ride under the fill: the unfilled stretch of the
       track shows where 25/50/75 sit, and the fill covers them. */
    background-image: linear-gradient(90deg, var(--chart-grid) 0 1px, transparent 1px);
    background-size: 25% 100%;
    overflow: hidden;
  }
  .bar-fill {
    display: block;
    height: 100%;
    border-radius: var(--radius-pill);
    background: linear-gradient(90deg, var(--green-700), var(--green-500));
  }
  .bar-value {
    font: 600 0.6em/1 var(--font-body);
    color: var(--gold-light);
    text-align: right;
    min-width: 3.4em;
  }
  /* The shared ruler. The empty outer cells repeat the bar-row columns
     (an empty .bar-value carries the same 3.4em minimum), so the tick
     labels sit exactly under the tracks on every chart. */
  .chart-scale {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 40% max-content;
    align-items: center;
    gap: 0.6em;
    margin: 0.5em 0 0;
  }
  .scale-ticks {
    display: flex;
    justify-content: space-between;
    font: 500 0.5em/1 var(--font-body);
    color: var(--text-muted-on-dark);
  }
  .scale-ticks i { font-style: normal; }
  .chart-scale .bar-value { visibility: hidden; }
  .source {
    margin: 0.9em 0 0;
    font: 400 0.5em/1.45 var(--font-body);
    color: var(--text-muted-on-dark);
  }

  /* ---- steps ------------------------------------------------------- */
  .steps {
    margin: 0;
    padding: 1.1em 1.25em 1.15em;
    border: 1px solid var(--forest-edge);
    border-radius: var(--radius-lg);
    background: var(--card-v3-bg);
  }
  .steps-label {
    margin: 0 0 0.85em;
    font: 600 0.55em/1 var(--font-body);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--gold-light);
  }
  .steps ol { margin: 0; padding: 0; list-style: none; display: grid; gap: 0.85em; }
  .step { display: grid; grid-template-columns: 1.9em 1fr; gap: 0.5em; align-items: start; }
  .step-number {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 1.9em;
    height: 1.9em;
    border-radius: 50%;
    font: 660 0.78em/1 var(--font-display);
    color: var(--forest-night);
    background: linear-gradient(180deg, var(--gold-light), var(--gold));
  }
  .step-text {
    font: 400 0.82em/1.6 var(--font-reading);
    color: var(--text-on-dark);
    text-wrap: pretty;
  }

  /* ---- icon practice cards ------------------------------------------
     The dedicated Amalan pages carry a line icon per step. The icon
     tile takes the column the gold disc used to hold, and the disc
     shrinks to a corner badge so the step still reads as numbered. */
  .steps.has-icons ol { gap: 1.05em; }
  .steps.has-icons { padding: 1.25em 1.35em 1.3em; }
  .steps.has-icons .step { grid-template-columns: 2.4em 1fr; gap: 0.6em; }
  .step-mark { position: relative; display: block; width: 2.4em; height: 2.4em; }
  .step-ico {
    display: block;
    width: 100%;
    height: 100%;
    border: 1px solid var(--forest-edge);
    border-radius: var(--radius-md);
    background: var(--forest-night);
    overflow: hidden;
  }
  .step-ico img { display: block; width: 100%; height: 100%; object-fit: cover; }
  .steps.has-icons .step-number {
    position: absolute;
    top: -0.45em;
    right: -0.45em;
    width: 1.6em;
    height: 1.6em;
    box-shadow: 0 2px 6px rgb(0 0 0 / 0.45);
  }

  /* ---- sayings ----------------------------------------------------- */
  .sayings { margin: 0; padding: 0; list-style: none; display: grid; gap: 0.95em; }
  .saying {
    padding: 0.9em 1.1em;
    border-left: 2px solid var(--gold);
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
    background: var(--card-v3-bg);
  }
  .saying-text {
    margin: 0 0 0.6em;
    font: italic 400 0.9em/1.65 var(--font-reading);
    color: var(--cream);
    text-wrap: pretty;
  }
  .saying-source {
    margin: 0;
    font: 500 0.55em/1.35 var(--font-body);
    letter-spacing: 0.04em;
    color: var(--green-300);
  }

  /* ---- reflection --------------------------------------------------
     A worksheet has to be writable: each prompt is followed by its own
     ruled lines with room to write, so the dotted rules never sit tight
     under the prompt. */
  .reflection { margin: 0; padding: 0; list-style: none; display: grid; gap: 1.3em; }
  .prompt { display: grid; gap: 0.7em; }
  .prompt-text {
    margin: 0;
    font: 400 0.88em/1.55 var(--font-reading);
    color: var(--cream);
    text-wrap: pretty;
  }
  .prompt-number {
    /* Inline, not inline-block: an inline box of its own sits a pixel off
       the text baseline, which reads as a stray word on its own line. */
    display: inline;
    padding-right: 0.55em;
    color: var(--gold-light);
    font-family: var(--font-display);
    font-weight: 660;
    white-space: nowrap;
  }
  .prompt-lines { display: grid; gap: 0.95em; padding-top: 0.4em; }
  .write-line {
    display: block;
    height: 1.9em;
    border-bottom: 1px dotted var(--gold-deep);
  }

  /* ---- folio ------------------------------------------------------- */
  .folio {
    display: flex;
    justify-content: space-between;
    margin: auto 0 0;
    padding-top: 1.1em;
    font: 500 0.48em/1 var(--font-body);
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--gold-light);
  }
  .folio-back {
    margin: auto 0 0;
    padding-top: 1.1em;
    font: 500 0.48em/1 var(--font-body);
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--gold-light);
  }

  /* ---- back matter -------------------------------------------------
     The closing page is a safety notice, so it is composed as one: the
     helpline block is centred in the sheet rather than stranded at the
     top. It keeps the edition's type scale: a notice is not a reason to
     set the same role at a different size. */
  .backmatter { justify-content: center; }
  .backmatter .kicker { margin-bottom: 0; }
  .backmatter .page-body { flex: 0 1 auto; gap: 1.6em; }
  .backmatter .art-panel { height: 62mm; }
  .backmatter .prose p {
    text-align: left;
    margin-bottom: 0.9em;
  }
  .backmatter .prose p:first-child {
    font-weight: 600;
    color: var(--gold-light);
    letter-spacing: 0.01em;
  }
  .backmatter .prose p:last-child {
    margin-bottom: 0;
    color: var(--text-muted-on-dark);
  }
  .backmatter .folio-back { margin-top: 1.6em; }

  /* ---- cover ------------------------------------------------------- */
  .cover { padding: 0; align-items: stretch; justify-content: stretch; }
  .cover-frame {
    position: absolute;
    inset: 12mm;
    border: 1px solid var(--gold-deep);
    padding: 9mm;
  }
  .cover-inner {
    position: relative;
    height: 100%;
    border: 1px solid var(--gold);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 12mm 14mm;
  }
  .cover .kicker { margin: 0 0 0.35em; width: 100%; }
  .emblem { width: 74mm; height: auto; margin-bottom: 0.4em; }

  /* The foil wordmark is a rasterised PNG (see FOIL_MARKUP), because
     Chrome's print path does not clip a gradient to the glyphs. The
     type-based fallback below is used when no raster is supplied. */
  .foil {
    display: block;
    width: 118mm;
    height: auto;
    margin: 0 auto 0.3em;
  }
  .wordmark {
    margin: 0;
    font: 560 1.7em/1 var(--font-display);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--foil-gold-flat);
  }
  .wordmark-accent {
    margin: 0.1em 0 0;
    font: 660 3.75em/1 var(--font-display);
    letter-spacing: 0.06em;
    color: var(--foil-emerald-flat);
  }
  .cover-title {
    margin: 0.6em 0 0;
    font: 520 1.95em/1.18 var(--font-display);
    color: var(--cream);
    text-wrap: balance;
  }
  .cover-title em { font-style: italic; color: var(--gold-light); }
  .cover-tagline {
    margin: 0.2em auto 0;
    max-width: 30em;
    font: italic 400 0.78em/1.55 var(--font-reading);
    color: var(--green-300);
    text-wrap: balance;
  }
  .tier-ribbon {
    margin: 0.4em 0 0;
    padding: 0.1em 0.45em;
    border-radius: var(--radius-sm);
    font: italic 400 0.66em/1 var(--font-script);
    color: var(--gold-light);
    background: var(--ribbon-bg);
    border: 1px solid var(--gold);
  }
  .cover .byline { margin: 0.4em 0 0; width: 100%; }
  .seal {
    position: absolute;
    right: 17mm;
    bottom: 17mm;
    width: 22mm;
    height: auto;
    transform: rotate(-8deg);
    filter: drop-shadow(0 8px 18px rgb(0 0 0 / 0.55));
  }
"""


# --------------------------------------------------------------------------
# layout audit
# --------------------------------------------------------------------------

# The blocks whose last line must never hold a single word.
AUDITED_BLOCKS = (
    ".prose p",
    ".step-text",
    ".saying-text",
    ".prompt-text",
    ".thread-line",
    ".bar-label",
    ".page-title",
    ".page-subtitle",
    ".pull-quote",
    ".chart-title",
    ".source",
    ".steps-label",
    ".saying-source",
)

# Measures, in the browser: how full each page is, and how many words sit
# on the last line of each text block. A block whose last line holds one
# word is a runt — the reader sees a stray word hanging on its own.
_AUDIT_SCRIPT = """
<script>
(function () {
  const BLOCKS = %s;
  const ROLES = %s;

  function roleSizes(page) {
    const sizes = {};
    Object.keys(ROLES).forEach(function (key) {
      const el = page.querySelector(ROLES[key]);
      sizes[key] = el ? Math.round(parseFloat(getComputedStyle(el).fontSize) * 10) / 10 : null;
    });
    return sizes;
  }
  function lastLineWords(el) {
    const words = [];
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      const text = node.nodeValue;
      const re = /\\S+/g;
      let match;
      while ((match = re.exec(text)) !== null) {
        const range = document.createRange();
        range.setStart(node, match.index);
        range.setEnd(node, match.index + match[0].length);
        const rects = range.getClientRects();
        if (!rects.length) continue;
        const rect = rects[rects.length - 1];
        words.push({ word: match[0], top: Math.round(rect.top * 2) / 2 });
      }
    }
    if (!words.length) return null;
    // Group words into lines by their top edge, allowing a small
    // tolerance: an inline box in a different font can sit a pixel off
    // the text baseline without being on a line of its own.
    const TOLERANCE = 3;
    const lines = [];
    for (const w of words.sort((a, b) => a.top - b.top)) {
      let line = lines.find(l => Math.abs(l.top - w.top) <= TOLERANCE);
      if (!line) {
        line = { top: w.top, words: [] };
        lines.push(line);
      }
      line.words.push(w.word);
    }
    lines.sort((a, b) => a.top - b.top);
    const last = lines[lines.length - 1];
    return {
      lines: lines.length,
      lastWords: last.words.length,
      lastText: last.words.join(' '),
    };
  }

  function pageFill(page) {
    const style = getComputedStyle(page);
    const inner = page.clientHeight - parseFloat(style.paddingTop) - parseFloat(style.paddingBottom);
    const body = page.querySelector('.page-body');
    let used = 0;
    if (body) {
      const gap = parseFloat(getComputedStyle(body).rowGap) || 0;
      const children = Array.from(body.children);
      // Only the block heights count. Every block inside the body carries
      // no vertical margin: the one exception is the closing quote, whose
      // auto margin pins it to the foot of the sheet. Counting margins
      // here would report every page as full simply because of that gap.
      children.forEach(function (child, i) {
        used += child.offsetHeight;
        if (i < children.length - 1) used += gap;
      });
    }
    return { used: Math.round(used), inner: Math.round(inner) };
  }

  window.addEventListener('load', function () {
    document.fonts.ready.then(function () {
      const pages = Array.from(document.querySelectorAll('.page'));
      const report = { pages: [], runts: [], overflows: [] };
      pages.forEach(function (page, index) {
        const fill = pageFill(page);
        const kind = page.classList.contains('cover') ? 'cover'
          : page.classList.contains('backmatter') ? 'backmatter'
          : 'content';
        report.pages.push({
          index: index,
          kind: kind,
          used: fill.used,
          inner: fill.inner,
          sizes: roleSizes(page),
        });
        document.querySelectorAll(BLOCKS.join(', ')).forEach(function (el) {
          if (!page.contains(el)) return;
          const info = lastLineWords(el);
          if (!info || info.lines < 2) return;
          if (info.lastWords < 2) {
            report.runts.push({
              page: index,
              block: el.className,
              lines: info.lines,
              lastText: info.lastText,
              text: el.textContent.trim().slice(0, 60),
            });
          }
        });
        // A block that is clipped has lost copy, so it must be reported
        // rather than hidden by the overflow rule.
        page.querySelectorAll('.pull-quote, .bar-label, .page-title').forEach(function (el) {
          if (el.scrollWidth > el.clientWidth + 1) {
            report.overflows.push({
              page: index,
              block: el.className,
              scrollWidth: el.scrollWidth,
              clientWidth: el.clientWidth,
              text: el.textContent.trim().slice(0, 70),
            });
          }
        });
      });
      const pre = document.createElement('pre');
      pre.id = 'audit';
      pre.textContent = JSON.stringify(report);
      document.body.appendChild(pre);
    });
  });
})();
</script>
"""


def audit_layout(document: str) -> dict:
    """Measure page fill, type sizes and single-word last lines.

    Chrome does the measuring, because only the browser knows where the
    lines actually broke and what each role computed to. The HTML is
    written to disk and loaded over ``file://`` so the linked brand
    tokens and fonts apply.
    """
    chrome = find_chrome()
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "audit.html"
        source.write_text(
            document.replace(
                "</body>",
                _AUDIT_SCRIPT
                % (json.dumps(list(AUDITED_BLOCKS)), json.dumps(UNIFORM_ROLES))
                + "</body>",
            ),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                chrome,
                "--headless=new",
                "--no-sandbox",
                "--disable-gpu",
                "--hide-scrollbars",
                "--allow-file-access-from-files",
                "--virtual-time-budget=10000",
                "--dump-dom",
                source.as_uri(),
            ],
            capture_output=True,
            check=False,
            text=True,
            timeout=180,
        )

    match = re.search(r'<pre id="audit">(.*?)</pre>', result.stdout, re.S)
    if not match:
        raise PocketError("The layout audit did not report. Chrome may have failed to load the page.")
    return json.loads(match.group(1).replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">"))


# A page should read as composed, not padded out. A page that cannot hold
# its copy at the edition's one type scale is a copy problem, not a reason
# to shrink the type. These bounds only catch a page that has drifted so
# far it no longer reads as composed.
MIN_FILL = 0.42
MAX_FILL = 0.98

# The text roles whose rendered size must be identical on every page.
UNIFORM_ROLES = {
    "body": ".prose p",
    "title": ".page-title",
    "subtitle": ".page-subtitle",
    "chart": ".chart-title",
    "note": ".chart-note",
    "label": ".bar-label",
    "step": ".step-text",
    "quote": ".pull-quote",
    "saying": ".saying-text",
    "prompt": ".prompt-text",
    "thread": ".thread-line",
}


def measure_pocket(doc: PocketDoc) -> dict:
    """Measure the composed edition in Chrome and return the report.

    There is no solver any more. The edition is set at one type scale, so
    the only thing to measure is whether each page's copy fits the sheet
    and whether every text role landed at the same size everywhere.
    """
    return audit_layout(build_pocket_html(doc))


def check_uniform_type(report: dict) -> list[str]:
    """Return the text roles that are not the same size on every page."""
    seen: dict[str, set[float]] = {}
    for page in report["pages"]:
        for role, size in (page.get("sizes") or {}).items():
            if size is None:
                continue
            seen.setdefault(role, set()).add(round(float(size), 1))
    return [
        f"{role}: {', '.join(f'{s}px' for s in sorted(sizes))}"
        for role, sizes in sorted(seen.items())
        if len(sizes) > 1
    ]


def check_fill(report: dict) -> list[str]:
    """Return the pages whose copy does not fit, or is too thin to read.

    The cover is a fixed brand composition and the closing page is a
    centred notice, so neither is held to the reading-page fill band.
    """
    problems = []
    for entry in report["pages"]:
        if entry.get("kind") in {"cover", "backmatter"}:
            continue
        inner = entry["inner"]
        if not inner:
            continue
        ratio = entry["used"] / inner
        if ratio > MAX_FILL:
            problems.append(f"page {entry['index']} overflows ({ratio:.0%})")
        elif ratio < MIN_FILL:
            problems.append(f"page {entry['index']} is too thin ({ratio:.0%})")
    return problems


def build_pocket_html(doc: PocketDoc, foil: str | None = None) -> str:
    """Render the pocket edition to a complete A4 HTML document.

    ``foil`` is the URI of the rasterised wordmark for the cover. There is
    no per-page scale factor: the edition shares one type scale.
    """
    pages: list[str] = []
    folio = 0
    for page in doc.pages:
        if page.kind == "cover":
            pages.append(_cover_page(page, foil))
            continue
        folio += 1
        pages.append(_interior_page(page, folio))

    fonts = "\n".join(
        f"""@font-face {{
  font-family: '{family}';
  src: url('{(FONTS / filename).as_uri()}') format('woff2');
  font-weight: 400 700;
  font-style: {style};
  font-display: block;
}}"""
        for family, filename, style in (
            ("Fraunces", "FrauncesDisplay.woff2", "normal"),
            ("Fraunces", "FrauncesDisplayItalic.woff2", "italic"),
            ("Source Serif 4", "SourceSerifText.woff2", "normal"),
            ("Inter", "InterUI.woff2", "normal"),
        )
    )

    return f"""<!DOCTYPE html>
<html lang="ms">
<head>
<meta charset="utf-8" />
<title>{_e(doc.title.replace("*", ""))}</title>
<link rel="stylesheet" href="{TOKENS.as_uri()}" />
<style>
{fonts}
{_page_css()}
</style>
</head>
<body>
{''.join(pages)}
</body>
</html>
"""


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------


def find_chrome() -> str:
    for name in CHROME_CANDIDATES:
        found = shutil.which(name)
        if found:
            return found
    raise PocketError("No headless Chrome found. Install google-chrome or chromium.")


def render_foil_wordmark(wordmark: str, accent: str, output: Path) -> Path:
    """Rasterise the foil wordmark to a transparent PNG.

    Done in the screenshot path because that is where Chrome honours
    ``background-clip: text``. The print path drops it and prints the
    gradient as a band behind the letters.
    """
    chrome = find_chrome()
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    markup = FOIL_MARKUP % {
        "font": (FONTS / "FrauncesDisplay.woff2").as_uri(),
        "width": 1200,
        "wordmark_px": 104,
        "accent_px": 200,
        "wordmark": wordmark,
        "accent": accent,
    }

    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "foil.html"
        source.write_text(markup, encoding="utf-8")
        subprocess.run(
            [
                chrome,
                "--headless=new",
                "--no-sandbox",
                "--disable-gpu",
                "--hide-scrollbars",
                "--allow-file-access-from-files",
                "--default-background-color=00000000",
                "--force-device-scale-factor=2",
                "--virtual-time-budget=10000",
                f"--screenshot={output}",
                "--window-size=1200,400",
                source.as_uri(),
            ],
            capture_output=True,
            check=True,
            timeout=180,
        )

    if not output.exists() or output.stat().st_size == 0:
        raise PocketError("Chrome did not rasterise the foil wordmark.")
    return output


def render_pocket_pdf(doc: PocketDoc, output: Path) -> Path:
    """Write the pocket edition to an A4 PDF.

    The edition is set at one type scale, so rendering needs no per-page
    scale factors: the HTML that was measured is the HTML that prints.
    """
    chrome = find_chrome()
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        cover = next((p for p in doc.pages if p.kind == "cover"), None)
        foil_uri = None
        if cover is not None and cover.wordmark:
            foil = render_foil_wordmark(
                cover.wordmark, cover.wordmark_accent, Path(tmp) / "foil.png"
            )
            foil_uri = foil.as_uri()
        document = build_pocket_html(doc, foil_uri)
        source = Path(tmp) / "pocket.html"
        source.write_text(document, encoding="utf-8")
        subprocess.run(
            [
                chrome,
                "--headless=new",
                "--no-sandbox",
                "--disable-gpu",
                "--hide-scrollbars",
                "--allow-file-access-from-files",
                "--no-pdf-header-footer",
                "--virtual-time-budget=10000",
                f"--print-to-pdf={output}",
                source.as_uri(),
            ],
            capture_output=True,
            check=True,
            timeout=180,
        )

    if not output.exists() or output.stat().st_size == 0:
        raise PocketError("Chrome did not produce a PDF.")
    return output
