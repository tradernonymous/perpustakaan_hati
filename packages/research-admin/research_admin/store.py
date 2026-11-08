"""Private SQLite research storage; OAuth credentials stay encrypted or in the OS keyring."""

import base64
import hashlib
import json
import os
import sqlite3
import subprocess
from contextlib import closing
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken


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
        return closing(sqlite3.connect(self.db_path))

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

    def init_schema(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd = os.open(self.db_path, os.O_CREAT | os.O_WRONLY, 0o600)
        os.close(fd)
        os.chmod(self.db_path, 0o600)
        with closing(sqlite3.connect(self.db_path)) as db, db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS token (id INTEGER PRIMARY KEY CHECK(id=1), expires_at INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS secret (id INTEGER PRIMARY KEY CHECK(id=1), value BLOB NOT NULL);
                CREATE TABLE IF NOT EXISTS insights (
                    id INTEGER PRIMARY KEY, theme TEXT NOT NULL, quote TEXT NOT NULL,
                    source_url TEXT NOT NULL, ebook_idea TEXT NOT NULL, created_at TEXT NOT NULL,
                    UNIQUE(theme, quote, source_url)
                );
                CREATE TABLE IF NOT EXISTS research_runs (
                    id INTEGER PRIMARY KEY, created_at TEXT NOT NULL, posts_sampled INTEGER NOT NULL,
                    selected_posts INTEGER NOT NULL, insights_count INTEGER NOT NULL,
                    themes_json TEXT NOT NULL, limitations TEXT NOT NULL, posts_json TEXT NOT NULL DEFAULT '[]'
                );
                CREATE TABLE IF NOT EXISTS content_drafts (
                    id INTEGER PRIMARY KEY, kind TEXT NOT NULL, title TEXT NOT NULL,
                    content_json TEXT NOT NULL, source_ids_json TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'draft', created_at TEXT NOT NULL
                );
            """)
            columns = {row[1] for row in db.execute("PRAGMA table_info(research_runs)")}
            if "posts_json" not in columns:
                db.execute("ALTER TABLE research_runs ADD COLUMN posts_json TEXT NOT NULL DEFAULT '[]'")

    def save_token(self, access_token: str, expires_at: int) -> None:
        self.vault.set(access_token)
        with closing(sqlite3.connect(self.db_path)) as db, db:
            db.execute("INSERT OR REPLACE INTO token VALUES (1, ?)", (expires_at,))

    def token_expiry(self) -> int | None:
        with closing(sqlite3.connect(self.db_path)) as db:
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
        with closing(sqlite3.connect(self.db_path)) as db, db:
            db.execute("DELETE FROM token")

    def save_insights(self, items: list[dict]) -> None:
        created = datetime.now(UTC).isoformat()
        with closing(sqlite3.connect(self.db_path)) as db, db:
            db.executemany(
                "INSERT OR IGNORE INTO insights(theme, quote, source_url, ebook_idea, created_at) VALUES (?, ?, ?, ?, ?)",
                [(i["theme"], i["quote"], i["source_url"], i.get("ebook_idea", ""), created) for i in items],
            )

    def list_insights(self, *, query: str = "", limit: int = 500) -> list[dict]:
        limit = min(max(int(limit), 1), 1000)
        with closing(sqlite3.connect(self.db_path)) as db:
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

    def save_research_run(self, *, posts_sampled: int, selected_posts: int, insights: list[dict], limitations: str, posts: list[dict] | None = None) -> int:
        created = datetime.now(UTC).isoformat()
        themes = sorted({str(item.get("theme", "")).strip() for item in insights if item.get("theme")})
        safe_posts = []
        for post in (posts or [])[:5]:
            metrics = post.get("metrics", {})
            safe_posts.append({
                "id": str(post.get("id", ""))[:80], "text": str(post.get("text", ""))[:2000],
                "permalink": str(post.get("permalink", ""))[:500], "timestamp": str(post.get("timestamp", ""))[:80],
                "metrics": {key: max(0, int(metrics.get(key, 0))) for key in ("views", "likes", "replies", "reposts", "quotes") if str(metrics.get(key, "")).lstrip("-").isdigit()},
                "engagement_score": max(0, int(post.get("engagement_score", 0) or 0)),
            })
        with closing(sqlite3.connect(self.db_path)) as db, db:
            cursor = db.execute(
                "INSERT INTO research_runs(created_at, posts_sampled, selected_posts, insights_count, themes_json, limitations, posts_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (created, posts_sampled, selected_posts, len(insights), json.dumps(themes, ensure_ascii=False), limitations[:2000], json.dumps(safe_posts, ensure_ascii=False)),
            )
            return int(cursor.lastrowid)

    def get_insights_by_ids(self, insight_ids: list[int]) -> list[dict]:
        ids = list(dict.fromkeys(int(value) for value in insight_ids))[:20]
        if not ids:
            return []
        placeholders = ",".join("?" for _ in ids)
        with closing(sqlite3.connect(self.db_path)) as db:
            db.row_factory = sqlite3.Row
            rows = db.execute(f"SELECT * FROM insights WHERE id IN ({placeholders})", ids)
            by_id = {int(row["id"]): dict(row) for row in rows}
        return [by_id[value] for value in ids if value in by_id]

    def list_research_runs(self, limit: int = 50) -> list[dict]:
        with closing(sqlite3.connect(self.db_path)) as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("SELECT * FROM research_runs ORDER BY id DESC LIMIT ?", (min(max(int(limit), 1), 200),))
            result = []
            for row in rows:
                item = dict(row)
                item["themes"] = json.loads(item.pop("themes_json"))
                item["posts"] = json.loads(item.pop("posts_json"))
                result.append(item)
            return result

    def save_drafts(self, items: list[dict], source_ids: list[int]) -> list[dict]:
        created = datetime.now(UTC).isoformat()
        saved = []
        with closing(sqlite3.connect(self.db_path)) as db, db:
            for item in items:
                cited_ids = sorted(set(item.get("source_ids", source_ids)))
                cursor = db.execute(
                    "INSERT INTO content_drafts(kind, title, content_json, source_ids_json, status, created_at) VALUES (?, ?, ?, ?, 'draft', ?)",
                    (item["kind"], item["title"], json.dumps(item["content"], ensure_ascii=False), json.dumps(cited_ids), created),
                )
                saved.append({"id": int(cursor.lastrowid), **item, "source_ids": cited_ids, "status": "draft", "created_at": created})
        return saved

    def list_drafts(self, *, status: str = "", limit: int = 100) -> list[dict]:
        with closing(sqlite3.connect(self.db_path)) as db:
            db.row_factory = sqlite3.Row
            if status in ("draft", "approved", "archived"):
                rows = db.execute("SELECT * FROM content_drafts WHERE status = ? ORDER BY id DESC LIMIT ?", (status, min(max(int(limit), 1), 200)))
            else:
                rows = db.execute("SELECT * FROM content_drafts ORDER BY id DESC LIMIT ?", (min(max(int(limit), 1), 200),))
            result = []
            for row in rows:
                item = dict(row)
                item["content"] = json.loads(item.pop("content_json"))
                item["source_ids"] = json.loads(item.pop("source_ids_json"))
                result.append(item)
            return result

    def update_draft_status(self, draft_id: int, status: str) -> bool:
        if status not in ("draft", "approved", "archived"):
            return False
        with closing(sqlite3.connect(self.db_path)) as db, db:
            cursor = db.execute("UPDATE content_drafts SET status = ? WHERE id = ?", (status, draft_id))
            return cursor.rowcount == 1
