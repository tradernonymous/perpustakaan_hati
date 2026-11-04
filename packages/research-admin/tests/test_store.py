import sqlite3
from unittest.mock import patch

import pytest

from research_admin.store import EncryptedVault, SecretVault, Store, StoreError


class MemoryVault:
    def __init__(self):
        self.value = None

    def get(self):
        return self.value

    def set(self, value):
        self.value = value

    def delete(self):
        self.value = None


@pytest.fixture
def store(tmp_path):
    s = Store(str(tmp_path / "research.db"), vault=MemoryVault())
    s.init_schema()
    return s


def test_token_roundtrip_replaces_and_stays_out_of_sqlite(store):
    assert store.get_token() is None
    store.save_token("old-secret", 100)
    store.save_token("new-secret", 200)
    token = store.get_token()
    assert (token.access_token, token.expires_at) == ("new-secret", 200)
    assert "new-secret" not in repr(token)
    with sqlite3.connect(store.db_path) as db:
        dump = "".join(db.iterdump())
    assert "new-secret" not in dump and "old-secret" not in dump
    store.delete_token()
    assert store.get_token() is None


def test_insights_persist_and_repeat_runs_do_not_duplicate(store):
    item = {"theme": "Trust", "quote": "I can't trust", "source_url": "https://www.threads.com/@sample/post/1", "ebook_idea": "A reflection on trust"}
    store.save_insights([item])
    store.save_insights([item])
    result = Store(store.db_path, vault=store.vault).list_insights()
    assert len(result) == 1
    assert all(result[0][key] == value for key, value in item.items())
    assert result[0]["created_at"].endswith("+00:00")
    assert __import__("os").stat(store.db_path).st_mode & 0o777 == 0o600


def test_vault_unavailable_is_safe_and_never_stores_plaintext(store):
    with patch.object(store.vault, "set", side_effect=StoreError("keyring unavailable")):
        with pytest.raises(StoreError):
            store.save_token("secret", 123)
    assert store.get_token() is None


def test_secret_tool_absent_is_actionable(tmp_path):
    vault = SecretVault(str(tmp_path / "db"))
    with patch("research_admin.store.subprocess.run", side_effect=FileNotFoundError):
        with pytest.raises(StoreError, match="keyring"):
            vault.set("secret")


def test_encrypted_vault_roundtrip_keeps_plaintext_out_of_sqlite(tmp_path):
    db = str(tmp_path / "research.db")
    store = Store(db, vault=EncryptedVault(db, "a-long-random-token-key"))
    store.init_schema()
    store.save_token("threads-secret-token", 999)
    assert store.get_token().access_token == "threads-secret-token"
    with sqlite3.connect(db) as conn:
        dump = "".join(conn.iterdump())
    assert "threads-secret-token" not in dump
    store.delete_token()
    assert store.get_token() is None


def test_encrypted_vault_wrong_key_is_safe_error(tmp_path):
    db = str(tmp_path / "research.db")
    store = Store(db, vault=EncryptedVault(db, "right-key-material"))
    store.init_schema()
    store.save_token("threads-secret-token", 999)
    with pytest.raises(StoreError, match="decrypt") as error:
        Store(db, vault=EncryptedVault(db, "wrong-key-material")).get_token()
    assert "threads-secret-token" not in str(error.value)


def test_encrypted_vault_requires_key(tmp_path):
    with pytest.raises(StoreError, match="RESEARCH_TOKEN_KEY"):
        EncryptedVault(str(tmp_path / "research.db"), "")
