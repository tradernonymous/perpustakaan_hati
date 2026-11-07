"""Tests for the per-buyer watermark engine.

The watermark is what stops a buyer from sharing their PDF. The brand rule
(docs/brand/ui-kit.md -> "Watermark") is:

  * every paid page carries "Cop Perpustakaan Hati" diagonally at -20 degrees,
    10% opacity, gold-deep, bottom-right;
  * a buyer line "<Nama Pembeli> · <email>" at 7pt and 14% opacity sits
    bottom-centre, but only on pages 2-6, so the spread still reads clean.

The visible-vs-invisible choice is settled: VISIBLE. It is the Malaysian
market standard and it is what the storefront's watermarkPdf already does.

The copy line must land on EVERY page, so it uses a paged-media margin box
rather than a per-section element. The buyer line uses @page:nth() so it can
be confined to pages 2-6 without knowing the page count.

Run:
    uv run --project packages/ebook-builder pytest packages/ebook-builder/tests -q
"""
from __future__ import annotations

import pytest

from ebook_builder.watermark import Buyer, Watermark, build_watermark_css, watermark_label


def test_buyer_formats_the_label():
    label = watermark_label(Buyer(name="Aisyah Rahman", email="aisyah@example.com"))
    assert label == "Aisyah Rahman · aisyah@example.com"


def test_buyer_without_email_uses_name_only():
    assert watermark_label(Buyer(name="Aisyah Rahman")) == "Aisyah Rahman"


def test_buyer_without_name_uses_email_only():
    assert watermark_label(Buyer(email="aisyah@example.com")) == "aisyah@example.com"


def test_anonymous_buyer_has_a_neutral_label():
    label = watermark_label(Buyer())
    assert label == "Salinan Peribadi"


def test_buyer_rejects_a_name_with_markup():
    with pytest.raises(ValueError):
        Buyer(name="<script>x</script>")


def test_buyer_rejects_an_email_with_markup():
    with pytest.raises(ValueError):
        Buyer(email="a@b.com\" onload=\"x")


def test_watermark_css_uses_the_brand_angle_and_opacity():
    css = build_watermark_css(Watermark(copy_line="Cop Perpustakaan Hati"))
    assert "-20deg" in css
    assert "0.1" in css


def test_copy_line_sits_in_a_margin_box_so_it_repeats_on_every_page():
    css = build_watermark_css(Watermark(copy_line="Cop Perpustakaan Hati"))
    assert "@page" in css
    assert "@bottom-right" in css


def test_watermark_css_omits_the_buyer_line_when_there_is_no_buyer():
    css = build_watermark_css(Watermark(copy_line="Cop Perpustakaan Hati"))
    assert "buyer" not in css.lower()


def test_watermark_css_includes_the_buyer_line_when_there_is_one():
    css = build_watermark_css(
        Watermark(copy_line="Cop Perpustakaan Hati", buyer_label="Aisyah Rahman · a@example.com")
    )
    assert "Aisyah Rahman" in css


def test_buyer_line_is_limited_to_the_early_pages():
    css = build_watermark_css(
        Watermark(copy_line="Cop Perpustakaan Hati", buyer_label="Aisyah Rahman", buyer_pages=(2, 6))
    )
    for page in range(2, 7):
        assert f"@page:nth({page})" in css
    assert "@page:nth(1)" not in css
    assert "@page:nth(7)" not in css


def test_buyer_line_escapes_quotes():
    css = build_watermark_css(Watermark(buyer_label="O'Brien"))
    assert "O\\'Brien" in css


def test_buyer_line_escapes_backslashes():
    css = build_watermark_css(Watermark(buyer_label=r"a\b"))
    assert "a\\\\b" in css
