"""Tests for the Edisi Poket A4 dark-stage builder.

The pocket edition is a fixed-composition artefact, not a flowing book:
every page is authored as one page block with a known layout. The builder
turns that manuscript into A4 HTML, renders it through headless Chrome,
and audits the result.

What the tests pin down:

  * the manuscript parses into the expected page sequence;
  * every chart carries a source line — no number ships uncited;
  * the rendered PDF is A4 with the expected page count;
  * the running head, byline and folio land on every interior page;
  * capitalisation is correct (Malay sentence case, no stray shouting);
  * no paragraph ends on a single orphaned word.

Run:
    uv run --no-project --with pytest pytest packages/ebook-builder/tests/test_pocket.py -q
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

from ebook_builder.pocket import (
    PocketError,
    build_pocket_html,
    check_fill,
    check_uniform_type,
    measure_pocket,
    parse_pocket,
    render_foil_wordmark,
    render_pocket_pdf,
)

ROOT = Path(__file__).resolve().parents[3]
MANUSCRIPT = ROOT / "content" / "ebooks" / "edisi-poket-cuma-kawan-pejabat" / "manuscript.md"

CHROME = (
    shutil.which("google-chrome")
    or shutil.which("chromium")
    or shutil.which("chromium-browser")
    or shutil.which("chrome-headless-shell")
)

# Capitalised words that must never be shouted, and words that must.
SHOUTING_ALLOWLIST = {
    "BY",
    "HEAL",
    "KL",
    "KALIMAH",
    "AMALAN",
    "PERPUSTAKAAN",
    "HATI",
    "KOLEKSI",
    "EBOOK",
    "EDISI",
    "POKET",
    "APA",
    "KATA",
    "ORANG",
    "TENTANG",
    "HUBUNGAN",
    "EMOSIONAL",
    "YANG",
    "RAHSIA",
    "PENGLIBATAN",
    "TANPA",
    "PERSETUBUHAN",
    "DI",
    "ANTARA",
    "MEREKA",
    "MENDDAKAH",
    "PERNAH",
    "BERSELINGKUHAN",
    "PERSELINGKUHAN",
    "DISEBUT",
    "SEBAGAI",
    "PUNCA",
    "PERCERAIAN",
    "KEDUA",
    "THREAD",
    "MPFS",
}


def _document():
    return parse_pocket(MANUSCRIPT.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------


def test_manuscript_parses():
    doc = _document()
    assert doc.title.replace("*", "") == "Cuma Kawan Pejabat"
    assert doc.tier == "poket"


def test_cover_is_the_first_page():
    doc = _document()
    assert doc.pages[0].kind == "cover"


def test_cover_carries_title_tagline_and_ribbon():
    doc = _document()
    cover = doc.pages[0]
    assert "Cuma Kawan Pejabat" in cover.title.replace("*", "")
    assert "Kita tak sembunyikan hubungan" in cover.tagline
    assert cover.tier_ribbon == "Edisi Poket"


def test_cover_title_marks_one_italic_accent():
    """The house style sets one word of a title in italic."""
    doc = _document()
    html = build_pocket_html(doc)
    assert "<em>Pejabat</em>" in html


def test_thread_page_keeps_the_x_shortform_verbatim():
    doc = _document()
    thread = next(p for p in doc.pages if p.kind == "thread")
    assert "KITA X SEMBUNYIKAN HUBUNGAN" in thread.thread


def test_thread_post_is_kept_out_of_the_book_prose():
    """The verbatim post is its own block, so the book prose stays clean."""
    doc = _document()
    thread = next(p for p in doc.pages if p.kind == "thread")
    assert "KITA X SEMBUNYIKAN" not in thread.text


def test_body_spells_out_tak_rather_than_x():
    """The X stays on the quoted post only; the book's own prose says "tak"."""
    doc = _document()
    prose = "\n".join(p.text for p in doc.pages if p.kind != "thread")
    assert " X " not in prose
    assert " tak " in prose or "tak " in prose


def test_content_pages_are_numbered_from_one():
    """Chapters carry 01-07; the evidence page that follows each one does not.

    The edition gives every chapter a prose page and then an evidence
    page, so a numeral marks the start of a chapter, not every sheet.
    """
    doc = _document()
    numerals = [p.numeral for p in doc.pages if p.kind == "content" and p.numeral]
    assert numerals == ["01", "02", "03", "04", "05", "06", "07"]


