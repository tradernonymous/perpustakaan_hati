"""Environment-only configuration; secret values never appear in repr."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from collections.abc import Mapping

REQUIRED_KEYS = ("THREADS_CLIENT_ID", "THREADS_CLIENT_SECRET", "OPENROUTER_API_KEY")


class MissingSecretError(ValueError):
    """Configuration is incomplete."""


def default_db_path() -> str:
    return str(Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "perpustakaan-hati/research.db")


@dataclass
class Settings:
    threads_client_id: str = ""
    threads_client_secret: str = field(default="", repr=False)
    openrouter_api_key: str = field(default="", repr=False)
    admin_password: str = field(default="", repr=False)
    redirect_uri: str = "http://127.0.0.1:8787/auth/callback"
    db_path: str = field(default_factory=default_db_path)
    openrouter_model: str = "openrouter/free"

    def missing_threads(self) -> list[str]:
        return [key for key, value in (("THREADS_CLIENT_ID", self.threads_client_id), ("THREADS_CLIENT_SECRET", self.threads_client_secret)) if not value]

    @classmethod
    def from_env(cls, environ: Mapping[str, str], *, strict: bool = True) -> "Settings":
        missing = [key for key in REQUIRED_KEYS if not environ.get(key)]
        if strict and missing:
            raise MissingSecretError("missing required env vars: " + ", ".join(missing))
        return cls(
            threads_client_id=environ.get("THREADS_CLIENT_ID", ""),
            threads_client_secret=environ.get("THREADS_CLIENT_SECRET", ""),
            openrouter_api_key=environ.get("OPENROUTER_API_KEY", ""),
            admin_password=environ.get("RESEARCH_ADMIN_PASSWORD", ""),
            redirect_uri=environ.get("THREADS_REDIRECT_URI", "http://127.0.0.1:8787/auth/callback"),
            db_path=environ.get("RESEARCH_DB_PATH", default_db_path()),
            openrouter_model=environ.get("OPENROUTER_MODEL", "openrouter/free"),
        )
