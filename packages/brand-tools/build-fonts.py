#!/usr/bin/env python3
"""Perpustakaan Hati — brand font subsetting.

Builds the four self-hosted woff2 brand faces from the upstream variable
fonts, subset to a fixed character set and pinned to the axis values the
brand actually uses.

Why subset at all: the full variable fonts are 2.9 MB combined. The brand
subset is ~360 KB, which matters on a slow phone connection in Malaysia and
keeps the PDF/EPUB build small.

Why pin axes: the brand uses one optical size and one weight range per
face. Pinning `opsz`, `SOFT` and `WONK` removes the unused variation
instances and lets the renderer pick the correct static instance without
guessing. `wght` is deliberately kept as a RANGE — a pinned weight would
make any other weight request silently fall back to a system font.

Usage:
    uv run --no-project --with fonttools --with brotli \
        python packages/brand-tools/build-fonts.py

Requires the upstream variable TTFs in packages/brand-tools/fonts/source/.
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"
SOURCE = FONTS / "source"
OUT = FONTS

# The brand glyph set: full printable ASCII plus the typographic marks the
# Malay copy and the brand itself actually use. Anything outside this set
# silently falls back to a system font at render time — including Greek
# delta (Δ), which the accessibility notes use.
CHARSET = (
    "".join(chr(c) for c in range(0x20, 0x7F))     # printable ASCII
    + "¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿"
    + "ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞß"
    + "àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ"
    + "ŒœŠšŸŽžƒˆ˜–—‘’‚“”„†‡•…‰‹›€™"
    + "←↑→↓↔⇒⇐ΔΩπ"
)

# Not every face carries every mark — Fraunces has no arrows or Greek, and
# Source Serif 4 has no double-headed arrows. Subsetting to a character the
# source font does not contain silently drops it, and the renderer then
# falls back to a system font. So each face keeps only what it actually
# has, and every face must still cover the ASCII + Latin-1 base that the
# Malay copy needs.
REQUIRED = "".join(chr(c) for c in range(0x20, 0x7F)) + "·—–‘’“”…†‡•"


def face_charset(source_path: Path) -> str:
    """The subset charset for one face: what the source font can actually
    render, minus characters no face is expected to need."""
    available = set(TTFont(source_path).getBestCmap())
    wanted = set(CHARSET)
    keep = {c for c in wanted if ord(c) in available}
    keep |= {c for c in REQUIRED if ord(c) in available}
    return "".join(sorted(keep))

# name -> (source file, axis pins, weight range, output file)
# `axis pins` fixes the variation axes at the values the brand uses.
# `wght` is never pinned: it stays a range so any weight resolves correctly.
FACES = {
    "FrauncesDisplay": {
        "source": "Fraunces.ttf",
        "pins": {"opsz": 120, "SOFT": 40, "WONK": 1},
        "wght_range": (400, 700),
        "out": "FrauncesDisplay.woff2",
    },
    "FrauncesDisplayItalic": {
        "source": "Fraunces-Italic.ttf",
        "pins": {"opsz": 120, "SOFT": 0, "WONK": 0},
        "wght_range": (400, 700),
        "out": "FrauncesDisplayItalic.woff2",
    },
    "SourceSerifText": {
        "source": "SourceSerif4.ttf",
        "pins": {"opsz": 14},
        "wght_range": (400, 600),
        "out": "SourceSerifText.woff2",
    },
    "InterUI": {
        "source": "Inter.ttf",
        "pins": {"opsz": 20},
        "wght_range": (400, 700),
        "out": "InterUI.woff2",
    },
}


# Upstream variable fonts, from the Google Fonts repository. The build
# downloads them on demand so the 2.8 MB of source TTFs never have to live
# in the repo — only the ~340 KB subsets are committed.
UPSTREAM = {
    "Fraunces.ttf":
        "https://raw.githubusercontent.com/google/fonts/main/ofl/fraunces/"
        "Fraunces%5BSOFT%2CWONK%2Copsz%2Cwght%5D.ttf",
    "Fraunces-Italic.ttf":
        "https://raw.githubusercontent.com/google/fonts/main/ofl/fraunces/"
        "Fraunces-Italic%5BSOFT%2CWONK%2Copsz%2Cwght%5D.ttf",
    "SourceSerif4.ttf":
        "https://raw.githubusercontent.com/google/fonts/main/ofl/sourceserif4/"
        "SourceSerif4%5Bopsz%2Cwght%5D.ttf",
    "Inter.ttf":
        "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/"
        "Inter%5Bopsz%2Cwght%5D.ttf",
}


def ensure_source(filename: str) -> Path:
    """Return the local path of an upstream variable font, downloading it
    into the (git-ignored) source folder if it is not there yet."""
    path = SOURCE / filename
    if path.exists():
        return path
    url = UPSTREAM[filename]
    print(f"downloading {filename} ...")
    SOURCE.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as response:
        path.write_bytes(response.read())
    print(f"  {path.stat().st_size / 1024:.0f} KB")
    return path


def build(name: str, spec: dict) -> None:
    src = ensure_source(spec["source"])

    font = TTFont(src)

    # 1. pin the non-weight axes, and LIMIT wght to the brand range with
    #    its light end as the new default. The limit must go through the
    #    instancer: it re-solves the outlines and deltas. Merely relabelling
    #    fvar (the old approach) left Fraunces at its upstream default of
    #    900, so "regular" was Black and 700 resolved to 900.
    lo, hi = spec["wght_range"]
    limits = {**spec["pins"], "wght": (lo, lo, hi)}
    inst = instancer.instantiateVariableFont(font, limits, inplace=False)

    # The instancer can leave gvar without a .notdef entry, which makes the
    # subsetter's gvar pass raise KeyError. Give it an empty variation set
    # before subsetting.
    if "gvar" in inst and ".notdef" not in inst["gvar"].variations:
        inst["gvar"].variations[".notdef"] = []

    # 2. subset to the brand charset
    options = subset.Options()
    options.flavor = "woff2"
    options.desubroutinize = True
    options.drop_tables += ["DSIG"]
    options.layout_features = ["kern", "liga", "calt", "ccmp", "locl", "mark", "mkmk"]
    options.name_IDs = ["*"]
    options.notdef_outline = True
    options.recalc_bounds = True
    options.hinting = True
    # Do not stamp the current time into head.modified — that would make
    # every rebuild a different file and `git diff` permanently noisy.
    options.recalc_timestamp = False

    charset = face_charset(src)
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(text=charset)
    subsetter.subset(inst)

    # Pin head timestamps to a fixed value so the build is byte-reproducible.
    epoch = 3600 * 24 * 365 * 25   # 1995-01-01, a fixed arbitrary stamp
    inst["head"].modified = epoch
    inst["head"].created = epoch
    inst.recalcTimestamp = False   # otherwise head.compile() re-stamps "now"

    inst.save(OUT / spec["out"])

    # 4. verify
    check = TTFont(OUT / spec["out"])
    cmap = check.getBestCmap()
    missing = [c for c in charset if c.strip() and ord(c) not in cmap]
    size = (OUT / spec["out"]).stat().st_size
    axes = (
        [(a.axisTag, a.minValue, a.maxValue) for a in check["fvar"].axes]
        if "fvar" in check
        else []
    )
    print(
        f"{name:22} {size/1024:6.1f} KB  axes={axes}"
        + (f"  MISSING {''.join(missing)!r}" if missing else "  charset ok")
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    SOURCE.mkdir(parents=True, exist_ok=True)
    for name, spec in FACES.items():
        build(name, spec)
    total = sum((OUT / s["out"]).stat().st_size for s in FACES.values())
    print(f"total {total/1024:.1f} KB")


if __name__ == "__main__":
    sys.exit(main())