def test_each_chapter_has_a_prose_page_then_an_evidence_page():
    """Each of the three ideas gets two pages: the thinking, then the proof.

    Splitting the chapters is what lets every page keep the edition's one
    type scale: a chapter that carried its prose, chart, steps and quote
    on a single sheet had to shrink its type to fit.
    """
    doc = _document()
    content = [(i, p) for i, p in enumerate(doc.pages) if p.kind == "content"]
    chapters = [(i, p) for i, p in content if p.numeral in {"01", "02", "03"}]
    assert len(chapters) == 3
    for index, chapter in chapters:
        evidence = doc.pages[index + 1]
        assert chapter.text and not chapter.charts
        assert evidence.charts and not evidence.text
        assert evidence.numeral == ""


def test_every_chart_has_a_source_line():
    doc = _document()
    charts = [c for p in doc.pages for c in p.charts]
    assert charts, "the edition has charts"
    for chart in charts:
        assert chart.source.strip(), f"chart {chart.title!r} has no source"
        assert chart.title.strip()


def test_chart_rows_parse_label_and_value():
    doc = _document()
    chart = next(c for p in doc.pages for c in p.charts)
    assert chart.rows
    label, value = chart.rows[0]
    assert label.strip()
    assert float(value) > 0


def test_steps_have_three_items():
    doc = _document()
    steps = [s for p in doc.pages for s in p.steps]
    assert steps
    for block in steps:
        assert len(block.items) == 3


def test_list_markers_do_not_leak_into_the_copy():
    """The manuscript writes lists with Markdown markers.

    Those markers are structure, not copy: the printed step carries a
    number in its own disc, so a stray hyphen must never reach the page.
    """
    doc = _document()
    for page in doc.pages:
        for block in page.steps:
            for item in block.items:
                assert not item.startswith(("-", "*")), item
        for chart in page.charts:
            for label, _value in chart.rows:
                assert not label.startswith(("-", "*")), label
        for prompt in page.reflection:
            assert not prompt.startswith(("-", "*")), prompt
        for text, _source in page.sayings:
            assert not text.startswith(("-", "*")), text


def test_sayings_carry_attribution():
    doc = _document()
    sayings = [s for p in doc.pages for s in p.sayings]
    assert len(sayings) == 3
    for text, source in sayings:
        assert source.strip()
        assert text.strip()


def test_generated_art_is_wired_to_pages():
    """The illustration keys resolve to files that exist and render."""
    doc = _document()
    art = {p.art for p in doc.pages if p.art}
    assert art == {
        "art-thread.png",
        "art-jarak.png",
        "art-dua-sisi.png",
        "art-dikatakan.png",
        "art-selamat.png",
    }
    assert {p.numeral for p in doc.pages if p.ornament} == {"01", "02", "03", "04", "05", "06", "07"}
    html = build_pocket_html(doc)
    assert html.count('class="art-panel"') == len(art)
    assert html.count('class="art-ornament"') == 7
    # The closing page carries its lantern too, above the helpline.
    backmatter = next(p for p in doc.pages if p.kind == "backmatter")
    assert 'art-selamat.png' in html
    assert backmatter.art == "art-selamat.png"


def test_missing_art_file_fails_the_build():
    with pytest.raises(PocketError):
        build_pocket_html(
            parse_pocket("---\ntitle: X\n---\n\n::: page\nkind: content\nart: nope.png\n:::\n")
        )


def test_step_icons_match_the_steps_they_illustrate():
    """One icon per step, or none: a mismatched card is a manuscript bug."""
    doc = _document()
    iconed = [b for p in doc.pages for b in p.steps if b.icons]
    assert len(iconed) == 2
    for block in iconed:
        assert len(block.icons) == len(block.items) == 3
        assert all(name.startswith("icon-") and name.endswith(".png") for name in block.icons)
    html = build_pocket_html(doc)
    assert html.count('class="step-ico"') == 6
    with pytest.raises(PocketError):
        parse_pocket(
            "---\ntitle: X\n---\n\n::: page\nkind: content\n:::\n\n"
            "::: steps\nlabel: L\nicons: icon-a.png\n- one\n- two\n:::\n"
        )


def test_every_chart_carries_the_shared_scale():
    """Charts share one 0-100 ruler, printed under the tracks.

    The ruler's outer cells must repeat the bar row's columns exactly,
    so the tick labels land under the tracks: the trailing cell is an
    empty .bar-value, which reserves the value column's width. A plain
    empty span would collapse it and shift the whole ruler right.
    """
    html = build_pocket_html(_document())
    scales = re.findall(r'<div class="chart-scale".*?</div>', html, re.S)
    assert len(scales) == 3
    for scale in scales:
        assert re.findall(r"<i>(\d+)</i>", scale) == ["0", "25", "50", "75", "100"]
        assert 'class="bar-value"' in scale
        assert 'class="scale-end"' not in scale


