FROM ghcr.io/astral-sh/uv:bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

ENV UV_PYTHON_INSTALL_DIR /python
ENV UV_PYTHON_PREFERENCE=only-managed
RUN uv python install 3.12

WORKDIR /app
COPY pyproject.toml uv.lock /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM debian:bookworm-slim

RUN groupadd -g 10001 app && \
   useradd -u 10000 -g app app && \
   groupadd -g 10002 python && \
   useradd -u 10001 -g python python

COPY --from=builder --chown=python:python /python /python
COPY --from=builder --chown=app:app /app /app
USER app
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:5000/ || exit 1

CMD ["gunicorn", "--chdir", "/app", "-b", "0.0.0.0:5000", "app:create_app()"]