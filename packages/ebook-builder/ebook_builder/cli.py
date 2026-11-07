"""Command line for the eBook builder.

    ebook-builder build content/ebooks/tier-1-free --tier poket --out dist
    ebook-builder build content/ebooks/tier-2-standard --name "Aisyah" --email a@example.com

Every ``.md`` file in the source directory is a manuscript. The build
produces one PDF per manuscript, watermarked for the buyer.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .manuscript import ManuscriptError, parse_markdown
from .pdf import RenderError, render_pdf
from .watermark import Buyer

TIER_BY_DIRECTORY = {
    "tier-1-free": "poket",
    "tier-2-standard": "membangun",
    "tier-3-premium": "teman-hidup",
}


def _slug(text: str) -> str:
    keep = [c.lower() if c.isalnum() else "-" for c in text.strip()]
    slug = "".join(keep)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "ebook"


def _build(args: argparse.Namespace) -> int:
    source = Path(args.source)
    if not source.is_dir():
        print(f"error: {source} is not a directory", file=sys.stderr)
        return 1
    manuscripts = sorted(source.glob("*.md"))
    if not manuscripts:
        print(f"error: no .md manuscripts found in {source}", file=sys.stderr)
        return 1

    tier = args.tier or TIER_BY_DIRECTORY.get(source.name, "poket")
    buyer = Buyer(name=args.name or "", email=args.email or "")
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    built = []
    for path in manuscripts:
        manuscript = parse_markdown(path.read_text(encoding="utf-8"))
        if not manuscript.tier:
            manuscript.meta["tier"] = tier
        if not manuscript.title:
            manuscript.meta["title"] = path.stem.replace("-", " ").title()
        name = f"{_slug(manuscript.title or path.stem)}-{_slug(tier)}.pdf"
        target = out_dir / name
        render_pdf(manuscript, target, buyer, html_output=out_dir / f"{target.stem}.html")
        built.append(target)
        print(f"built {target}")

    print(f"{len(built)} file(s) built for tier '{tier}'")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ebook-builder", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="build PDFs from a manuscript directory")
    build.add_argument("source", help="directory holding the .md manuscripts")
    build.add_argument("--tier", choices=sorted(TIER_BY_DIRECTORY.values()), help="tier override")
    build.add_argument("--out", default="dist", help="output directory (default: dist)")
    build.add_argument("--name", default="", help="buyer name for the watermark")
    build.add_argument("--email", default="", help="buyer email for the watermark")

    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            return _build(args)
    except (ManuscriptError, RenderError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
