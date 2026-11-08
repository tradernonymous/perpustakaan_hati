"""Build the AJE turtle mark — 3D vector art in two colourways.

Armazas Jaya Enterprise (AJE) is Rahimam's company. Its turtle mark is the
same drawing in both of the brand's own logos: the green "armazas JAYA
Enterprise" wordmark and the black-and-gold "ONE STOP CENTRE AJE" seal.
This script rebuilds that turtle alone, background removed, as reproducible
3D vector art.

    emerald  green face, dark green extrusion — the wordmark colourway
    noir     gold face, near-black extrusion — the seal colourway

The geometry in ``aje/turtle-path.txt`` was traced once from the green
wordmark (the cleanest, largest copy of the drawing) with potrace via
``uv run --no-project --with pillow --with numpy --with potracer python``:

    crop x 540-1290 of the logo, isolate green pixels, invert, upscale 2x,
    median-filter, trace with turdsize=14, alphamax=1.0, opttolerance=0.25,
    then convert the resulting curves to absolute M/L/C path data.

The path is the brand's own drawing — do not redraw, re-type or approximate
it. Rebuild the SVG/PNG set with:

    uv run --no-project --with pillow --with numpy --with potracer \
      python packages/brand-tools/build-aje-turtle.py

PNG export uses any local headless Chromium (google-chrome, chromium,
chromium-browser, microsoft-edge). Without one, the SVGs are still written
and the PNG step is skipped with a warning. Backgrounds stay transparent.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PATH_FILE = HERE / "aje" / "turtle-path.txt"
OUT_DIRS = (ROOT / "docs" / "brand" / "assets" / "aje", ROOT / "apps" / "web" / "public" / "brand" / "aje")

# Content bounds of the traced path, in trace coordinates.
MINX, MAXX, MINY, MAXY = 71.0, 1499.0, 18.3, 940.2
CANVAS_W, PAD = 1024, 44
SIZES = (1024, 512, 256)

CHROME_CANDIDATES = (
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "microsoft-edge",
    "chrome-headless-shell",
)


def geometry() -> tuple[str, float, float, int]:
    d = " ".join(PATH_FILE.read_text(encoding="utf-8").split())
    w, h = MAXX - MINX, MAXY - MINY
    scale = (CANVAS_W - 2 * PAD) / w
    height = round(h * scale + 2 * PAD)
    tx = PAD - MINX * scale
    ty = (height - h * scale) / 2 - MINY * scale
    return d, tx, ty, height


def ramp(start: str, end: str, steps: int) -> list[str]:
    a = tuple(int(start[i : i + 2], 16) for i in (1, 3, 5))
    b = tuple(int(end[i : i + 2], 16) for i in (1, 3, 5))
    return [
        "#%02x%02x%02x" % tuple(round(a[k] + (b[k] - a[k]) * i / (steps - 1)) for k in range(3))
        for i in range(steps)
    ]


def build(
    *,
    title: str,
    face_stops: tuple[tuple[str, str], ...],
    extrude_from: str,
    extrude_to: str,
    rim: str,
    depth: int = 16,
    step: float = 0.62,
) -> str:
    d, tx, ty, height = geometry()
    face = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in face_stops)
    extrusion = "".join(
        f'<use href="#turtle" fill="{c}" transform="translate({i * 0.18:.2f} {i * step:.2f})"/>'
        for i, c in zip(range(depth, 0, -1), ramp(extrude_from, extrude_to, depth))
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{height}" viewBox="0 0 {CANVAS_W} {height}" role="img" aria-label="{title}">
  <title>{title}</title>
  <desc>Armazas Jaya Enterprise (AJE) turtle mark, rebuilt as 3D vector art from the company's own logo. Transparent ground.</desc>
  <defs>
    <path id="turtle" d="{d}" fill-rule="evenodd"/>
    <linearGradient id="face" x1=".1" y1="0" x2=".86" y2="1">{face}</linearGradient>
    <linearGradient id="rim" x1="0" y1="0" x2=".35" y2="1">
      <stop offset="0" stop-color="{rim}" stop-opacity=".95"/>
      <stop offset=".5" stop-color="{rim}" stop-opacity=".12"/>
      <stop offset="1" stop-color="{rim}" stop-opacity=".5"/>
    </linearGradient>
    <filter id="bevel" x="-12%" y="-12%" width="124%" height="124%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="2.6" result="b"/>
      <feSpecularLighting in="b" surfaceScale="4.5" specularConstant="1" specularExponent="26" lighting-color="#ffffff" result="sp">
        <fePointLight x="300" y="120" z="260"/>
      </feSpecularLighting>
      <feComposite in="sp" in2="SourceAlpha" operator="in" result="spc"/>
      <feComposite in="SourceGraphic" in2="spc" operator="arithmetic" k1="0" k2="1" k3=".9" k4="0"/>
    </filter>
    <filter id="cast" x="-20%" y="-20%" width="140%" height="150%"><feGaussianBlur stdDeviation="13"/></filter>
  </defs>
  <g transform="translate({tx:.2f} {ty:.2f}) scale({(CANVAS_W - 2 * PAD) / (MAXX - MINX):.5f})">
    <g filter="url(#cast)" opacity=".5" transform="translate(7 28)"><use href="#turtle" fill="#000000"/></g>
    {extrusion}
    <g filter="url(#bevel)"><use href="#turtle" fill="url(#face)"/></g>
    <use href="#turtle" fill="none" stroke="url(#rim)" stroke-width="2.2" stroke-opacity=".55"/>
  </g>
</svg>
'''


VARIANTS = {
    "aje-turtle-emerald": dict(
        title="AJE turtle mark — emerald",
        face_stops=(
            (".08", "#dcf6e6"),
            (".3", "#7db895"),
            (".55", "#3f9167"),
            (".8", "#1d5a3d"),
            ("1", "#0b2418"),
        ),
        extrude_from="#2a7f52",
        extrude_to="#04120b",
        rim="#e6fff0",
    ),
    "aje-turtle-noir": dict(
        title="AJE turtle mark — gold on black",
        face_stops=(
            (".08", "#fff9e4"),
            (".3", "#f0cf8d"),
            (".55", "#c9a86a"),
            (".8", "#8a6224"),
            ("1", "#3e2a0b"),
        ),
        extrude_from="#6b4c17",
        extrude_to="#070503",
        rim="#fff1c9",
    ),
}


def chrome() -> str | None:
    for name in CHROME_CANDIDATES:
        found = shutil.which(name)
        if found:
            return found
    return None


def export_png(browser: str, svg: Path, width: int, height: int) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "page.html"
        page.write_text(
            "<!doctype html><meta charset=utf-8>"
            f"<style>html,body{{margin:0;background:transparent}}"
            f"img{{display:block;width:{width}px;height:auto}}</style>"
            f'<img src="{svg.as_uri()}">',
            encoding="utf-8",
        )
        target = svg.with_name(f"{svg.stem}-{width}.png")
        subprocess.run(
            [
                browser,
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--force-device-scale-factor=1",
                "--default-background-color=00000000",
                f"--window-size={width},{height}",
                f"--screenshot={target}",
                page.as_uri(),
            ],
            check=True,
            capture_output=True,
        )
        print(f"  {target.relative_to(ROOT)}")


def main() -> None:
    browser = chrome()
    for name, spec in VARIANTS.items():
        svg_text = build(**spec)
        primary = OUT_DIRS[0] / f"{name}.svg"
        primary.parent.mkdir(parents=True, exist_ok=True)
        primary.write_text(svg_text, encoding="utf-8")
        # Web copy + the other mirror directories.
        for out in OUT_DIRS[1:]:
            out.mkdir(parents=True, exist_ok=True)
            (out / f"{name}.svg").write_text(svg_text, encoding="utf-8")
        print(f"{primary.relative_to(ROOT)}  ({len(svg_text) // 1024} KB)")
        if not browser:
            continue
        height = int(svg_text.split('height="', 1)[1].split('"', 1)[0])
        for width in SIZES:
            png_height = round(height * width / CANVAS_W)
            export_png(browser, primary, width, png_height)
            for out in OUT_DIRS[1:]:
                shutil.copy2(primary.with_name(f"{name}-{width}.png"), out / f"{name}-{width}.png")
    if not browser:
        print("no headless Chromium found — SVGs written, PNG export skipped")


if __name__ == "__main__":
    main()
