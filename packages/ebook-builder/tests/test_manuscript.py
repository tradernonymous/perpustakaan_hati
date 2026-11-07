"""Tests for the manuscript parser.

A manuscript is a Markdown file with optional YAML-ish front matter. The
parser's job is to turn it into a list of typed blocks that the typesetter
can lay out. Every block maps to exactly one of the brand's master layouts
(docs/brand/ui-kit.md -> "Master layouts"), so the typesetter never has to
guess.

Run:
    uv run --project packages/ebook-builder pytest packages/ebook-builder/tests -q
"""
from __future__ import annotations

import pytest

from ebook_builder.manuscript import (
    Block,
    BlockKind,
    Manuscript,
    ManuscriptError,
    parse_markdown,
)


def test_front_matter_is_parsed_into_metadata():
    doc = parse_markdown(
        "---\n"
        "title: Edisi Poket\n"
        "tier: poket\n"
        "tagline: Teman hati sementara menunggu bas atau train.\n"
        "---\n\n"
        "# Satu\n\nBadan teks.\n"
    )
    assert doc.meta["title"] == "Edisi Poket"
    assert doc.meta["tier"] == "poket"
    assert doc.meta["tagline"].startswith("Teman hati")


def test_missing_front_matter_yields_empty_metadata():
    doc = parse_markdown("# Tanpa front matter\n")
    assert doc.meta == {}
    assert doc.blocks


def test_heading_becomes_chapter_opener():
    doc = parse_markdown("# Kenapa hubungan sakit\n\nTeks.\n")
    opener = doc.blocks[0]
    assert opener.kind is BlockKind.CHAPTER_OPENER
    assert opener.title == "Kenapa hubungan sakit"


def test_paragraphs_become_body_blocks():
    doc = parse_markdown("Paragraf pertama.\n\nParagraf kedua.\n")
    kinds = [b.kind for b in doc.blocks]
    assert kinds == [BlockKind.BODY, BlockKind.BODY]
    assert "Paragraf pertama." in doc.blocks[0].text


def test_blockquote_becomes_pull_quote():
    doc = parse_markdown("> Tulisian yang memulihkan.\n")
    assert doc.blocks[0].kind is BlockKind.PULL_QUOTE
    assert "Tulisian" in doc.blocks[0].text


def test_list_becomes_body_with_list_html():
    doc = parse_markdown("- Satu\n- Dua\n")
    block = doc.blocks[0]
    assert block.kind is BlockKind.BODY
    assert "<ul>" in block.text


def test_hrule_becomes_page_break():
    doc = parse_markdown("Satu.\n\n---\n\nDua.\n")
    assert BlockKind.PAGE_BREAK in [b.kind for b in doc.blocks]


def test_fenced_code_block_is_preserved():
    doc = parse_markdown("```\nkata\n```\n")
    assert doc.blocks[0].kind is BlockKind.BODY
    assert "<pre>" in doc.blocks[0].text


def test_special_sections_map_to_their_own_layouts():
    doc = parse_markdown(
        "## Skrip Bincang\n\n"
        "### Saya mahu kata\n\nAku perlukan masa.\n\n"
        "### Cara aku kata\n\nAku perlukan satu malam.\n"
    )
    kinds = [b.kind for b in doc.blocks]
    assert BlockKind.SCRIPT_ROW in kinds
    assert BlockKind.SCRIPT_ROW in kinds


def test_worksheet_section_is_detected_by_its_heading():
    doc = parse_markdown("## Buku Kerja\n\n### Hari 1\n\nTulis satu perkara.\n")
    assert any(b.kind is BlockKind.WORKSHEET for b in doc.blocks)


def test_reflection_card_is_detected_by_its_marker():
    doc = parse_markdown("::: card\nKad Refleksi · HATI\n:::\n")
    assert doc.blocks[0].kind is BlockKind.REFLECTION_CARD


def test_back_matter_is_detected_by_its_marker():
    doc = parse_markdown("::: backmatter\nTalian HEAL 15555\n:::\n")
    assert doc.blocks[0].kind is BlockKind.BACK_MATTER


def test_unknown_fence_marker_is_an_error():
    with pytest.raises(ManuscriptError):
        parse_markdown("::: nonsense\napa\n:::\n")


def test_unterminated_fence_is_an_error():
    with pytest.raises(ManuscriptError):
        parse_markdown("::: card\nKad Refleksi\n")


def test_manuscript_metadata_helpers():
    doc = parse_markdown("---\ntitle: Edisi Membangun\ntier: membangun\n---\n\n# Satu\n")
    assert isinstance(doc, Manuscript)
    assert doc.title == "Edisi Membangun"
    assert doc.tier == "membangun"


def test_block_dataclass_carries_its_payload():
    block = Block(kind=BlockKind.BODY, text="hello")
    assert block.kind is BlockKind.BODY
    assert block.text == "hello"
