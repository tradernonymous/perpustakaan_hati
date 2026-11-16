"""Render the three tier covers to PNG.

The brand already has a cover recipe — ``packages/ebook-builder/templates/
cover.html`` — but nothing ever rendered it, so the storefront shipped a
placeholder frame for every edition and the three tiers looked like the
same book three times over.

This renders that template once per tier:

    uv run --no-project python packages/brand-tools/build-tier-covers.py

Output (1200x1800, 6x9in at 200dpi):
    docs/brand/preview/cover-edisi-poket.png
    docs/brand/preview/cover-edisi-membangun.png
    docs/brand/preview/cover-teman-hidup.png

and the web copies:
    apps/web/public/ebooks/cover-<tier>.png

The renderer is headless Chrome, not WeasyPrint: WeasyPrint does not
implement ``-webkit-background-clip: text``, so the foil wordmark would
print as a solid band instead of a gradient inside the letters.

Each tier gets its own cover because each tier gets its own colour, its
own metal and its own silhouette. The seal is never the same shape twice,
so the covers stay tellable apart even in black and white.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "packages" / "ebook-builder" / "templates" / "cover.html"
PREVIEW = ROOT / "docs" / "brand" / "preview"
WEB_EBOOKS = ROOT / "apps" / "web" / "public" / "ebooks"

# tier id -> (title, subtitle, tier class, seal file)
TIERS = (
    ("poket", "Edisi Poket", "Teman hati sementara menunggu bas atau train.", "tier-free", "seal-edisi-poket.svg"),
    ("membangun", "Edisi Membangun", "Panduan yang paling jujur dan paling mudah diikuti.", "tier-standard", "seal-edisi-membangun.svg"),
    ("teman-hidup", "Teman Hidup", "Bacaan, kerja, dan skrip, teman hidup.", "tier-premium", "seal-teman-hidup.svg"),
)

CHROME_CANDIDATES = (
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "chrome-headless-shell",
    "microsoft-edge",
)


def find_chrome() -> str:
    for name in CHROME_CANDIDATES:
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit("No headless Chrome found. Install google-chrome or chromium.")


def render(template: str, output: Path) -> Path:
    """Screenshot one cover page to a PNG."""
    chrome = find_chrome()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "cover.html"
        source.write_text(template, encoding="utf-8")
        subprocess.run(
            [
                chrome,
                "--headless=new",
                "--no-sandbox",
                "--disable-gpu",
                "--hide-scrollbars",
                "--allow-file-access-from-files",
                "--force-device-scale-factor=1",
                "--window-size=1200,1800",
                "--virtual-time-budget=10000",
                f"--screenshot={output}",
                source.as_uri(),
            ],
            capture_output=True,
            check=True,
            timeout=180,
        )
    if not output.exists() or output.stat().st_size == 0:
        raise SystemExit(f"Chrome did not produce {output}")
    return output


def _absolutise(html: str) -> str:
    """Rewrite the template's relative asset and font paths to file URIs.

    The template is written next to the brand files so it can be opened
    in a browser straight from the repo. This builder renders it from a
    temporary directory, so those relative paths would resolve to
    nothing: the seal and the brand fonts would silently fall back to
    a system serif and a missing image.
    """
    for relative in (
        "../../../docs/brand/design-tokens.css",
        "../../../docs/brand/assets/",
        "../../../packages/brand-tools/fonts/",
    ):
        target = (TEMPLATE.parent / relative).resolve()
        replacement = target.as_uri() + ("/" if relative.endswith("/") else "")
        html = html.replace(relative, replacement)
    return html


def cover_html(tier_class: str, title: str, subtitle: str, seal: str) -> str:
    """The brand cover template, filled in for one tier."""
    raw = TEMPLATE.read_text(encoding="utf-8")
    html = _absolutise(raw)
    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{TIER}}", title)
    html = html.replace("{{SUBTITLE}}", subtitle)
    html = html.replace('class="cover ph-stage tier-free"', f'class="cover ph-stage {tier_class}"')
    # Only this tier's seal stays on the cover. The other two are removed
    # outright, so a template mistake cannot ship two seals on one cover.
    for _, _, _, _, other in TIERS:
        if other != seal:
            html = re.sub(
                rf'<img class="seal seal-[a-z-]+" src="[^"]*{re.escape(other)}"[^>]*/>',
                "",
                html,
            )
    return html


def main() -> int:
    for tier, title, subtitle, tier_class, seal in TIERS:
        html = cover_html(tier_class, title, subtitle, seal)
        target = PREVIEW / f"cover-{tier}.png"
        render(html, target)
        print(f"wrote {target.relative_to(ROOT)}")

        web = WEB_EBOOKS / f"cover-{tier}.png"
        web.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(target, web)
        print(f"wrote {web.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
