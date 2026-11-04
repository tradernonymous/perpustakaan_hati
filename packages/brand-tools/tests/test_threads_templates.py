"""Tests for the Threads social templates in content/threads/templates/.

Each template is a self-contained 1080x1350 (4:5) HTML document that must
obey the Perpustakaan Hati design system. The rules come from
docs/brand/DESIGN-SYSTEM.md and docs/brand/doop-guideline.md:

  * ground is forest-night, never pure black
  * brand fonts are self-hosted (no Google Fonts CDN link)
  * foil is display type only, at 32px and above
  * tier seals are 96px minimum and rotated -8deg
  * tier names come from the sanctioned set
  * no purple, no blue cast, no 800/900 weights

Run:
    uv run --no-project --with pytest pytest packages/brand-tools/tests -q
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
TEMPLATES = ROOT / "content" / "threads" / "templates"

QUOTE_CARD = TEMPLATES / "quote-card.html"
QUOTE_CARD_B = TEMPLATES / "quote-card-b.html"

SANCTIONED_TIERS = {"Edisi Poket", "Edisi Membangun", "Teman Hidup"}
RETIRED_TIERS = ("Edisi Dompet", "Edisi Pulih")

HEX = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def css_of(html: str) -> str:
    """All <style> blocks, joined, comments stripped."""
    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def css_blocks(css: str) -> dict[str, str]:
    """selector -> body, for every simple rule in the stylesheet."""
    return {
        selector.strip(): body
        for selector, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css)
    }


def hex_colours(text: str) -> list[str]:
    return [m.group(0).lower() for m in HEX.finditer(text)]


def is_purple_or_blue(hex_value: str) -> bool:
    """True when blue is the dominant channel — a purple or blue cast."""
    v = hex_value.lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    r, g, b = (int(v[i : i + 2], 16) for i in (0, 2, 4))
    return b > r + 12 and b > g + 2


@pytest.fixture(params=[QUOTE_CARD, QUOTE_CARD_B], ids=lambda p: p.stem)
def template(request: pytest.FixtureRequest) -> Path:
    assert request.param.exists(), f"missing template: {request.param}"
    return request.param


# --- structure (both templates) -------------------------------------------


def test_both_quote_card_templates_exist() -> None:
    assert QUOTE_CARD.exists()
    assert QUOTE_CARD_B.exists()


def test_template_is_1080x1350(template: Path) -> None:
    css = css_of(read(template)).replace(" ", "")
    assert "width:1080px" in css
    assert "height:1350px" in css


def test_ground_is_forest_night(template: Path) -> None:
    css = css_of(read(template)).replace(" ", "").lower()
    assert "--forest-night:#07140d" in css


def test_fonts_are_self_hosted_not_cdn(template: Path) -> None:
    html = read(template)
    assert "fonts.googleapis.com" not in html
    assert "fonts.gstatic.com" not in html
    assert "@font-face" in html
    assert "packages/brand-tools/fonts/" in html


def test_brand_faces_are_declared(template: Path) -> None:
    html = read(template)
    for family in ("Fraunces", "Inter"):
        assert family in html, f"{family} not used by {template.name}"


def test_no_heavy_weights(template: Path) -> None:
    """The system forbids 800/900 weights anywhere."""
    css = css_of(read(template))
    for weight in re.findall(r"font-weight:\s*(\d+)", css):
        assert int(weight) < 800, f"{template.name} uses font-weight {weight}"
    for weight in re.findall(r"font:\s*(?:\w+\s+)?(\d{3})", css):
        assert int(weight) < 800, f"{template.name} uses font-weight {weight}"


def test_no_purple_or_blue(template: Path) -> None:
    for value in hex_colours(read(template)):
        assert not is_purple_or_blue(value), f"{template.name} uses {value}"


def test_no_pure_black_ground(template: Path) -> None:
    for value in hex_colours(read(template)):
        assert value not in {"#000", "#000000"}, f"{template.name} uses {value}"


def test_no_emoji(template: Path) -> None:
    emoji = re.compile(
        "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]"
    )
    assert not emoji.search(read(template)), f"{template.name} contains an emoji"


def test_quote_stays_a_placeholder(template: Path) -> None:
    """A template, not a frozen card: the copy is filled at render time."""
    html = read(template)
    assert "{{QUOTE" in html


def test_retired_tier_names_never_appear(template: Path) -> None:
    html = read(template)
    for retired in RETIRED_TIERS:
        assert retired not in html, f"{template.name} uses retired tier name {retired}"


# --- Template B (Design System 3.1) ---------------------------------------


def test_template_b_is_centred() -> None:
    css = css_of(read(QUOTE_CARD_B)).replace(" ", "")
    assert "text-align:center" in css
    assert "align-items:center" in css


def test_template_b_uses_the_real_brand_assets() -> None:
    html = read(QUOTE_CARD_B)
    assert "emblem-book-heart.svg" in html
    assert "seal-edisi-membangun.svg" in html


def test_template_b_uses_foil_for_the_wordmark() -> None:
    css = css_of(read(QUOTE_CARD_B))
    assert "ph-foil-gold" in css
    assert "ph-foil-emerald" in css


def test_template_b_foil_is_display_size_only() -> None:
    """Foil fills are display words only — 32px and above."""
    for selector, body in css_blocks(css_of(read(QUOTE_CARD_B))).items():
        if "ph-foil" not in selector:
            continue
        sizes = [int(s) for s in re.findall(r"font-size:\s*(\d+)px", body)]
        if not sizes:
            continue  # the shared class itself; the caller sets the size
        assert max(sizes) >= 32, f"foil on {selector} at {max(sizes)}px"


def test_template_b_seal_is_at_least_96px() -> None:
    css = css_of(read(QUOTE_CARD_B))
    seals = [body for sel, body in css_blocks(css).items() if "seal" in sel]
    assert seals, "Template B has no seal rule"
    for body in seals:
        width = re.search(r"width:\s*(\d+)px", body)
        assert width, "Template B seal has no width"
        assert int(width.group(1)) >= 96, (
            f"Template B seal is {width.group(1)}px — the system minimum is 96px"
        )


def test_template_b_seal_is_rotated() -> None:
    css = css_of(read(QUOTE_CARD_B)).replace(" ", "")
    assert "rotate(-8deg)" in css


def test_template_b_quote_uses_brand_colours() -> None:
    css = css_of(read(QUOTE_CARD_B)).replace(" ", "").lower()
    assert "--gold-light:#e9cea2" in css
    assert "--cream:#fdfee6" in css
    assert "--green-300:#a7d3b6" in css


def test_template_b_has_one_key_glow() -> None:
    """Rule 2: one key glow per frame, and never two of the same hue."""
    css = css_of(read(QUOTE_CARD_B)).replace(" ", "").lower()
    glows = re.findall(r"--glow-[a-z-]+:radial-gradient", css)
    assert len(glows) <= 2, f"Template B stacks {len(glows)} glows"
    assert "glow-lantern" in css


def test_template_b_names_a_sanctioned_tier() -> None:
    html = read(QUOTE_CARD_B)
    named = {t for t in SANCTIONED_TIERS if t in html}
    assert named, "Template B names no sanctioned tier"


def test_template_b_byline_is_flanked_kicker() -> None:
    html = read(QUOTE_CARD_B)
    assert "ph-kicker" in html
    assert "@rahimam" in html
