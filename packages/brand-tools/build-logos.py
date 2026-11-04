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


# --------------------------------------------------------------------------
# Design System 3.0 "Gilded Grove"
# --------------------------------------------------------------------------
# v3 tokens (must match docs/brand/design-tokens.css)
FOREST_NIGHT = "#07140d"
GREEN_900 = "#123d2a"
GREEN_700 = "#2d7954"
GREEN_600 = "#3f9167"
GREEN_300 = "#a7d3b6"
CREAM = "#fdfee6"
PAPER = "#f4efe6"
LINEN = "#eae2d4"
BURGUNDY = "#5c1e17"
HEART_RUBY = "#c8343c"
LANTERN = "#f2b85c"


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


def v3_defs(p: str) -> str:
    """Shared v3 gradients. `p` prefixes ids so several files never clash."""
    return f"""    <linearGradient id="{p}-foil-gold" x1="0" y1="0" x2="0.12" y2="1">
      <stop offset="0" stop-color="#fff1c9"/>
      <stop offset="0.24" stop-color="#ecc983"/>
      <stop offset="0.48" stop-color="#b8904a"/>
      <stop offset="0.58" stop-color="#9a7638"/>
      <stop offset="0.78" stop-color="#f1d79b"/>
      <stop offset="1" stop-color="#b8904a"/>
    </linearGradient>
    <linearGradient id="{p}-foil-emerald" x1="0" y1="0" x2="0.12" y2="1">
      <stop offset="0" stop-color="#d9f3df"/>
      <stop offset="0.22" stop-color="#8fd0a6"/>
      <stop offset="0.46" stop-color="{GREEN_600}"/>
      <stop offset="0.58" stop-color="{GREEN_700}"/>
      <stop offset="0.76" stop-color="{GREEN_300}"/>
      <stop offset="1" stop-color="{GREEN_600}"/>
    </linearGradient>
    <linearGradient id="{p}-page" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{CREAM}"/>
      <stop offset="0.7" stop-color="{PAPER}"/>
      <stop offset="1" stop-color="{LINEN}"/>
    </linearGradient>
    <linearGradient id="{p}-cover" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{GREEN_700}"/>
      <stop offset="1" stop-color="{GREEN_900}"/>
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
    <filter id="{p}-blur" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="14"/>
    </filter>
"""


HEART_D = ("M300,262 C246,214 186,176 186,118 C186,76 218,48 254,48 "
           "C278,48 293,60 300,78 C307,60 322,48 346,48 C382,48 414,76 414,118 "
           "C414,176 354,214 300,262 Z")


