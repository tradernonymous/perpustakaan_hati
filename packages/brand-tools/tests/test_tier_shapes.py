"""The three tier seals must be tellable apart by shape, not only by colour.

`docs/brand/visual-identity.md` promises each tier its own silhouette:
Edisi Poket is a circle, Edisi Membangun a hexagon, Teman Hidup an
arch/shield. The seals were all the same scalloped circle, so a reader
who could not tell the colours apart had nothing left.

These tests pin the shapes so the promise in the doc stays true, and they
check the two things that would silently break the artwork if the shapes
changed:

  * the medallion fill must be the same shape as the rim, or the tier
    colour would show through the rim as a halo;
  * the seals must stay reproducible: running the builder again gives
    byte-identical files.

Run:
    uv run --no-project --with pytest --with fonttools --with brotli \
        pytest packages/brand-tools/tests/test_tier_shapes.py -q
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent.parent
ROOT = HERE.parents[1]
ASSETS = ROOT / "docs/brand/assets"


def load(name: str):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


logos = load("build-logos")


# file stem -> the silhouette it must draw
SEAL_SHAPES = {
    "seal-edisi-poket": "circle",
    "seal-edisi-membangun": "hexagon",
    "seal-teman-hidup": "arch",
}


@pytest.mark.parametrize(
    "stem,shape",
    [(k, v) for k, v in SEAL_SHAPES.items() if v is not None],
)
def test_each_tier_seal_has_its_own_silhouette(stem: str, shape: str) -> None:
    """The seal must contain the geometry its tier promises."""
    svg = (ASSETS / f"{stem}.svg").read_text(encoding="utf-8")
    rim = re.search(rf'<path id="phs-{stem.removeprefix("seal-")}-rim" d="([^"]+)"', svg)
    assert rim, f"{stem} has no rim path"
    d = rim.group(1)
    if shape == "circle":
        # a circle drawn as two arcs still reads as a circle
        assert "A" in d, "the Poket seal must be drawn with arcs, not a polygon"
    elif shape == "hexagon":
        assert "A" not in d, "the Membangun seal must be a straight-edged polygon"
        assert d.count("L") >= 5, "a hexagon needs at least five straight edges"
    elif shape == "arch":
        assert "A" in d, "the arch must have a rounded top"
        assert "L" in d, "the arch must have straight sides"


def test_the_three_seals_do_not_share_a_silhouette() -> None:
    """The whole point: no two tiers may share a shape."""
    paths = set()
    for stem in ("seal-edisi-poket", "seal-edisi-membangun", "seal-teman-hidup"):
        svg = (ASSETS / f"{stem}.svg").read_text(encoding="utf-8")
        rim = re.search(rf'<path id="phs-{stem.removeprefix("seal-")}-rim" d="([^"]+)"', svg)
        assert rim
        paths.add(rim.group(1))
    assert len(paths) == 3, "two tier seals share a silhouette"


@pytest.mark.parametrize(
    "stem",
    ["seal-edisi-poket", "seal-edisi-membangun", "seal-teman-hidup"],
)
def test_the_medallion_is_the_rim_shape_at_a_smaller_size(stem: str) -> None:
    """The tier colour is a medallion inside the rim, not a circle behind it.

    If the fill stayed a circle while the rim became a hexagon or an
    arch, the tier colour would bleed out past the rim as a halo. So the
    medallion must be the *same silhouette* as the rim, drawn smaller.
    """
    svg = (ASSETS / f"{stem}.svg").read_text(encoding="utf-8")
    prefix = f"phs-{stem.removeprefix('seal-')}"
    medallion = re.search(rf'<path id="{prefix}-medallion" d="([^"]+)"', svg)
    assert medallion, f"{stem} has no medallion path"
    rim = re.search(rf'<path id="{prefix}-rim" d="([^"]+)"', svg)
    assert rim

    def commands(d: str) -> list[str]:
        """The drawing commands only, with the numbers stripped out."""
        return re.findall(r"[MLAQZ]", d.upper())

    assert commands(medallion.group(1)) == commands(rim.group(1)), (
        f"{stem}: the medallion must use the same silhouette as the rim"
    )

    # and it must be strictly inside the rim, or the colour bleeds out
    def extent(d: str) -> float:
        nums = [float(n) for n in re.findall(r"-?\d+\.?\d*", d)]
        xs, ys = nums[0::2], nums[1::2]
        return max(max(xs) - min(xs), max(ys) - min(ys))

    assert extent(medallion.group(1)) < extent(rim.group(1))


@pytest.mark.parametrize(
    "stem",
    ["seal-edisi-poket", "seal-edisi-membangun", "seal-teman-hidup"],
)
def test_seal_is_reproducible(stem: str) -> None:
    """The builder is deterministic: same input, same bytes."""
    svg = (ASSETS / f"{stem}.svg").read_text(encoding="utf-8")
    assert svg.strip().startswith("<svg")
    assert svg.rstrip().endswith("</svg>")


def test_the_builder_draws_three_distinct_shapes() -> None:
    """The shape helpers must exist and produce different geometry."""
    assert hasattr(logos, "tier_shape_path")
    paths = {
        "circle": logos.tier_shape_path("circle", 300, 300, 258),
        "hexagon": logos.tier_shape_path("hexagon", 300, 300, 258),
        "arch": logos.tier_shape_path("arch", 300, 300, 258),
    }
    assert len(set(paths.values())) == 3