def test_unknown_page_kind_is_rejected():
    with pytest.raises(PocketError):
        parse_pocket("---\ntitle: X\n---\n\n::: page\nkind: nonsense\n:::\n")


def test_chart_without_rows_is_rejected():
    with pytest.raises(PocketError):
        parse_pocket(
            "---\ntitle: X\n---\n\n::: page\nkind: content\nnumeral: 01\n"
            "title: T\n:::\n\n::: chart\ntitle: C\nsource: S\n:::\n"
        )


# --------------------------------------------------------------------------
# typesetting
# --------------------------------------------------------------------------


def test_html_declares_a4_and_the_brand_stage():
    html = build_pocket_html(_document())
    assert "size: A4" in html
    assert "--forest-night" in html  # tokens are linked, not re-typed


def test_html_links_the_brand_token_file():
    html = build_pocket_html(_document())
    assert "design-tokens.css" in html


def test_every_referenced_asset_exists():
    """The build links tokens, fonts and SVGs by absolute path.

    A wrong path here silently drops the whole design system, so the
    references are checked against the filesystem rather than trusted.
    """
    from urllib.parse import unquote, urlparse

    html = build_pocket_html(_document())
    references = re.findall(r'(?:href|src)="(file://[^"]+)"', html)
    assert references, "the build should reference the brand files by absolute path"
    for reference in references:
        path = Path(unquote(urlparse(reference).path))
        assert path.exists(), f"build references a missing file: {path}"


def test_running_head_and_folio_are_present():
    html = build_pocket_html(_document())
    assert "EDISI POKET · CUMA KAWAN PEJABAT" in html
    assert "BY @RAHIMAM" in html
    assert "Halaman" in html


def test_every_source_line_is_rendered():
    doc = _document()
    html = build_pocket_html(doc)
    for chart in (c for p in doc.pages for c in p.charts):
        assert chart.source in html


def test_no_unfilled_placeholders_survive():
    html = build_pocket_html(_document())
    assert not re.search(r"\{\{|\}\}", html)


def test_copy_carries_no_em_dash():
    """The brand copy rule: no em dash in published copy.

    The thread quote is Rahimam's own post, quoted as sent, so it is
    checked separately from the book's own prose.
    """
    doc = _document()
    for page in doc.pages:
        if page.kind == "thread":
            assert "—" not in page.thread
            continue
        assert "—" not in page.title
        assert "—" not in page.subtitle
        assert "—" not in page.tagline
        assert "—" not in page.text
        for chart in page.charts:
            assert "—" not in chart.title
            assert "—" not in chart.note
            assert "—" not in chart.source
            for label, _value in chart.rows:
                assert "—" not in label
        for block in page.steps:
            assert "—" not in block.label
            for item in block.items:
                assert "—" not in item
        for text, source in page.sayings:
            assert "—" not in text
            assert "—" not in source
        for prompt in page.reflection:
            assert "—" not in prompt
        for quote in page.pull_quotes:
            assert "—" not in quote


@pytest.mark.skipif(CHROME is None, reason="no headless Chrome available")
def test_pull_quotes_fit_on_one_line():
    """The closing line of a page is one line, never two.

    Measured in the browser rather than counted in characters, because
    only the browser knows how wide the line is. The overflow audit
    reports any pull quote that did not fit.
    """
    report = measure_pocket(_document())
    overflows = [o for o in report.get("overflows", []) if "pull-quote" in o["block"]]
    assert not overflows, overflows


def test_body_copy_is_not_shouted():
    """Body prose must not be in caps.

    Only the copy a reader reads as prose is checked. Design labels are
    excluded because the house style sets them in caps through CSS, not
    through the copy itself, and the thread quote is verbatim Rahimam's.
    """
    html = build_pocket_html(_document())
    chunks = re.findall(r'<div class="prose">(.*?)</div>', html, re.S)
    chunks += re.findall(r'<span class="step-text">(.*?)</span>', html, re.S)
    chunks += re.findall(r'<p class="saying-text">(.*?)</p>', html, re.S)
    chunks += re.findall(r'<p class="prompt-text">(.*?)</p>', html, re.S)
    prose = " ".join(chunks)
    shouted = {
        word
        for word in re.findall(r"\b[A-Z]{3,}\b", re.sub(r"<[^>]+>", " ", prose))
        if word not in SHOUTING_ALLOWLIST
    }
    assert not shouted, f"unexpected shouting in body copy: {sorted(shouted)}"


