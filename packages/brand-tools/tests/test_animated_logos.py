"""The web logo files are generated, never hand-edited.

build-web-lockup.py derives apps/web/public/brand/lockup-hero.svg from the
sanctioned lockup; build-animated-logos.py derives the animated copies in
apps/web/public/brand/animated/. These tests fail when a source logo changed
but the derived files were not regenerated (or were edited by hand), and they
pin the brand rules for the motion: it ends on the original artwork, the
sheen never loops, and reduced motion turns everything off.

Run:
    uv run --no-project --with pytest pytest packages/brand-tools/tests -q
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent.parent
ROOT = HERE.parents[1]


def load(name: str):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


web_lockup = load("build-web-lockup")
animated = load("build-animated-logos")


def test_web_lockup_is_fresh() -> None:
    expected = web_lockup.derive(web_lockup.SRC.read_text(encoding="utf-8"))
    assert web_lockup.OUT.read_text(encoding="utf-8") == expected, \
        "run: uv run --no-project python packages/brand-tools/build-web-lockup.py"


@pytest.mark.parametrize("name", sorted(animated.JOBS))
def test_animated_logo_is_fresh(name: str) -> None:
    assert (animated.OUT / name).read_text(encoding="utf-8") == animated.render(name), \
        "run: uv run --no-project python packages/brand-tools/build-animated-logos.py"


@pytest.mark.parametrize("name", sorted(animated.JOBS))
def test_motion_ends_on_the_artwork_and_respects_reduced_motion(name: str) -> None:
    svg = animated.render(name)
    assert "prefers-reduced-motion: reduce" in svg
    # one-shot animations start from an offset state and fall back to the
    # artwork; only the glint twinkle and the seal ring may loop.
    for rule in re.findall(r"\.phx-[\w-]+ \{[^}]*animation:[^}]*\}", svg):
        if "infinite" in rule:
            assert rule.startswith((".phx-twinkle", ".phx-turn")), rule
        else:
            assert "backwards" in rule, rule


def test_animation_adds_no_artwork() -> None:
    """Stripping the motion markup from the emblem gives back the source."""
    src = (animated.ASSETS / "emblem-book-heart.svg").read_text(encoding="utf-8")
    out = animated.render("emblem-book-heart.svg")
    out = re.sub(r"\n  <style>.*?</style>", "", out, flags=re.S)
    out = out.replace(' pathLength="1"', "")
    out = re.sub(r' class="phx-[\w-]+"', "", out)
    out = out.replace('\n  <g>\n  <g>', '\n  <g>', 1).replace('\n  </g>\n  </g>', '\n  </g>', 1)
    assert out == src
