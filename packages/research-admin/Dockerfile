# Railway image for the Threads research admin.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY research_admin ./research_admin
RUN uv sync --locked --no-dev

# Railway mounts the persistent volume here; override RESEARCH_DB_PATH to change it.
ENV RESEARCH_DB_PATH=/data/research.db
EXPOSE 8080

CMD ["python", "-m", "research_admin"]
