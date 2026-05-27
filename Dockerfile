FROM ghcr.io/astral-sh/uv:latest AS uv_bin

FROM python:3.12-slim

COPY --from=uv_bin /uv /uvx /bin/

WORKDIR /app

# UV_COMPILE_BYTECODE=1 here is good for the build stage
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_CACHE_DIR=/tmp/uv_cache

COPY pyproject.toml uv.lock ./

# Install dependencies without dev group
RUN uv sync --frozen --no-install-project --no-dev

COPY . .

# Final sync and bytecode compilation
RUN uv sync --frozen --no-dev

# Disable compilation in runtime to save CPU
ENV UV_COMPILE_BYTECODE=0

CMD [ "sh", "app/start.sh" ]