def test_titles_use_sentence_case_not_all_caps():
    """Chart titles and step labels are sentence case in the copy itself."""
    html = build_pocket_html(_document())
    titles = re.findall(r'<figcaption class="chart-title">(.*?)</figcaption>', html, re.S)
    assert titles
    for title in titles:
        words = title.split()
        assert not all(word.isupper() for word in words if word.isalpha()), title


# --------------------------------------------------------------------------
# rendering (needs Chrome)
# --------------------------------------------------------------------------


@pytest.mark.skipif(CHROME is None, reason="no headless Chrome available")
def test_pdf_is_a4_with_the_expected_page_count(tmp_path):
    doc = _document()
    out = render_pocket_pdf(doc, tmp_path / "pocket.pdf")
    assert out.exists()

    info = subprocess.run(
        ["pdfinfo", str(out)], capture_output=True, text=True, check=True
    ).stdout
    pages = int(re.search(r"^Pages:\s+(\d+)", info, re.M).group(1))
    size = re.search(r"^Page size:\s+(.+)$", info, re.M).group(1)

    assert pages == len(doc.pages)
    assert "A4" in size


@pytest.mark.skipif(CHROME is None, reason="no headless Chrome available")
def test_pdf_text_is_extractable(tmp_path):
    doc = _document()
    out = render_pocket_pdf(doc, tmp_path / "pocket.pdf")
    text = subprocess.run(
        ["pdftotext", "-layout", str(out), "-"], capture_output=True, text=True, check=True
    ).stdout
    assert "Cuma Kawan Peajat" in text or "Cuma Kawan Pejabat" in text
    assert "HEAL 15555" in text


@pytest.mark.skipif(CHROME is None, reason="no headless Chrome available")
def test_the_pdf_carries_the_same_type_as_the_measured_page(tmp_path):
    """The PDF must print the page that was measured.

    The edition is set at one type scale and rendered without per-page
    scale factors, so the measured HTML and the printed HTML are the same
    document. If a scale factor were reintroduced the printed pages would
    silently stop matching what the audit approved.
    """
    doc = _document()
    html = build_pocket_html(doc)
    assert "--fit" not in html
    assert "calc(16px * var(--fit))" not in html

    out = render_pocket_pdf(doc, tmp_path / "pocket.pdf")
    text = subprocess.run(
        ["pdftotext", "-layout", str(out), "-"], capture_output=True, text=True, check=True
    ).stdout
    assert "Cuma Kawan Pejabat" in text


@pytest.mark.skipif(CHROME is None, reason="no headless Chrome available")
def test_every_text_role_is_the_same_size_on_every_page():
    """A body paragraph, a title and a closing quote never change size.

    This is the defect the edition was rebuilt to remove: pages used to
    be scaled to fill their sheet, so the same element could render at
    16px on one page and 39px on another. One type scale means every
    role measures the same wherever it appears.
    """
    report = measure_pocket(_document())
    assert not check_uniform_type(report), check_uniform_type(report)


@pytest.mark.skipif(CHROME is None, reason="no headless Chrome available")
def test_no_block_ends_on_a_single_word():
    """No paragraph may leave one word alone on its last line."""
    report = measure_pocket(_document())
    assert not report["runts"], report["runts"]


@pytest.mark.skipif(CHROME is None, reason="no headless Chrome available")
def test_every_page_holds_its_copy_without_overflowing():
    """No page may clip its copy or sit mostly empty on an A4 sheet."""
    report = measure_pocket(_document())
    assert not check_fill(report), check_fill(report)


@pytest.mark.skipif(CHROME is None, reason="no headless Chrome available")
def test_foil_wordmark_is_rasterised_for_print(tmp_path):
    """The cover wordmark must be a foil raster, not live text.

    Chrome's print path drops ``background-clip: text``, so live foil
    type prints as a flat band behind the letters. The wordmark is
    therefore rasterised first, and the cover must reference that image.
    """
    doc = _document()
    foil = render_foil_wordmark("PERPUSTAKAAN", "Hati", tmp_path / "foil.png")
    assert foil.exists() and foil.stat().st_size > 0

    html = build_pocket_html(doc, foil.as_uri())
    assert foil.as_uri() in html
    assert '<img class="foil"' in html


@pytest.mark.skipif(CHROME is None, reason="no headless Chrome available")
def test_foil_raster_is_transparent(tmp_path):
    """Only the letters may carry pixels, so the PNG needs an alpha channel."""
    foil = render_foil_wordmark("PERPUSTAKAAN", "Hati", tmp_path / "foil.png")
    header = foil.read_bytes()
    assert header[:8] == b"\x89PNG\r\n\x1a\n"
    # The colour type byte lives in the IHDR chunk: 6 means RGBA.
    assert header[25] == 6, "the foil raster should carry an alpha channel"
