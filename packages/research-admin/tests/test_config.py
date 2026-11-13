import pytest

from research_admin.config import MissingSecretError, Settings


def test_from_env_reads_all_secrets():
    s = Settings.from_env(
        {
            "THREADS_CLIENT_ID": "id",
            "THREADS_CLIENT_SECRET": "sec",
            "OPENROUTER_API_KEY": "key",
        }
    )
    assert s.threads_client_id == "id"
    assert s.threads_client_secret == "sec"
    assert s.openrouter_api_key == "key"


def test_from_env_missing_secret_raises_with_key_names():
    try:
        Settings.from_env({})
        raise AssertionError("should raise")
    except MissingSecretError as e:
        assert "THREADS_CLIENT_ID" in str(e)


def test_unconfigured_startup_and_default_model():
    s = Settings.from_env({}, strict=False)
    assert s.openrouter_model == "openai/gpt-6-luna"
    assert "THREADS_CLIENT_ID" in s.missing_threads()
    assert not s.admin_password


def test_redirect_and_model_overrides_and_secret_repr():
    s = Settings.from_env({
        "THREADS_REDIRECT_URI": "https://localhost:8787/auth/callback",
        "OPENROUTER_MODEL": "vendor/example:free",
        "RESEARCH_ADMIN_PASSWORD": "private-admin-password",
        "OPENROUTER_API_KEY": "private-provider-key",
    }, strict=False)
    assert s.redirect_uri == "https://localhost:8787/auth/callback"
    assert s.openrouter_model == "vendor/example:free"
    assert "private-admin-password" not in repr(s)
    assert "private-provider-key" not in repr(s)


def test_railway_public_domain_fills_redirect_and_hosts():
    s = Settings.from_env({
        "RAILWAY_ENVIRONMENT": "production",
        "RAILWAY_PUBLIC_DOMAIN": "perpustakaan-production.up.railway.app",
        "RESEARCH_ADMIN_PASSWORD": "a-long-admin-password",
    }, strict=False)
    assert s.redirect_uri == "https://perpustakaan-production.up.railway.app/auth/callback"
    assert s.allowed_hosts == ("perpustakaan-production.up.railway.app",)
    assert s.public_mode is True


def test_explicit_redirect_and_hosts_override_railway_domain():
    s = Settings.from_env({
        "RAILWAY_ENVIRONMENT": "production",
        "RAILWAY_PUBLIC_DOMAIN": "internal.up.railway.app",
        "RESEARCH_ADMIN_PASSWORD": "a-long-admin-password",
        "THREADS_REDIRECT_URI": "https://research.example.com/auth/callback",
        "RESEARCH_ALLOWED_HOSTS": "research.example.com",
    }, strict=False)
    assert s.redirect_uri == "https://research.example.com/auth/callback"
    assert s.allowed_hosts == ("research.example.com",)


def test_public_mode_reports_every_problem_at_once():
    with pytest.raises(MissingSecretError) as error:
        Settings.from_env({"RAILWAY_ENVIRONMENT": "production", "RESEARCH_ADMIN_PASSWORD": "short"}, strict=False)
    message = str(error.value)
    assert "12 characters" in message
    assert "RAILWAY_PUBLIC_DOMAIN" in message


def test_public_mode_accepts_explicit_https_without_railway_domain():
    s = Settings.from_env({
        "RESEARCH_PUBLIC": "1",
        "RESEARCH_ADMIN_PASSWORD": "a-long-admin-password",
        "THREADS_REDIRECT_URI": "https://research.example.com/auth/callback",
        "RESEARCH_ALLOWED_HOSTS": "research.example.com",
    }, strict=False)
    assert s.public_mode is True
    assert s.secure_cookies is True


def test_railway_environment_turns_on_public_secure_defaults():
    s = Settings.from_env({
        "RAILWAY_ENVIRONMENT": "production",
        "RESEARCH_ADMIN_PASSWORD": "a-long-admin-password",
        "THREADS_REDIRECT_URI": "https://perpustakaan.up.railway.app/auth/callback",
    }, strict=False)
    assert s.public_mode is True
    assert s.secure_cookies is True


def test_allowed_hosts_are_configurable():
    s = Settings.from_env({"RESEARCH_ALLOWED_HOSTS": "perpustakaan.up.railway.app, localhost"}, strict=False)
    assert s.allowed_hosts == ("perpustakaan.up.railway.app", "localhost")


def test_public_mode_refuses_short_or_missing_admin_password():
    with pytest.raises(MissingSecretError, match="at least 12"):
        Settings.from_env({"RAILWAY_ENVIRONMENT": "production", "RESEARCH_ADMIN_PASSWORD": "short"}, strict=False)
    with pytest.raises(MissingSecretError, match="at least 12"):
        Settings.from_env({"RAILWAY_ENVIRONMENT": "production"}, strict=False)


def test_public_mode_requires_https_redirect():
    with pytest.raises(MissingSecretError, match="https"):
        Settings.from_env({"RAILWAY_ENVIRONMENT": "production", "RESEARCH_ADMIN_PASSWORD": "a-long-admin-password"}, strict=False)


def test_sqlite_vault_requires_a_key():
    with pytest.raises(MissingSecretError, match="RESEARCH_TOKEN_KEY"):
        Settings.from_env({"RESEARCH_VAULT": "sqlite"}, strict=False)


def test_unknown_vault_is_rejected():
    with pytest.raises(MissingSecretError, match="RESEARCH_VAULT"):
        Settings.from_env({"RESEARCH_VAULT": "magic"}, strict=False)


def test_db_path_defaults_to_user_state_dir():
    s = Settings.from_env(
        {
            "THREADS_CLIENT_ID": "id",
            "THREADS_CLIENT_SECRET": "sec",
            "OPENROUTER_API_KEY": "key",
        }
    )
    assert s.db_path.endswith("research.db")
