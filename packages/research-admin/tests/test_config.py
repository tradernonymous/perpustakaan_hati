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


def test_unconfigured_startup_and_free_model():
    s = Settings.from_env({}, strict=False)
    assert s.openrouter_model == "openrouter/free"
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


def test_db_path_defaults_to_user_state_dir():
    s = Settings.from_env(
        {
            "THREADS_CLIENT_ID": "id",
            "THREADS_CLIENT_SECRET": "sec",
            "OPENROUTER_API_KEY": "key",
        }
    )
    assert s.db_path.endswith("research.db")
