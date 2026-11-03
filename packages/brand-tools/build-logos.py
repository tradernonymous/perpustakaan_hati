#!/usr/bin/env python3
"""Perpustakaan Hati — logo generator.

Renders the production logo SVGs with brand type converted to OUTLINES
(paths), so the files never depend on a font being installed on the
reader's machine or on Google Fonts being reachable.

Also renders a 3D wordmark variant. "3D type" here means a *treatment*:
the same Fraunces outlines are extruded in vector, given a rim light and
an ambient shadow. It is deliberately not a novelty 3D font — that would
break the editorial character of the brand and add a font dependency.

Usage:
    uv run --no-project --with fonttools --with brotli \
        python packages/brand-tools/build-logos.py

Requires the subset fonts in packages/brand-tools/fonts/.
"""
from __future__ import annotations

from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"
OUT = HERE.parent.parent / "docs" / "brand" / "assets"

# ---- brand tokens (must match docs/brand/design-tokens.css) ----
INK = "#0a0a0c"
GOLD = "#c9a86a"
GOLD_LIGHT = "#e9cea2"
GOLD_DEEP = "#a07b45"
GREEN = "#5b9b7d"
GREEN_DEEP = "#123d2a"
GREEN_400 = "#7db895"
LIME = "#c8e986"


def centred(font: TTFont, text: str, size: float, tracking: float,
            centre: float, baseline: float) -> str:
    """Convert `text` to an SVG path `d` string, horizontally centred.

    Glyph outlines are read from the font file and emitted as filled paths,
    so the rendered result is identical on every machine.
    """
    upem = font["head"].unitsPerEm
    scale = size / upem
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    glyph_set = font.getGlyphSet()

    advances = []
    for ch in text:
        gname = cmap.get(ord(ch))
        advances.append(0.0 if gname is None else hmtx[gname][0] * scale)
    width = sum(advances) + tracking * max(0, len(text) - 1)

    pen = SVGPathPen(glyph_set)
    cursor = centre - width / 2
    for ch, advance in zip(text, advances):
        gname = cmap.get(ord(ch))
        if gname is not None:
            tpen = TransformPen(pen, (scale, 0, 0, -scale, cursor, baseline))
            glyph_set[gname].draw(tpen)
        cursor += advance + tracking
    return pen.getCommands()


def svg_doc(width: int, height: int, body: str, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-label="{title}">\n{body}</svg>\n'
    )


def build_wordmark(fraunces: TTFont, inter: TTFont) -> None:
    W = H = 1200
    p1 = centred(fraunces, "PERPUSTAKAAN", 92, 18, 600, 462)
    p2 = centred(fraunces, "HATI", 92, 18, 600, 592)
    pb = centred(inter, "— by @rahimam —", 32, 8, 600, 792)
    body = f"""  <!--
    Perpustakaan Hati — primary wordmark (production SVG, outlined type)
    Source: docs/brand/visual-identity.md -> "Logo & watermark stamp"
    Colors: gold {GOLD} on ink {INK}
    Type: Fraunces (display) + Inter (byline). Text is converted to paths,
    so no font installation or network access is needed to render.
    Usage: web header, eBook cover, Threads card, print.
  -->
  <rect width="{W}" height="{H}" fill="{INK}"/>

  <line x1="230" y1="332" x2="970" y2="332" stroke="{GOLD_DEEP}" stroke-width="2"/>

  <path fill="{GOLD}" d="{p1}"/>
  <path fill="{GOLD}" d="{p2}"/>

  <line x1="230" y1="700" x2="970" y2="700" stroke="{GOLD_DEEP}" stroke-width="2"/>

  <path fill="{GOLD_LIGHT}" d="{pb}"/>

  <rect x="578" y="862" width="44" height="7" fill="{GREEN}"/>
"""
    (OUT / "wordmark-primary.svg").write_text(
        svg_doc(W, H, body, "Perpustakaan Hati wordmark"), encoding="utf-8")


