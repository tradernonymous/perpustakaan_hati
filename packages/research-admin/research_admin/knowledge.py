"""Personal Knowledge Graph, Wiki-Link extraction, and bounded Brand Fact-Sheet compilation."""

import re

WIKI_LINK_RE = re.compile(r"\[\[([a-zA-Z0-9_\-\s]{2,64})\]\]")

DEFAULT_KNOWLEDGE_NODES = (
    {
        "slug": "brand-voice-malaysia",
        "title": "Brand Voice & Storytelling Bank",
        "category": "brand",
        "summary": "Calm, non-clinical, empathetic Malaysian voice in Bahasa Melayu and casual English without em dashes.",
        "body": (
            "Write as an observant friend in a quiet library at twilight, never as a clinical therapist or preachy guru. "
            "Bridge everyday Malaysian scenes (kopi panas, trafik balik kerja, senyap malam) with gentle emotional honesty. "
            "Follow [[guardrails-no-diagnosis]] and pair reflective threads with [[product-pustaka-bridge]]."
        ),
    },
    {
        "slug": "guardrails-no-diagnosis",
        "title": "Editorial Guardrails & Safety Boundaries",
        "category": "guardrails",
        "summary": "Never diagnose conditions, promise clinical cures, or use typographic em dashes.",
        "body": (
            "Never diagnose mental health disorders, prescribe clinical treatment, or guarantee healing outcomes. "
            "For crisis or self-harm distress signals in replies, respond warmly with human compassion and suggest reaching "
            "Befrienders KL (03-7627 2929) or trusted professionals without acting as a counsellor. "
            "Never invent quotes or permalinks, and keep prose free of em dashes."
        ),
    },
    {
        "slug": "formats-threads-cards",
        "title": "Threads Hooks & Daylight Grove Cards",
        "category": "formats",
        "summary": "High-retention 3-part threads, 4-angle hooks, and quote-card layouts for @rahimam.",
        "body": (
            "Keep single Threads posts concise under 500 characters ending in a soft reflective question. "
            "Visual cards use Warm Parchment (#FBF7F0), Forest Pine (#2F4B3B), Terracotta (#B96444), Fraunces display headings, "
            "and @rahimam rainbow accent Pill. Linked to [[brand-voice-malaysia]] and [[product-pustaka-bridge]]."
        ),
    },
    {
        "slug": "product-pustaka-bridge",
        "title": "Pustaka, Kelab & Surat Hati Bridge",
        "category": "catalog",
        "summary": "Connects organic Threads pain points to ebooks, Kelab reading circles, and Surat Hati notes.",
        "body": (
            "Each ebook outline builds a 3-to-5 chapter progression from named pain points toward calm agency. "
            "Markdown exports align directly with packages/ebook-builder chapter format and Pustaka storefront themes."
        ),
    },
)

DEFAULT_SEGMENTS = (
    {
        "slug": "emotional_exhaustion",
        "label": "Quiet Burnout & Overthinking",
        "description": "Readers feeling mentally drained, carrying unspoken expectations at night.",
        "keywords": ["penat", "overthinking", "sunyi", "drained", "burnout", "tidur", "letih"],
    },
    {
        "slug": "quiet_boundary",
        "label": "Boundaries & People-Pleasing",
        "description": "Readers learning to say no gently without guilt or family friction.",
        "keywords": ["boundary", "boundaries", "guilt", "serba salah", "tolak", "no", "family", "keluarga"],
    },
    {
        "slug": "spiritual_grounding",
        "label": "Faith, Redha & Inner Calm",
        "description": "Readers seeking emotional steadiness rooted in prayer, sabar, and redha.",
        "keywords": ["redha", "ikhlas", "doa", "tenang", "sabar", "tawakal", "sujud"],
    },
)


def extract_wiki_links(text: str) -> list[str]:
    """Extract normalised slugs from Obsidian-style `[[wiki-links]]`."""
    links: list[str] = []
    seen: set[str] = set()
    for match in WIKI_LINK_RE.findall(str(text or "")):
        slug = "-".join(match.strip().lower().split())[:80]
        if slug and slug not in seen:
            seen.add(slug)
            links.append(slug)
    return links


def ensure_default_knowledge(store) -> None:
    """Seed Perpustakaan Hati starter Knowledge Graph nodes and segments once if empty."""
    if not store.list_knowledge_nodes():
        for node in DEFAULT_KNOWLEDGE_NODES:
            links = extract_wiki_links(node["body"])
            store.upsert_knowledge_node(
                node["slug"],
                node["title"],
                node["body"],
                {"category": node["category"], "summary": node["summary"], "links": links},
            )
    if not store.list_audience_segments():
        for seg in DEFAULT_SEGMENTS:
            store.upsert_audience_segment(
                slug=seg["slug"],
                label=seg["label"],
                description=seg["description"],
                keywords=seg["keywords"],
            )


def compile_fact_sheet(store, *, max_chars: int = 1600) -> str:
    """Build a bounded Fact-Sheet block from saved knowledge nodes for prompt grounding."""
    nodes = store.list_knowledge_nodes()
    if not nodes:
        return ""
    lines: list[str] = []
    used = 0
    for node in nodes:
        summary = node.get("summary") or node.get("body", "")[:180]
        entry = f"- [{node.get('category', 'brand')}] {node.get('title', '')}: {summary}".strip()
        if used + len(entry) + 1 > max_chars:
            break
        lines.append(entry)
        used += len(entry) + 1
    return "\n".join(lines)
