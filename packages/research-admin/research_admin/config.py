"""Environment-only configuration; secret values never appear in repr."""

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

REQUIRED_KEYS = ("THREADS_CLIENT_ID", "THREADS_CLIENT_SECRET", "OPENROUTER_API_KEY")
DEFAULT_HOSTS = ("127.0.0.1", "localhost", "testserver")
TRUE_VALUES = {"1", "true", "yes", "on"}


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
    openrouter_model: str = "openai/gpt-6-luna"
    allowed_hosts: tuple[str, ...] = DEFAULT_HOSTS
    secure_cookies: bool = False
    public_mode: bool = False
    vault_kind: str = "keyring"
    token_key: str = field(default="", repr=False)
    groq_api_key: str = field(default="", repr=False)
    nim_api_key: str = field(default="", repr=False)
    openai_compat_base_url: str = ""
    openai_compat_api_key: str = field(default="", repr=False)
    ai_provider_priority: tuple[str, ...] = ("openrouter", "groq", "nim", "openai_compat")
    allowed_models: tuple[str, ...] = ()
    threads_webhook_verify_token: str = field(default="", repr=False)
    threads_app_secret: str = field(default="", repr=False)
    telegram_bot_token: str = field(default="", repr=False)
    telegram_chat_id: str = ""
    mini_app_url: str = ""
    web_internal_url: str = ""
    sync_secret: str = field(default="", repr=False)
    watchlist_hours: int = 24

    def missing_threads(self) -> list[str]:
        return [key for key, value in (("THREADS_CLIENT_ID", self.threads_client_id), ("THREADS_CLIENT_SECRET", self.threads_client_secret)) if not value]

    @classmethod
    def from_env(cls, environ: Mapping[str, str], *, strict: bool = True) -> "Settings":
        missing = [key for key in REQUIRED_KEYS if not environ.get(key)]
        if strict and missing:
            raise MissingSecretError("missing required env vars: " + ", ".join(missing))
        public_mode = environ.get("RESEARCH_PUBLIC", "").strip().lower() in TRUE_VALUES or bool(environ.get("RAILWAY_ENVIRONMENT"))
        # Railway injects the generated domain; derive the callback and host allowlist from it
        # so a deploy only needs the secrets, not hand-typed URLs.
        public_domain = environ.get("RAILWAY_PUBLIC_DOMAIN", "").strip().lower().split("/")[0]
        password = environ.get("RESEARCH_ADMIN_PASSWORD", "")
        redirect_uri = (environ.get("THREADS_REDIRECT_URI") or environ.get("THREADS_REDIRECT_URL") or "").strip()
        if not redirect_uri:
            redirect_uri = f"https://{public_domain}/auth/callback" if public_mode and public_domain else "http://127.0.0.1:8787/auth/callback"
        problems = []
        if public_mode:
            if len(password) < 12:
                problems.append("RESEARCH_ADMIN_PASSWORD must be at least 12 characters")
            if not redirect_uri.startswith("https://"):
                problems.append("THREADS_REDIRECT_URI must be an https:// URL, or generate a public domain so RAILWAY_PUBLIC_DOMAIN is set")
        if problems:
            raise MissingSecretError("public mode is misconfigured: " + "; ".join(problems) + ".")
        vault_kind = environ.get("RESEARCH_VAULT", "keyring").strip().lower()
        if vault_kind not in ("keyring", "sqlite"):
            raise MissingSecretError("RESEARCH_VAULT must be 'keyring' or 'sqlite'.")
        token_key = environ.get("RESEARCH_TOKEN_KEY", "")
        if vault_kind == "sqlite" and not token_key:
            raise MissingSecretError("RESEARCH_TOKEN_KEY is required when RESEARCH_VAULT=sqlite.")
        hosts = tuple(host.strip().lower() for host in environ.get("RESEARCH_ALLOWED_HOSTS", "").split(",") if host.strip())
        if not hosts and public_mode and public_domain:
            hosts = (public_domain,)
        priority = tuple(
            p.strip().lower()
            for p in environ.get("AI_PROVIDER_PRIORITY", "openrouter,groq,nim,openai_compat").split(",")
            if p.strip()
        ) or ("openrouter", "groq", "nim", "openai_compat")
        allowed_models = tuple(m.strip() for m in environ.get("RESEARCH_ALLOWED_MODELS", "").split(",") if m.strip())
        try:
            watchlist_hours = max(1, int(environ.get("RESEARCH_WATCHLIST_HOURS", "24") or "24"))
        except ValueError:
            watchlist_hours = 24
        return cls(
            threads_client_id=environ.get("THREADS_CLIENT_ID", ""),
            threads_client_secret=environ.get("THREADS_CLIENT_SECRET", ""),
            openrouter_api_key=environ.get("OPENROUTER_API_KEY", ""),
            admin_password=password,
            redirect_uri=redirect_uri,
            db_path=environ.get("RESEARCH_DB_PATH", default_db_path()),
            openrouter_model=environ.get("OPENROUTER_MODEL", "openai/gpt-6-luna"),
            allowed_hosts=hosts or DEFAULT_HOSTS,
            secure_cookies=public_mode or environ.get("RESEARCH_SECURE_COOKIES", "").strip().lower() in TRUE_VALUES,
            public_mode=public_mode,
            vault_kind=vault_kind,
            token_key=token_key,
            groq_api_key=environ.get("GROQ_API_KEY", ""),
            nim_api_key=environ.get("NIM_API_KEY", ""),
            openai_compat_base_url=environ.get("OPENAI_COMPAT_BASE_URL", "").strip().rstrip("/"),
            openai_compat_api_key=environ.get("OPENAI_COMPAT_API_KEY", ""),
            ai_provider_priority=priority,
            allowed_models=allowed_models,
            threads_webhook_verify_token=environ.get("THREADS_WEBHOOK_VERIFY_TOKEN", ""),
            threads_app_secret=environ.get("THREADS_APP_SECRET", ""),
            telegram_bot_token=environ.get("TELEGRAM_BOT_TOKEN", ""),
            telegram_chat_id=environ.get("TELEGRAM_CHAT_ID", "").strip(),
            mini_app_url=environ.get("MINI_APP_URL", "").strip().rstrip("/"),
            web_internal_url=environ.get("WEB_INTERNAL_URL", "").strip().rstrip("/"),
            sync_secret=environ.get("RESEARCH_SYNC_SECRET", ""),
            watchlist_hours=watchlist_hours,
        )
