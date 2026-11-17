#!/usr/bin/env python3
"""Perpustakaan Hati — palette contrast & colour-blindness checker.

Computes, for every token pair that matters in the brand:

  * WCAG 2.1 contrast ratio (relative luminance, not estimated)
  * CIE76 Delta-E between the pair under normal vision and under simulated
    protanopia / deuteranopia / tritanopia

Usage:
    uv run --no-project python packages/brand-tools/check-contrast.py
    uv run --no-project python packages/brand-tools/check-contrast.py --json

Exit code is non-zero if any *required* pair fails its target, so this can be
wired into CI or a pre-commit hook.
"""
from __future__ import annotations

import json
import sys

# --------------------------------------------------------------------------
# colour maths
# --------------------------------------------------------------------------


def hex_to_rgb(value: str) -> tuple[float, float, float]:
    v = value.strip().lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    if len(v) != 6:
        raise ValueError(f"not a hex colour: {value}")
    return tuple(int(v[i : i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def _linearise(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(value: str) -> float:
    r, g, b = (_linearise(c) for c in hex_to_rgb(value))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def rgb_to_lab(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    r, g, b = (_linearise(c) for c in rgb)
    x = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047
    y = (r * 0.2126 + g * 0.7152 + b * 0.0722) / 1.00000
    z = (r * 0.0193 + g * 0.1192 + b * 0.9505) / 1.08883

    def f(t: float) -> float:
        return t ** (1 / 3) if t > 216 / 24389 else (841 / 108) * t + 4 / 29

    fx, fy, fz = f(x), f(y), f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def delta_e(a: str, b: str) -> float:
    la, lb = rgb_to_lab(hex_to_rgb(a)), rgb_to_lab(hex_to_rgb(b))
    return sum((x - y) ** 2 for x, y in zip(la, lb)) ** 0.5


# --------------------------------------------------------------------------
# colour-blindness simulation (Brettel / Viénot-style LMS matrices)
# --------------------------------------------------------------------------

# Matrices operate on linear RGB. Each row is the new R, G, B contribution.
CVD_MATRICES: dict[str, tuple[tuple[float, float, float], ...]] = {
    "protanopia": (
        (0.11238, 0.88762, 0.0),
        (0.07276, 0.92724, 0.0),
        (0.00390, 0.00000, 0.99610),
    ),
    "deuteranopia": (
        (0.29275, 0.70725, 0.0),
        (0.04474, 0.95526, 0.0),
        (0.0, 0.0, 1.0),
    ),
    "tritanopia": (
        (1.0, 0.0, 0.0),
        (0.03670, 0.96330, 0.0),
        (0.0, 0.0, 1.0),
    ),
}


def simulate(value: str, kind: str) -> str:
    m = CVD_MATRICES[kind]
    lin = [_linearise(c) for c in hex_to_rgb(value)]
    out = []
    for row in m:
        v = sum(row[i] * lin[i] for i in range(3))
        v = max(0.0, min(1.0, v))
        v = 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055
        out.append(round(max(0, min(255, round(v * 255)))))
    return "#%02x%02x%02x" % tuple(out)


# --------------------------------------------------------------------------
# the palette
# --------------------------------------------------------------------------

PALETTE = {
    # grounds
    "ink": "#0a0a0c",
    "ink-raised": "#121416",
    "ink-soft": "#17171a",
    "ink-elevated": "#202226",
    # green ramp (Living Green)
    "green-950": "#0b2418",
    "green-900": "#123d2a",
    "green-800": "#1d5a3d",
    "green-700": "#2d7954",
    "green-600": "#3f9167",
    "green-500": "#5b9b7d",
    "green-400": "#7db895",
    "green-300": "#a7d3b6",
    "green-200": "#cbe8d5",
    "green-100": "#e4f4e9",
    "lime-glow": "#c8e986",
    "mint-glass": "#9de1c1",
    # legacy / brand
    "gold": "#c9a86a",
    "gold-light": "#e9cea2",
    "gold-deep": "#a07b45",
    "burgundy": "#5c1e17",
    "burgundy-deep": "#3f1711",
    "burgundy-light": "#c25a58",
    "terracotta": "#da725b",
    "cream": "#fdfee6",
    "paper": "#f4efe6",
    "linen": "#eae2d4",
    "text-on-dark": "#e6e2da",
    "text-muted-on-dark": "#a49c8d",
    "burgundy-text-dark": "#f0a3a0",
    "burgundy-text-light": "#8a2f2f",
    "text-on-light": "#0a0a0c",
    "stone-light": "#a49c8d",
    "sepia": "#573a2f",
    # Design System 3.1 "Gilded Grove"
    "forest-night": "#07140d",
    "forest-raised": "#0d2117",
    "forest-soft": "#142c20",
    "foil-emerald-low": "#2d7954",
    "foil-gold-low": "#9a7638",
    "heart-ruby": "#c8343c",
    "lantern": "#f2b85c",
    # Design System 3.2 "Daylight Grove" — the light page layer
    "daylight": "#f7f4ea",
    "daylight-raised": "#fffdf6",
    "sage": "#e9f0e6",
    "daylight-edge": "#d2c4a8",
    "ink-grove": "#12251b",
    "muted-grove": "#4f5f53",
    "gold-ink": "#7a5a22",
    "gold-ink-soft": "#96742f",
    # Design System 3.5 "Ladder of Light" — the per-tier ramp.
    # One set per tier: ink (on light), on-dark, fill, band, edge.
    "tier-poket-ink": "#1d5a3d",
    "tier-poket-on-dark": "#7db895",
    "tier-poket-fill": "#2d7954",
    "tier-poket-band": "#e4f4e9",
    "tier-poket-edge": "#8fc0a5",
    "tier-membangun-ink": "#7a5a22",
    "tier-membangun-on-dark": "#e9cea2",
    "tier-membangun-fill": "#c9a86a",
    "tier-membangun-band": "#f7efdd",
    "tier-membangun-edge": "#c9a86a",
    "tier-teman-hidup-ink": "#5c1e17",
    "tier-teman-hidup-on-dark": "#d4746f",
    "tier-teman-hidup-fill": "#a34a56",
    "tier-teman-hidup-band": "#f3e3e0",
    "tier-teman-hidup-edge": "#c9978f",
    # AJE — Armazas Jaya Enterprise branch (black + gold)
    "aje-black": "#0a0a0a",
    "aje-black-raised": "#151515",
    "aje-gold": "#c9a86a",
    "aje-gold-light": "#e9cea2",
    "aje-gold-deep": "#8a6224",
    "aje-cream": "#fdfee6",
}

# (foreground, background, required ratio, human reason)
REQUIRED_PAIRS = [
    ("text-on-dark", "ink", 4.5, "body copy on the main ground"),
    ("text-on-dark", "ink-soft", 4.5, "body copy on card surface"),
    ("text-on-dark", "ink-elevated", 4.5, "body copy on overlay surface"),
    ("gold-light", "ink", 4.5, "headings on the main ground"),
    ("gold-light", "ink-soft", 4.5, "headings on card surface"),
    ("green-400", "ink", 4.5, "green text / icon on the main ground"),
    ("green-300", "ink", 4.5, "green text on the main ground"),
    ("lime-glow", "ink", 4.5, "3D rim light on the main ground"),
    ("burgundy-light", "ink", 4.5, "premium tier badge text on the main ground"),
    ("terracotta", "ink", 4.5, "CTA text on the main ground"),
    ("ink", "green-500", 4.5, "ink label on a green fill"),
    ("ink", "green-600", 4.5, "ink label on a green fill"),
    ("ink", "gold", 4.5, "ink label on a gold fill"),
    ("ink", "cream", 4.5, "ink body copy on a cream ground"),
    ("ink", "paper", 4.5, "ink body copy on a paper ground"),
    ("ink", "linen", 4.5, "ink body copy on a linen ground"),
    ("green-900", "cream", 4.5, "green heading on a cream ground"),
    ("green-800", "cream", 4.5, "green body copy on a cream ground"),
    ("green-900", "paper", 4.5, "green heading on a paper ground"),
    ("green-800", "paper", 4.5, "green body copy on a paper ground"),
    ("burgundy", "cream", 4.5, "burgundy text on a cream ground"),
    ("sepia", "cream", 4.5, "sepia text on a cream ground"),
    # ---- Design System 3.1 "Gilded Grove" ------------------------------
    # forest-night replaces ink as the default dark ground: a green-black,
    # so even "empty" space reads green.
    ("text-on-dark", "forest-night", 4.5, "body copy on the v3 main ground"),
    ("text-on-dark", "forest-raised", 4.5, "body copy on a v3 card"),
    ("text-on-dark", "forest-soft", 4.5, "body copy on a v3 overlay"),
    ("gold-light", "forest-night", 4.5, "headings on the v3 main ground"),
    ("green-400", "forest-night", 4.5, "green text on the v3 main ground"),
    ("green-300", "forest-raised", 4.5, "green text on a v3 card"),
    ("stone-light", "forest-night", 4.5, "muted copy on the v3 ground"),
    # ---- Design System 3.7 "Dark Grove": storefront default surface ----
    ("text-muted-on-dark", "forest-night", 4.5, "muted copy on the dark page ground"),
    ("text-muted-on-dark", "forest-raised", 4.5, "muted copy on a dark card"),
    ("text-muted-on-dark", "forest-soft", 4.5, "muted copy / placeholder on a dark input"),
    ("gold-light", "forest-raised", 4.5, "gold heading on a dark card"),
    ("green-300", "forest-soft", 4.5, "green label on a dark input"),
    ("burgundy-text-dark", "forest-night", 4.5, "error text on the dark page ground"),
    ("burgundy-text-dark", "forest-raised", 4.5, "error text on a dark card"),
    ("burgundy-text-dark", "forest-soft", 4.5, "error text on a dark input"),
    ("burgundy-text-light", "daylight", 4.5, "error text on the ivory ground"),
    ("green-400", "forest-soft", 3.0, "progress fill against its dark track (non-text)"),
    # foil gradients are display-size only: their darkest stop must still
    # clear 3:1 (WCAG large text) so the word never drops out.
    ("foil-emerald-low", "forest-night", 3.0, "darkest emerald-foil stop, display type"),
    ("foil-gold-low", "forest-night", 3.0, "darkest gold-foil stop, display type"),
    # non-text graphics (WCAG 1.4.11): 3:1 against the ground
    ("heart-ruby", "forest-night", 3.0, "emblem heart against the v3 ground"),
    ("lantern", "forest-night", 3.0, "lantern glow core against the v3 ground"),
    # components
    ("gold-light", "green-800", 4.5, "ribbon banner label on emerald"),
    ("cream", "green-700", 4.5, "seal badge label on emerald"),
    ("cream", "burgundy", 4.5, "seal badge label on burgundy"),
    ("ink", "gold", 4.5, "seal badge label on gold"),
    ("forest-night", "green-500", 4.5, "forest label on a green CTA"),
    # ---- Design System 3.2 "Daylight Grove" ---------------------------
    ("ink-grove", "daylight", 4.5, "body copy on the ivory page ground"),
    ("muted-grove", "daylight", 4.5, "muted copy on the ivory page ground"),
    ("gold-ink", "daylight", 4.5, "gold small caps / rules text on ivory"),
    ("gold-ink", "sage", 4.5, "gold text on the alternated sage band"),
    ("green-800", "daylight", 4.5, "green body copy on ivory"),
    ("green-900", "sage", 4.5, "green heading on the sage band"),
    ("ink-grove", "daylight-raised", 4.5, "card copy on a light card"),
    ("daylight-edge", "daylight", 1.5, "warm hairline against the ground"),
    # ---- AJE branch ----------------------------------------------------
    ("aje-cream", "aje-black", 4.5, "AJE body copy on AJE black"),
    ("aje-gold-light", "aje-black", 4.5, "AJE headings on AJE black"),
    ("aje-gold", "aje-black", 3.0, "AJE gold rule / mark on AJE black (graphic)"),
    ("aje-black", "aje-gold", 4.5, "AJE CTA label on gold"),
    ("aje-gold-deep", "aje-cream", 4.5, "AJE gold text on AJE cream"),
    # ---- Design System 3.5 "Ladder of Light" — the per-tier ramp ------
    # Each tier's ink must read as text on every light ground the
    # storefront puts it on.
    ("tier-poket-ink", "daylight", 4.5, "Edisi Poket tier text on ivory"),
    ("tier-poket-ink", "sage", 4.5, "Edisi Poket tier text on the sage band"),
    ("tier-poket-ink", "daylight-raised", 4.5, "Edisi Poket tier text on a light card"),
    ("tier-membangun-ink", "daylight", 4.5, "Edisi Membangun tier text on ivory"),
    ("tier-membangun-ink", "sage", 4.5, "Edisi Membangun tier text on the sage band"),
    ("tier-membangun-ink", "daylight-raised", 4.5, "Edisi Membangun tier text on a light card"),
    ("tier-teman-hidup-ink", "daylight", 4.5, "Teman Hidup tier text on ivory"),
    ("tier-teman-hidup-ink", "sage", 4.5, "Teman Hidup tier text on the sage band"),
    ("tier-teman-hidup-ink", "daylight-raised", 4.5, "Teman Hidup tier text on a light card"),
    # ...and on its own pale band.
    ("tier-poket-ink", "tier-poket-band", 4.5, "Edisi Poket tier text on its own band"),
    ("tier-membangun-ink", "tier-membangun-band", 4.5, "Edisi Membangun tier text on its own band"),
    ("tier-teman-hidup-ink", "tier-teman-hidup-band", 4.5, "Teman Hidup tier text on its own band"),
    # The on-dark variants carry tier names on the dark forest stage.
    ("tier-poket-on-dark", "forest-night", 4.5, "Edisi Poket tier text on the dark stage"),
    ("tier-poket-on-dark", "forest-raised", 4.5, "Edisi Poket tier text on a dark card"),
    ("tier-poket-on-dark", "forest-soft", 4.5, "Edisi Poket tier text on a dark overlay"),
    ("tier-membangun-on-dark", "forest-night", 4.5, "Edisi Membangun tier text on the dark stage"),
    ("tier-membangun-on-dark", "forest-raised", 4.5, "Edisi Membangun tier text on a dark card"),
    ("tier-membangun-on-dark", "forest-soft", 4.5, "Edisi Membangun tier text on a dark overlay"),
    ("tier-teman-hidup-on-dark", "forest-night", 4.5, "Teman Hidup tier text on the dark stage"),
    ("tier-teman-hidup-on-dark", "forest-raised", 4.5, "Teman Hidup tier text on a dark card"),
    ("tier-teman-hidup-on-dark", "forest-soft", 4.5, "Teman Hidup tier text on a dark overlay"),
    # The tier fill is a solid block with a label sitting on it.
    ("cream", "tier-poket-fill", 4.5, "label on the Edisi Poket tier fill"),
    ("ink", "tier-membangun-fill", 4.5, "label on the Edisi Membangun tier fill"),
    ("cream", "tier-teman-hidup-fill", 4.5, "label on the Teman Hidup tier fill"),
    # As a non-text graphic on the dark stage (WCAG 1.4.11).
    ("tier-poket-fill", "forest-night", 3.0, "Edisi Poket tier block on the dark stage"),
    ("tier-membangun-fill", "forest-night", 3.0, "Edisi Membangun tier block on the dark stage"),
    ("tier-teman-hidup-fill", "forest-night", 3.0, "Teman Hidup tier block on the dark stage"),
    # The hairline that separates a tier band from its neighbours.
    ("tier-poket-edge", "tier-poket-band", 1.5, "Edisi Poket band edge"),
    ("tier-membangun-edge", "tier-membangun-band", 1.5, "Edisi Membangun band edge"),
    ("tier-teman-hidup-edge", "tier-teman-hidup-band", 1.5, "Teman Hidup band edge"),
    # ---- Design System 3.6 "Precise Grove" ----------------------------
    # The focus ring is a non-text indicator: WCAG 2.2 SC 2.4.11 asks for
    # 3:1 against the ground the ring is drawn on.
    ("green-300", "forest-night", 3.0, "3.6 focus ring on the dark stage"),
    ("green-300", "forest-raised", 3.0, "3.6 focus ring on a dark card"),
    ("green-800", "daylight", 3.0, "3.6 focus ring on the ivory ground"),
    ("green-800", "sage", 3.0, "3.6 focus ring on the sage band"),
    # Selected text is still text: 4.5:1 on the selection fill.
    ("cream", "green-800", 4.5, "3.6 selected text on the dark selection fill"),
    ("ink-grove", "green-200", 4.5, "3.6 selected text on the light selection fill"),
    # prefers-contrast: more raises the hairline to a readable edge.
    ("gold-ink-soft", "daylight", 3.0, "3.6 high-contrast hairline on ivory"),
]

# tier colours must remain tellable apart without relying on hue alone
TIER_PAIRS = [
    ("green-500", "gold", "Edisi Poket vs Edisi Membangun"),
    ("gold", "burgundy-light", "Edisi Membangun vs Teman Hidup"),
    ("green-500", "burgundy-light", "Edisi Poket vs Teman Hidup"),
    # The 3.5 tier ramp, checked in the three roles the storefront uses.
    ("tier-poket-ink", "tier-membangun-ink", "tier ink: Edisi Poket vs Edisi Membangun"),
    ("tier-membangun-ink", "tier-teman-hidup-ink", "tier ink: Edisi Membangun vs Teman Hidup"),
    ("tier-poket-ink", "tier-teman-hidup-ink", "tier ink: Edisi Poket vs Teman Hidup"),
    ("tier-poket-on-dark", "tier-membangun-on-dark", "tier on-dark: Edisi Poket vs Edisi Membangun"),
    ("tier-membangun-on-dark", "tier-teman-hidup-on-dark", "tier on-dark: Edisi Membangun vs Teman Hidup"),
    ("tier-poket-on-dark", "tier-teman-hidup-on-dark", "tier on-dark: Edisi Poket vs Teman Hidup"),
    ("tier-poket-fill", "tier-membangun-fill", "tier fill: Edisi Poket vs Edisi Membangun"),
    ("tier-membangun-fill", "tier-teman-hidup-fill", "tier fill: Edisi Membangun vs Teman Hidup"),
    ("tier-poket-fill", "tier-teman-hidup-fill", "tier fill: Edisi Poket vs Teman Hidup"),
]

DELTA_E_MIN = 10.0


def grade(ratio: float) -> str:
    if ratio >= 7:
        return "AAA"
    if ratio >= 4.5:
        return "AA"
    if ratio >= 3:
        return "AA-large"
    return "FAIL"


def main() -> int:
    as_json = "--json" in sys.argv
    failures: list[str] = []
    rows: list[dict] = []

    for fg, bg, need, why in REQUIRED_PAIRS:
        ratio = contrast(PALETTE[fg], PALETTE[bg])
        ok = ratio >= need
        rows.append(
            {
                "kind": "contrast",
                "fg": fg,
                "bg": bg,
                "ratio": round(ratio, 2),
                "required": need,
                "grade": grade(ratio),
                "pass": ok,
                "note": why,
            }
        )
        if not ok:
            failures.append(f"{fg} on {bg}: {ratio:.2f}:1 (needs {need}:1) — {why}")

    for a, b, why in TIER_PAIRS:
        worst = float("inf")
        worst_kind = ""
        per_kind = {}
        for kind in ("protanopia", "deuteranopia", "tritanopia"):
            de = delta_e(simulate(PALETTE[a], kind), simulate(PALETTE[b], kind))
            per_kind[kind] = round(de, 1)
            if de < worst:
                worst, worst_kind = de, kind
        normal = delta_e(PALETTE[a], PALETTE[b])
        ok = worst >= DELTA_E_MIN
        rows.append(
            {
                "kind": "cvd",
                "fg": a,
                "bg": b,
                "normal_de": round(normal, 1),
                "worst_de": round(worst, 1),
                "worst_kind": worst_kind,
                "per_kind": per_kind,
                "pass": ok,
                "note": why,
            }
        )
        if not ok:
            failures.append(
                f"{a} vs {b}: worst CVD dE {worst:.1f} ({worst_kind}) — needs {DELTA_E_MIN}"
            )

    if as_json:
        print(json.dumps({"rows": rows, "failures": failures}, indent=2))
    else:
        print("=" * 78)
        print("CONTRAST (WCAG 2.1) — required pairs")
        print("=" * 78)
        for r in rows:
            if r["kind"] != "contrast":
                continue
            mark = "ok  " if r["pass"] else "FAIL"
            print(
                f"{mark} {r['fg']:>16} on {r['bg']:<14} {r['ratio']:>6.2f}:1 "
                f"{r['grade']:<9} (needs {r['required']}) — {r['note']}"
            )
        print()
        print("=" * 78)
        print("COLOUR-BLINDNESS (tier separation, CIE76 dE, threshold 10)")
        print("=" * 78)
        for r in rows:
            if r["kind"] != "cvd":
                continue
            mark = "ok  " if r["pass"] else "FAIL"
            print(
                f"{mark} {r['fg']:>16} vs {r['bg']:<16} normal {r['normal_de']:>5.1f}  "
                f"worst {r['worst_de']:>5.1f} ({r['worst_kind']:<13}) — {r['note']}"
            )
            print(f"       {r['per_kind']}")
        print()
        print("=" * 78)
        print("RAMP REPORT (every green step on every ground)")
        print("=" * 78)
        greens = [k for k in PALETTE if k.startswith("green-") or k in ("lime-glow", "mint-glass")]
        for ground in ("forest-night", "ink", "ink-soft", "cream", "paper"):
            print(f"  on {ground}:")
            for g in greens:
                print(f"    {g:<12} {contrast(PALETTE[g], PALETTE[ground]):>6.2f}:1")
        print()
        if failures:
            print(f"FAILURES ({len(failures)}):")
            for f in failures:
                print("  - " + f)
        else:
            print("All required pairs pass.")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
