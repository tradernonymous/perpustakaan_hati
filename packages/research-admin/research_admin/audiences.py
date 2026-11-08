"""Evidence-backed, non-demographic audience segments from saved insights."""

from collections import defaultdict

SEGMENTS = (
    ("Trust & boundaries", ("trust", "kepercayaan", "boundary", "boundaries", "batas", "curang", "cheat", "red flag")),
    ("Healing after a breakup", ("breakup", "putus", "perpisahan", "move on", "ex", "bekas", "healing", "pulih")),
    ("Self-worth & identity", ("self-worth", "harga diri", "self esteem", "value", "nilai diri", "identity", "identiti")),
    ("Communication & conflict", ("communicat", "komunikasi", "conflict", "konflik", "argue", "bergaduh", "talk", "berbincang")),
    ("Unhealthy relationship patterns", ("toxic", "abuse", "abusive", "narciss", "manipulat", "control", "mengawal", "gaslight")),
)


def segment_for(insight: dict) -> str:
    text = f"{insight.get('theme', '')} {insight.get('quote', '')}".casefold()
    for label, terms in SEGMENTS:
        if any(term in text for term in terms):
            return label
    return "Needs further research"


def build_audiences(insights: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in insights:
        grouped[segment_for(item)].append(item)
    result = []
    for name, evidence in grouped.items():
        themes = sorted({str(item["theme"]) for item in evidence})
        result.append({
            "name": name,
            "evidence_count": len(evidence),
            "themes": themes,
            "evidence": evidence,
            "ebook_angles": sorted({str(item["ebook_idea"]) for item in evidence if item.get("ebook_idea")}),
            "source_ids": sorted({int(item["id"]) for item in evidence}),
            "basis": "Working segment inferred from the themes and wording of sampled posts/replies; not a demographic profile.",
        })
    return sorted(result, key=lambda item: (-item["evidence_count"], item["name"]))
