#!/bin/bash

uv run alembic upgrade head

uv run python -m app.scripts.create_admin

if [ "$ENV" = "dev" ]; then
    uv run python -m app.scripts.seed_db
fi

uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
