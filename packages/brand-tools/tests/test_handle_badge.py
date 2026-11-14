"""The @rahimam handle: lowercase name, the "@" set in a rainbow-ring badge.

Brand reference is the lowercase "@rahimam" lockup: a lowercase word beside a
circular rainbow ring around a dark disc with a white @. The style is scoped to
the handle only, so every other kicker label stays uppercase gold.

Run:
    uv run --no-project --with pytest pytest packages/brand-tools/tests/test_handle_badge.py -q
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOKENS = ROOT / "docs" / "brand" / "design-tokens.css"
WEB = ROOT / "apps" / "web" / "styles" / "design-tokens.css"
SHEET = ROOT / "docs" / "brand" / "templates" / "design-system-3-sheet.html"


def tokens_css() -> str:
    return TOKENS.read_text(encoding="utf-8")


def test_rainbow_ring_token_is_a_conic_gradient() -> None:
    assert re.search(r"--rainbow-ring:\s*conic-gradient\(", tokens_css()), (
        "the rainbow ring must be a conic-gradient token"
    )


def test_handle_is_lowercase() -> None:
    assert re.search(r"\.ph-handle\s*\{[^}]*text-transform:\s*lowercase", tokens_css()), (
        ".ph-handle must set text-transform: lowercase"
    )


def test_at_badge_rings_a_dark_disc() -> None:
    css = tokens_css()
    assert re.search(r"\.ph-at\s*\{[^}]*var\(--rainbow-ring\)", css), (
        ".ph-at must paint the rainbow ring"
    )
    assert re.search(r"\.ph-at\s*\{[^}]*radial-gradient\((?:circle\s+)?closest-side", css), (
        ".ph-at must cut a dark disc inside the ring"
    )
    assert re.search(r"\.ph-at\s*\{[^}]*border-radius:\s*50%", css), (
        ".ph-at must be circular"
    )


def test_other_kickers_stay_uppercase() -> None:
    assert re.search(r"\.ph-kicker\s*\{[^}]*text-transform:\s*uppercase", tokens_css()), (
        "the handle change must not lowercase other kicker labels"
    )


def test_web_copy_matches_docs_copy() -> None:
    assert WEB.read_text(encoding="utf-8") == tokens_css()


def test_showcase_sheet_renders_the_handle() -> None:
    html = SHEET.read_text(encoding="utf-8")
    assert 'class="ph-handle"' in html, "the showcase sheet must render .ph-handle"
    assert 'class="ph-at"' in html, "the showcase sheet must render the .ph-at badge"