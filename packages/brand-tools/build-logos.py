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

import math
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

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
    depth = 18          # extrusion depth in user units (1px layers)

    p1 = centred(fraunces, "PERPUSTAKAAN", 118, 22, 800, 430)
    p2 = centred(fraunces, "HATI", 118, 22, 800, 592)
    pb = centred(inter, "— by @rahimam —", 34, 9, 800, 760)

    def side_layers(ref: str) -> str:
        """Solid extruded side face — 1px layers of one shared outline
        (`<use>`), dark green darkening toward the back. 1px steps keep
        the side wall continuous at every weight (2px steps striped once
        the type was set at its real, lighter weight)."""
        out = []
        for i in range(depth, 0, -1):
            dx = round(i * 0.34, 2)
            k = 1 - i / depth
            r = round(18 + 20 * k)
            g = round(61 + 36 * k)
            b = round(42 + 28 * k)
            out.append(f'    <use href="#{ref}" fill="rgb({r},{g},{b})" transform="translate({dx},{i})"/>')
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
    <path id="ph-l1" d="{p1}"/>
    <path id="ph-l2" d="{p2}"/>
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
{side_layers("ph-l1")}
{side_layers("ph-l2")}
  </g>

  <!-- lit edge: the first 2px of side wall catching the key light -->
  <use href="#ph-l1" fill="{GREEN_400}" opacity="0.55" transform="translate(0.5,2)"/>
  <use href="#ph-l2" fill="{GREEN_400}" opacity="0.55" transform="translate(0.5,2)"/>

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


# --------------------------------------------------------------------------
# Design System 3.0 "Gilded Grove" — refined type + 3D (v3.1)
# --------------------------------------------------------------------------
# v3 tokens (must match docs/brand/design-tokens.css)
FOREST_NIGHT = "#07140d"
GREEN_950 = "#0b2418"
GREEN_900 = "#123d2a"
GREEN_800 = "#1d5a3d"
GREEN_700 = "#2d7954"
GREEN_600 = "#3f9167"
GREEN_300 = "#a7d3b6"
CREAM = "#fdfee6"
PAPER = "#f4efe6"
LINEN = "#eae2d4"
BURGUNDY = "#5c1e17"
HEART_RUBY = "#c8343c"
LANTERN = "#f2b85c"

# Type weights per role (the fonts are variable 400-700; see build-fonts.py).
# These mirror --weight-* in design-tokens.css.
W_DISPLAY = 560   # spaced caps: PERPUSTAKAAN, wordmarks — Trajan-like, not heavy
W_HERO = 660      # the hero word: HATI, seal main word
W_LABEL = 600     # Inter caps labels on seals
W_BYLINE = 500    # Inter kicker / byline


def weight(font: TTFont, wght: float) -> TTFont:
    """Static instance of a variable brand font at `wght`. Outline tools
    read default outlines, so every weight must be instanced explicitly."""
    if "fvar" not in font:
        return font
    return instancer.instantiateVariableFont(font, {"wght": wght}, inplace=False)


def text_width(font: TTFont, text: str, size: float, tracking: float) -> float:
    """Advance width of `text` in user units, same maths as `centred`."""
    scale = size / font["head"].unitsPerEm
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    total = sum(hmtx[cmap[ord(c)]][0] * scale for c in text if ord(c) in cmap)
    return total + tracking * max(0, len(text) - 1)


def fitted(font: TTFont, text: str, size: float, tracking: float,
           centre: float, baseline: float, max_width: float) -> str:
    """`centred`, but shrinks size + tracking until the line fits."""
    w = text_width(font, text, size, tracking)
    if w > max_width:
        k = max_width / w
        size, tracking = size * k, tracking * k
    return centred(font, text, size, tracking, centre, baseline)


def mix(a: str, b: str, t: float) -> str:
    """Linear blend of two hex colours (t=0 -> a, t=1 -> b)."""
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))


