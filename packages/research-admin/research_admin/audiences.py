"""Evidence-backed, non-demographic audience segments from saved insights."""

from collections import defaultdict

from .followers import author_of

SEGMENTS = (
    ("Trust & boundaries", ("trust", "kepercayaan", "boundary", "boundaries", "batas", "curang", "cheat", "red flag")),
    ("Healing after a breakup", ("breakup", "putus", "perpisahan", "move on", "ex", "bekas", "healing", "pulih")),
    ("Self-worth & identity", ("self-worth", "harga diri", "self esteem", "value", "nilai diri", "identity", "identiti")),
    ("Communication & conflict", ("communicat", "komunikasi", "conflict", "konflik", "argue", "bergaduh", "talk", "berbincang")),
    ("Unhealthy relationship patterns", ("toxic", "abuse", "abusive", "narciss", "manipulat", "control", "mengawal", "gaslight")),
)


def segment_for(insight: dict, *, custom_segments: list[dict] | None = None) -> str:
    text = f"{insight.get('theme', '')} {insight.get('quote', '')}".casefold()
    for seg in custom_segments or []:
        label = str(seg.get("label", "")).strip()
        terms = [str(t).strip().casefold() for t in seg.get("keywords", []) if str(t).strip()]
        if label and terms and any(term in text for term in terms):
            return label
    for label, terms in SEGMENTS:
        if any(term in text for term in terms):
            return label
    return "Needs further research"


def build_audiences(
    insights: list[dict],
    drafts: list[dict] | None = None,
    *,
    custom_segments: list[dict] | None = None,
) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in insights:
        grouped[segment_for(item, custom_segments=custom_segments)].append(item)
    active_drafts = [d for d in (drafts or []) if isinstance(d, dict) and d.get("status") != "archived"]
    result = []
    for name, evidence in grouped.items():
        themes = sorted({str(item["theme"]) for item in evidence})
        source_ids = sorted({int(item["id"]) for item in evidence if str(item.get("id", "")).isdigit()})
        source_set = set(source_ids)
        voices = sorted({author_of(item.get("source_url")) for item in evidence if author_of(item.get("source_url"))})
        linked_drafts = [
            d for d in active_drafts
            if any(int(sid) in source_set for sid in d.get("source_ids", []) if str(sid).isdigit())
        ]
        approved_count = sum(1 for d in linked_drafts if d.get("status") == "approved")
        result.append({
            "name": name,
            "evidence_count": len(evidence),
            "themes": themes,
            "evidence": evidence,
            "ebook_angles": sorted({str(item["ebook_idea"]) for item in evidence if item.get("ebook_idea")}),
            "source_ids": source_ids,
            "voices": voices,
            "draft_count": len(linked_drafts),
            "approved_draft_count": approved_count,
            "needs_drafts": len(linked_drafts) == 0 and len(evidence) > 0,
            "basis": "Working segment inferred from the themes and wording of sampled posts/replies; not a demographic profile.",
        })
    return sorted(result, key=lambda item: (-item["evidence_count"], item["name"]))
