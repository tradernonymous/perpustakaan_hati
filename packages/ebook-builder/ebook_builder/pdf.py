"""Render the typeset HTML to a print-grade PDF.

WeasyPrint is the renderer: it is a real CSS paged-media engine, so the
brand's ``@page`` rules, print colours and page breaks behave the way a
printer expects. Chrome would render the same HTML but gives no control
over page boxes.

The output is PDF/A-friendly enough for print-on-demand: embedded fonts,
trim 6x9in, no transparency-dependent content.
"""

from __future__ import annotations

from pathlib import Path

from .manuscript import Manuscript
from .typesetter import typeset
from .watermark import Buyer


class RenderError(RuntimeError):
    """The PDF could not be produced."""


def render_pdf(
    manuscript: Manuscript,
    output: Path,
    buyer: Buyer | None = None,
    html_output: Path | None = None,
) -> Path:
    """Write the manuscript to a PDF at ``output``."""
    # Imported here, not at module level: WeasyPrint pulls in a large native
    # stack, and the parser and typesetter must stay importable without it.
    try:
        from weasyprint import HTML
    except ImportError:  # pragma: no cover - dependency is declared
        raise RenderError(
            "WeasyPrint is not installed. Run 'uv sync' in packages/ebook-builder."
        ) from None

    document = typeset(manuscript, buyer)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if html_output is not None:
        html_path = Path(html_output)
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(document, encoding="utf-8")
    try:
        HTML(string=document, base_url=str(output.parent)).write_pdf(str(output))
    except Exception as exc:  # WeasyPrint raises a wide range of errors
        raise RenderError(f"Could not render the PDF: {exc}") from None
    return output