def v3_defs(p: str) -> str:
    """Shared v3 paint servers + filters. `p` prefixes ids per file."""
    return f"""    <linearGradient id="{p}-foil-gold" x1="0" y1="0" x2="0.1" y2="1">
      <stop offset="0" stop-color="#fff4d6"/>
      <stop offset="0.2" stop-color="#f0d08e"/>
      <stop offset="0.46" stop-color="#c49a52"/>
      <stop offset="0.54" stop-color="#9a7638"/>
      <stop offset="0.62" stop-color="#d9b46c"/>
      <stop offset="0.84" stop-color="#f6e2ad"/>
      <stop offset="1" stop-color="#b8904a"/>
    </linearGradient>
    <linearGradient id="{p}-foil-emerald" x1="0" y1="0" x2="0.1" y2="1">
      <stop offset="0" stop-color="#e3f7e8"/>
      <stop offset="0.2" stop-color="#9edab2"/>
      <stop offset="0.46" stop-color="{GREEN_600}"/>
      <stop offset="0.54" stop-color="{GREEN_700}"/>
      <stop offset="0.62" stop-color="#4fa477"/>
      <stop offset="0.84" stop-color="#b6e3c4"/>
      <stop offset="1" stop-color="{GREEN_600}"/>
    </linearGradient>
    <linearGradient id="{p}-page" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fffef4"/>
      <stop offset="0.65" stop-color="{PAPER}"/>
      <stop offset="1" stop-color="{LINEN}"/>
    </linearGradient>
    <linearGradient id="{p}-page-edge" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f1d79b"/>
      <stop offset="1" stop-color="#9a7638"/>
    </linearGradient>
    <linearGradient id="{p}-cover" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{GREEN_700}"/>
      <stop offset="0.55" stop-color="{GREEN_800}"/>
      <stop offset="1" stop-color="{GREEN_950}"/>
    </linearGradient>
    <radialGradient id="{p}-lantern" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="{LANTERN}" stop-opacity="0.55"/>
      <stop offset="0.45" stop-color="{LANTERN}" stop-opacity="0.16"/>
      <stop offset="1" stop-color="{LANTERN}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="{p}-emerald-glow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="{GREEN_600}" stop-opacity="0.55"/>
      <stop offset="1" stop-color="{GREEN_600}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="{p}-vignette" cx="0.5" cy="0.45" r="0.75">
      <stop offset="0.55" stop-color="#000" stop-opacity="0"/>
      <stop offset="1" stop-color="#000" stop-opacity="0.75"/>
    </radialGradient>
    <radialGradient id="{p}-glint" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#fff" stop-opacity="1"/>
      <stop offset="0.25" stop-color="#fff4d6" stop-opacity="0.6"/>
      <stop offset="1" stop-color="#fff4d6" stop-opacity="0"/>
    </radialGradient>
    <filter id="{p}-blur" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="14"/>
    </filter>
    <filter id="{p}-contact" x="-10%" y="-10%" width="120%" height="140%">
      <feGaussianBlur stdDeviation="3"/>
    </filter>
{bevel_filter(f"{p}-bevel", 1.6, 3.2)}
{bevel_filter(f"{p}-bevel-soft", 3.0, 4.5)}
{deboss_filter(f"{p}-deboss")}"""


def bevel_filter(fid: str, radius: float, depth: float) -> str:
    """Chiselled-metal bevel from real lighting maths, keyed light top-left.

    1. blur the glyph alpha into a height map (radius = bevel width)
    2. diffuse light shades the slopes: lit edges up, far edges down,
       flat face unchanged (arithmetic keeps the foil colour on the face)
    3. specular light adds a hot rim on the lit slope
    Everything is clipped back to the glyph, so the outline never grows.
    """
    return f"""    <filter id="{fid}" x="-5%" y="-10%" width="110%" height="125%" color-interpolation-filters="sRGB">
      <feGaussianBlur in="SourceAlpha" stdDeviation="{radius}" result="h"/>
      <feDiffuseLighting in="h" surfaceScale="{depth}" diffuseConstant="1" lighting-color="#fff" result="d">
        <feDistantLight azimuth="235" elevation="50"/>
      </feDiffuseLighting>
      <feComposite in="SourceGraphic" in2="d" operator="arithmetic" k1="0.75" k2="0.42" k3="0" k4="0" result="shaded"/>
      <feSpecularLighting in="h" surfaceScale="{depth}" specularConstant="0.85" specularExponent="26"
                          lighting-color="#fffbe8" result="s">
        <feDistantLight azimuth="235" elevation="42"/>
      </feSpecularLighting>
      <feComposite in="s" in2="SourceAlpha" operator="in" result="sIn"/>
      <feComposite in="shaded" in2="sIn" operator="arithmetic" k1="0" k2="1" k3="0.7" k4="0" result="lit"/>
      <feComposite in="lit" in2="SourceAlpha" operator="in"/>
    </filter>"""


