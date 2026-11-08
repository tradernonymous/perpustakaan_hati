#!/usr/bin/env python3
"""Animated web copies of the Design System 3.1 logos.

Sources (never modified):
    docs/brand/assets/emblem-book-heart.svg
    docs/brand/assets/seal-edisi-poket.svg / -membangun.svg / seal-teman-hidup.svg
    apps/web/public/brand/lockup-hero.svg      (from build-web-lockup.py)
Output:
    apps/web/public/brand/animated/<same name>.svg

The motion is a CSS <style> block embedded in each SVG, so it plays even when
the file is shown with a plain <img> (SVG-as-image runs CSS animation, not
script). Every animation starts from a hidden/offset state using
`animation-fill-mode: backwards` and ENDS ON THE ORIGINAL ARTWORK, so:
  * with prefers-reduced-motion the file is the static logo, identical in
    appearance to the source,
  * nothing is added to the brand mark that the static mark does not have.

Choreography (the same on every mark that contains the emblem):
  1. rise   — the open book lifts 18px into place,
  2. draw   — the emerald heart tube draws itself up out of the spine
              (stroke-dashoffset on pathLength="1"),
  3. trace  — the thin ruby inner line traces after it,
  4. glint  — the star glint twinkles (slow loop; decorative, tiny).
Lockup only:
  5. PERPUSTAKAAN settles in, the HATI extrusion fades up and the HATI face
     lifts out of its own 14px slab (the 3D depth "opens"),
  6. one foil sheen sweeps across HATI (once — brand rule: never looped).
Seals only:
  7. the dashed gilt ring turns slowly.

Run after build-logos.py and build-web-lockup.py:
    uv run --no-project python packages/brand-tools/build-animated-logos.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "docs/brand/assets"
PUBLIC = ROOT / "apps/web/public/brand"
OUT = PUBLIC / "animated"

EASE_OUT = "cubic-bezier(0.16, 1, 0.3, 1)"
EASE_IO = "cubic-bezier(0.65, 0, 0.35, 1)"


def style(extra: str = "") -> str:
    return f"""<style>
    /* build-animated-logos.py: every animation ends on the original artwork */
    @keyframes phx-rise {{ from {{ opacity: 0; transform: translateY(18px); }} }}
    @keyframes phx-draw {{ from {{ stroke-dashoffset: 1; }} to {{ stroke-dashoffset: 0; }} }}
    @keyframes phx-twinkle {{ 0%, 100% {{ opacity: 1; transform: scale(1); }} 50% {{ opacity: 0.35; transform: scale(0.6); }} }}
    .phx-rise {{ animation: phx-rise 0.9s {EASE_OUT} 0.1s backwards; }}
    .phx-draw {{ stroke-dasharray: 1; animation: phx-draw 1.6s {EASE_IO} 0.45s backwards; }}
    .phx-trace {{ stroke-dasharray: 1; animation: phx-draw 1.2s {EASE_IO} 1.35s backwards; }}
    .phx-twinkle {{ transform-box: fill-box; transform-origin: center; animation: phx-twinkle 4.8s ease-in-out 2.6s infinite; }}{extra}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
  </style>"""


LOCKUP_CSS = f"""
    @keyframes phx-fade {{ from {{ opacity: 0; transform: translateY(-14px); }} }}
    @keyframes phx-depth {{ from {{ opacity: 0; }} }}
    @keyframes phx-lift {{ from {{ transform: translate(2.1px, 14px); }} }}
    @keyframes phx-sheen {{ from {{ transform: translateX(-1150px); }} to {{ transform: translateX(0); }} }}
    .phx-fade {{ animation: phx-fade 0.9s {EASE_OUT} 0.9s backwards; }}
    .phx-depth {{ animation: phx-depth 0.6s ease-out 1.25s backwards; }}
    .phx-lift {{ animation: phx-lift 1.1s {EASE_OUT} 1.35s backwards; }}
    .phx-sheen {{ animation: phx-sheen 1.6s {EASE_IO} 2.5s backwards; }}"""

SEAL_CSS = """
    @keyframes phx-turn { to { transform: rotate(360deg); } }
    .phx-turn { transform-box: view-box; transform-origin: 300px 300px; animation: phx-turn 60s linear infinite; }"""


def sub(pattern: str, repl, s: str, what: str, count: int = 1) -> str:
    """re.subn that fails loudly if the source layout changed."""
    out, n = re.subn(pattern, repl, s, count=count, flags=re.S)
    if n != count:
        raise SystemExit(f"build-animated-logos: expected {count} x {what}, found {n}; "
                         "has build-logos.py changed the layer layout?")
    return out


def emblem_motion(s: str) -> str:
    # 7 tube strokes + 1 blurred tube shadow draw on; the ruby line traces after.
    s = sub(r'<path (fill="none" stroke="[^"]*"(?: stroke-opacity="[^"]*")? stroke-width="(?:27|30)")',
            r'<path pathLength="1" class="phx-draw" \1', s, "heart tube stroke", count=8)
    s = sub(r'<path (fill="none" stroke="#c8343c")', r'<path pathLength="1" class="phx-trace" \1', s, "ruby line")
    s = sub(r'<circle ([^>]*fill="url\(#[\w-]+-glint\)")', r'<circle class="phx-twinkle" \1', s, "glint halo")
    s = sub(r'<path (fill="#fffbe8")', r'<path class="phx-twinkle" \1', s, "glint star")
    # the book (the first group in the file) rises into place
    return sub(r'(\n  <g(?: transform="[^"]*")?>.*?\n  </g>)',
               r'\n  <g class="phx-rise">\1\n  </g>', s, "emblem group")


def add_style(s: str, extra: str = "") -> str:
    return sub(r'(<svg [^>]*>)', lambda m: m.group(1) + "\n  " + style(extra), s, "svg root")


def lockup(s: str) -> str:
    s = add_style(emblem_motion(s), LOCKUP_CSS)
    s = sub(r'((?:\n  <use href="#phl-perp"[^\n]*){5})',
            r'\n  <g class="phx-fade">\1\n  </g>', s, "PERPUSTAKAAN block")
    s = sub(r'((?:\n  <use href="#phl-hati"[^\n]*){16})',
            r'\n  <g class="phx-depth">\1\n  </g>', s, "HATI extrusion")
    s = sub(r'((?:\n  <use href="#phl-hati"[^\n]*){2})\n\n</svg>',
            r'\n  <g class="phx-lift">\1\n  </g>\n  <g clip-path="url(#phx-hati-clip)">'
            r'\n    <rect class="phx-sheen" x="1350" y="600" width="170" height="260" fill="url(#phx-sheen-band)"/>'
            r'\n  </g>\n</svg>', s, "HATI face")
    return sub(r'\n  </defs>',
               '\n    <clipPath id="phx-hati-clip"><use href="#phl-hati"/></clipPath>'
               '\n    <linearGradient id="phx-sheen-band" x1="0" y1="0" x2="1" y2="0" gradientTransform="skewX(-18)">'
               '\n      <stop offset="0" stop-color="#fff" stop-opacity="0"/>'
               '\n      <stop offset="0.5" stop-color="#fff" stop-opacity="0.55"/>'
               '\n      <stop offset="1" stop-color="#fff" stop-opacity="0"/>'
               '\n    </linearGradient>\n  </defs>', s, "defs end")


def seal(s: str) -> str:
    s = add_style(emblem_motion(s), SEAL_CSS)
    return sub(r'<circle ([^>]*stroke-dasharray="2 9"[^>]*/>)', r'<circle class="phx-turn" \1', s, "gilt ring")


def emblem(s: str) -> str:
    return add_style(emblem_motion(s))


JOBS = {
    "emblem-book-heart.svg": (ASSETS, emblem),
    "lockup-hero.svg": (PUBLIC, lockup),
    "seal-edisi-poket.svg": (ASSETS, seal),
    "seal-edisi-membangun.svg": (ASSETS, seal),
    "seal-teman-hidup.svg": (ASSETS, seal),
}


def render(name: str) -> str:
    src_dir, fn = JOBS[name]
    return fn((src_dir / name).read_text(encoding="utf-8"))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name in JOBS:
        (OUT / name).write_text(render(name), encoding="utf-8")
        print(f"wrote {(OUT / name).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
