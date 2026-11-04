"""Rendered-output checks for the Threads templates, plus token sync.

Static tests read the HTML. These tests render each template in headless
Chrome and look at the real pixels:

  * the screenshot has the template's declared size
  * the picture is not blank
  * the average colour is green-led (green is the dominant channel)
  * gold is present (frame, rules, bylines)

A second group keeps the copied token snapshot in doop-guideline.md aligned
with docs/brand/design-tokens.css, so the two cannot drift apart silently.

Skipped automatically when Chrome or Pillow is not available.

Run:
    uv run --no-project --with pillow --with pytest pytest packages/brand-tools/tests -q
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
TEMPLATES = ROOT / "content" / "threads" / "templates"
TOKENS = ROOT / "docs" / "brand" / "design-tokens.css"
GUIDELINE = ROOT / "docs" / "brand" / "doop-guideline.md"

CHROME = (
    shutil.which("google-chrome")
    or shutil.which("chromium")
    or shutil.which("chromium-browser")
    or shutil.which("chrome-headless-shell")
)

RENDERED = {
    "quote-card.html": (1080, 1350),
    "quote-card-b.html": (1080, 1350),
    "quote-card-c.html": (1080, 1350),
    "carousel.html": (1080, 1080),
}


def render(template: Path, size: tuple[int, int], out: Path) -> Path:
    subprocess.run(
        [
            CHROME,
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--hide-scrollbars",
            "--allow-file-access-from-files",
            f"--window-size={size[0]},{size[1]}",
            "--virtual-time-budget=5000",
            f"--screenshot={out}",
            template.as_uri(),
        ],
        check=True,
        capture_output=True,
        timeout=90,
    )
    return out


@pytest.fixture(scope="module")
def pil():
    return pytest.importorskip("PIL.Image")


ImageStat = pytest.importorskip("PIL.ImageStat")


@pytest.fixture(params=sorted(RENDERED), ids=lambda n: Path(n).stem, scope="module")
def shot(request, pil, tmp_path_factory):
    if CHROME is None:
        pytest.skip("no headless Chrome available")
    name = request.param
    out = tmp_path_factory.mktemp("render") / f"{Path(name).stem}.png"
    render(TEMPLATES / name, RENDERED[name], out)
    return name, pil.open(out).convert("RGB")


def test_render_has_declared_size(shot) -> None:
    name, img = shot
    assert img.size == RENDERED[name]


def test_render_is_not_blank(shot) -> None:
    _, img = shot
    low, high = img.convert("L").getextrema()
    assert high - low > 80, "render looks blank or flat"


def test_render_is_green_led(shot) -> None:
    _, img = shot
    r, g, b = ImageStat.Stat(img).mean
    assert g > r and g > b, f"mean colour ({r:.0f},{g:.0f},{b:.0f}) is not green-led"


def test_render_shows_gold(shot) -> None:
    _, img = shot
    small = img.resize((img.width // 4, img.height // 4))
    gold = sum(
        1
        for r, g, b in small.get_flattened_data()
        if r > 150 and 120 < g < 215 and 60 < b < 170 and r > g > b
    )
    assert gold > 40, "no gold found in the render"


# --- token sync -----------------------------------------------------------


def custom_props(css: str) -> dict[str, str]:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    props: dict[str, str] = {}
    for name, value in re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", css):
        props[name] = re.sub(r"(?<![\d])\.(\d)", r"0.\1", re.sub(r"\s+", "", value).lower())
    return props


def test_guideline_tokens_match_design_tokens() -> None:
    block = re.search(r"```css\s*:root\{(.*?)\n\}", GUIDELINE.read_text(), re.S)
    assert block, "doop-guideline.md has no :root token snapshot"
    snapshot = custom_props(block.group(1))
    source = custom_props(TOKENS.read_text())
    assert snapshot, "token snapshot is empty"
    drift = {
        name: (value, source[name])
        for name, value in snapshot.items()
        if name in source and not name.startswith("--font-") and source[name] != value
    }
    assert not drift, f"guideline token snapshot drifted from design-tokens.css: {drift}"


def test_guideline_tokens_exist_in_design_tokens() -> None:
    block = re.search(r"```css\s*:root\{(.*?)\n\}", GUIDELINE.read_text(), re.S)
    snapshot = custom_props(block.group(1))
    source = custom_props(TOKENS.read_text())
    missing = [n for n in snapshot if n not in source and not n.startswith("--font-")]
    assert not missing, f"snapshot tokens absent from design-tokens.css: {missing}"
