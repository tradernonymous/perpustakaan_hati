"""Run the local research admin server on loopback only."""

import os

import uvicorn

from .app import create_app
from .config import Settings


def main() -> None:
    uvicorn.run(
        create_app(Settings.from_env(dict(os.environ), strict=False)),
        host="127.0.0.1",
        port=int(os.environ.get("RESEARCH_ADMIN_PORT", "8787")),
        access_log=False,
    )


if __name__ == "__main__":
    main()