def build_monogram(fraunces: TTFont, inter: TTFont) -> None:
    W = H = 1200
    ph = centred(fraunces, "PH", 360, 0, 600, 686)
    wm = centred(inter, "PERPUSTAKAAN HATI", 44, 13, 600, 962)
    body = f"""  <!--
    Perpustakaan Hati — compact monogram / stamp (production SVG, outlined type)
    Source: docs/brand/visual-identity.md -> "Logo & watermark stamp"
    Use for: favicon, avatar, cover badge, small footer lockup.
  -->
  <rect width="{W}" height="{H}" fill="{INK}"/>

  <rect x="140" y="140" width="920" height="920" fill="none" stroke="{GOLD_DEEP}" stroke-width="6"/>
  <rect x="170" y="170" width="860" height="860" fill="none" stroke="{GOLD}" stroke-width="1.5"/>

  <path fill="{GOLD}" d="{ph}"/>

  <rect x="470" y="762" width="260" height="10" fill="{GREEN}"/>

  <path fill="{GOLD_LIGHT}" d="{wm}"/>
"""
    (OUT / "monogram-stamp.svg").write_text(
        svg_doc(W, H, body, "Perpustakaan Hati compact mark"), encoding="utf-8")


def build_cop_stamp(fraunces: TTFont, inter: TTFont) -> None:
    W, H = 900, 300
    t1 = centred(fraunces, "Cop Perpustakaan Hati", 40, 6, 450, 138)
    t2 = centred(inter, "NAMA PEMBELI · CONTOH@EMAIL.COM", 22, 5, 450, 210)
    body = f"""  <!--
    Perpustakaan Hati — "Cop Perpustakaan Hati" watermark stamp (production SVG, outlined type)
    Source: docs/brand/visual-identity.md -> "Logo & watermark stamp"
    Placement: bottom-right of every paid eBook page, rotated -20deg by the
    compiler, 10% opacity. Buyer name/email line is injected by the Phase 2
    watermarking engine (placeholder below).
  -->
  <g fill="none" stroke="{GOLD}" stroke-width="3">
    <rect x="12" y="40" width="876" height="220"/>
  </g>
  <g fill="none" stroke="{GOLD_DEEP}" stroke-width="1.5">
    <rect x="26" y="54" width="848" height="192"/>
  </g>

  <path fill="{GOLD}" d="{t1}"/>

  <line x1="180" y1="166" x2="720" y2="166" stroke="{GOLD_DEEP}" stroke-width="2"/>

  <path fill="{GOLD_LIGHT}" d="{t2}"/>

  <rect x="395" y="228" width="110" height="6" fill="{GREEN}"/>
"""
    (OUT / "cop-stamp.svg").write_text(
        svg_doc(W, H, body, "Cop Perpustakaan Hati watermark stamp"), encoding="utf-8")


