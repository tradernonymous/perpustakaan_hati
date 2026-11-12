"""Copy rules for the brand, checked against the published surfaces.

The rules come from docs/brand/DESIGN-SYSTEM.md -> "Copy rules". The one
that has to be enforced mechanically is the em dash: it is easy to reintroduce
in a heading or a chart row, and it reads as imported English punctuation in
Malay copy.

This checks reader-facing text only. Code comments, CSS comments and SVG
source comments are not copy, so they are stripped before the scan.

Run:
    uv run --no-project --with pytest pytest packages/brand-tools/tests/test_copy_rules.py -q
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]

EM_DASH = "—"

# Published copy: the surfaces a reader sees.
COPY_FILES = [
    ROOT / "content" / "ebooks" / "edisi-poket-cuma-kawan-pejabat" / "manuscript.md",
    ROOT / "content" / "ebooks" / "tier-1-free" / "outline.md",
    ROOT / "content" / "ebooks" / "tier-2-standard" / "chapters.md",
    ROOT / "content" / "ebooks" / "tier-2-standard" / "manuscript" / "edisi-membangun.md",
    ROOT / "content" / "ebooks" / "tier-3-premium" / "bundle.md",
    ROOT / "content" / "ebooks" / "tier-3-premium" / "manuscript" / "teman-hidup.md",
    ROOT / "apps" / "web" / "src" / "content.ts",
    ROOT / "apps" / "web" / "src" / "games" / "nurture.ts",
    ROOT / "apps" / "web" / "src" / "games" / "workbook.ts",
]

# The Threads templates and the eBook interior are copy in HTML form.
HTML_COPY = [
    ROOT / "content" / "threads" / "templates" / "quote-card.html",
    ROOT / "content" / "threads" / "templates" / "quote-card-b.html",
    ROOT / "content" / "threads" / "templates" / "quote-card-c.html",
    ROOT / "content" / "threads" / "templates" / "carousel.html",
    ROOT / "packages" / "ebook-builder" / "templates" / "ebook-interior.html",
]

# The locked tier subcopy lives here and is asserted by the web tests.
LOCKED_COPY = [
    (ROOT / "docs" / "brand" / "tier-naming.md", "Bacaan, kerja, dan skrip, teman hidup."),
]


def _strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def _strip_code_comments(text: str) -> str:
    """Remove JS, TS and CSS comments, keeping string literals intact."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"^\s*//.*$", "", text, flags=re.M)
    return text


def _string_literals(text: str) -> list[str]:
    """Every quoted string in the file, which is where copy lives."""
    return re.findall(r'"([^"\n]*)"|\'([^\'\n]*)\'', text)


@pytest.mark.parametrize("path", COPY_FILES, ids=lambda p: p.name)
def test_markdown_copy_has_no_em_dash(path: Path):
    if not path.exists():
        pytest.skip(f"{path.name} is not present")
    text = path.read_text(encoding="utf-8")
    assert EM_DASH not in text, f"{path.name} uses the em dash; the brand copy rule forbids it"


@pytest.mark.parametrize("path", HTML_COPY, ids=lambda p: p.name)
def test_html_copy_has_no_em_dash(path: Path):
    if not path.exists():
        pytest.skip(f"{path.name} is not present")
    text = _strip_html_comments(path.read_text(encoding="utf-8"))
    assert EM_DASH not in text, f"{path.name} uses the em dash; the brand copy rule forbids it"


@pytest.mark.parametrize("path", COPY_FILES, ids=lambda p: p.name)
def test_typescript_copy_has_no_em_dash(path: Path):
    if not path.exists():
        pytest.skip(f"{path.name} is not present")
    text = _strip_code_comments(path.read_text(encoding="utf-8"))
    for group in _string_literals(text):
        literal = group[0] or group[1]
        assert EM_DASH not in literal, f"{path.name} has the em dash in a string: {literal!r}"


def test_locked_tier_subcopy_is_em_dash_free():
    """The Teman Hidup subcopy is locked copy, so it carries the rule too."""
    path, expected = LOCKED_COPY[0]
    text = path.read_text(encoding="utf-8")
    assert expected in text, "the locked subcopy changed; update the file and the web test"
    assert EM_DASH not in expected


def test_storefront_tier_subcopy_matches_the_brand_doc():
    """apps/web and the brand doc must say the same thing."""
    doc = (ROOT / "docs" / "brand" / "tier-naming.md").read_text(encoding="utf-8")
    web = (ROOT / "apps" / "web" / "src" / "content.ts").read_text(encoding="utf-8")
    expected = "Bacaan, kerja, dan skrip, teman hidup."
    assert expected in doc
    assert expected in web


def test_copy_rules_are_documented():
    """The rule has to live in the design system, or nobody will follow it."""
    system = (ROOT / "docs" / "brand" / "DESIGN-SYSTEM.md").read_text(encoding="utf-8")
    assert "Copy rules" in system
    assert "em dash" in system
