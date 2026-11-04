"""Regression tests for the self-hosted brand fonts.

The bug these guard against: build-fonts.py used to *relabel* the wght axis
as 400-700 without moving the outlines. Fraunces ships with a default
weight of 900, so every "regular" brand glyph was secretly Black, and
font-weight 700 resolved to 900 as well.

The test measures real ink: the filled area of a few glyphs in the built
woff2 at weight 400 and 700, compared with the upstream variable font
instanced at the same axis values. They must agree within 1.5%.

Run:
    uv run --no-project --with fonttools --with brotli --with pytest \
        pytest packages/brand-tools/tests -q
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from fontTools.pens.areaPen import AreaPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = Path(__file__).resolve().parent.parent
FONTS = HERE / "fonts"
SOURCE = FONTS / "source"

spec = importlib.util.spec_from_file_location("build_fonts", HERE / "build-fonts.py")
build_fonts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_fonts)  # type: ignore[union-attr]

SAMPLE = "HAThin"


def ink(font: TTFont, text: str = SAMPLE) -> float:
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    total = 0.0
    for ch in text:
        pen = AreaPen(gs)
        gs[cmap[ord(ch)]].draw(pen)
        total += abs(pen.value)
    return total


def at(font: TTFont, **axes: float) -> TTFont:
    if "fvar" not in font:
        return font
    return instancer.instantiateVariableFont(font, axes, inplace=False)


CASES = [(name, w) for name, s in build_fonts.FACES.items()
         for w in s["wght_range"]]


@pytest.mark.parametrize("name,weight", CASES)
def test_built_weight_matches_upstream(name: str, weight: int) -> None:
    face = build_fonts.FACES[name]
    src = SOURCE / face["source"]
    if not src.exists():
        pytest.skip(f"upstream source not downloaded: {src.name}")

    expected = ink(at(TTFont(src), **face["pins"], wght=weight))
    built = TTFont(FONTS / face["out"])
    got = ink(at(built, wght=weight))

    assert got == pytest.approx(expected, rel=0.015), (
        f"{name} at wght {weight}: ink {got:.0f} vs upstream {expected:.0f}"
    )


@pytest.mark.parametrize("name", list(build_fonts.FACES))
def test_default_instance_is_the_regular_weight(name: str) -> None:
    """Tools that read default outlines (build-logos.py, PDF engines that
    ignore variation) must get the light end of the range, not Black."""
    face = build_fonts.FACES[name]
    src = SOURCE / face["source"]
    if not src.exists():
        pytest.skip(f"upstream source not downloaded: {src.name}")
    lo = face["wght_range"][0]
    expected = ink(at(TTFont(src), **face["pins"], wght=lo))
    got = ink(TTFont(FONTS / face["out"]))
    assert got == pytest.approx(expected, rel=0.015)
