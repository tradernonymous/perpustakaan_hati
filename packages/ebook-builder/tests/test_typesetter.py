"""Tests for the typesetter.

The typesetter turns typed blocks into the branded interior HTML. It owns
three things the tests pin down:

  * the cover and title page are always the first two pages, in that order;
  * the cover carries the tier, title, subtitle and the byline, and the tier
    class selects the tier's colour (green / gold / burgundy);
  * every paid page carries the watermark stamp, and the buyer line appears
    only where the brand rule allows it.

Run:
    uv run --project packages/ebook-builder pytest packages/ebook-builder/tests -q
"""
from __future__ import annotations

from ebook_builder.manuscript import parse_markdown
from ebook_builder.typesetter import typeset
from ebook_builder.watermark import Buyer

MANUSCRIPT = """---
title: Edisi Poket
tier: poket
tagline: Teman hati sementara menunggu bas atau train.
---

# Kenapa Buku Ini

> Sekali baca, lama terasa.

Badan teks yang panjang.

---

## Skrip Bincang

### Saya mahu kata

Aku perlukan masa.

### Cara aku kata

Aku perlukan satu malam.
"""


def test_cover_is_the_first_page():
    html = typeset(parse_markdown(MANUSCRIPT), Buyer())
    assert html.index("layout-cover") < html.index("layout-title-page")


def test_cover_carries_the_title_and_subtitle():
    html = typeset(parse_markdown(MANUSCRIPT), Buyer())
    assert "Edisi Poket" in html
    assert "Teman hati sementara menunggu bas atau train." in html


def test_cover_uses_the_green_tier_class():
    html = typeset(parse_markdown(MANUSCRIPT), Buyer())
    assert "tier-free" in html


def test_gold_tier_uses_the_standard_class():
    doc = parse_markdown("---\ntitle: Edisi Membangun\ntier: membangun\n---\n\n# Satu\n")
    html = typeset(doc, Buyer())
    assert "tier-standard" in html


def test_burgundy_tier_uses_the_premium_class():
    doc = parse_markdown("---\ntitle: Teman Hidup\ntier: teman-hidup\n---\n\n# Satu\n")
    html = typeset(doc, Buyer())
    assert "tier-premium" in html


def test_unknown_tier_falls_back_to_the_free_class():
    doc = parse_markdown("---\ntitle: X\ntier: weird\n---\n\n# Satu\n")
    html = typeset(doc, Buyer())
    assert "tier-free" in html


def test_byline_is_present():
    html = typeset(parse_markdown(MANUSCRIPT), Buyer())
    assert "@rahimam" in html


def test_watermark_stamp_is_on_the_pages():
    html = typeset(parse_markdown(MANUSCRIPT), Buyer())
    assert "Cop Perpustakaan Hati" in html


def test_buyer_line_appears_when_a_buyer_is_given():
    html = typeset(parse_markdown(MANUSCRIPT), Buyer(name="Aisyah Rahman", email="a@example.com"))
    assert "Aisyah Rahman" in html


def test_anonymous_build_has_no_buyer_line():
    html = typeset(parse_markdown(MANUSCRIPT), Buyer())
    assert "Salinan Peribadi" not in html


def test_chapter_opener_is_rendered():
    html = typeset(parse_markdown(MANUSCRIPT), Buyer())
    assert "layout-chapter-opener" in html
    assert "Kenapa Buku Ini" in html


def test_pull_quote_is_rendered():
    html = typeset(parse_markdown(MANUSCRIPT), Buyer())
    assert "layout-pull-quote" in html


def test_script_rows_carry_their_column():
    html = typeset(parse_markdown(MANUSCRIPT), Buyer())
    assert "want" in html
    assert "how" in html


def test_body_html_is_inserted():
    html = typeset(parse_markdown(MANUSCRIPT), Buyer())
    assert "Badan teks yang panjang." in html


def test_the_result_is_a_complete_html_document():
    html = typeset(parse_markdown(MANUSCRIPT), Buyer())
    assert html.strip().startswith("<!DOCTYPE html>")
    assert "</html>" in html


def test_folios_are_numbered():
    html = typeset(parse_markdown(MANUSCRIPT), Buyer())
    assert 'class="folio"' in html


def test_the_buyer_line_is_confined_to_the_early_pages():
    html = typeset(parse_markdown(MANUSCRIPT), Buyer(name="Aisyah Rahman"))
    assert "@page:nth(2)" in html
    assert "@page:nth(6)" in html
    assert "@page:nth(7)" not in html
