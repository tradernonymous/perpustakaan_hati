"""Import one approved research export into the build-time storefront catalog."""

import argparse
import fcntl
import json
import os
import tempfile
from contextlib import suppress
from pathlib import Path

WEB = Path(__file__).resolve().parents[1]
CATALOG = WEB / "src/publication/catalog.json"
KEYS = {"schema_version", "id", "slug", "tier", "title", "summary", "artwork", "sample", "status", "revision"}
TIERS = ("poket", "membangun", "teman-hidup")


def unique_keys(pairs):
    record = dict(pairs)
    if len(record) != len(pairs):
        raise ValueError("Duplicate JSON property")
    return record


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys)


def validate(item):
    if not isinstance(item, dict) or item.keys() != KEYS:
        raise ValueError("Expected exactly the version 1 public fields")
    if type(item["schema_version"]) is not int or item["schema_version"] != 1:
        raise ValueError("Unsupported publication schema")
    tier = item["tier"]
    if tier not in TIERS or item["id"] != tier or item["slug"] != tier:
        raise ValueError("Invalid product identity")
    if item["status"] != "published":
        raise ValueError("A published revision is required")
    if type(item["revision"]) is not int or not 1 <= item["revision"] <= 2**53 - 1:
        raise ValueError("Invalid revision")
    for key, limit in (("title", 120), ("summary", 600)):
        value = item[key]
        if not isinstance(value, str) or not 1 <= len(value) <= limit or value.strip() != value:
            raise ValueError(f"Invalid {key}")
        if len(value.splitlines()) != 1 or any(ord(c) < 32 or c in "<>\x7f" for c in value):
            raise ValueError(f"{key} must be one line of plain text")
        value.encode("utf-8")  # Reject unpaired surrogates from escaped input.
    cover = f"/ebooks/cover-{tier}.png"
    if item["artwork"] != cover or not (WEB / "public" / cover[1:]).is_file():
        raise ValueError("Unknown or missing public cover")
    if item["sample"] not in (None, "/#bab"):
        raise ValueError("Unknown public sample")


def import_item(source):
    item = read_json(source)
    validate(item)
    # The directory inode survives replacement of catalog.json and process exits.
    lock = os.open(CATALOG.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX)
        catalog = read_json(CATALOG)
        if not isinstance(catalog, list):
            raise ValueError("Invalid existing catalog")
        by_tier = {}
        for previous in catalog:
            validate(previous)
            if previous["tier"] in by_tier:
                raise ValueError("Duplicate tier in existing catalog")
            by_tier[previous["tier"]] = previous
        previous = by_tier.get(item["tier"])
        if previous == item:
            return "Already imported"
        if previous and item["revision"] <= previous["revision"]:
            raise ValueError("Stale or conflicting revision. Export the latest published revision.")
        by_tier[item["tier"]] = item
        rows = [by_tier[tier] for tier in TIERS if tier in by_tier]
        payload = json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        with tempfile.NamedTemporaryFile(dir=CATALOG.parent, delete=False) as temp:
            try:
                temp.write(payload.encode("utf-8"))
                temp.flush()
                os.fchmod(temp.fileno(), 0o644)
                os.fsync(temp.fileno())
                os.replace(temp.name, CATALOG)
            finally:
                with suppress(FileNotFoundError):
                    os.unlink(temp.name)
        return "Imported"
    finally:
        os.close(lock)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path, help="One JSON file downloaded from the research publication review")
    args = parser.parse_args()
    try:
        print(import_item(args.export))
    except (ValueError, OSError) as error:
        parser.exit(1, f"Import failed: {error}\n")
