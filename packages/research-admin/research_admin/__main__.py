"""Run the research admin; loopback by default, platform port when hosted."""

import os

import uvicorn

from .app import create_app
from .config import MissingSecretError, Settings
from .jobs import JobWorker


def _port(value: str) -> int:
    try:
        port = int(value)
    except ValueError:
        raise SystemExit("PORT must be a number.") from None
    if not 1 <= port <= 65535:
        raise SystemExit("PORT must be between 1 and 65535.")
    return port


def main() -> None:
    try:
        settings = Settings.from_env(dict(os.environ), strict=False)
    except MissingSecretError as exc:
        raise SystemExit(f"Configuration error: {exc} Set the missing variables and redeploy.") from None
    port = _port(os.environ.get("PORT") or os.environ.get("RESEARCH_ADMIN_PORT") or "8787")
    host = os.environ.get("RESEARCH_ADMIN_HOST") or ("0.0.0.0" if settings.public_mode else "127.0.0.1")
    app = create_app(settings)
    worker = JobWorker(app.state.process_next_job, poll_seconds=2.0)
    worker.start()
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            access_log=False,
            # Deliberately ignore X-Forwarded-For: a spoofable client address would
            # let an attacker rotate around the login rate limiter.
            proxy_headers=False,
        )
    finally:
        worker.stop()


if __name__ == "__main__":
    main()