def deboss_filter(fid: str) -> str:
    """Stamped-in label: dark inner edge on top, light catch on the bottom."""
    return f"""    <filter id="{fid}" x="-5%" y="-20%" width="110%" height="140%">
      <feOffset in="SourceAlpha" dx="0" dy="2.2" result="down"/>
      <feComposite in="SourceAlpha" in2="down" operator="out" result="topEdge"/>
      <feFlood flood-color="#000" flood-opacity="0.45"/>
      <feComposite in2="topEdge" operator="in" result="shade"/>
      <feOffset in="SourceAlpha" dx="0" dy="1.6" result="lowAlpha"/>
      <feComposite in="lowAlpha" in2="SourceAlpha" operator="out" result="catch"/>
      <feFlood flood-color="#fff" flood-opacity="0.28"/>
      <feComposite in2="catch" operator="in" result="light"/>
      <feMerge><feMergeNode in="light"/><feMergeNode in="SourceGraphic"/><feMergeNode in="shade"/></feMerge>
    </filter>"""


def extrude(ref: str, depth: int, near: str, far: str, dx_per: float = 0.0) -> str:
    """Solid extrusion: `depth` 1px copies of `<use href=ref>` from far
    (back) to near (just behind the face), blending colour near -> far.
    `<use>` keeps the file small — one path, many references."""
    out = []
    for i in range(depth, 0, -1):
        t = (i - 1) / max(1, depth - 1)
        out.append(f'<use href="#{ref}" fill="{mix(near, far, t)}" '
                   f'transform="translate({round(i * dx_per, 2)},{i})"/>')
    return "\n  ".join(out)


def glint(cx: float, cy: float, r: float, p: str) -> str:
    """A four-point star glint — the 'light catches the metal' accent."""
    k = r * 0.14
    star = (f"M{cx},{cy - r} Q{cx + k},{cy - k} {cx + r},{cy} Q{cx + k},{cy + k} {cx},{cy + r} "
            f"Q{cx - k},{cy + k} {cx - r},{cy} Q{cx - k},{cy - k} {cx},{cy - r} Z")
    return (f'<circle cx="{cx}" cy="{cy}" r="{r * 0.55}" fill="url(#{p}-glint)"/>'
            f'<path fill="#fffbe8" opacity="0.95" d="{star}"/>')


HEART_D = ("M300,262 C246,214 186,176 186,118 C186,76 218,48 254,48 "
           "C278,48 293,60 300,78 C307,60 322,48 346,48 C382,48 414,76 414,118 "
           "C414,176 354,214 300,262 Z")


def emblem(p: str, glints: bool = True) -> str:
    """Book-heart emblem in a 600x420 box.

    3D construction, back to front: heart cast shadow; heart tube
    (extruded 6px in green-900, emerald foil face, lit by the bevel filter
    so it reads as a rounded metal tube); emerald cover with a thickness
    edge; page block with gilt edges; four fanned pages with a spine
    shadow; a single glint where the lantern light hits the heart."""
    def page(side: int, dy: float, spread: float) -> str:
        def x(v: float) -> float:
            return round(300 + side * (v * spread), 1)
        return (f"M300,{232 + dy} C{x(60)},{192 + dy} {x(160)},{182 + dy} {x(230)},{206 + dy} "
                f"L{x(240)},{314 + dy} C{x(160)},{292 + dy} {x(60)},{300 + dy} 300,{340 + dy} Z")

    cover_d = ("M300,262 C228,214 116,206 40,228 L28,346 C116,326 228,334 300,372 "
               "C372,334 484,326 572,346 L560,228 C484,206 372,214 300,262 Z")
    parts = [
        f'<path id="{p}-coverpath" d="{cover_d}"/>',
        # cover thickness: 6 darkening 1px layers under the board
        extrude(f"{p}-coverpath", 6, GREEN_900, GREEN_950),
        f'<use href="#{p}-coverpath" fill="url(#{p}-cover)" stroke="url(#{p}-foil-gold)" '
        f'stroke-width="3.5" filter="url(#{p}-bevel-soft)"/>',
        # heart: soft cast shadow on the pages, then the tube
        f'<path fill="none" stroke="#000" stroke-opacity="0.45" stroke-width="30" '
        f'filter="url(#{p}-blur)" transform="translate(6,16)" d="{HEART_D}"/>',
    ]
    for i in range(6, 0, -1):
        parts.append(f'<path fill="none" stroke="{mix(GREEN_800, GREEN_950, (i - 1) / 5)}" '
                     f'stroke-width="27" stroke-linejoin="round" transform="translate({i * 0.4},{i})" '
                     f'd="{HEART_D}"/>')
    parts += [
        f'<path fill="none" stroke="url(#{p}-foil-emerald)" stroke-width="27" stroke-linejoin="round" '
        f'filter="url(#{p}-bevel-soft)" d="{HEART_D}"/>',
        f'<path fill="none" stroke="{HEART_RUBY}" stroke-width="4.5" stroke-linejoin="round" '
        f'transform="translate(300,155) scale(0.775) translate(-300,-155)" d="{HEART_D}"/>',
    ]
    # page block: gilt edges visible under the top pages
    for side in (-1, 1):
        parts.append(f'<path fill="url(#{p}-page-edge)" d="{page(side, 24, 0.975)}"/>')
    for i, (dy, spread) in enumerate([(18, 0.98), (12, 0.99), (6, 1.0), (0, 1.0)]):
        for side in (-1, 1):
            parts.append(
                f'<path fill="url(#{p}-page)" stroke="#b8904a" stroke-width="{1.2 if i < 3 else 2.2}" '
                f'stroke-linejoin="round" d="{page(side, dy, spread)}"/>')
    # spine shadow: the gutter where the two top pages meet
    parts.append(f'<path fill="#8a6a35" opacity="0.28" filter="url(#{p}-contact)" '
                 f'd="M292,236 C296,280 296,312 296,338 L304,338 C304,312 304,280 308,236 Z"/>')
    for k in range(4):
        y = 238 + k * 18
        parts.append(f'<path fill="none" stroke="#b8904a" stroke-opacity="0.4" stroke-width="2" '
                     f'd="M286,{y + 8} C250,{y - 12} 190,{y - 18} 120,{y - 2}"/>')
        parts.append(f'<path fill="none" stroke="#b8904a" stroke-opacity="0.4" stroke-width="2" '
                     f'd="M314,{y + 8} C350,{y - 12} 410,{y - 18} 480,{y - 2}"/>')
    if glints:
        parts.append(glint(214, 84, 22, p))
    return "\n    ".join(parts)