def emblem(p: str) -> str:
    """Book-heart emblem in a 600x420 box: an emerald-bound open book with
    fanned cream pages, and an emerald-foil heart rising from the spine.
    Pure vector, no type. Wrap in <g transform> to place and scale."""
    def page(side: int, dy: float, spread: float) -> str:
        # side = -1 (left) or +1 (right); x mirrored around the spine (300)
        def x(v: float) -> float:
            return round(300 + side * (v * spread), 1)
        return (f"M300,{232 + dy} C{x(60)},{192 + dy} {x(160)},{182 + dy} {x(230)},{206 + dy} "
                f"L{x(240)},{314 + dy} C{x(160)},{292 + dy} {x(60)},{300 + dy} 300,{340 + dy} Z")

    cover = (f'<path fill="url(#{p}-cover)" stroke="url(#{p}-foil-gold)" stroke-width="4" '
             f'd="M300,262 C228,214 116,206 40,228 L28,346 C116,326 228,334 300,372 '
             f'C372,334 484,326 572,346 L560,228 C484,206 372,214 300,262 Z"/>')
    pages = []
    for i, (dy, spread) in enumerate([(18, 0.98), (12, 0.99), (6, 1.0), (0, 1.0)]):
        for side in (-1, 1):
            pages.append(
                f'<path fill="url(#{p}-page)" stroke="#b8904a" stroke-width="{1.5 if i < 3 else 2.5}" '
                f'stroke-linejoin="round" d="{page(side, dy, spread)}"/>')
    # gilt text-line hints on the top page
    lines = []
    for k in range(4):
        y = 238 + k * 18
        lines.append(f'<path fill="none" stroke="#b8904a" stroke-opacity="0.45" stroke-width="2" '
                     f'd="M286,{y + 8} C250,{y - 12} 190,{y - 18} 120,{y - 2}"/>')
        lines.append(f'<path fill="none" stroke="#b8904a" stroke-opacity="0.45" stroke-width="2" '
                     f'd="M314,{y + 8} C350,{y - 12} 410,{y - 18} 480,{y - 2}"/>')
    heart = (
        f'<path fill="none" stroke="#000" stroke-opacity="0.5" stroke-width="30" '
        f'filter="url(#{p}-blur)" transform="translate(0,14)" d="{HEART_D}"/>'
        f'<path fill="none" stroke="{GREEN_900}" stroke-width="30" stroke-linejoin="round" '
        f'transform="translate(0,5)" d="{HEART_D}"/>'
        f'<path fill="none" stroke="url(#{p}-foil-emerald)" stroke-width="26" '
        f'stroke-linejoin="round" d="{HEART_D}"/>'
        f'<path fill="none" stroke="{HEART_RUBY}" stroke-width="5" stroke-linejoin="round" '
        f'transform="translate(300,155) scale(0.78) translate(-300,-155)" d="{HEART_D}"/>'
        f'<path fill="none" stroke="#ffffff" stroke-opacity="0.55" stroke-width="3" '
        f'stroke-linecap="round" d="M214,96 C222,72 244,62 262,64"/>'
    )
    return "\n    ".join([cover, heart, *pages, *lines])


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
    Transparent background: place on forest-night, ink or green-950.
    Minimum size: 48px wide (favicon uses monogram-stamp.svg instead).
  -->
  <defs>
{v3_defs(p)}  </defs>
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
    p1 = centred(fraunces, "PERPUSTAKAAN", 92, 20, 800, 560)
    p2 = centred(fraunces, "HATI", 236, 26, 800, 790)
    pb = centred(inter, "BY @RAHIMAM", 26, 9, 800, 858)
    pt = centred(fraunces_it, "Karya untuk jiwa yang pernah terluka", 40, 0.5, 800, 930)
    bw = text_width(inter, "BY @RAHIMAM", 26, 9) / 2

    extrude = "\n".join(
        f'  <path fill="rgb({18 + i},{61 + i * 3},{42 + i * 2})" transform="translate(0,{10 - i})" d="{p2}"/>'
        for i in range(0, 10, 2))

    body = f"""  <!--
    Perpustakaan Hati — cinematic lockup (Design System 3.0 "Gilded Grove")
    Source: docs/brand/visual-identity.md -> "Design System 3.0"
    Green leads: forest-night ground, emerald glow, emerald-foil HATI.
    Gold frames: gold-foil PERPUSTAKAAN, gilt rules, gold byline.
    Use: Threads/IG headers, store hero, video opener, posters.
    NOT for: site header at < 320px wide (use wordmark-primary.svg).
  -->
  <defs>
{v3_defs(p)}  </defs>
{stage(p, W, H, 360)}

  <g transform="translate(560,92) scale(0.8)">
    {emblem(p)}
  </g>

  <!-- PERPUSTAKAAN — gold foil with a dark cast shadow -->
  <path fill="#000" opacity="0.55" filter="url(#{p}-blur)" transform="translate(0,10)" d="{p1}"/>
  <path fill="#5a4320" transform="translate(0,3)" d="{p1}"/>
  <path fill="url(#{p}-foil-gold)" d="{p1}"/>

  <!-- HATI — emerald foil, extruded in green-900. The gold rim is a gold
       copy peeking 3px above the face (a stroke would trace the variable
       font's overlapping contours, e.g. the H crossbar). -->
  <path fill="#000" opacity="0.6" filter="url(#{p}-blur)" transform="translate(0,22)" d="{p2}"/>
{extrude}
  <path fill="url(#{p}-foil-gold)" transform="translate(0,-3)" d="{p2}"/>
  <path fill="url(#{p}-foil-emerald)" d="{p2}"/>

  {flank(800, 849, bw + 26, 250, GOLD)}
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
    """Scalloped tier seals (one per tier). Tier colour is the fill; the
    rim is foil. Label contrast is checked by check-contrast.py."""
    names = []
    for fname, top, main, bottom, fill, fg, rim in SEALS:
        p = "phs-" + fname.removeprefix("seal-").removesuffix(".svg")
        pt = centred(inter, top, 34, 10, 300, 252)
        pm = fitted(fraunces, main, 92, 6, 300, 350, 330)
        pbm = centred(inter, bottom, 26, 7, 300, 426)
        scallop = scallop_path(300, 300, 262, 40, 7)
        body = f"""  <!--
    Perpustakaan Hati — tier seal "{top} {main}" (Design System 3.0)
    Source: docs/brand/tier-naming.md (tier colour is fixed)
    Use: eBook covers, store cards, Threads promo cards. Min 96px wide.
  -->
  <defs>
{v3_defs(p)}  </defs>
  <path fill="#000" opacity="0.45" filter="url(#{p}-blur)" transform="translate(0,14)" d="{scallop}"/>
  <path fill="url(#{p}-{rim})" d="{scallop}"/>
  <circle cx="300" cy="300" r="226" fill="{fill}"/>
  <circle cx="300" cy="300" r="226" fill="url(#{p}-vignette)" opacity="0.5"/>
  <circle cx="300" cy="300" r="206" fill="none" stroke="url(#{p}-{rim})" stroke-width="3"
          stroke-dasharray="2 9" stroke-linecap="round"/>
  <g transform="translate(246,128) scale(0.18)">
    {emblem(p)}
  </g>
  <path fill="{fg}" d="{pt}"/>
  <path fill="{fg}" d="{pm}"/>
  <path fill="{fg}" fill-opacity="0.6" d="M210,386 L390,386 L390,388 L210,388 Z"/>
  <path fill="{fg}" d="{pbm}"/>
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
    build_wordmark(fraunces, inter)
    build_monogram(fraunces, inter)
    build_cop_stamp(fraunces, inter)
    build_wordmark_3d(fraunces, inter)
    build_emblem()
    build_lockup_cinematic(fraunces, fraunces_it, inter)
    seals = build_seals(fraunces, inter)
    for name in ("wordmark-primary.svg", "monogram-stamp.svg", "cop-stamp.svg",
                 "wordmark-3d.svg", "emblem-book-heart.svg", "lockup-cinematic.svg",
                 *seals):
        print("wrote docs/brand/assets/" + name)


if __name__ == "__main__":
    main()
