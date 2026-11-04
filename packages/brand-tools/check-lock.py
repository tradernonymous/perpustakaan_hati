#!/usr/bin/env python3
"""Perpustakaan Hati — design-system lock check.

Design System 3.1 "Gilded Grove" is LOCKED. This script fails (exit 1) if:
  1. the set of files in docs/brand/assets is not exactly the sanctioned set
  2. any locked file's SHA-256 differs from design-system.lock.json
  3. any file still references a removed (2.0) asset
  4. a required token is missing from design-tokens.css

Changing the system on purpose:
  1. edit the source (tokens / build scripts), rebuild assets
  2. run check-contrast.py and the pytest suite
  3. bump the version in DESIGN-SYSTEM.md
  4. uv run --no-project python packages/brand-tools/check-lock.py --update

Usage:
    uv run --no-project python packages/brand-tools/check-lock.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCK = Path(__file__).with_name("design-system.lock.json")

ASSETS = {
    "cop-stamp.svg", "emblem-book-heart.svg", "lockup-cinematic.svg",
    "monogram-stamp.svg", "seal-edisi-membangun.svg", "seal-edisi-poket.svg",
    "seal-teman-hidup.svg",
}
LOCKED = [
    "docs/brand/design-tokens.css",
    "docs/brand/DESIGN-SYSTEM.md",
    "docs/brand/doop-guideline.md",
    "packages/ui/tailwind.config.js",
    "packages/ui/shadcn-theme.css",
    "packages/brand-tools/fonts/FrauncesDisplay.woff2",
    "packages/brand-tools/fonts/FrauncesDisplayItalic.woff2",
    "packages/brand-tools/fonts/InterUI.woff2",
    "packages/brand-tools/fonts/SourceSerifText.woff2",
    *[f"docs/brand/assets/{a}" for a in sorted(ASSETS)],
]
REMOVED = ["wordmark-primary", "wordmark-3d", "design-system-sheet.html",
           "design-system-2-1"]
REQUIRED_TOKENS = ["--forest-night", "--foil-emerald", "--foil-gold", "--heart-ruby",
                   "--depth-emerald", "--weight-hero", "--green-500", "--ph-lock-version"]
SCAN = [".md", ".html", ".css", ".js", ".py", ".json"]
SKIP = {".git", "node_modules", ".claude", ".idea", ".vscode", ".ruff_cache"}
SELF = {"check-lock.py", "design-system.lock.json", "DESIGN-SYSTEM.md"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    errors: list[str] = []
    present = {p.name for p in (ROOT / "docs/brand/assets").iterdir()}
    for extra in sorted(present - ASSETS):
        errors.append(f"unsanctioned asset: docs/brand/assets/{extra}")
    for gone in sorted(ASSETS - present):
        errors.append(f"missing asset: docs/brand/assets/{gone}")

    tokens = (ROOT / "docs/brand/design-tokens.css").read_text()
    for t in REQUIRED_TOKENS:
        if t + ":" not in tokens:
            errors.append(f"missing token {t}")

    for path in ROOT.rglob("*"):
        if (not path.is_file() or path.suffix not in SCAN or path.name in SELF
                or SKIP & set(path.relative_to(ROOT).parts)
                or path.relative_to(ROOT).parts[0].startswith(".")):
            continue
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        for name in REMOVED:
            if name in text and not (path.name == "visual-identity.md" and "removed" in text):
                errors.append(f"{path.relative_to(ROOT)} references removed asset '{name}'")

    current = {f: sha(ROOT / f) for f in LOCKED if (ROOT / f).exists()}
    if "--update" in sys.argv:
        if errors:
            print("refusing to update lock while checks fail:")
            print("\n".join("  - " + e for e in errors))
            return 1
        LOCK.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")
        print(f"lock updated: {len(current)} files")
        return 0

    locked = json.loads(LOCK.read_text()) if LOCK.exists() else {}
    for f, digest in current.items():
        if f not in locked:
            errors.append(f"not in lock: {f}")
        elif locked[f] != digest:
            errors.append(f"CHANGED since lock: {f}")
    for f in locked.keys() - current.keys():
        errors.append(f"locked file missing: {f}")

    if errors:
        print("DESIGN SYSTEM LOCK: FAIL")
        print("\n".join("  - " + e for e in errors))
        print("If the change is intentional see the header of this script.")
        return 1
    print(f"DESIGN SYSTEM LOCK: ok ({len(current)} files, v3.1)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