def stage(p: str, w: int, h: int, glow_cy: float) -> str:
    """Cinematic ground: forest-night + emerald glow + lantern glow + vignette."""
    return f"""  <rect width="{w}" height="{h}" fill="{FOREST_NIGHT}"/>
  <ellipse cx="{w / 2}" cy="{glow_cy}" rx="{w * 0.48}" ry="{h * 0.5}" fill="url(#{p}-emerald-glow)"/>
  <ellipse cx="{w / 2}" cy="{glow_cy - h * 0.08}" rx="{w * 0.26}" ry="{h * 0.3}" fill="url(#{p}-lantern)"/>
  <rect width="{w}" height="{h}" fill="url(#{p}-vignette)"/>"""


def flank(cx: float, y: float, gap: float, length: float, colour: str) -> str:
    """Two tapering hairlines either side of a centred label + diamond tips."""
    l1, l2 = cx - gap - length, cx - gap
    r1, r2 = cx + gap, cx + gap + length
    return (f'<path fill="{colour}" d="M{l1},{y} L{l2},{y - 1.5} L{l2},{y + 1.5} Z"/>'
            f'<path fill="{colour}" d="M{r2},{y} L{r1},{y - 1.5} L{r1},{y + 1.5} Z"/>'
            f'<path fill="{colour}" d="M{l2 + 8},{y - 5} l5,5 l-5,5 l-5,-5 Z"/>'
            f'<path fill="{colour}" d="M{r1 - 8},{y - 5} l5,5 l-5,5 l-5,-5 Z"/>')


def build_emblem() -> None:
    p = "phe"
    body = f"""  <!--
    Perpustakaan Hati — book-heart emblem (Design System 3.0)
    Source: docs/brand/visual-identity.md -> "Design System 3.0"
    An emerald-bound open book; a foil heart rises from the spine.
    3D: extruded cover board + heart tube, lighting-filter bevel, gilt
    page block, spine shadow, one glint. Transparent background.
    Minimum size: 48px wide (below that use monogram-stamp.svg).
  -->
  <defs>
{v3_defs(p)}
  </defs>
  <ellipse cx="300" cy="170" rx="210" ry="170" fill="url(#{p}-lantern)"/>
  <g>
    {emblem(p)}
  </g>
"""
    (OUT / "emblem-book-heart.svg").write_text(
        svg_doc(600, 420, body, "Perpustakaan Hati book-heart emblem"), encoding="utf-8")


