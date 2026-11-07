"""Per-buyer watermarking for the eBook build.

The watermark is what stops a buyer from sharing their PDF. The brand rule
(docs/brand/ui-kit.md -> "Watermark") is:

  * every paid page carries "Cop Perpustakaan Hati" diagonally at -20 degrees,
    10% opacity, gold-deep, bottom-right;
  * a buyer line "<Nama Pembeli> · <email>" at 7pt and 14% opacity sits
    bottom-centre, but only on pages 2-6, so the spread still reads clean.

Visible over invisible: a visible stamp is the Malaysian market standard and
matches what the storefront already does when it stamps a delivered PDF.

The stamp has to land on *every* page, not only on the pages that happen to
start a section. WeasyPrint's paged-media margin boxes are the right tool:
``@page`` applies to every page, and ``@page:nth(N)`` to one page, so the
buyer line can be confined to pages 2-6 without knowing the page count.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

COPY_LINE = "Cop Perpustakaan Hati"
ANONYMOUS_LABEL = "Salinan Peribadi"

# Anything that could break out of the text node or the CSS attribute.
_UNSAFE = re.compile(r"[<>\"]")


@dataclass
class Buyer:
    """Who the copy is licensed to. Both fields are optional."""

    name: str = ""
    email: str = ""

    def __post_init__(self) -> None:
        self.name = _clean(self.name)
        self.email = _clean(self.email)

    @property
    def is_anonymous(self) -> bool:
        return not (self.name or self.email)


@dataclass
class Watermark:
    """The stamp to place on a build."""

    copy_line: str = COPY_LINE
    buyer_label: str = ""
    buyer_pages: tuple[int, int] = field(default=(2, 6))
    colour: str = "var(--gold-deep)"


def _clean(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if _UNSAFE.search(text):
        raise ValueError("Buyer details must not contain markup characters.")
    # A newline in a label would break the one-line stamp.
    return " ".join(text.split())


def watermark_label(buyer: Buyer) -> str:
    """The buyer line as printed: name, then email, joined by a middot."""
    if buyer.is_anonymous:
        return ANONYMOUS_LABEL
    if buyer.name and buyer.email:
        return f"{buyer.name} · {buyer.email}"
    return buyer.name or buyer.email


def build_watermark_css(watermark: Watermark) -> str:
    """CSS for the stamp and, when present, the early-pages buyer line.

    The copy line goes in a margin box so it repeats on every printed page.
    The buyer line uses ``@page:nth()`` so it appears on pages 2-6 only.
    """
    rules = [
        "@page {",
        "  @bottom-right {",
        "    content: '" + _css_escape(watermark.copy_line) + "';",
        "    font-family: 'Inter', sans-serif;",
        "    font-size: 8pt;",
        "    letter-spacing: 0.12em;",
        f"    color: {watermark.colour};",
        "    opacity: 0.1;",
        "    transform: rotate(-20deg);",
        "  }",
        "}",
    ]
    if watermark.buyer_label:
        first, last = watermark.buyer_pages
        rules.append(".buyer-line { display: none; }")
        for page in range(first, last + 1):
            rules.extend([
                f"@page:nth({page}) {{",
                "  @bottom-center {",
                f"    content: '{_css_escape(watermark.buyer_label)}';",
                "    font-family: 'Inter', sans-serif;",
                "    font-size: 7pt;",
                "    color: var(--sepia-deep);",
                "    opacity: 0.14;",
                "  }",
                "}",
            ])
    return "\n".join(rules)


def _css_escape(value: str) -> str:
    """Make a string safe to sit inside a CSS single-quoted string."""
    return str(value or "").replace("\\", "\\\\").replace("'", "\\'")
