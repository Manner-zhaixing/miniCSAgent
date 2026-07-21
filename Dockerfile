FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock README.md ./
COPY main.py ./
COPY src ./src

RUN uv sync --locked --no-dev

EXPOSE 8000

CMD ["/app/.venv/bin/uvicorn", "mini_cs_agent.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
