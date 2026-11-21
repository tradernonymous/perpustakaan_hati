"""Versioned, manually reviewed catalog copy. No private research tables are exported."""

import re

EDITIONS = {"poket": "Edisi Poket", "membangun": "Edisi Membangun", "teman-hidup": "Teman Hidup"}
MAX_REVISION = 2**53 - 1
STEPS = {"review": ("draft", "review"), "approve": ("review", "approved"), "publish": ("approved", "published")}
FIELDS = "revision, title, summary, sample, status, restored_from"
SCHEMA = """
CREATE TABLE IF NOT EXISTS catalog_revisions (
    tier TEXT NOT NULL, revision INTEGER NOT NULL, title TEXT NOT NULL, summary TEXT NOT NULL,
    sample TEXT, status TEXT NOT NULL, restored_from INTEGER,
    PRIMARY KEY (tier, revision)
);
CREATE TABLE IF NOT EXISTS catalog_events (
    id INTEGER PRIMARY KEY, tier TEXT NOT NULL, revision INTEGER NOT NULL,
    event TEXT NOT NULL, outcome TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


class PublicationError(ValueError):
    def __init__(self, message, code=422):
        super().__init__(message)
        self.code = code


def _text(value, limit):
    if (not isinstance(value, str) or not value or len(value) > limit or value.strip() != value
            or re.search(r"[\x00-\x1f\x7f<>\u0085\u2028\u2029]", value)):
        raise PublicationError(f"Enter single-line public copy of 1–{limit} characters without markup or outer spaces.")
    return value


def _revision(value):
    if not isinstance(value, str) or not re.fullmatch(r"0|[1-9][0-9]{0,15}", value) or int(value) > MAX_REVISION:
        raise PublicationError("Invalid revision number.")
    return int(value)


def _latest(db, tier, *, published=False):
    condition = " AND status='published'" if published else ""
    row = db.execute(f"SELECT {FIELDS} FROM catalog_revisions WHERE tier=?{condition} ORDER BY revision DESC LIMIT 1", (tier,)).fetchone()
    return dict(zip(FIELDS.split(", "), row, strict=True)) if row else None


def _projection(tier, row):
    return {
        "schema_version": 1, "id": tier, "slug": tier, "tier": tier, "revision": row["revision"],
        "title": row["title"], "summary": row["summary"], "sample": row["sample"],
        "artwork": f"/ebooks/cover-{tier}.png", "status": row["status"],
    }


def _insert(db, tier, expected, title, summary, sample, *, restored=None):  # noqa: PLR0913, PLR0917
    if expected >= MAX_REVISION:
        raise PublicationError("Revision limit reached.", 409)
    db.execute("INSERT INTO catalog_revisions VALUES (?,?,?,?,?,?,?)",
               (tier, expected + 1, title, summary, sample, "published" if restored else "draft", restored))


class Publications:
    def __init__(self, connect):
        self.connect = connect
        with connect() as db, db:
            db.executescript(SCHEMA)

    def get(self, tier, *, published):
        with self.connect() as db:
            row = _latest(db, tier, published=published)
        if not row:
            raise PublicationError("No matching revision.", 404)
        return _projection(tier, row)

    def workspace(self):
        with self.connect() as db:
            db.execute("BEGIN")
            result = []
            for tier, label in EDITIONS.items():
                history = [r[0] for r in db.execute(
                    "SELECT revision FROM catalog_revisions WHERE tier=? AND status='published' ORDER BY revision DESC", (tier,))]
                event = db.execute("SELECT event, outcome FROM catalog_events WHERE tier=? ORDER BY id DESC LIMIT 1", (tier,)).fetchone()
                confirmed = db.execute("SELECT MAX(revision) FROM catalog_events WHERE tier=? AND event='confirm-live' AND outcome='ok'", (tier,)).fetchone()[0]
                result.append({"confirmed": confirmed, "tier": tier, "label": label, "latest": _latest(db, tier), "history": history, "event": event})
            return result

    def change(self, tier, action, data):
        if tier not in EDITIONS or action not in {*STEPS, "draft", "rollback", "confirm-live"}:
            raise PublicationError("Unknown edition or action.", 404)
        expected = _revision(data.get("expected"))
        with self.connect() as db, db:
            db.execute("BEGIN IMMEDIATE")
            row = _latest(db, tier)
            current = row["revision"] if row else 0
            try:
                self._apply(db, tier, action, data, row, expected, current)
            except PublicationError as exc:
                db.execute("INSERT INTO catalog_events(tier,revision,event,outcome) VALUES (?,?,?,?)",
                           (tier, expected, action, str(exc)))
                db.commit()
                raise
            result = _latest(db, tier)
            db.execute("INSERT INTO catalog_events(tier,revision,event,outcome) VALUES (?,?,?,?)",
                       (tier, result["revision"], action, "ok"))
            return _projection(tier, result)

    @staticmethod
    def _apply(db, tier, action, data, row, expected, current):  # noqa: PLR0913, PLR0917
        extra = {"draft": {"title", "summary", "sample"}, "rollback": {"target"}}.get(action, set())
        if data.keys() - {"expected", "csrf"} - extra:
            raise PublicationError("Unrecognized field.")
        target = _revision(data.get("target")) if action == "rollback" else None
        if current != expected:
            if action == "rollback" and current == expected + 1 and row["restored_from"] == target:
                return
            raise PublicationError("Revision has changed. Reload the workspace before retrying.", 409)
        if action == "draft":
            sample = data.get("sample") or None
            if sample not in (None, "/#bab"):
                raise PublicationError("Choose the approved storefront sample.")
            _insert(db, tier, expected, _text(data.get("title"), 120), _text(data.get("summary"), 600), sample)
        elif action == "confirm-live":
            if not row or row["status"] != "published":
                raise PublicationError("Confirm only a published revision observed on the live storefront.", 409)
        elif action == "rollback":
            published = _latest(db, tier, published=True)
            if not published or target >= published["revision"]:
                raise PublicationError("Choose a revision published before the latest export.", 409)
            previous = db.execute("SELECT title,summary,sample FROM catalog_revisions WHERE tier=? AND revision=? AND status='published'",
                                  (tier, target)).fetchone()
            if not previous:
                raise PublicationError("Revision was never published.", 409)
            _insert(db, tier, expected, *previous, restored=target)
        else:
            before, after = STEPS[action]
            if not row or row["status"] not in (before, after):
                raise PublicationError("Review the current revision and its status before retrying.", 409)
            db.execute("UPDATE catalog_revisions SET status=? WHERE tier=? AND revision=?", (after, tier, expected))