def build_lockup_cinematic(fraunces: TTFont, fraunces_it: TTFont, inter: TTFont) -> None:
    """Hero lockup: emblem + PERPUSTAKAAN (gold foil) + HATI (emerald foil,
    extruded) + flanked byline + italic tagline, on the cinematic stage."""
    p = "phl"
    W, H = 1600, 1000
    f_disp, f_hero = weight(fraunces, W_DISPLAY), weight(fraunces, W_HERO)
    f_by = weight(inter, W_BYLINE)
    p1 = centred(f_disp, "PERPUSTAKAAN", 90, 22, 800, 560)
    p2 = centred(f_hero, "HATI", 236, 30, 800, 792)
    pb = centred(f_by, "BY @RAHIMAM", 25, 10, 800, 864)
    pt = centred(fraunces_it, "Karya untuk jiwa yang pernah terluka", 40, 0.6, 800, 934)
    bw = text_width(f_by, "BY @RAHIMAM", 25, 10) / 2

    body = f"""  <!--
    Perpustakaan Hati — cinematic lockup (Design System 3.0 "Gilded Grove")
    Source: docs/brand/visual-identity.md -> "Design System 3.0"
    Green leads: forest-night ground, emerald glow, emerald-foil HATI.
    Gold frames: gold-foil PERPUSTAKAAN, gilt rules, gold byline.
    3D: 14px graded extrusion + contact shadow + ambient shadow, and a
    lighting-filter bevel on both foil lines.
    Use: Threads/IG headers, store hero, video opener, posters.
    NOT for: site header at < 320px wide (use wordmark-primary.svg).
  -->
  <defs>
{v3_defs(p)}
    <path id="{p}-perp" d="{p1}"/>
    <path id="{p}-hati" d="{p2}"/>
  </defs>
{stage(p, W, H, 360)}

  <g transform="translate(560,92) scale(0.8)">
    {emblem(p)}
  </g>

  <!-- PERPUSTAKAAN — gold foil, 4px extrusion, bevel -->
  <use href="#{p}-perp" fill="#000" opacity="0.5" filter="url(#{p}-blur)" transform="translate(0,12)"/>
  {extrude(f"{p}-perp", 4, "#7a5a28", "#3a2a14")}
  <use href="#{p}-perp" fill="url(#{p}-foil-gold)" filter="url(#{p}-bevel)"/>

  <!-- HATI — emerald foil, 14px graded extrusion, gold rim, bevel -->
  <use href="#{p}-hati" fill="#000" opacity="0.6" filter="url(#{p}-blur)" transform="translate(4,30)"/>
  <use href="#{p}-hati" fill="#000" opacity="0.7" filter="url(#{p}-contact)" transform="translate(1,16)"/>
  {extrude(f"{p}-hati", 14, GREEN_800, GREEN_950, 0.15)}
  <use href="#{p}-hati" fill="url(#{p}-foil-gold)" transform="translate(0,-2.5)"/>
  <use href="#{p}-hati" fill="url(#{p}-foil-emerald)" filter="url(#{p}-bevel)"/>

  {flank(800, 855, bw + 26, 250, GOLD)}
  <path fill="{GOLD_LIGHT}" d="{pb}"/>
  <path fill="{GREEN_300}" d="{pt}"/>
"""
    (OUT / "lockup-cinematic.svg").write_text(
        svg_doc(W, H, body, "Perpustakaan Hati cinematic lockup"), encoding="utf-8")


def scallop_path(cx: float, cy: float, r: float, bumps: int, depth: float) -> str:
    """Closed scalloped circle: `bumps` quadratic lobes of `depth` outward."""
    pts = []
    for i in range(bumps):
        a0 = 2 * math.pi * i / bumps
        a1 = 2 * math.pi * (i + 0.5) / bumps
        a2 = 2 * math.pi * (i + 1) / bumps
        if i == 0:
            pts.append(f"M{cx + r * math.cos(a0):.1f},{cy + r * math.sin(a0):.1f}")
        rc = r + depth * 2
        pts.append(f"Q{cx + rc * math.cos(a1):.1f},{cy + rc * math.sin(a1):.1f} "
                   f"{cx + r * math.cos(a2):.1f},{cy + r * math.sin(a2):.1f}")
    return " ".join(pts) + " Z"


