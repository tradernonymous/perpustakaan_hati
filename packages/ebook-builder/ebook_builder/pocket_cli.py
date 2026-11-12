"""Build the Edisi Poket pocket edition PDF.

Usage:
    uv run --project packages/ebook-builder python -m ebook_builder.pocket_cli \\
        content/ebooks/edisi-poket-cuma-kawan-pejabat/manuscript.md \\
        --out docs/brand/preview/ebook-edisi-poket-cuma-kawan-pejabat.pdf

The edition is set at one type scale. The build measures every page in
headless Chrome, then refuses to ship when a page does not hold its copy,
when the copy leaves a page too thin, when any text block ends on a single
word, or when a text role is not the same size on every page.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .pocket import (
    PocketError,
    check_fill,
    check_uniform_type,
    measure_pocket,
    parse_pocket,
    render_pocket_pdf,
)


def _size_cell(sizes: dict, role: str) -> str:
    value = sizes.get(role)
    return f"{value:>5.1f}" if value is not None else "    -"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pocket", description=__doc__)
    parser.add_argument("manuscript", help="path to the pocket manuscript")
    parser.add_argument("--out", default="dist/edisi-poket.pdf", help="output PDF path")
    args = parser.parse_args(argv)

    source = Path(args.manuscript)
    if not source.is_file():
        print(f"error: {source} is not a file", file=sys.stderr)
        return 1

    try:
        doc = parse_pocket(source.read_text(encoding="utf-8"))
        report = measure_pocket(doc)
        output = render_pocket_pdf(doc, Path(args.out))
    except PocketError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print("page   fill  body  title  quote")
    for entry in report["pages"]:
        page = entry["index"]
        inner = entry["inner"]
        fill = entry["used"] / inner if inner else 0
        sizes = entry.get("sizes") or {}
        print(
            f"{page:>4}  {fill:>4.0%}  {_size_cell(sizes, 'body')}  "
            f"{_size_cell(sizes, 'title')}  {_size_cell(sizes, 'quote')}"
        )

    problems: list[str] = []
    problems.extend(check_fill(report))
    problems.extend(f"type is not uniform: {issue}" for issue in check_uniform_type(report))
    problems.extend(
        f"page {runt['page']} [{runt['block']}] ends on a single word: {runt['lastText']!r}"
        for runt in report["runts"]
    )
    problems.extend(
        f"page {over['page']} [{over['block']}] is clipped: {over['text']!r}"
        for over in report.get("overflows", [])
    )

    if problems:
        print(f"error: {len(problems)} layout problem(s):", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1

    print(f"built {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
