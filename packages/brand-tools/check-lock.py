#!/usr/bin/env python3
"""Perpustakaan Hati — design-system consistency check.

The system is NOT hard-locked. This script is an advisory reviewer: it reports
drift (new assets, removed assets, missing tokens, references to retired 2.0
assets, files changed since the last sanctioned baseline) but never blocks a
build. Brand discipline lives in the docs, not in a checksum gate.

Usage:
    uv run --no-project python packages/brand-tools/check-lock.py            # advisory, always exit 0
    uv run --no-project python packages/brand-tools/check-lock.py --strict    # exit 1 on warnings (opt-in CI gate)
    uv run --no-project python packages/brand-tools/check-lock.py --update    # refresh the baseline checksums

Environment:
    PH_CHECK_ROOT   override the repo root (used by the tests)
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("PH_CHECK_ROOT") or Path(__file__).resolve().parents[2])
BASELINE_NAME = "design-system.baseline.json"

ASSETS = {
    "cop-stamp.svg", "emblem-book-heart.svg", "lockup-cinematic.svg",
    "monogram-stamp.svg", "seal-edisi-membangun.svg", "seal-edisi-poket.svg",
    "seal-teman-hidup.svg", "aje",
}
TRACKED = [
    "docs/brand/design-tokens.css",
    "docs/brand/DESIGN-SYSTEM.md",
    "docs/brand/doop-guideline.md",
    "packages/ui/tailwind.config.js",
    "packages/ui/shadcn-theme.css",
    "packages/brand-tools/fonts/FrauncesDisplay.woff2",
    "packages/brand-tools/fonts/FrauncesDisplayItalic.woff2",
    "packages/brand-tools/fonts/InterUI.woff2",
    "packages/brand-tools/fonts/SourceSerifText.woff2",
    *[f"docs/brand/assets/{a}" for a in sorted(ASSETS) if a != "aje"],
    "docs/brand/assets/aje/aje-turtle-emerald.svg",
    "docs/brand/assets/aje/aje-turtle-noir.svg",
    "docs/brand/aje.md",
]
REMOVED = ["wordmark-primary", "wordmark-3d", "design-system-sheet.html",
           "design-system-2-1"]
REQUIRED_TOKENS = ["--forest-night", "--foil-emerald", "--foil-gold", "--heart-ruby",
                   "--depth-emerald", "--weight-hero", "--green-500", "--ph-system-version"]
SCAN = [".md", ".html", ".css", ".js", ".py", ".json"]
SKIP = {".git", "node_modules", ".claude", ".idea", ".vscode", ".ruff_cache",
        "tests", "__pycache__"}
SELF = {"check-lock.py", BASELINE_NAME, "DESIGN-SYSTEM.md"}
# Files that deliberately name retired assets to say "do not bring these back".
RETIREMENT_DOCS = {"DESIGN-SYSTEM.md", "visual-identity.md"}
CURRENT_VERSION = "3.2"
CURRENT_SHOWCASE = "docs/brand/preview/design-system-3-1.png"
CURRENT_SHOWCASE_REFERENCE = "preview/design-system-3-1.png"
ACTIVE_TEMPLATES = (
    "content/threads/templates/quote-card.html",
    "content/threads/templates/quote-card-b.html",
    "content/threads/templates/carousel.html",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def baseline_path(root: Path) -> Path:
    """The baseline lives beside this script, but inside a sandboxed root."""
    if root == Path(__file__).resolve().parents[2]:
        return Path(__file__).with_name(BASELINE_NAME)
    return root / "packages/brand-tools" / BASELINE_NAME


def collect(root: Path) -> tuple[list[str], list[str]]:
    """Return (warnings, errors).

    Warnings are advisory drift signals. Errors are conditions the checker
    cannot judge at all (e.g. the token file is missing).
    """
    warnings: list[str] = []
    errors: list[str] = []

    assets_dir = root / "docs/brand/assets"
    if not assets_dir.is_dir():
        errors.append("missing directory: docs/brand/assets")
        return warnings, errors

    present = {p.name for p in assets_dir.iterdir()}
    for extra in sorted(present - ASSETS):
        warnings.append(f"unsanctioned asset: docs/brand/assets/{extra}")
    for gone in sorted(ASSETS - present):
        warnings.append(f"missing asset: docs/brand/assets/{gone}")

    tokens_path = root / "docs/brand/design-tokens.css"
    if not tokens_path.exists():
        errors.append("missing file: docs/brand/design-tokens.css")
    else:
        tokens = tokens_path.read_text()
        for t in REQUIRED_TOKENS:
            if t + ":" not in tokens:
                warnings.append(f"missing token {t}")
        if f"--ph-system-version: '{CURRENT_VERSION}.0'" not in tokens:
            warnings.append(
                f"current version token is not Design System {CURRENT_VERSION}"
            )

    design_doc = root / "docs/brand/DESIGN-SYSTEM.md"
    if design_doc.exists():
        text = design_doc.read_text(errors="ignore")
        if "design-system-3-0.png" in text:
            warnings.append("stale showcase reference: design-system-3-0.png")
        if CURRENT_SHOWCASE_REFERENCE not in text:
            warnings.append(
                f"current showcase is not referenced: {CURRENT_SHOWCASE_REFERENCE}"
            )

    showcase = root / CURRENT_SHOWCASE
    if not showcase.exists():
        warnings.append(f"missing current showcase: {CURRENT_SHOWCASE}")

    theme = root / "docs/brand/brand-theme.md"
    if theme.exists():
        text = theme.read_text(errors="ignore").lower()
        if "gold leads" in text or "gold stays the primary accent" in text:
            warnings.append("brand guidance is not green-led")

    doop = root / "docs/brand/doop-guideline.md"
    if doop.exists():
        text = doop.read_text(errors="ignore").lower()
        if "fonts.googleapis.com" in text or "fonts.gstatic.com" in text:
            warnings.append("Doop guidance prescribes Google Fonts runtime loading")

    for relative in ACTIVE_TEMPLATES:
        template = root / relative
        if not template.exists():
            warnings.append(f"missing active template: {relative}")
            continue
        text = template.read_text(errors="ignore").lower()
        if "fonts.googleapis.com" in text or "fonts.gstatic.com" in text:
            warnings.append(f"active template uses Google Fonts: {relative}")

    for path in root.rglob("*"):
        if (not path.is_file() or path.suffix not in SCAN or path.name in SELF
                or SKIP & set(path.relative_to(root).parts)
                or path.relative_to(root).parts[0].startswith(".")):
            continue
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        for name in REMOVED:
            if name in text and path.name not in RETIREMENT_DOCS:
                warnings.append(f"{path.relative_to(root)} references removed asset '{name}'")

    baseline_file = baseline_path(root)
    baseline: dict[str, str] = {}
    if baseline_file.exists():
        try:
            baseline = json.loads(baseline_file.read_text())
        except json.JSONDecodeError:
            errors.append(f"unreadable baseline: {baseline_file}")

    current = {f: sha(root / f) for f in TRACKED if (root / f).exists()}
    for f, digest in current.items():
        if f not in baseline:
            warnings.append(f"not in baseline: {f}")
        elif baseline[f] != digest:
            warnings.append(f"changed since baseline: {f}")
    for f in baseline.keys() - current.keys():
        warnings.append(f"tracked file missing: {f}")

    return warnings, errors


def main() -> int:
    warnings, errors = collect(ROOT)

    if errors:
        print("DESIGN SYSTEM CHECK: ERROR")
        for e in errors:
            print(f"  ! {e}")
        return 1

    if warnings:
        print(f"DESIGN SYSTEM CHECK: {len(warnings)} warning(s) — advisory only")
        for w in warnings:
            print(f"  - {w}")
        print("The system is not locked: these are notes, not blockers.")
    else:
        print("DESIGN SYSTEM CHECK: ok — no drift detected")

    if "--update" in sys.argv:
        current = {f: sha(ROOT / f) for f in TRACKED if (ROOT / f).exists()}
        target = baseline_path(ROOT)
        target.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")
        print(f"baseline updated: {len(current)} files")
        return 0

    if "--strict" in sys.argv and warnings:
        print("STRICT: treating warnings as failures.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
