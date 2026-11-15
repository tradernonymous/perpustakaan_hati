"""Private SQLite research storage; OAuth credentials stay encrypted or in the OS keyring."""

import base64
import hashlib
import json
import os
import sqlite3
import subprocess
import time
from contextlib import closing
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

VALID_JOB_KINDS = ("research", "drafts", "graph_sync", "watchlist", "keyword_search", "scheduled_publish")
VALID_DRAFT_STATUSES = ("draft", "approved", "archived", "scheduled", "published")


def _safe_json_loads(raw: str | None, fallback):
    if not raw:
        return fallback
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError, ValueError):
        return fallback


def _compact_job_result(result: dict, max_chars: int = 48000) -> str:
    """Serialize job result safely within max_chars without cutting JSON mid-token."""
    dumped = json.dumps(result, ensure_ascii=False)
    if len(dumped) <= max_chars:
        return dumped
    trimmed = dict(result)
    for key in ("raw_replies", "engagers", "posts"):
        if isinstance(trimmed.get(key), list) and len(trimmed[key]) > 5:
            trimmed[key] = trimmed[key][:5]
            trimmed[f"{key}_truncated"] = True
            dumped = json.dumps(trimmed, ensure_ascii=False)
            if len(dumped) <= max_chars:
                return dumped
    summary = {
        k: v
        for k, v in trimmed.items()
        if isinstance(v, (int, float, bool, str)) or (isinstance(v, list) and len(v) <= 10)
    }
    summary["result_compacted"] = True
    dumped = json.dumps(summary, ensure_ascii=False)
    if len(dumped) <= max_chars:
        return dumped
    return json.dumps({"result_compacted": True, "summary_keys": sorted(result.keys())[:20]}, ensure_ascii=False)


class StoreError(RuntimeError):
    """Safe storage error, with no credential contents."""


class SecretVault:
    def __init__(self, db_path: str):
        self.account = hashlib.sha256(str(Path(db_path).resolve()).encode()).hexdigest()

    def _run(self, operation: str, value: str | None = None):
        command = ["secret-tool", operation]
        if operation == "store":
            command += ["--label=Perpustakaan Hati Threads access"]
        command += ["service", "perpustakaan-hati-threads", "account", self.account]
        try:
            result = subprocess.run(command, input=value, text=True, capture_output=True, timeout=20)
        except (OSError, subprocess.TimeoutExpired):
            raise StoreError("OS keyring unavailable. Install secret-tool and unlock your keyring.") from None
        if result.returncode and not (operation in ("lookup", "clear") and result.returncode == 1 and not result.stderr.strip()):
            raise StoreError("OS keyring operation failed. Unlock your keyring and retry.")
        return result.stdout.rstrip("\n") or None

    def get(self) -> str | None:
        return self._run("lookup")

    def set(self, value: str) -> None:
        self._run("store", value)

    def delete(self) -> None:
        self._run("clear")


class EncryptedVault:
    """Encrypted-at-rest token for hosts without a desktop keyring (Railway).

    The ciphertext lives beside the research data; the key comes from the
    platform's secret store (RESEARCH_TOKEN_KEY) and is never written to disk.
    """

    def __init__(self, db_path: str, key: str):
        if not key:
            raise StoreError("RESEARCH_TOKEN_KEY is not set; cannot decrypt the stored Threads token.")
        self.db_path = str(Path(db_path).expanduser())
        self.fernet = Fernet(base64.urlsafe_b64encode(hashlib.sha256(key.encode()).digest()))

    def _connect(self):
        return closing(sqlite3.connect(self.db_path, timeout=10.0))

    def get(self) -> str | None:
        with self._connect() as db:
            row = db.execute("SELECT value FROM secret WHERE id=1").fetchone()
        if not row:
            return None
        try:
            return self.fernet.decrypt(bytes(row[0])).decode()
        except (InvalidToken, ValueError):
            raise StoreError("Stored Threads token cannot be decrypted; check RESEARCH_TOKEN_KEY and reconnect Threads.") from None

    def set(self, value: str) -> None:
        with self._connect() as db, db:
            db.execute("INSERT OR REPLACE INTO secret VALUES (1, ?)", (self.fernet.encrypt(value.encode()),))

    def delete(self) -> None:
        with self._connect() as db, db:
            db.execute("DELETE FROM secret")


def build_vault(settings) -> SecretVault | EncryptedVault:
    if getattr(settings, "vault_kind", "keyring") == "sqlite":
        return EncryptedVault(settings.db_path, settings.token_key)
    return SecretVault(settings.db_path)


@dataclass
class StoredToken:
    access_token: str = field(repr=False)
    expires_at: int