def build_wordmark_3d(fraunces: TTFont, inter: TTFont) -> None:
    """Extruded 3D wordmark — a vector treatment, not a 3D font.

    The Fraunces outlines are stacked in depth to form a real extruded
    solid: a dark green side face, a lit green edge, then the gold face
    with a light bevel. Everything is vector, so it scales to a poster
    without blurring and needs no font on the reader's machine.
    """
    W, H = 1600, 900
    depth = 22          # extrusion depth in user units
    step = 2            # layer spacing

    p1 = centred(fraunces, "PERPUSTAKAAN", 118, 22, 800, 430)
    p2 = centred(fraunces, "HATI", 118, 22, 800, 592)
    pb = centred(inter, "— by @rahimam —", 34, 9, 800, 760)

    def side_layers(path_d: str) -> str:
        """Solid extruded side face — dark green, darkening toward the back.

        Every layer is a full glyph copy offset downward, so the visible
        sliver below the face reads as one continuous side wall rather
        than a stack of separate outlines.
        """
        out = []
        for i in range(depth // step, 0, -1):
            dy = i * step
            dx = round(i * step * 0.34)   # slight lateral shift so vertical
            k = 1 - (i * step / depth)          # strokes show a side wall too
            r = round(18 + 20 * k)
            g = round(61 + 36 * k)
            b = round(42 + 28 * k)
            out.append(
                f'    <path fill="rgb({r},{g},{b})" '
                f'transform="translate({dx},{dy})" d="{path_d}"/>'
            )
        return "\n".join(out)

    body = f"""  <!--
    Perpustakaan Hati — 3D wordmark (campaign asset)
    Source: docs/brand/visual-identity.md -> "3D logo direction"
    Construction: Fraunces outlines extruded in vector. No 3D font, no
    runtime font dependency, sharp at any output size.
    Use: social headers, event posters, video openers.
    NOT for: site header, eBook cover, PDF master (use wordmark-primary.svg).
  -->
  <defs>
    <radialGradient id="ph-glow" cx="50%" cy="42%" r="62%">
      <stop offset="0%" stop-color="{GREEN_DEEP}" stop-opacity="0.7"/>
      <stop offset="100%" stop-color="{INK}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="ph-face" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#eed7a4"/>
      <stop offset="45%" stop-color="{GOLD}"/>
      <stop offset="100%" stop-color="#ab8950"/>
    </linearGradient>
    <linearGradient id="ph-rim" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{LIME}" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="{GREEN_400}" stop-opacity="0"/>
    </linearGradient>
    <filter id="ph-soft" x="-25%" y="-25%" width="150%" height="170%">
      <feGaussianBlur stdDeviation="30"/>
    </filter>
  </defs>

  <rect width="{W}" height="{H}" fill="{INK}"/>
  <ellipse cx="800" cy="400" rx="620" ry="320" fill="url(#ph-glow)"/>

  <!-- soft ambient shadow cast down-right onto the ink ground -->
  <g filter="url(#ph-soft)" opacity="0.6" fill="#000000">
    <path transform="translate(26,40)" d="{p1}"/>
    <path transform="translate(26,40)" d="{p2}"/>
  </g>

  <!-- solid extrusion: dark green side wall -->
  <g>
{side_layers(p1)}
{side_layers(p2)}
  </g>

  <!-- a single lit edge catching light on the right of the solid -->
  <path fill="{GREEN_400}" opacity="0.45" transform="translate(3,{depth})" d="{p1}"/>
  <path fill="{GREEN_400}" opacity="0.45" transform="translate(3,{depth})" d="{p2}"/>

  <!-- the gold face -->
  <path fill="url(#ph-face)" d="{p1}"/>
  <path fill="url(#ph-face)" d="{p2}"/>

  <!-- thin light bevel just under the top edge of each line -->
  <g opacity="0.45">
    <path fill="url(#ph-rim)" transform="translate(0,-2)" d="{p1}"/>
    <path fill="url(#ph-rim)" transform="translate(0,-2)" d="{p2}"/>
  </g>

  <line x1="330" y1="660" x2="1270" y2="660" stroke="{GOLD_DEEP}" stroke-width="2"/>
  <path fill="{GOLD_LIGHT}" d="{pb}"/>

  <rect x="756" y="812" width="88" height="8" fill="{GREEN}"/>
"""
    (OUT / "wordmark-3d.svg").write_text(
        svg_doc(W, H, body, "Perpustakaan Hati 3D wordmark"), encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fraunces = TTFont(FONTS / "FrauncesDisplay.woff2")
    inter = TTFont(FONTS / "InterUI.woff2")
    build_wordmark(fraunces, inter)
    build_monogram(fraunces, inter)
    build_cop_stamp(fraunces, inter)
    build_wordmark_3d(fraunces, inter)
    for name in ("wordmark-primary.svg", "monogram-stamp.svg", "cop-stamp.svg",
                 "wordmark-3d.svg"):
        print("wrote docs/brand/assets/" + name)


if __name__ == "__main__":
    main()
