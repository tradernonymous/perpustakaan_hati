"""Phase 1 — shared foundations: scoped ebook-tier tokens, motion tokens,
canonical/generated sync, and the review specimen sheet.

These tests pin the Phase 1 contract from
`docs/superpowers/plans/2026-11-19-brand-storefront-research-ebook-video-upgrade.md`:

  * the two design-token CSS copies stay byte-identical;
  * every tier gets an *ebook-scoped* token group (page ground, ink,
    heading, rule, ornament, reflection field) declared inside a scoped
    class, so a white Edisi Membangun PDF can never turn the storefront
    white;
  * motion roles (feedback / entrance / scene) exist with a
    reduced-motion equivalent;
  * `docs/brand/design-tokens.json` declares the same version and token
    groups as the CSS;
  * a specimen sheet exists and shows the required component states and
    all three tier specimens, using design tokens only (no raw hex);
  * the new tier token pairs meet WCAG contrast on their own grounds.

Run:
    uv run --no-project --with pytest --with fonttools --with brotli \
        pytest packages/brand-tools/tests/test_phase1_foundations.py -q
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent.parent
ROOT = HERE.parents[1]
TOKENS = ROOT / "docs" / "brand" / "design-tokens.css"
WEB_TOKENS = ROOT / "apps" / "web" / "styles" / "design-tokens.css"
TOKENS_JSON = ROOT / "docs" / "brand" / "design-tokens.json"
SPECIMEN = ROOT / "docs" / "brand" / "specimens" / "foundations.html"

TIERS = ("poket", "membangun", "teman-hidup")
EBOOK_ROLES = ("page", "ink", "heading", "rule", "ornament", "field", "field-ink", "wash")
MOTION_TOKENS = (
    "motion-feedback-dur",
    "motion-feedback-ease",
    "motion-entrance-dur",
    "motion-entrance-ease",
    "motion-scene-dur",
    "motion-scene-ease",
    "motion-reduced-dur",
)
SPECIMEN_SECTIONS = (
    "book-depth",
    "buttons",
    "forms",
    "navigation",
    "cards",
    "dialogs",
    "states-loading",
    "states-empty",
    "states-success",
    "states-error",
)


def css_text() -> str:
    return TOKENS.read_text(encoding="utf-8")


def token_value(css: str, name: str) -> str | None:
    """Resolve one token, following a single level of var() indirection."""
    m = re.search(rf"--{re.escape(name)}:\s*([^;]+);", css)
    if not m:
        return None
    value = m.group(1).strip()
    ref = re.fullmatch(r"var\((--[a-z0-9-]+)\)", value)
    if ref:
        m2 = re.search(rf"--{ref.group(1)[2:]}:\s*([^;]+);", css)
        if m2:
            return m2.group(1).strip()
    return value


# --------------------------------------------------------------------------
# token declarations
# --------------------------------------------------------------------------


def test_canonical_declares_scoped_ebook_tier_tokens() -> None:
    css = css_text()
    for tier in TIERS:
        for role in EBOOK_ROLES:
            assert f"--ebook-{tier}-{role}:" in css, (
                f"missing --ebook-{tier}-{role} in docs/brand/design-tokens.css"
            )


def test_ebook_tier_tokens_are_scoped_not_global() -> None:
    """Tier ebook tokens must live inside a scoped class, never in :root.

    A white Edisi Membangun ground must not leak into the storefront.
    """
    css = css_text()
    for tier in TIERS:
        scoped = re.search(
            rf"\.ph-ebook-{tier}\s*\{{[^}}]*--ebook-{tier}-page:", css
        )
        assert scoped, f".ph-ebook-{tier} scope block with --ebook-{tier}-page not found"
    # the scoped blocks must not be declared on :root or html/body
    root_block = re.search(r":root\s*\{([^}]*)\}", css)
    assert root_block, ":root block not found"
    assert "--ebook-poket-page" not in root_block.group(1)
    assert "--ebook-membangun-page" not in root_block.group(1)
    assert "--ebook-teman-hidup-page" not in root_block.group(1)


def test_motion_role_tokens_declared() -> None:
    css = css_text()
    for name in MOTION_TOKENS:
        assert f"--{name}:" in css, f"missing --{name} in design-tokens.css"


def test_reduced_motion_zeroes_motion_durations() -> None:
    css = css_text()
    block = re.search(
        r"@media \(prefers-reduced-motion: reduce\)\s*\{\s*:root\s*\{([^}]*)\}", css
    )
    assert block, "prefers-reduced-motion :root block not found"
    body = block.group(1)
    for name in ("motion-feedback-dur", "motion-entrance-dur", "motion-scene-dur"):
        m = re.search(rf"--{name}:\s*([^;]+);", body)
        assert m, f"--{name} not zeroed under prefers-reduced-motion"
        assert m.group(1).strip().endswith("ms")
        assert m.group(1).strip().startswith("0"), (
            f"--{name} must be 0 under reduced motion, got {m.group(1).strip()}"
        )


# --------------------------------------------------------------------------
# sync
# --------------------------------------------------------------------------


def test_web_copy_is_byte_identical_to_canonical() -> None:
    assert TOKENS.read_bytes() == WEB_TOKENS.read_bytes(), (
        "apps/web/styles/design-tokens.css is out of sync with "
        "docs/brand/design-tokens.css"
    )


def test_json_declares_current_version_and_new_groups() -> None:
    data = json.loads(TOKENS_JSON.read_text(encoding="utf-8"))
    css_version = token_value(css_text(), "ph-system-version")
    assert css_version, "--ph-system-version missing"
    declared = data["$meta"]["version"]
    assert declared == css_version.strip("'\""), (
        f"design-tokens.json version {declared} != css version {css_version}"
    )
    assert "motion" in data, "design-tokens.json missing the motion group"
    assert "ebook" in data, "design-tokens.json missing the ebook group"
    for tier in TIERS:
        assert tier in data["ebook"], f"design-tokens.json missing ebook.{tier}"
        for role in EBOOK_ROLES:
            assert role in data["ebook"][tier], (
                f"design-tokens.json missing ebook.{tier}.{role}"
            )
    for name in MOTION_TOKENS:
        assert name in data["motion"], f"design-tokens.json missing motion.{name}"


def test_storefront_type_and_book_material_match_css() -> None:
    data = json.loads(TOKENS_JSON.read_text(encoding="utf-8"))
    css = css_text()
    scope = data["storefrontType"]["$scope"]
    block = re.search(rf"{re.escape(scope)}\s*\{{([^}}]+)\}}", css)
    assert block, f"missing typography scope {scope}"
    for group, stylesheet in (("storefrontType", block.group(1)), ("bookMaterial", css)):
        for name, value in data[group].items():
            if not name.startswith("$"):
                actual = token_value(stylesheet, name)
                assert actual, f"missing token {name}"
                assert " ".join(actual.split()) == str(value)


def test_json_ebook_values_match_css_values() -> None:
    data = json.loads(TOKENS_JSON.read_text(encoding="utf-8"))
    css = css_text()
    for tier in TIERS:
        for role in EBOOK_ROLES:
            css_value = token_value(css, f"ebook-{tier}-{role}")
            assert css_value, f"css token --ebook-{tier}-{role} not found"
            json_value = data["ebook"][tier][role]
            if isinstance(json_value, dict):
                json_value = json_value.get("ref", json_value)
                json_value = json_value.replace("ebook.", "ebook-").replace(".", "-")
                json_value = json_value.replace("ebook-", "ebook-", 1)
            assert str(json_value) in css_value or css_value in str(json_value), (
                f"ebook.{tier}.{role} = {json_value!r} does not match css {css_value!r}"
            )


# --------------------------------------------------------------------------
# contrast on the new tier pairs
# --------------------------------------------------------------------------

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("check_contrast", HERE / "check-contrast.py")
check_contrast = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_contrast)  # type: ignore[union-attr]


@pytest.mark.parametrize("tier", TIERS)
def test_ebook_tier_text_pairs_meet_wcag(tier: str) -> None:
    css = css_text()
    page = token_value(css, f"ebook-{tier}-page")
    assert page and page.startswith("#"), f"ebook-{tier}-page must be a literal hex colour"
    for role, floor in (("ink", 4.5), ("heading", 4.5), ("field-ink", 4.5)):
        fg = token_value(css, f"ebook-{tier}-{role}")
        assert fg and fg.startswith("#"), f"ebook-{tier}-{role} must be a literal hex"
        ratio = check_contrast.contrast(fg, page)
        assert ratio >= floor, (
            f"ebook {tier}: {role} {fg} on page {page} = {ratio:.2f}:1, needs {floor}"
        )
    # ornament/rule are graphics (WCAG 1.4.11) — 3:1 against the page
    for role in ("rule", "ornament"):
        fg = token_value(css, f"ebook-{tier}-{role}")
        assert fg and fg.startswith("#"), f"ebook-{tier}-{role} must be a literal hex"
        ratio = check_contrast.contrast(fg, page)
        assert ratio >= 3.0, (
            f"ebook {tier}: {role} {fg} on page {page} = {ratio:.2f}:1, needs 3.0"
        )


@pytest.mark.parametrize("tier", TIERS)
def test_ebook_wash_and_field_contrast(tier: str) -> None:
    css = css_text()
    for role, ground in (("ink", "wash"), ("heading", "wash"), ("field-ink", "field")):
        fg = token_value(css, f"ebook-{tier}-{role}")
        bg = token_value(css, f"ebook-{tier}-{ground}")
        assert fg and bg and check_contrast.contrast(fg, bg) >= 4.5


# --------------------------------------------------------------------------
# specimen sheet
# --------------------------------------------------------------------------


def test_specimen_sheet_exists_and_covers_required_states() -> None:
    assert SPECIMEN.exists(), f"missing specimen sheet: {SPECIMEN}"
    html = SPECIMEN.read_text(encoding="utf-8")
    for section in SPECIMEN_SECTIONS:
        assert f'data-specimen="{section}"' in html, (
            f"specimen sheet missing section {section}"
        )
    for tier in TIERS:
        assert f'data-specimen="tier-{tier}"' in html, (
            f"specimen sheet missing tier specimen {tier}"
        )


def test_specimen_sheet_uses_tokens_only() -> None:
    """No raw hex colours in the specimen — everything resolves through tokens."""
    html = SPECIMEN.read_text(encoding="utf-8")
    raw = re.findall(r"#[0-9a-fA-F]{3,8}\b", html)
    assert not raw, f"specimen sheet contains raw hex colours: {raw[:5]}"
    assert "design-tokens.css" in html, "specimen sheet must link the token sheet"


def test_specimen_sheet_links_canonical_tokens() -> None:
    html = SPECIMEN.read_text(encoding="utf-8")
    assert re.search(r'href="[^"]*design-tokens\.css"', html), (
        "specimen sheet must link design-tokens.css"
    )
