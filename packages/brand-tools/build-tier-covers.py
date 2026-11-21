"""Make the catalog images from the actual covers of the three edition manuscripts.

Run from the repository root with the ebook-builder environment and Poppler:
    uv run --project packages/ebook-builder python packages/brand-tools/build-tier-covers.py

Only the cover image is public. Each source PDF is generated without buyer data
in a temporary directory, even if personalized downloads exist on this machine.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from ebook_builder.manuscript import parse_markdown
from ebook_builder.pdf import render_pdf

ROOT = Path(__file__).resolve().parents[2]
BOOKS = ROOT / "content" / "ebooks"
MANUSCRIPTS = {
    "poket": BOOKS / "tier-1-free/manuscript/edisi-poket.md",
    "membangun": BOOKS / "tier-2-standard/manuscript/edisi-membangun.md",
    "teman-hidup": BOOKS / "tier-3-premium/manuscript/teman-hidup.md",
}


def main() -> None:
    # Stage all six derivatives before replacing the previous gallery.
    with tempfile.TemporaryDirectory() as temporary:
        staging = Path(temporary)
        outputs: list[tuple[Path, Path]] = []
        for tier, source in MANUSCRIPTS.items():
            manuscript = parse_markdown(source.read_text(encoding="utf-8"))
            if manuscript.tier != tier:
                raise ValueError(f"Expected {tier!r} front matter in {source}")
            pdf = render_pdf(manuscript, staging / f"{tier}.pdf")
            for directory, dpi in (("docs/brand/preview", 200), ("apps/web/public/ebooks", 100)):
                prefix = staging / f"{tier}-{dpi}"
                subprocess.run(
                    ["pdftocairo", "-png", "-singlefile", "-f", "1", "-l", "1",
                     "-r", str(dpi), str(pdf), str(prefix)],
                    check=True,
                )
                outputs.append((prefix.with_suffix(".png"), ROOT / directory / f"cover-{tier}.png"))

        for image, destination in outputs:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(image, destination)
            print(destination.relative_to(ROOT))


if __name__ == "__main__":
    main()
