"""Private SQLite research storage; OAuth credentials stay in Secret Service."""

import hashlib
import os
import sqlite3
import subprocess
from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


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
                CREATE TABLE IF NOT EXISTS insights (
                    id INTEGER PRIMARY KEY, theme TEXT NOT NULL, quote TEXT NOT NULL,
                    source_url TEXT NOT NULL, ebook_idea TEXT NOT NULL, created_at TEXT NOT NULL,
                    UNIQUE(theme, quote, source_url)
                );
            """)

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
        created = datetime.now(timezone.utc).isoformat()
        with closing(sqlite3.connect(self.db_path)) as db, db:
            db.executemany(
                "INSERT OR IGNORE INTO insights(theme, quote, source_url, ebook_idea, created_at) VALUES (?, ?, ?, ?, ?)",
                [(i["theme"], i["quote"], i["source_url"], i.get("ebook_idea", ""), created) for i in items],
            )

    def list_insights(self) -> list[dict]:
        with closing(sqlite3.connect(self.db_path)) as db:
            db.row_factory = sqlite3.Row
            return [dict(row) for row in db.execute("SELECT * FROM insights ORDER BY id DESC")]
