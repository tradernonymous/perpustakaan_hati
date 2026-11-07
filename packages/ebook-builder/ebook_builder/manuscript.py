"""Parse a manuscript into typed blocks the typesetter can lay out.

A manuscript is Markdown with optional front matter. Every block maps to
exactly one of the brand's master layouts (docs/brand/ui-kit.md ->
"Master layouts"), so the typesetter never has to guess what a heading or a
blockquote wants to become.

The marker syntax ``::: name ... :::`` is how a manuscript asks for a
layout that Markdown cannot express on its own: a reflection card, the
back-matter helpline page.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

from markdown_it import MarkdownIt

MD = MarkdownIt("commonmark").enable("strikethrough")

# A level-2 heading containing one of these switches the section that follows
# into a special mode, so its level-3 headings become worksheets or scripts.
WORKSHEET_SECTION = re.compile(r"buku kerja|kit refleksi", re.IGNORECASE)
SCRIPT_SECTION = re.compile(r"skrip", re.IGNORECASE)
WANT_COLUMN = re.compile(r"saya mahu kata", re.IGNORECASE)
HOW_COLUMN = re.compile(r"cara aku kata", re.IGNORECASE)

FENCE_MARKERS = {
    "card": "reflection-card",
    "backmatter": "back-matter",
}


class ManuscriptError(ValueError):
    """The manuscript is not something we can typeset."""


class BlockKind(str, Enum):
    COVER = "cover"
    TITLE_PAGE = "title-page"
    CHAPTER_OPENER = "chapter-opener"
    BODY = "body"
    PULL_QUOTE = "pull-quote"
    PAGE_BREAK = "page-break"
    WORKSHEET = "worksheet"
    REFLECTION_CARD = "reflection-card"
    SCRIPT_ROW = "script-row"
    BACK_MATTER = "back-matter"


@dataclass
class Block:
    kind: BlockKind
    text: str = ""
    title: str = ""
    meta: dict = field(default_factory=dict)


@dataclass
class Manuscript:
    meta: dict = field(default_factory=dict)
    blocks: list[Block] = field(default_factory=list)

    @property
    def title(self) -> str:
        return str(self.meta.get("title", ""))

    @property
    def tier(self) -> str:
        return str(self.meta.get("tier", ""))

    @property
    def tagline(self) -> str:
        return str(self.meta.get("tagline", ""))

    @property
    def subtitle(self) -> str:
        return str(self.meta.get("subtitle", "") or self.tagline)


def _front_matter(lines: list[str]) -> tuple[dict, list[str]]:
    """Split leading ``---`` front matter from the body."""
    if not lines or lines[0].strip() != "---":
        return {}, lines
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            meta = {}
            for raw in lines[1:index]:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                key, separator, value = line.partition(":")
                if not separator:
                    continue
                meta[key.strip().lower()] = value.strip().strip('"').strip("'")
            return meta, lines[index + 1:]
    raise ManuscriptError("Front matter is never closed with '---'.")


def _render(markdown: str) -> str:
    return MD.render(markdown).strip()


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _strip_quote(markdown: str) -> str:
    lines = []
    for raw in markdown.splitlines():
        stripped = raw.lstrip()
        if stripped.startswith(">"):
            lines.append(stripped[1:].strip())
        else:
            lines.append(raw)
    return " ".join(part.strip() for part in lines if part.strip())


def parse_markdown(source: str) -> Manuscript:
    """Turn manuscript Markdown into a list of typed blocks."""
    if not isinstance(source, str):
        raise ManuscriptError("Manuscript must be text.")
    lines = source.replace("\r\n", "\n").split("\n")
    meta, body = _front_matter(lines)

    blocks: list[Block] = []
    mode = ""
    index = 0
    chunk: list[str] = []

    # A worksheet or script heading owns the content that follows it, so the
    # heading and its body must end up in the same block.
    pending: Block | None = None

    def flush() -> None:
        nonlocal pending
        if not chunk:
            return
        markdown = "\n".join(chunk).strip()
        chunk.clear()
        if not markdown:
            return
        if markdown.startswith(">"):
            blocks.append(Block(kind=BlockKind.PULL_QUOTE, text=_strip_quote(markdown)))
            return
        html = _render(markdown)
        if pending is not None:
            pending.text = f"{pending.text}\n{html}" if pending.text else html
            return
        blocks.append(Block(kind=BlockKind.BODY, text=html))

    while index < len(body):
        line = body[index]
        stripped = line.strip()

        if stripped.startswith(":::"):
            marker = stripped[3:].strip().lower()
            if marker not in FENCE_MARKERS:
                raise ManuscriptError(f"Unknown manuscript marker '::: {marker}'.")
            closing = index + 1
            while closing < len(body) and body[closing].strip() != ":::":
                closing += 1
            if closing >= len(body):
                raise ManuscriptError(f"Marker '::: {marker}' is never closed.")
            inner = "\n".join(body[index + 1:closing]).strip()
            pending = None
            blocks.append(Block(kind=BlockKind(FENCE_MARKERS[marker]), text=inner))
            index = closing + 1
            continue

        if stripped.startswith("```"):
            closing = index + 1
            while closing < len(body) and not body[closing].strip().startswith("```"):
                closing += 1
            if closing >= len(body):
                raise ManuscriptError("Code block is never closed.")
            code = "\n".join(body[index + 1:closing])
            pending = None
            blocks.append(Block(kind=BlockKind.BODY, text=f"<pre><code>{_escape(code)}</code></pre>"))
            index = closing + 1
            continue

        if stripped.startswith("#"):
            flush()
            level = len(stripped) - len(stripped.lstrip("#"))
            heading = stripped[level:].strip()
            if level == 1:
                pending = None
                blocks.append(Block(kind=BlockKind.CHAPTER_OPENER, title=heading))
            elif level == 2:
                mode = ""
                pending = None
                if WORKSHEET_SECTION.search(heading):
                    mode = "worksheet"
                elif SCRIPT_SECTION.search(heading):
                    mode = "script"
                blocks.append(Block(kind=BlockKind.BODY, text=_render(f"## {heading}")))
            else:
                if mode == "worksheet":
                    pending = Block(kind=BlockKind.WORKSHEET, title=heading)
                    blocks.append(pending)
                elif mode == "script":
                    column = "want" if WANT_COLUMN.search(heading) else "how" if HOW_COLUMN.search(heading) else "other"
                    pending = Block(kind=BlockKind.SCRIPT_ROW, title=heading, meta={"column": column})
                    blocks.append(pending)
                else:
                    pending = None
                    blocks.append(Block(kind=BlockKind.BODY, text=_render(f"### {heading}")))
            index += 1
            continue

        if stripped == "---":
            flush()
            pending = None
            blocks.append(Block(kind=BlockKind.PAGE_BREAK))
            index += 1
            continue

        if not stripped:
            flush()
            index += 1
            continue

        chunk.append(line)
        index += 1

    flush()
    return Manuscript(meta=meta, blocks=blocks)
