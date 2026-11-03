#!/usr/bin/env python3
"""Perpustakaan Hati — logo generator.

Renders the production logo SVGs with brand type converted to OUTLINES
(paths), so the files never depend on a font being installed on the
reader's machine or on Google Fonts being reachable.

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


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fraunces = TTFont(FONTS / "FrauncesDisplay.woff2")
    inter = TTFont(FONTS / "InterUI.woff2")
    build_wordmark(fraunces, inter)
    build_monogram(fraunces, inter)
    build_cop_stamp(fraunces, inter)
    for name in ("wordmark-primary.svg", "monogram-stamp.svg", "cop-stamp.svg"):
        print("wrote docs/brand/assets/" + name)


if __name__ == "__main__":
    main()