class Store:
    def __init__(self, db_path: str, *, vault=None):
        self.db_path = str(Path(db_path).expanduser())
        self.vault = vault if vault is not None else SecretVault(self.db_path)

    def _connect(self):
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA foreign_keys=ON")
        return closing(conn)

    @staticmethod
    def _ensure_columns(db: sqlite3.Connection, table: str, specs: tuple[tuple[str, str], ...]) -> None:
        columns = {row[1] for row in db.execute(f"PRAGMA table_info({table})")}
        for column, ddl in specs:
            if column not in columns:
                db.execute(ddl)

    def init_schema(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd = os.open(self.db_path, os.O_CREAT | os.O_WRONLY, 0o600)
        os.close(fd)
        os.chmod(self.db_path, 0o600)
        with self._connect() as db, db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS token (id INTEGER PRIMARY KEY CHECK(id=1), expires_at INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS token_meta (
                    id INTEGER PRIMARY KEY CHECK(id=1),
                    user_id TEXT NOT NULL DEFAULT '',
                    username TEXT NOT NULL DEFAULT '',
                    scopes_json TEXT NOT NULL DEFAULT '[]',
                    refreshed_at TEXT NOT NULL DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS secret (id INTEGER PRIMARY KEY CHECK(id=1), value BLOB NOT NULL);
                CREATE TABLE IF NOT EXISTS insights (
                    id INTEGER PRIMARY KEY, theme TEXT NOT NULL, quote TEXT NOT NULL,
                    source_url TEXT NOT NULL, ebook_idea TEXT NOT NULL, created_at TEXT NOT NULL,
                    source_type TEXT NOT NULL DEFAULT 'threads_reply',
                    engagement_weight INTEGER NOT NULL DEFAULT 1,
                    UNIQUE(theme, quote, source_url)
                );
                CREATE TABLE IF NOT EXISTS research_runs (
                    id INTEGER PRIMARY KEY, created_at TEXT NOT NULL, posts_sampled INTEGER NOT NULL,
                    selected_posts INTEGER NOT NULL, insights_count INTEGER NOT NULL,
                    themes_json TEXT NOT NULL, limitations TEXT NOT NULL, posts_json TEXT NOT NULL DEFAULT '[]',
                    post_limit INTEGER NOT NULL DEFAULT 50, top_posts INTEGER NOT NULL DEFAULT 5,
                    replies_per_post INTEGER NOT NULL DEFAULT 50, focus TEXT NOT NULL DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS content_drafts (
                    id INTEGER PRIMARY KEY, kind TEXT NOT NULL, title TEXT NOT NULL,
                    content_json TEXT NOT NULL, source_ids_json TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'draft', created_at TEXT NOT NULL,
                    scheduled_at TEXT NOT NULL DEFAULT '',
                    variants_json TEXT NOT NULL DEFAULT '[]',
                    starred INTEGER NOT NULL DEFAULT 0,
                    format_meta_json TEXT NOT NULL DEFAULT '{}',
                    visual_html TEXT NOT NULL DEFAULT '',
                    published_post_id TEXT NOT NULL DEFAULT '',
                    published_permalink TEXT NOT NULL DEFAULT '',
                    published_at TEXT NOT NULL DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS audience (
                    id INTEGER PRIMARY KEY CHECK(id=1), followers_json TEXT NOT NULL,
                    following_json TEXT NOT NULL, imported_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS audience_snapshots (
                    id INTEGER PRIMARY KEY,
                    imported_at TEXT NOT NULL,
                    followers_count INTEGER NOT NULL DEFAULT 0,
                    following_count INTEGER NOT NULL DEFAULT 0,
                    followers_json TEXT NOT NULL DEFAULT '[]',
                    following_json TEXT NOT NULL DEFAULT '[]'
                );
                CREATE TABLE IF NOT EXISTS graph_audience (
                    id INTEGER PRIMARY KEY CHECK(id=1),
                    profile_json TEXT NOT NULL DEFAULT '{}',
                    followers_count INTEGER NOT NULL DEFAULT 0,
                    previous_followers_count INTEGER,
                    metrics_json TEXT NOT NULL DEFAULT '{}',
                    demographics_json TEXT NOT NULL DEFAULT '{}',
                    engagers_json TEXT NOT NULL DEFAULT '[]',
                    synced_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS graph_metric_history (
                    id INTEGER PRIMARY KEY,
                    recorded_at TEXT NOT NULL,
                    followers_count INTEGER NOT NULL DEFAULT 0,
                    views INTEGER NOT NULL DEFAULT 0,
                    likes INTEGER NOT NULL DEFAULT 0,
                    replies INTEGER NOT NULL DEFAULT 0,
                    reposts INTEGER NOT NULL DEFAULT 0,
                    quotes INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS unfollow_queue (
                    username_key TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    status TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY, kind TEXT NOT NULL, status TEXT NOT NULL,
                    params_json TEXT NOT NULL, result_json TEXT NOT NULL DEFAULT '{}',
                    error TEXT NOT NULL DEFAULT '', cancel_requested INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL, started_at TEXT, finished_at TEXT
                );
                CREATE TABLE IF NOT EXISTS oauth_states (
                    state TEXT PRIMARY KEY,
                    verifier TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS auth_failures (
                    ip TEXT PRIMARY KEY,
                    failures INTEGER NOT NULL DEFAULT 0,
                    window_started_at REAL NOT NULL,
                    locked_until REAL NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS engagement_inbox (
                    id INTEGER PRIMARY KEY,
                    reply_id TEXT UNIQUE NOT NULL,
                    post_id TEXT NOT NULL DEFAULT '',
                    post_permalink TEXT NOT NULL DEFAULT '',
                    username TEXT NOT NULL DEFAULT '',
                    text TEXT NOT NULL,
                    is_hidden INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'open',
                    draft_reply TEXT NOT NULL DEFAULT '',
                    sentiment TEXT NOT NULL DEFAULT 'neutral',
                    created_at TEXT NOT NULL,
                    replied_at TEXT NOT NULL DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS ai_usage (
                    id INTEGER PRIMARY KEY,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    prompt_tokens INTEGER NOT NULL DEFAULT 0,
                    completion_tokens INTEGER NOT NULL DEFAULT 0,
                    duration_ms INTEGER NOT NULL DEFAULT 0,
                    ok INTEGER NOT NULL DEFAULT 1,
                    error TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS knowledge_nodes (
                    id INTEGER PRIMARY KEY,
                    slug TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'brand',
                    summary TEXT NOT NULL DEFAULT '',
                    body TEXT NOT NULL DEFAULT '',
                    links_json TEXT NOT NULL DEFAULT '[]',
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS knowledge_edges (
                    source_slug TEXT NOT NULL,
                    target_slug TEXT NOT NULL,
                    relation TEXT NOT NULL DEFAULT 'wiki_link',
                    PRIMARY KEY (source_slug, target_slug, relation)
                );
                CREATE TABLE IF NOT EXISTS audience_segments (
                    id INTEGER PRIMARY KEY,
                    slug TEXT UNIQUE NOT NULL,
                    label TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    keywords_json TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY,
                    channel TEXT NOT NULL,
                    dedupe_key TEXT NOT NULL,
                    message TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'sent',
                    error TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS watchlist_config (
                    id INTEGER PRIMARY KEY CHECK(id=1),
                    enabled INTEGER NOT NULL DEFAULT 0,
                    interval_hours INTEGER NOT NULL DEFAULT 24,
                    keywords_json TEXT NOT NULL DEFAULT '[]',
                    focus TEXT NOT NULL DEFAULT '',
                    last_run_at TEXT NOT NULL DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS external_signals (
                    id INTEGER PRIMARY KEY,
                    source TEXT NOT NULL,
                    external_id TEXT NOT NULL,
                    theme TEXT NOT NULL,
                    quote TEXT NOT NULL,
                    url TEXT NOT NULL DEFAULT '',
                    meta_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    UNIQUE(source, external_id)
                );
            """)
            self._ensure_columns(
                db,
                "research_runs",
                (
                    ("posts_json", "ALTER TABLE research_runs ADD COLUMN posts_json TEXT NOT NULL DEFAULT '[]'"),
                    ("post_limit", "ALTER TABLE research_runs ADD COLUMN post_limit INTEGER NOT NULL DEFAULT 50"),
                    ("top_posts", "ALTER TABLE research_runs ADD COLUMN top_posts INTEGER NOT NULL DEFAULT 5"),
                    ("replies_per_post", "ALTER TABLE research_runs ADD COLUMN replies_per_post INTEGER NOT NULL DEFAULT 50"),
                    ("focus", "ALTER TABLE research_runs ADD COLUMN focus TEXT NOT NULL DEFAULT ''"),
                ),
            )
            self._ensure_columns(
                db,
                "insights",
                (
                    ("source_type", "ALTER TABLE insights ADD COLUMN source_type TEXT NOT NULL DEFAULT 'threads_reply'"),
                    ("engagement_weight", "ALTER TABLE insights ADD COLUMN engagement_weight INTEGER NOT NULL DEFAULT 1"),
                ),
            )
            self._ensure_columns(
                db,
                "content_drafts",
                (
                    ("scheduled_at", "ALTER TABLE content_drafts ADD COLUMN scheduled_at TEXT NOT NULL DEFAULT ''"),
                    ("variants_json", "ALTER TABLE content_drafts ADD COLUMN variants_json TEXT NOT NULL DEFAULT '[]'"),
                    ("starred", "ALTER TABLE content_drafts ADD COLUMN starred INTEGER NOT NULL DEFAULT 0"),
                    ("format_meta_json", "ALTER TABLE content_drafts ADD COLUMN format_meta_json TEXT NOT NULL DEFAULT '{}'"),
                    ("visual_html", "ALTER TABLE content_drafts ADD COLUMN visual_html TEXT NOT NULL DEFAULT ''"),
                    ("published_post_id", "ALTER TABLE content_drafts ADD COLUMN published_post_id TEXT NOT NULL DEFAULT ''"),
                    ("published_permalink", "ALTER TABLE content_drafts ADD COLUMN published_permalink TEXT NOT NULL DEFAULT ''"),
                    ("published_at", "ALTER TABLE content_drafts ADD COLUMN published_at TEXT NOT NULL DEFAULT ''"),
                ),
            )

    def health_check(self) -> dict:
        try:
            with self._connect() as db:
                row = db.execute("SELECT 1").fetchone()
                mode_row = db.execute("PRAGMA journal_mode").fetchone()
            size = Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0
            return {
                "ok": bool(row and row[0] == 1),
                "db_path": self.db_path,
                "journal_mode": str(mode_row[0]) if mode_row else "",
                "size_bytes": size,
            }
        except sqlite3.Error as exc:
            return {"ok": False, "error": str(exc)[:200]}

    def backup_dir(self, dest_dir: str | Path | None = None) -> Path:
        base = Path(dest_dir) if dest_dir else Path(self.db_path).parent / "backups"
        base.mkdir(parents=True, exist_ok=True, mode=0o700)
        return base

    def backup_database(self, dest_dir: str | Path | None = None, *, keep: int = 7) -> Path:
        target_dir = self.backup_dir(dest_dir)
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        dest = target_dir / f"research-{stamp}.db"
        if dest.exists():
            dest = target_dir / f"research-{stamp}-{int(time.time() * 1000)}.db"
        with self._connect() as src, closing(sqlite3.connect(dest)) as dst:
            src.backup(dst)
        os.chmod(dest, 0o600)
        backups = sorted(target_dir.glob("research-*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
        for stale in backups[max(1, int(keep)):]:
            stale.unlink(missing_ok=True)
        return dest

    def latest_backup_path(self, dest_dir: str | Path | None = None) -> Path:
        target_dir = self.backup_dir(dest_dir)
        backups = sorted(target_dir.glob("research-*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
        if backups:
            return backups[0]
        return self.backup_database(target_dir)

    def save_token(self, access_token: str, expires_at: int) -> None:
        self.vault.set(access_token)
        with self._connect() as db, db:
            db.execute("INSERT OR REPLACE INTO token VALUES (1, ?)", (expires_at,))

    def save_token_meta(self, *, user_id: str = "", username: str = "", scopes: list[str] | tuple[str, ...] = ()) -> None:
        refreshed = datetime.now(UTC).isoformat()
        with self._connect() as db, db:
            db.execute(
                "INSERT INTO token_meta(id, user_id, username, scopes_json, refreshed_at) VALUES (1, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET user_id = excluded.user_id, username = excluded.username, "
                "scopes_json = excluded.scopes_json, refreshed_at = excluded.refreshed_at",
                (str(user_id)[:80], str(username).lstrip("@")[:80], json.dumps(list(scopes)), refreshed),
            )

    def get_token_meta(self) -> dict | None:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            row = db.execute("SELECT * FROM token_meta WHERE id = 1").fetchone()
        if not row:
            return None
        return {
            "user_id": str(row["user_id"]),
            "username": str(row["username"]),
            "scopes": _safe_json_loads(row["scopes_json"], []),
            "refreshed_at": str(row["refreshed_at"]),
        }

    def token_expiry(self) -> int | None:
        with self._connect() as db:
            row = db.execute("SELECT expires_at FROM token WHERE id=1").fetchone()
        return row[0] if row else None

    def get_token(self) -> StoredToken | None:
        expiry = self.token_expiry()
        if expiry is None:
            return None
        token = self.vault.get()
        return StoredToken(token, expiry) if token else None

    def delete_token(self) -> None:
        self.vault.delete()
        with self._connect() as db, db:
            db.execute("DELETE FROM token")
            db.execute("DELETE FROM token_meta")

    def save_insights(self, items: list[dict]) -> None:
        created = datetime.now(UTC).isoformat()
        with self._connect() as db, db:
            db.executemany(
                "INSERT OR IGNORE INTO insights(theme, quote, source_url, ebook_idea, created_at, source_type, engagement_weight) VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        i["theme"],
                        i["quote"],
                        i["source_url"],
                        i.get("ebook_idea", ""),
                        created,
                        str(i.get("source_type", "threads_reply"))[:40],
                        max(1, int(i.get("engagement_weight", 1) or 1)),
                    )
                    for i in items
                ],
            )

    def list_insights(self, *, query: str = "", limit: int = 500) -> list[dict]:
        limit = min(max(int(limit), 1), 1000)
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            if query.strip():
                term = query.strip().casefold()
                rows = db.execute(
                    "SELECT * FROM insights WHERE instr(lower(theme), ?) > 0 OR instr(lower(quote), ?) > 0 OR instr(lower(ebook_idea), ?) > 0 ORDER BY id DESC LIMIT ?",
                    (term, term, term, limit),
                )
            else:
                rows = db.execute("SELECT * FROM insights ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in rows]

    def save_research_run(self, *, posts_sampled: int, selected_posts: int, insights: list[dict], limitations: str, posts: list[dict] | None = None,  # noqa: PLR0913
                          post_limit: int = 50, top_posts: int = 5, replies_per_post: int = 50, focus: str = "") -> int:
        created = datetime.now(UTC).isoformat()
        themes = sorted({str(item.get("theme", "")).strip() for item in insights if item.get("theme")})
        focus = " ".join(str(focus or "").split())[:500]
        safe_posts = []
        for post in (posts or [])[:max(1, int(top_posts))]:
            metrics = post.get("metrics", {})
            safe_posts.append({
                "id": str(post.get("id", ""))[:80], "text": str(post.get("text", ""))[:2000],
                "permalink": str(post.get("permalink", ""))[:500], "timestamp": str(post.get("timestamp", ""))[:80],
                "metrics": {key: max(0, int(metrics.get(key, 0))) for key in ("views", "likes", "replies", "reposts", "quotes") if str(metrics.get(key, "")).lstrip("-").isdigit()},
                "engagement_score": max(0, int(post.get("engagement_score", 0) or 0)),
            })
        with self._connect() as db, db:
            cursor = db.execute(
                "INSERT INTO research_runs(created_at, posts_sampled, selected_posts, insights_count, themes_json, limitations, posts_json, post_limit, top_posts, replies_per_post, focus) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (created, posts_sampled, selected_posts, len(insights), json.dumps(themes, ensure_ascii=False), limitations[:2000], json.dumps(safe_posts, ensure_ascii=False),
                 max(1, int(post_limit)), max(1, int(top_posts)), max(1, int(replies_per_post)), focus),
            )
            return int(cursor.lastrowid)

    def get_insights_by_ids(self, insight_ids: list[int]) -> list[dict]:
        ids = list(dict.fromkeys(int(value) for value in insight_ids))[:20]
        if not ids:
            return []
        placeholders = ",".join("?" for _ in ids)
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            rows = db.execute(f"SELECT * FROM insights WHERE id IN ({placeholders})", ids)
            by_id = {int(row["id"]): dict(row) for row in rows}
        return [by_id[value] for value in ids if value in by_id]

    def list_research_runs(self, limit: int = 50) -> list[dict]:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("SELECT * FROM research_runs ORDER BY id DESC LIMIT ?", (min(max(int(limit), 1), 200),))
            result = []
            for row in rows:
                item = dict(row)
                item["themes"] = _safe_json_loads(item.pop("themes_json"), [])
                item["posts"] = _safe_json_loads(item.pop("posts_json"), [])
                result.append(item)
            return result

    @staticmethod
    def _draft_row(row) -> dict:
        item = dict(row)
        item["content"] = _safe_json_loads(item.pop("content_json"), {})
        item["source_ids"] = _safe_json_loads(item.pop("source_ids_json"), [])
        item["variants"] = _safe_json_loads(item.pop("variants_json", "[]"), [])
        item["format_meta"] = _safe_json_loads(item.pop("format_meta_json", "{}"), {})
        item["starred"] = bool(item.get("starred", 0))
        return item

    def save_drafts(self, items: list[dict], source_ids: list[int]) -> list[dict]:
        created = datetime.now(UTC).isoformat()
        saved = []
        with self._connect() as db, db:
            for item in items:
                cited_ids = sorted(set(item.get("source_ids", source_ids)))
                variants = item.get("variants") if isinstance(item.get("variants"), list) else []
                format_meta = item.get("format_meta") if isinstance(item.get("format_meta"), dict) else {}
                cursor = db.execute(
                    "INSERT INTO content_drafts(kind, title, content_json, source_ids_json, status, created_at, variants_json, format_meta_json) VALUES (?, ?, ?, ?, 'draft', ?, ?, ?)",
                    (
                        item["kind"],
                        item["title"],
                        json.dumps(item["content"], ensure_ascii=False),
                        json.dumps(cited_ids),
                        created,
                        json.dumps(variants, ensure_ascii=False),
                        json.dumps(format_meta, ensure_ascii=False),
                    ),
                )
                saved.append({
                    "id": int(cursor.lastrowid),
                    **item,
                    "source_ids": cited_ids,
                    "variants": variants,
                    "format_meta": format_meta,
                    "starred": False,
                    "status": "draft",
                    "created_at": created,
                    "scheduled_at": "",
                    "published_post_id": "",
                    "published_permalink": "",
                    "published_at": "",
                })
        return saved

    def list_drafts(self, *, status: str = "", limit: int = 100) -> list[dict]:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            if status in VALID_DRAFT_STATUSES:
                rows = db.execute("SELECT * FROM content_drafts WHERE status = ? ORDER BY starred DESC, id DESC LIMIT ?", (status, min(max(int(limit), 1), 200)))
            else:
                rows = db.execute("SELECT * FROM content_drafts ORDER BY id DESC LIMIT ?", (min(max(int(limit), 1), 200),))
            return [self._draft_row(row) for row in rows]

    def update_draft_status(self, draft_id: int, status: str) -> bool:
        if status not in VALID_DRAFT_STATUSES:
            return False
        with self._connect() as db, db:
            cursor = db.execute("UPDATE content_drafts SET status = ? WHERE id = ?", (status, draft_id))
            return cursor.rowcount == 1

    def get_draft(self, draft_id: int) -> dict | None:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            row = db.execute("SELECT * FROM content_drafts WHERE id = ?", (int(draft_id),)).fetchone()
        return self._draft_row(row) if row else None

    def update_draft_content(self, draft_id: int, *, title: str | None = None, content: dict | None = None, format_meta: dict | None = None) -> bool:
        existing = self.get_draft(draft_id)
        if not existing:
            return False
        new_title = " ".join(str(title if title is not None else existing["title"]).split())[:160]
        if not new_title:
            return False
        new_content = content if isinstance(content, dict) else existing["content"]
        new_meta = format_meta if isinstance(format_meta, dict) else existing.get("format_meta", {})
        with self._connect() as db, db:
            cursor = db.execute(
                "UPDATE content_drafts SET title = ?, content_json = ?, format_meta_json = ? WHERE id = ?",
                (new_title, json.dumps(new_content, ensure_ascii=False), json.dumps(new_meta, ensure_ascii=False), int(draft_id)),
            )
            return cursor.rowcount == 1

    def toggle_draft_star(self, draft_id: int) -> bool | None:
        existing = self.get_draft(draft_id)
        if not existing:
            return None
        next_val = 0 if existing.get("starred") else 1
        with self._connect() as db, db:
            db.execute("UPDATE content_drafts SET starred = ? WHERE id = ?", (next_val, int(draft_id)))
        return bool(next_val)

    def update_draft_variants(self, draft_id: int, variants: list[dict]) -> bool:
        with self._connect() as db, db:
            cursor = db.execute(
                "UPDATE content_drafts SET variants_json = ? WHERE id = ?",
                (json.dumps(variants, ensure_ascii=False), int(draft_id)),
            )
            return cursor.rowcount == 1

    def update_draft_visual(self, draft_id: int, visual_html: str) -> bool:
        with self._connect() as db, db:
            cursor = db.execute(
                "UPDATE content_drafts SET visual_html = ? WHERE id = ?",
                (str(visual_html)[:150000], int(draft_id)),
            )
            return cursor.rowcount == 1

    def schedule_draft(self, draft_id: int, scheduled_at: str) -> bool:
        with self._connect() as db, db:
            cursor = db.execute(
                "UPDATE content_drafts SET scheduled_at = ?, status = 'scheduled' WHERE id = ?",
                (str(scheduled_at)[:60], int(draft_id)),
            )
            return cursor.rowcount == 1

    def list_due_scheduled_drafts(self, now_iso: str | None = None) -> list[dict]:
        now = now_iso or datetime.now(UTC).isoformat()
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            rows = db.execute(
                "SELECT * FROM content_drafts WHERE status = 'scheduled' AND scheduled_at != '' AND scheduled_at <= ? ORDER BY scheduled_at ASC",
                (now,),
            ).fetchall()
            return [self._draft_row(row) for row in rows]

    def mark_draft_published(self, draft_id: int, *, post_id: str = "", permalink: str = "") -> bool:
        published_at = datetime.now(UTC).isoformat()
        with self._connect() as db, db:
            cursor = db.execute(
                "UPDATE content_drafts SET status = 'published', published_post_id = ?, published_permalink = ?, published_at = ? WHERE id = ?",
                (str(post_id)[:80], str(permalink)[:500], published_at, int(draft_id)),
            )
            return cursor.rowcount == 1

    # -- follower import & graph audience ----------------------------------

    def save_graph_audience(
        self,
        *,
        profile: dict | None = None,
        followers_count: int | None = None,
        metrics: dict | None = None,
        demographics: dict | None = None,
        engagers: list[dict] | None = None,
    ) -> str:
        synced_at = datetime.now(UTC).isoformat()
        current = self.get_graph_audience() or {}
        next_profile = profile if isinstance(profile, dict) else current.get("profile", {})
        old_followers = current.get("followers_count")
        prev_followers = current.get("previous_followers_count")
        if followers_count is not None:
            next_followers = max(0, int(followers_count))
            if old_followers is not None and int(old_followers) > 0 and int(old_followers) != next_followers:
                prev_followers = int(old_followers)
        else:
            next_followers = max(0, int(old_followers or 0))
        next_metrics = metrics if isinstance(metrics, dict) else current.get("metrics", {})
        next_demographics = demographics if isinstance(demographics, dict) and demographics else current.get("demographics", {})
        next_engagers = engagers if isinstance(engagers, list) else current.get("engagers", [])
        with self._connect() as db, db:
            db.execute(
                "INSERT INTO graph_audience(id, profile_json, followers_count, previous_followers_count, metrics_json, demographics_json, engagers_json, synced_at) "
                "VALUES (1, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET profile_json = excluded.profile_json, "
                "followers_count = excluded.followers_count, previous_followers_count = excluded.previous_followers_count, "
                "metrics_json = excluded.metrics_json, demographics_json = excluded.demographics_json, "
                "engagers_json = excluded.engagers_json, synced_at = excluded.synced_at",
                (
                    json.dumps(next_profile, ensure_ascii=False),
                    next_followers,
                    prev_followers,
                    json.dumps(next_metrics, ensure_ascii=False),
                    json.dumps(next_demographics, ensure_ascii=False),
                    json.dumps(next_engagers, ensure_ascii=False),
                    synced_at,
                ),
            )
            db.execute(
                "INSERT INTO graph_metric_history(recorded_at, followers_count, views, likes, replies, reposts, quotes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    synced_at,
                    next_followers,
                    max(0, int(next_metrics.get("views", 0) or 0)),
                    max(0, int(next_metrics.get("likes", 0) or 0)),
                    max(0, int(next_metrics.get("replies", 0) or 0)),
                    max(0, int(next_metrics.get("reposts", 0) or 0)),
                    max(0, int(next_metrics.get("quotes", 0) or 0)),
                ),
            )
        return synced_at

    def list_graph_metric_history(self, limit: int = 30) -> list[dict]:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            rows = db.execute(
                "SELECT * FROM graph_metric_history ORDER BY id DESC LIMIT ?",
                (min(max(int(limit), 1), 100),),
            ).fetchall()
        return [dict(row) for row in reversed(rows)]

    def get_graph_audience(self) -> dict | None:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            row = db.execute("SELECT * FROM graph_audience WHERE id = 1").fetchone()
        if not row:
            return None
        return {
            "profile": _safe_json_loads(row["profile_json"], {}),
            "followers_count": int(row["followers_count"]),
            "previous_followers_count": int(row["previous_followers_count"]) if row["previous_followers_count"] is not None else None,
            "metrics": _safe_json_loads(row["metrics_json"], {}),
            "demographics": _safe_json_loads(row["demographics_json"], {}),
            "engagers": _safe_json_loads(row["engagers_json"], []),
            "synced_at": row["synced_at"],
        }

    def clear_graph_audience(self) -> bool:
        with self._connect() as db, db:
            cursor = db.execute("DELETE FROM graph_audience WHERE id = 1")
            return cursor.rowcount == 1

    def save_audience(self, followers: list[dict], following: list[dict]) -> str:
        imported = datetime.now(UTC).isoformat()
        followers_dump = json.dumps(followers, ensure_ascii=False)
        following_dump = json.dumps(following, ensure_ascii=False)
        with self._connect() as db, db:
            db.execute(
                "INSERT INTO audience(id, followers_json, following_json, imported_at) VALUES (1, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET followers_json = excluded.followers_json, "
                "following_json = excluded.following_json, imported_at = excluded.imported_at",
                (followers_dump, following_dump, imported),
            )
            db.execute(
                "INSERT INTO audience_snapshots(imported_at, followers_count, following_count, followers_json, following_json) VALUES (?, ?, ?, ?, ?)",
                (imported, len(followers), len(following), followers_dump, following_dump),
            )
            db.execute(
                "DELETE FROM audience_snapshots WHERE id NOT IN (SELECT id FROM audience_snapshots ORDER BY id DESC LIMIT 30)"
            )
        return imported

    def get_previous_audience_snapshot(self) -> dict | None:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("SELECT * FROM audience_snapshots ORDER BY id DESC LIMIT 2").fetchall()
        if len(rows) < 2:
            return None
        prev = rows[1]
        return {
            "id": int(prev["id"]),
            "imported_at": str(prev["imported_at"]),
            "followers_count": int(prev["followers_count"]),
            "following_count": int(prev["following_count"]),
            "followers": _safe_json_loads(prev["followers_json"], []),
            "following": _safe_json_loads(prev["following_json"], []),
        }

    def list_audience_snapshots(self, limit: int = 12) -> list[dict]:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            rows = db.execute(
                "SELECT id, imported_at, followers_count, following_count FROM audience_snapshots ORDER BY id DESC LIMIT ?",
                (min(max(int(limit), 1), 30),),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_audience(self) -> dict | None:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            row = db.execute("SELECT * FROM audience WHERE id = 1").fetchone()
        if not row:
            return None
        return {
            "followers": _safe_json_loads(row["followers_json"], []),
            "following": _safe_json_loads(row["following_json"], []),
            "imported_at": row["imported_at"],
        }

    def clear_audience(self) -> bool:
        with self._connect() as db, db:
            cursor = db.execute("DELETE FROM audience WHERE id = 1")
            db.execute("DELETE FROM unfollow_queue")
            return cursor.rowcount == 1

    def set_unfollow_status(self, usernames: list[str], status: str) -> int:
        if status not in ("later", "unfollowed", "keep"):
            raise StoreError("Invalid unfollow status.")
        cleaned = []
        seen = set()
        for raw in usernames or []:
            uname = str(raw or "").strip().lstrip("@")[:60]
            key = uname.casefold()
            if uname and key not in seen:
                seen.add(key)
                cleaned.append((key, uname))
        if not cleaned:
            return 0
        stamp = datetime.now(UTC).isoformat()
        with self._connect() as db, db:
            if status == "keep":
                db.executemany("DELETE FROM unfollow_queue WHERE username_key = ?", [(k,) for k, _ in cleaned])
            else:
                db.executemany(
                    "INSERT INTO unfollow_queue(username_key, username, status, updated_at) VALUES (?, ?, ?, ?) "
                    "ON CONFLICT(username_key) DO UPDATE SET username = excluded.username, status = excluded.status, updated_at = excluded.updated_at",
                    [(k, u, status, stamp) for k, u in cleaned],
                )
        return len(cleaned)

    def get_unfollow_map(self) -> dict[str, str]:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("SELECT username_key, status FROM unfollow_queue").fetchall()
        return {str(row["username_key"]): str(row["status"]) for row in rows}

    def list_unfollow_queue(self) -> list[dict]:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("SELECT username, status, updated_at FROM unfollow_queue ORDER BY updated_at DESC, username_key ASC").fetchall()
        return [
            {
                "username": str(row["username"]),
                "href": f"https://www.threads.com/@{row['username']}",
                "profile_url": f"https://www.threads.com/@{row['username']}",
                "since": 0,
                "follows_back": False,
                "days_followed": None,
                "tenure_bucket": "unknown",
                "unfollow_status": str(row["status"]),
                "replies_count": 0,
                "insight_count": 0,
            }
            for row in rows
        ]

    # -- job queue ---------------------------------------------------------

    @staticmethod
    def _job_row(row) -> dict:
        item = dict(row)
        item["params"] = _safe_json_loads(item.pop("params_json"), {})
        item["result"] = _safe_json_loads(item.pop("result_json"), {})
        item["cancel_requested"] = bool(item["cancel_requested"])
        return item

    def _job(self, job_id: int) -> dict | None:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            row = db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return self._job_row(row) if row else None

    def create_job(self, kind: str, params: dict) -> dict:
        if kind not in VALID_JOB_KINDS:
            raise StoreError("Unknown job kind.")
        created = datetime.now(UTC).isoformat()
        with self._connect() as db, db:
            cursor = db.execute(
                "INSERT INTO jobs(kind, status, params_json, created_at) VALUES (?, 'queued', ?, ?)",
                (kind, json.dumps(params, ensure_ascii=False), created),
            )
            job_id = int(cursor.lastrowid)
        return self._job(job_id)

    def list_jobs(self, limit: int = 20) -> list[dict]:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("SELECT * FROM jobs ORDER BY id DESC LIMIT ?", (min(max(int(limit), 1), 200),)).fetchall()
        return [self._job_row(row) for row in rows]

    def claim_job(self) -> dict | None:
        with self._connect() as db, db:
            db.row_factory = sqlite3.Row
            row = db.execute("SELECT * FROM jobs WHERE status = 'queued' ORDER BY id LIMIT 1").fetchone()
            if not row:
                return None
            started = datetime.now(UTC).isoformat()
            db.execute("UPDATE jobs SET status = 'running', started_at = ?, cancel_requested = 0 WHERE id = ?", (started, row["id"]))
            job_id = int(row["id"])
        return self._job(job_id)

    def finish_job(self, job_id: int, result: dict) -> None:
        with self._connect() as db, db:
            db.execute(
                "UPDATE jobs SET status = 'done', result_json = ?, finished_at = ?, cancel_requested = 0 WHERE id = ? AND status = 'running'",
                (_compact_job_result(result), datetime.now(UTC).isoformat(), job_id),
            )

    def fail_job(self, job_id: int, message: str) -> None:
        with self._connect() as db, db:
            db.execute(
                "UPDATE jobs SET status = 'failed', error = ?, finished_at = ?, cancel_requested = 0 WHERE id = ? AND status = 'running'",
                (str(message)[:2000], datetime.now(UTC).isoformat(), job_id),
            )

    def cancel_job(self, job_id: int) -> bool:
        """Queued jobs stop immediately; a running job is asked to stop between stages."""
        with self._connect() as db, db:
            cursor = db.execute(
                "UPDATE jobs SET status = 'cancelled', finished_at = ? WHERE id = ? AND status = 'queued'",
                (datetime.now(UTC).isoformat(), job_id),
            )
            if cursor.rowcount:
                return True
            cursor = db.execute("UPDATE jobs SET cancel_requested = 1 WHERE id = ? AND status = 'running'", (job_id,))
            return cursor.rowcount == 1

    def mark_job_cancelled(self, job_id: int) -> None:
        with self._connect() as db, db:
            db.execute(
                "UPDATE jobs SET status = 'cancelled', finished_at = ?, cancel_requested = 0 WHERE id = ? AND status = 'running'",
                (datetime.now(UTC).isoformat(), job_id),
            )

    def job_cancel_requested(self, job_id: int) -> bool:
        with self._connect() as db:
            row = db.execute("SELECT cancel_requested FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return bool(row and row[0])

    def retry_job(self, job_id: int) -> dict | None:
        job = self._job(job_id)
        if not job or job["kind"] not in VALID_JOB_KINDS or job["status"] not in ("failed", "cancelled"):
            return None
        return self.create_job(job["kind"], job["params"])

    def clear_queued_jobs(self) -> int:
        with self._connect() as db, db:
            cursor = db.execute("UPDATE jobs SET status = 'cancelled', finished_at = ? WHERE status = 'queued'", (datetime.now(UTC).isoformat(),))
            return cursor.rowcount

    def recover_interrupted_jobs(self) -> int:
        """A process restart loses the worker; running jobs cannot be resumed."""
        with self._connect() as db, db:
            cursor = db.execute(
                "UPDATE jobs SET status = 'failed', error = 'Interrupted by a restart. Retry the job.', finished_at = ? WHERE status = 'running'",
                (datetime.now(UTC).isoformat(),),
            )
            return cursor.rowcount

    # -- oauth state & rate limiting ---------------------------------------

    def save_oauth_state(self, state: str, verifier: str, *, ttl_seconds: int = 900, now_ts: float | None = None) -> None:
        now = datetime.fromtimestamp(now_ts, UTC) if now_ts is not None else datetime.now(UTC)
        expires = now + timedelta(seconds=max(60, int(ttl_seconds)))
        with self._connect() as db, db:
            db.execute("DELETE FROM oauth_states WHERE expires_at <= ?", (now.isoformat(),))
            db.execute(
                "INSERT OR REPLACE INTO oauth_states(state, verifier, created_at, expires_at) VALUES (?, ?, ?, ?)",
                (state, verifier, now.isoformat(), expires.isoformat()),
            )

    def consume_oauth_state(self, state: str, *, now_ts: float | None = None) -> str | None:
        now_dt = datetime.fromtimestamp(now_ts, UTC) if now_ts is not None else datetime.now(UTC)
        now_iso = now_dt.isoformat()
        with self._connect() as db, db:
            row = db.execute("SELECT verifier, expires_at FROM oauth_states WHERE state = ?", (state,)).fetchone()
            db.execute("DELETE FROM oauth_states WHERE state = ? OR expires_at <= ?", (state, now_iso))
        if not row or str(row[1]) <= now_iso:
            return None
        return str(row[0])

    def check_auth_locked(self, ip: str, *, now_ts: float | None = None) -> bool:
        now = float(now_ts if now_ts is not None else time.time())
        with self._connect() as db:
            row = db.execute("SELECT locked_until FROM auth_failures WHERE ip = ?", (ip[:80],)).fetchone()
        return bool(row and float(row[0]) > now)

    def record_auth_failure(
        self,
        ip: str,
        *,
        window_seconds: int = 300,
        limit: int = 5,
        lockout_seconds: int = 900,
        now_ts: float | None = None,
    ) -> bool:
        now = float(now_ts if now_ts is not None else time.time())
        key = ip[:80]
        with self._connect() as db, db:
            row = db.execute("SELECT failures, window_started_at, locked_until FROM auth_failures WHERE ip = ?", (key,)).fetchone()
            if not row or (now - float(row[1])) > window_seconds:
                failures = 1
                window_start = now
                locked_until = 0.0
            else:
                failures = int(row[0]) + 1
                window_start = float(row[1])
                locked_until = float(row[2])
            if failures >= limit:
                locked_until = max(locked_until, now + lockout_seconds)
            db.execute(
                "INSERT INTO auth_failures(ip, failures, window_started_at, locked_until) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(ip) DO UPDATE SET failures = excluded.failures, window_started_at = excluded.window_started_at, locked_until = excluded.locked_until",
                (key, failures, window_start, locked_until),
            )
        return locked_until > now

    def clear_auth_failures(self, ip: str) -> None:
        with self._connect() as db, db:
            db.execute("DELETE FROM auth_failures WHERE ip = ?", (ip[:80],))

    # -- engagement inbox --------------------------------------------------

    def upsert_inbox_items(self, items: list[dict]) -> int:
        if not items:
            return 0
        now_iso = datetime.now(UTC).isoformat()
        count = 0
        with self._connect() as db, db:
            for item in items:
                reply_id = str(item.get("reply_id") or item.get("id") or "").strip()[:80]
                text = " ".join(str(item.get("text") or "").split())[:2000]
                if not reply_id or not text:
                    continue
                db.execute(
                    "INSERT INTO engagement_inbox(reply_id, post_id, post_permalink, username, text, is_hidden, status, draft_reply, sentiment, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, 'open', '', ?, ?) "
                    "ON CONFLICT(reply_id) DO UPDATE SET post_id = COALESCE(NULLIF(excluded.post_id, ''), engagement_inbox.post_id), "
                    "post_permalink = COALESCE(NULLIF(excluded.post_permalink, ''), engagement_inbox.post_permalink), "
                    "username = COALESCE(NULLIF(excluded.username, ''), engagement_inbox.username), "
                    "text = excluded.text",
                    (
                        reply_id,
                        str(item.get("post_id", ""))[:80],
                        str(item.get("post_permalink", ""))[:500],
                        str(item.get("username", "")).lstrip("@")[:60],
                        text,
                        1 if item.get("is_hidden") else 0,
                        str(item.get("sentiment", "neutral"))[:24],
                        str(item.get("created_at") or now_iso)[:60],
                    ),
                )
                count += 1
        return count

    def list_inbox_items(self, *, status: str = "", limit: int = 100) -> list[dict]:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            if status in ("open", "replied", "dismissed"):
                rows = db.execute(
                    "SELECT * FROM engagement_inbox WHERE status = ? ORDER BY id DESC LIMIT ?",
                    (status, min(max(int(limit), 1), 300)),
                ).fetchall()
            else:
                rows = db.execute(
                    "SELECT * FROM engagement_inbox ORDER BY CASE status WHEN 'open' THEN 0 ELSE 1 END, id DESC LIMIT ?",
                    (min(max(int(limit), 1), 300),),
                ).fetchall()
        return [{**dict(row), "is_hidden": bool(row["is_hidden"])} for row in rows]

    def get_inbox_item(self, item_id: int) -> dict | None:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            row = db.execute("SELECT * FROM engagement_inbox WHERE id = ?", (int(item_id),)).fetchone()
        return {**dict(row), "is_hidden": bool(row["is_hidden"])} if row else None

    def save_inbox_draft_reply(self, item_id: int, draft_reply: str) -> bool:
        with self._connect() as db, db:
            cursor = db.execute(
                "UPDATE engagement_inbox SET draft_reply = ? WHERE id = ?",
                (str(draft_reply)[:1000], int(item_id)),
            )
            return cursor.rowcount == 1

    def mark_inbox_replied(self, item_id: int, reply_text: str = "") -> bool:
        replied_at = datetime.now(UTC).isoformat()
        with self._connect() as db, db:
            cursor = db.execute(
                "UPDATE engagement_inbox SET status = 'replied', draft_reply = CASE WHEN ? != '' THEN ? ELSE draft_reply END, replied_at = ? WHERE id = ?",
                (str(reply_text)[:1000], str(reply_text)[:1000], replied_at, int(item_id)),
            )
            return cursor.rowcount == 1

    def set_inbox_hidden(self, item_id: int, hidden: bool) -> bool:
        with self._connect() as db, db:
            cursor = db.execute(
                "UPDATE engagement_inbox SET is_hidden = ?, status = CASE WHEN ? = 1 AND status = 'open' THEN 'dismissed' ELSE status END WHERE id = ?",
                (1 if hidden else 0, 1 if hidden else 0, int(item_id)),
            )
            return cursor.rowcount == 1

    def update_inbox_status(self, item_id: int, status: str) -> bool:
        if status not in ("open", "replied", "dismissed"):
            return False
        with self._connect() as db, db:
            cursor = db.execute("UPDATE engagement_inbox SET status = ? WHERE id = ?", (status, int(item_id)))
            return cursor.rowcount == 1

    # -- AI telemetry ------------------------------------------------------

    def record_ai_usage(
        self,
        provider: str,
        model: str,
        operation: str,
        stats: dict | None = None,
    ) -> None:
        info = stats or {}
        with self._connect() as db, db:
            db.execute(
                "INSERT INTO ai_usage(provider, model, operation, prompt_tokens, completion_tokens, duration_ms, ok, error, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    str(provider)[:40],
                    str(model)[:120],
                    str(operation)[:60],
                    max(0, int(info.get("prompt_tokens", 0) or 0)),
                    max(0, int(info.get("completion_tokens", 0) or 0)),
                    max(0, int(info.get("duration_ms", 0) or 0)),
                    1 if info.get("ok", True) else 0,
                    str(info.get("error", ""))[:300],
                    datetime.now(UTC).isoformat(),
                ),
            )

    def ai_usage_summary(self, limit: int = 20) -> dict:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            rows = db.execute(
                "SELECT provider, COUNT(*) AS calls, SUM(ok) AS ok_calls, SUM(prompt_tokens) AS prompt_tokens, "
                "SUM(completion_tokens) AS completion_tokens, AVG(duration_ms) AS avg_ms FROM ai_usage GROUP BY provider"
            ).fetchall()
            recent = db.execute("SELECT * FROM ai_usage ORDER BY id DESC LIMIT ?", (min(max(int(limit), 1), 100),)).fetchall()
        return {
            "by_provider": [dict(r) for r in rows],
            "recent": [dict(r) for r in recent],
        }

    # -- knowledge graph & audience segments -------------------------------

    def upsert_knowledge_node(
        self,
        slug: str,
        title: str,
        body: str = "",
        meta: dict | None = None,
    ) -> dict:
        info = meta or {}
        category = str(info.get("category", "brand"))[:40]
        summary = str(info.get("summary", ""))[:500]
        links = info.get("links") or []
        clean_slug = "-".join(str(slug or "").strip().lower().split())[:80]
        clean_title = " ".join(str(title or clean_slug).split())[:160]
        clean_links = sorted({str(link).strip() for link in links if str(link).strip()})[:40]
        updated_at = datetime.now(UTC).isoformat()
        with self._connect() as db, db:
            db.execute(
                "INSERT INTO knowledge_nodes(slug, title, category, summary, body, links_json, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(slug) DO UPDATE SET title = excluded.title, category = excluded.category, "
                "summary = excluded.summary, body = excluded.body, links_json = excluded.links_json, updated_at = excluded.updated_at",
                (clean_slug, clean_title, category, summary, str(body)[:20000], json.dumps(clean_links, ensure_ascii=False), updated_at),
            )
            db.execute("DELETE FROM knowledge_edges WHERE source_slug = ?", (clean_slug,))
            if clean_links:
                db.executemany(
                    "INSERT OR IGNORE INTO knowledge_edges(source_slug, target_slug, relation) VALUES (?, ?, 'wiki_link')",
                    [(clean_slug, target[:80]) for target in clean_links],
                )
        return self.get_knowledge_node(clean_slug) or {}

    def get_knowledge_node(self, slug: str) -> dict | None:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            row = db.execute("SELECT * FROM knowledge_nodes WHERE slug = ?", (slug,)).fetchone()
        if not row:
            return None
        item = dict(row)
        item["links"] = _safe_json_loads(item.pop("links_json"), [])
        return item

    def list_knowledge_nodes(self) -> list[dict]:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("SELECT * FROM knowledge_nodes ORDER BY category ASC, title ASC").fetchall()
        out = []
        for row in rows:
            item = dict(row)
            item["links"] = _safe_json_loads(item.pop("links_json"), [])
            out.append(item)
        return out

    def delete_knowledge_node(self, slug: str) -> bool:
        with self._connect() as db, db:
            db.execute("DELETE FROM knowledge_edges WHERE source_slug = ? OR target_slug = ?", (slug, slug))
            cursor = db.execute("DELETE FROM knowledge_nodes WHERE slug = ?", (slug,))
            return cursor.rowcount == 1

    def list_knowledge_edges(self) -> list[dict]:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("SELECT source_slug, target_slug, relation FROM knowledge_edges ORDER BY source_slug, target_slug").fetchall()
        return [dict(row) for row in rows]

    def upsert_audience_segment(self, *, slug: str, label: str, description: str = "", keywords: list[str] | tuple[str, ...] = ()) -> dict:
        clean_slug = "_".join(str(slug or "").strip().lower().split())[:60]
        clean_keywords = [str(k).strip().lower()[:60] for k in keywords if str(k).strip()][:30]
        created = datetime.now(UTC).isoformat()
        with self._connect() as db, db:
            db.execute(
                "INSERT INTO audience_segments(slug, label, description, keywords_json, created_at) VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(slug) DO UPDATE SET label = excluded.label, description = excluded.description, keywords_json = excluded.keywords_json",
                (clean_slug, str(label)[:120], str(description)[:300], json.dumps(clean_keywords, ensure_ascii=False), created),
            )
            db.row_factory = sqlite3.Row
            row = db.execute("SELECT * FROM audience_segments WHERE slug = ?", (clean_slug,)).fetchone()
        return {**dict(row), "keywords": _safe_json_loads(row["keywords_json"], [])}

    def list_audience_segments(self) -> list[dict]:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("SELECT * FROM audience_segments ORDER BY id DESC").fetchall()
        return [{**dict(r), "keywords": _safe_json_loads(r["keywords_json"], [])} for r in rows]

    def delete_audience_segment(self, slug: str) -> bool:
        with self._connect() as db, db:
            cursor = db.execute("DELETE FROM audience_segments WHERE slug = ?", (slug,))
            return cursor.rowcount == 1

    # -- notifications, watchlist & web bridge signals ---------------------

    def recent_notification_exists(self, dedupe_key: str, *, within_seconds: int = 300) -> bool:
        cutoff = (datetime.now(UTC) - timedelta(seconds=max(1, int(within_seconds)))).isoformat()
        with self._connect() as db:
            row = db.execute(
                "SELECT 1 FROM notifications WHERE dedupe_key = ? AND created_at >= ? LIMIT 1",
                (dedupe_key[:120], cutoff),
            ).fetchone()
        return bool(row)

    def record_notification(self, *, channel: str, dedupe_key: str, message: str, status: str = "sent", error: str = "") -> None:
        with self._connect() as db, db:
            db.execute(
                "INSERT INTO notifications(channel, dedupe_key, message, status, error, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (str(channel)[:40], str(dedupe_key)[:120], str(message)[:2000], str(status)[:24], str(error)[:300], datetime.now(UTC).isoformat()),
            )

    def list_notifications(self, limit: int = 30) -> list[dict]:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("SELECT * FROM notifications ORDER BY id DESC LIMIT ?", (min(max(int(limit), 1), 100),)).fetchall()
        return [dict(row) for row in rows]

    def get_watchlist_config(self) -> dict:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            row = db.execute("SELECT * FROM watchlist_config WHERE id = 1").fetchone()
        if not row:
            return {"enabled": False, "interval_hours": 24, "keywords": [], "focus": "", "last_run_at": ""}
        return {
            "enabled": bool(row["enabled"]),
            "interval_hours": int(row["interval_hours"]),
            "keywords": _safe_json_loads(row["keywords_json"], []),
            "focus": str(row["focus"]),
            "last_run_at": str(row["last_run_at"]),
        }

    def save_watchlist_config(self, *, enabled: bool, interval_hours: int, keywords: list[str], focus: str = "") -> dict:
        clean_kw = [str(k).strip()[:80] for k in keywords if str(k).strip()][:15]
        hours = min(max(int(interval_hours), 1), 168)
        with self._connect() as db, db:
            db.execute(
                "INSERT INTO watchlist_config(id, enabled, interval_hours, keywords_json, focus, last_run_at) VALUES (1, ?, ?, ?, ?, '') "
                "ON CONFLICT(id) DO UPDATE SET enabled = excluded.enabled, interval_hours = excluded.interval_hours, "
                "keywords_json = excluded.keywords_json, focus = excluded.focus",
                (1 if enabled else 0, hours, json.dumps(clean_kw, ensure_ascii=False), str(focus)[:400]),
            )
        return self.get_watchlist_config()

    def touch_watchlist_run(self) -> str:
        stamp = datetime.now(UTC).isoformat()
        with self._connect() as db, db:
            db.execute(
                "INSERT INTO watchlist_config(id, enabled, interval_hours, keywords_json, focus, last_run_at) VALUES (1, 0, 24, '[]', '', ?) "
                "ON CONFLICT(id) DO UPDATE SET last_run_at = excluded.last_run_at",
                (stamp,),
            )
        return stamp

    def ingest_external_signals(self, source: str, signals: list[dict]) -> int:
        if not signals:
            return 0
        now_iso = datetime.now(UTC).isoformat()
        inserted = 0
        with self._connect() as db, db:
            for item in signals[:100]:
                ext_id = str(item.get("id") or item.get("external_id") or "")[:80]
                quote = " ".join(str(item.get("quote") or item.get("text") or "").split())[:600]
                theme = " ".join(str(item.get("theme") or source).split())[:80]
                if not ext_id or not quote:
                    continue
                cur = db.execute(
                    "INSERT OR IGNORE INTO external_signals(source, external_id, theme, quote, url, meta_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        str(source)[:40],
                        ext_id,
                        theme,
                        quote,
                        str(item.get("url", ""))[:500],
                        json.dumps(item.get("meta") if isinstance(item.get("meta"), dict) else {}, ensure_ascii=False),
                        now_iso,
                    ),
                )
                if cur.rowcount == 1:
                    inserted += 1
                    db.execute(
                        "INSERT OR IGNORE INTO insights(theme, quote, source_url, ebook_idea, created_at, source_type, engagement_weight) VALUES (?, ?, ?, ?, ?, ?, 2)",
                        (theme, quote, str(item.get("url") or f"internal://{source}/{ext_id}")[:500], str(item.get("ebook_idea", ""))[:300], now_iso, str(source)[:40]),
                    )
        return inserted

    def list_external_signals(self, limit: int = 50) -> list[dict]:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("SELECT * FROM external_signals ORDER BY id DESC LIMIT ?", (min(max(int(limit), 1), 200),)).fetchall()
        return [{**dict(r), "meta": _safe_json_loads(r["meta_json"], {})} for r in rows]
