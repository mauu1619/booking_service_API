#!/bin/bash

uv run alembic upgrade head

uv run create-admin

if [ "$ENV" = "dev" ]; then
    uv run seed
fi

uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