SEALS = [
    # file, top, main, bottom, fill, label colour, rim gradient
    ("seal-edisi-poket.svg", "EDISI", "POKET", "PERCUMA", GREEN_700, CREAM, "foil-gold"),
    ("seal-edisi-membangun.svg", "EDISI", "MEMBANGUN", "@RAHIMAM", GOLD, INK, "foil-emerald"),
    ("seal-teman-hidup.svg", "TEMAN", "HIDUP", "PREMIUM", BURGUNDY, CREAM, "foil-gold"),
]


def build_seals(fraunces: TTFont, inter: TTFont) -> list[str]:
    """Scalloped tier seals. 3D: extruded scalloped rim with a lighting
    bevel, a recessed (inner-shadowed) medallion, debossed labels."""
    names = []
    f_main, f_lab = weight(fraunces, W_HERO), weight(inter, W_LABEL)
    for fname, top, main, bottom, fill, fg, rim in SEALS:
        p = "phs-" + fname.removeprefix("seal-").removesuffix(".svg")
        pt = centred(f_lab, top, 32, 10, 300, 254)
        pm = fitted(f_main, main, 90, 5, 300, 350, 330)
        pbm = centred(f_lab, bottom, 24, 7, 300, 426)
        scallop = scallop_path(300, 300, 258, 40, 7)
        body = f"""  <!--
    Perpustakaan Hati — tier seal "{top} {main}" (Design System 3.0)
    Source: docs/brand/tier-naming.md (tier colour is fixed)
    3D: extruded foil rim + bevel, recessed medallion, debossed labels.
    Use: eBook covers, store cards, Threads promo cards. Min 96px wide.
  -->
  <defs>
{v3_defs(p)}
    <path id="{p}-rim" d="{scallop}"/>
    <radialGradient id="{p}-recess" cx="0.5" cy="0.42" r="0.55">
      <stop offset="0.8" stop-color="#000" stop-opacity="0"/>
      <stop offset="1" stop-color="#000" stop-opacity="0.45"/>
    </radialGradient>
  </defs>
  <use href="#{p}-rim" fill="#000" opacity="0.45" filter="url(#{p}-blur)" transform="translate(0,16)"/>
  {extrude(f"{p}-rim", 8, "#6b5228" if rim == "foil-gold" else GREEN_800,
           "#2e2310" if rim == "foil-gold" else GREEN_950)}
  <use href="#{p}-rim" fill="url(#{p}-{rim})" filter="url(#{p}-bevel-soft)"/>
  <circle cx="300" cy="300" r="226" fill="{fill}"/>
  <circle cx="300" cy="300" r="226" fill="url(#{p}-recess)"/>
  <circle cx="300" cy="300" r="225" fill="none" stroke="#000" stroke-opacity="0.35" stroke-width="3"/>
  <circle cx="300" cy="300" r="206" fill="none" stroke="url(#{p}-{rim})" stroke-width="3"
          stroke-dasharray="2 9" stroke-linecap="round"/>
  <g transform="translate(246,128) scale(0.18)">
    {emblem(p, glints=False)}
  </g>
  <g filter="url(#{p}-deboss)" fill="{fg}">
    <path d="{pt}"/>
    <path d="{pm}"/>
    <path fill-opacity="0.6" d="M210,386 L390,386 L390,388 L210,388 Z"/>
    <path d="{pbm}"/>
  </g>
  {glint(150, 132, 26, p)}
"""
        (OUT / fname).write_text(
            svg_doc(600, 600, body, f"{top.title()} {main.title()} seal"), encoding="utf-8")
        names.append(fname)
    return names


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fraunces = TTFont(FONTS / "FrauncesDisplay.woff2")
    fraunces_it = TTFont(FONTS / "FrauncesDisplayItalic.woff2")
    inter = TTFont(FONTS / "InterUI.woff2")
    # 2.0 assets: explicit weights (they used to inherit the Black default)
    build_wordmark(weight(fraunces, W_DISPLAY), weight(inter, W_BYLINE))
    build_monogram(weight(fraunces, W_HERO), weight(inter, W_LABEL))
    build_cop_stamp(weight(fraunces, W_DISPLAY), weight(inter, W_BYLINE))
    build_wordmark_3d(weight(fraunces, W_HERO), weight(inter, W_BYLINE))
    build_emblem()
    build_lockup_cinematic(fraunces, fraunces_it, inter)
    seals = build_seals(fraunces, inter)
    for name in ("wordmark-primary.svg", "monogram-stamp.svg", "cop-stamp.svg",
                 "wordmark-3d.svg", "emblem-book-heart.svg", "lockup-cinematic.svg",
                 *seals):
        print("wrote docs/brand/assets/" + name)


if __name__ == "__main__":
    main()
